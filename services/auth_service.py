import json
import secrets
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

import pymysql
from pymysql.cursors import DictCursor


VALID_ROLES = {"user", "admin"}


class AuthError(Exception):
    pass


class _MySQLConnection:
    def __init__(self, database_url):
        parsed = urlparse(database_url)
        self._conn = pymysql.connect(
            host=parsed.hostname or "127.0.0.1",
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=(parsed.path or "/").lstrip("/"),
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, _exc, _tb):
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()
        self._conn.close()

    def execute(self, sql, params=None):
        cursor = self._conn.cursor()
        cursor.execute(self._convert_sql(sql), params or ())
        return cursor

    def _convert_sql(self, sql):
        return sql.replace("?", "%s")


class UserStore:
    def __init__(self, database_url, secret_key, token_max_age=7 * 24 * 60 * 60):
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL is required. Example: "
                "mysql+pymysql://sework:password@127.0.0.1:3306/sework"
            )
        if not database_url.startswith(("mysql://", "mysql+pymysql://")):
            raise RuntimeError("DATABASE_URL must use mysql:// or mysql+pymysql://")

        self.database_url = database_url
        self.secret_key = secret_key
        self.token_max_age = token_max_age
        self.serializer = URLSafeTimedSerializer(secret_key)

    def init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(32) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(16) NOT NULL,
                    is_active TINYINT(1) NOT NULL DEFAULT 1,
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL,
                    CHECK (role IN ('user', 'admin'))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_indexes (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    index_name VARCHAR(64) NOT NULL,
                    collection_name VARCHAR(128) NOT NULL UNIQUE,
                    data_path TEXT NOT NULL,
                    source_format VARCHAR(32),
                    cell_count INT,
                    gene_count INT,
                    vector_dim INT,
                    embedding_key VARCHAR(128),
                    metadata_keys JSON NOT NULL,
                    hnsw_params JSON NOT NULL,
                    search_params JSON NOT NULL,
                    build_time_ms DOUBLE,
                    is_active TINYINT(1) NOT NULL DEFAULT 0,
                    status VARCHAR(32) NOT NULL DEFAULT 'ready',
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL,
                    UNIQUE KEY uq_user_index_name (user_id, index_name),
                    CONSTRAINT fk_user_indexes_user
                        FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS index_build_jobs (
                    job_id VARCHAR(64) NOT NULL PRIMARY KEY,
                    user_id INT NOT NULL,
                    data_path TEXT NOT NULL,
                    index_name VARCHAR(64) NOT NULL,
                    hnsw_params JSON NOT NULL,
                    search_params JSON NOT NULL,
                    activate TINYINT(1) NOT NULL DEFAULT 1,
                    status VARCHAR(32) NOT NULL,
                    stage VARCHAR(64) NOT NULL,
                    message TEXT,
                    progress_pct DOUBLE NOT NULL DEFAULT 0,
                    processed_cells INT NOT NULL DEFAULT 0,
                    total_cells INT NULL,
                    elapsed_seconds DOUBLE NOT NULL DEFAULT 0,
                    rate_cells_per_second DOUBLE NULL,
                    eta_seconds DOUBLE NULL,
                    dataset_summary JSON NULL,
                    history JSON NOT NULL,
                    result_json JSON NULL,
                    error_text TEXT NULL,
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL,
                    started_at VARCHAR(40) NULL,
                    finished_at VARCHAR(40) NULL,
                    INDEX idx_build_jobs_user_status (user_id, status, updated_at),
                    CONSTRAINT fk_build_jobs_user
                        FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

    def mark_unfinished_build_jobs_failed(self, reason="service restarted before task finished"):
        now = self._now()
        history_item = {"time": now, "stage": "failed", "text": reason}
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT job_id, history
                FROM index_build_jobs
                WHERE status IN ('queued', 'running')
                """
            ).fetchall()
            for row in rows:
                history = json.loads(row.get("history") or "[]")
                history.append(history_item)
                conn.execute(
                    """
                    UPDATE index_build_jobs
                    SET status = 'failed',
                        stage = 'failed',
                        message = ?,
                        error_text = ?,
                        finished_at = ?,
                        updated_at = ?,
                        history = ?
                    WHERE job_id = ?
                    """,
                    (
                        reason,
                        reason,
                        now,
                        now,
                        json.dumps(history[-12:], ensure_ascii=False),
                        row["job_id"],
                    ),
                )

    def register(self, username, password, role="user", admin_key=None, expected_admin_key=None):
        username = self._normalize_username(username)
        self._validate_password(password)

        if role not in VALID_ROLES:
            raise AuthError("role must be user or admin")

        now = self._now()
        password_hash = generate_password_hash(password)

        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (username, password_hash, role, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, 1, ?, ?)
                    """,
                    (username, password_hash, role, now, now),
                )
                user_id = cursor.lastrowid
        except pymysql.err.IntegrityError as exc:
            raise AuthError("username already exists") from exc

        return self.get_user(user_id)

    def login(self, username, password):
        username = self._normalize_username(username)
        user = self.get_user_by_username(username, include_password=True)
        if not user or not check_password_hash(user["password_hash"], password or ""):
            raise AuthError("invalid username or password")
        if not user["is_active"]:
            raise AuthError("user is disabled")

        public_user = self._public_user(user)
        token = self.create_token(public_user)
        return token, public_user

    def create_token(self, user):
        payload = {
            "user_id": user["id"],
            "nonce": secrets.token_urlsafe(8),
        }
        return self.serializer.dumps(payload, salt="auth-token")

    def verify_token(self, token):
        if not token:
            raise AuthError("missing authorization token")

        try:
            payload = self.serializer.loads(
                token,
                salt="auth-token",
                max_age=self.token_max_age,
            )
        except SignatureExpired as exc:
            raise AuthError("authorization token expired") from exc
        except BadSignature as exc:
            raise AuthError("invalid authorization token") from exc

        user = self.get_user(payload.get("user_id"))
        if not user:
            raise AuthError("user not found")
        if not user["is_active"]:
            raise AuthError("user is disabled")
        return user

    def list_users(self):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, username, role, is_active, created_at, updated_at
                FROM users
                ORDER BY id ASC
                """
            ).fetchall()
        return [self._public_user(dict(row)) for row in rows]

    def update_user(self, user_id, role=None, is_active=None):
        user = self.get_user(user_id)
        if not user:
            raise AuthError("user not found")

        updates = []
        values = []
        if role is not None:
            if role not in VALID_ROLES:
                raise AuthError("role must be user or admin")
            updates.append("role = ?")
            values.append(role)
        if is_active is not None:
            updates.append("is_active = ?")
            values.append(1 if bool(is_active) else 0)

        if not updates:
            return user

        updates.append("updated_at = ?")
        values.append(self._now())
        values.append(user_id)

        with self._connect() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                values,
            )
        return self.get_user(user_id)

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if not user:
            raise AuthError("user not found")

        with self._connect() as conn:
            conn.execute("DELETE FROM user_indexes WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

        return user

    def get_user(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, username, role, is_active, created_at, updated_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
        return self._public_user(dict(row)) if row else None

    def get_user_by_username(self, username, include_password=False):
        fields = "id, username, role, is_active, created_at, updated_at"
        if include_password:
            fields += ", password_hash"

        with self._connect() as conn:
            row = conn.execute(
                f"SELECT {fields} FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return dict(row) if row else None

    def user_count(self):
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return row["count"]

    def list_user_indexes(self, user_id):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, user_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, metadata_keys,
                    hnsw_params, search_params, build_time_ms, is_active, status,
                    created_at, updated_at
                FROM user_indexes
                WHERE user_id = ?
                ORDER BY updated_at DESC, id DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._row_to_user_index(row) for row in rows]

    def get_user_index(self, user_id, index_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    id, user_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, metadata_keys,
                    hnsw_params, search_params, build_time_ms, is_active, status,
                    created_at, updated_at
                FROM user_indexes
                WHERE user_id = ? AND id = ?
                """,
                (user_id, index_id),
            ).fetchone()
        return self._row_to_user_index(row) if row else None

    def get_active_user_index(self, user_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    id, user_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, metadata_keys,
                    hnsw_params, search_params, build_time_ms, is_active, status,
                    created_at, updated_at
                FROM user_indexes
                WHERE user_id = ? AND is_active = 1 AND status = 'ready'
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
            if row:
                return self._row_to_user_index(row)

            fallback = conn.execute(
                """
                SELECT
                    id, user_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, metadata_keys,
                    hnsw_params, search_params, build_time_ms, is_active, status,
                    created_at, updated_at
                FROM user_indexes
                WHERE user_id = ? AND status = 'ready'
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return self._row_to_user_index(fallback) if fallback else None

    def create_user_index(
        self,
        user_id,
        index_name,
        collection_name,
        data_path,
        source_format,
        cell_count,
        gene_count,
        vector_dim,
        embedding_key,
        metadata_keys,
        hnsw_params,
        search_params,
        build_time_ms,
        is_active=True,
        status="ready",
    ):
        index_name = self._normalize_index_name(index_name)
        now = self._now()
        metadata_keys_json = json.dumps(list(metadata_keys or []), ensure_ascii=False)
        hnsw_params_json = json.dumps(hnsw_params or {}, ensure_ascii=False)
        search_params_json = json.dumps(search_params or {}, ensure_ascii=False)

        try:
            with self._connect() as conn:
                if is_active:
                    conn.execute(
                        "UPDATE user_indexes SET is_active = 0, updated_at = ? WHERE user_id = ?",
                        (now, user_id),
                    )
                cursor = conn.execute(
                    """
                    INSERT INTO user_indexes (
                        user_id, index_name, collection_name, data_path, source_format,
                        cell_count, gene_count, vector_dim, embedding_key, metadata_keys,
                        hnsw_params, search_params, build_time_ms, is_active, status,
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        index_name,
                        collection_name,
                        str(data_path),
                        source_format,
                        int(cell_count),
                        int(gene_count),
                        int(vector_dim),
                        embedding_key,
                        metadata_keys_json,
                        hnsw_params_json,
                        search_params_json,
                        float(build_time_ms),
                        1 if is_active else 0,
                        status,
                        now,
                        now,
                    ),
                )
                index_id = cursor.lastrowid
        except pymysql.err.IntegrityError as exc:
            raise AuthError("index name already exists for this user") from exc

        return self.get_user_index(user_id, index_id)

    def set_active_user_index(self, user_id, index_id):
        index = self.get_user_index(user_id, index_id)
        if not index:
            raise AuthError("index not found")
        if index["status"] != "ready":
            raise AuthError("index is not ready")

        now = self._now()
        with self._connect() as conn:
            conn.execute(
                "UPDATE user_indexes SET is_active = 0, updated_at = ? WHERE user_id = ?",
                (now, user_id),
            )
            conn.execute(
                "UPDATE user_indexes SET is_active = 1, updated_at = ? WHERE id = ?",
                (now, index_id),
            )
        return self.get_user_index(user_id, index_id)

    def find_reusable_user_index(self, user_id, data_path, hnsw_params=None, search_params=None):
        normalized_path = str(data_path or "").strip()
        target_hnsw = json.dumps(hnsw_params or {}, ensure_ascii=False, sort_keys=True)
        target_search = json.dumps(search_params or {}, ensure_ascii=False, sort_keys=True)
        indexes = self.list_user_indexes(user_id)
        for item in indexes:
            if item["status"] != "ready":
                continue
            if str(item.get("data_path") or "").strip() != normalized_path:
                continue
            item_hnsw = json.dumps(item.get("hnsw_params") or {}, ensure_ascii=False, sort_keys=True)
            item_search = json.dumps(item.get("search_params") or {}, ensure_ascii=False, sort_keys=True)
            if item_hnsw == target_hnsw and item_search == target_search:
                return item
        return None

    def get_latest_running_build_job(self, user_id, data_path=None):
        query = """
            SELECT *
            FROM index_build_jobs
            WHERE user_id = ? AND status IN ('queued', 'running')
        """
        params = [user_id]
        if data_path is not None:
            query += " AND data_path = ?"
            params.append(str(data_path))
        query += " ORDER BY updated_at DESC, created_at DESC LIMIT 1"
        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        return self._row_to_build_job(row) if row else None

    def create_index_build_job(
        self,
        *,
        job_id,
        user_id,
        data_path,
        index_name,
        hnsw_params,
        search_params,
        activate,
        status,
        stage,
        message,
        progress_pct,
        processed_cells,
        total_cells,
        elapsed_seconds,
        rate_cells_per_second,
        eta_seconds,
        dataset_summary,
        history,
        result,
        error,
        created_at,
        updated_at,
        started_at,
        finished_at,
    ):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO index_build_jobs (
                    job_id, user_id, data_path, index_name, hnsw_params, search_params,
                    activate, status, stage, message, progress_pct, processed_cells, total_cells,
                    elapsed_seconds, rate_cells_per_second, eta_seconds, dataset_summary, history,
                    result_json, error_text, created_at, updated_at, started_at, finished_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    user_id,
                    str(data_path),
                    index_name,
                    json.dumps(hnsw_params or {}, ensure_ascii=False),
                    json.dumps(search_params or {}, ensure_ascii=False),
                    1 if bool(activate) else 0,
                    status,
                    stage,
                    message,
                    float(progress_pct or 0),
                    int(processed_cells or 0),
                    int(total_cells) if total_cells is not None else None,
                    float(elapsed_seconds or 0),
                    float(rate_cells_per_second) if rate_cells_per_second is not None else None,
                    float(eta_seconds) if eta_seconds is not None else None,
                    json.dumps(dataset_summary, ensure_ascii=False) if dataset_summary is not None else None,
                    json.dumps(history or [], ensure_ascii=False),
                    json.dumps(result, ensure_ascii=False) if result is not None else None,
                    error,
                    created_at,
                    updated_at,
                    started_at,
                    finished_at,
                ),
            )
        return self.get_index_build_job(job_id)

    def update_index_build_job(self, job_id, **fields):
        if not fields:
            return self.get_index_build_job(job_id)

        updates = []
        values = []
        json_fields = {
            "hnsw_params",
            "search_params",
            "dataset_summary",
            "history",
            "result_json",
        }
        renamed = {"result": "result_json", "error": "error_text"}

        for raw_key, raw_value in fields.items():
            key = renamed.get(raw_key, raw_key)
            if key in json_fields:
                updates.append(f"{key} = ?")
                values.append(json.dumps(raw_value, ensure_ascii=False) if raw_value is not None else None)
            else:
                updates.append(f"{key} = ?")
                values.append(raw_value)

        if "updated_at" not in fields:
            updates.append("updated_at = ?")
            values.append(self._now())

        values.append(job_id)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE index_build_jobs SET {', '.join(updates)} WHERE job_id = ?",
                values,
            )
        return self.get_index_build_job(job_id)

    def get_index_build_job(self, job_id):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM index_build_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            ).fetchone()
        return self._row_to_build_job(row) if row else None

    def _connect(self):
        return _MySQLConnection(self.database_url)

    def _normalize_username(self, username):
        username = (username or "").strip()
        if len(username) < 3 or len(username) > 32:
            raise AuthError("username length must be 3-32 characters")
        return username

    def _normalize_index_name(self, index_name):
        index_name = (index_name or "").strip()
        if len(index_name) < 3 or len(index_name) > 64:
            raise AuthError("index_name length must be 3-64 characters")
        return index_name

    def _validate_password(self, password):
        if not password or len(password) < 6:
            raise AuthError("password length must be at least 6 characters")

    def _public_user(self, user):
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "is_active": bool(user["is_active"]),
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }

    def _row_to_user_index(self, row):
        item = dict(row)
        item["is_active"] = bool(item["is_active"])
        item["metadata_keys"] = json.loads(item.get("metadata_keys") or "[]")
        item["hnsw_params"] = json.loads(item.get("hnsw_params") or "{}")
        item["search_params"] = json.loads(item.get("search_params") or "{}")
        return item

    def _row_to_build_job(self, row):
        item = dict(row)
        item["activate"] = bool(item.get("activate"))
        item["progress_pct"] = float(item.get("progress_pct") or 0)
        item["processed_cells"] = int(item.get("processed_cells") or 0)
        item["total_cells"] = int(item["total_cells"]) if item.get("total_cells") is not None else None
        item["elapsed_seconds"] = float(item.get("elapsed_seconds") or 0)
        item["rate_cells_per_second"] = (
            float(item["rate_cells_per_second"]) if item.get("rate_cells_per_second") is not None else None
        )
        item["eta_seconds"] = float(item["eta_seconds"]) if item.get("eta_seconds") is not None else None
        item["hnsw_params"] = json.loads(item.get("hnsw_params") or "{}")
        item["search_params"] = json.loads(item.get("search_params") or "{}")
        item["dataset_summary"] = json.loads(item.get("dataset_summary") or "null")
        item["history"] = json.loads(item.get("history") or "[]")
        item["result"] = json.loads(item.get("result_json") or "null")
        item["error"] = item.get("error_text")
        item.pop("result_json", None)
        item.pop("error_text", None)
        return item

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
