import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

import pymysql
from pymysql.cursors import DictCursor


VALID_ROLES = {"user", "admin", "super_admin"}


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
                    role ENUM('user', 'admin', 'super_admin') NOT NULL,
                    is_active TINYINT(1) NOT NULL DEFAULT 1,
                    display_name VARCHAR(64) NULL,
                    email VARCHAR(128) NULL,
                    last_login_at VARCHAR(40) NULL,
                    last_login_ip VARCHAR(64) NULL,
                    created_by INT NULL,
                    disabled_reason VARCHAR(255) NULL,
                    token_version INT NOT NULL DEFAULT 1,
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    owner_user_id INT NOT NULL,
                    dataset_name VARCHAR(128) NOT NULL,
                    data_path TEXT NOT NULL,
                    source_format VARCHAR(32) NULL,
                    cell_count INT NULL,
                    gene_count INT NULL,
                    vector_dim INT NULL,
                    embedding_key VARCHAR(128) NULL,
                    visualization_source VARCHAR(128) NULL,
                    metadata_summary JSON NULL,
                    status VARCHAR(32) NOT NULL DEFAULT 'ready',
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL,
                    UNIQUE KEY uq_user_dataset_path (owner_user_id, data_path(255)),
                    INDEX idx_datasets_owner_updated (owner_user_id, updated_at),
                    CONSTRAINT fk_datasets_owner
                        FOREIGN KEY (owner_user_id) REFERENCES users(id)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_indexes (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    dataset_id INT NULL,
                    index_name VARCHAR(64) NOT NULL,
                    collection_name VARCHAR(128) NOT NULL UNIQUE,
                    data_path TEXT NOT NULL,
                    source_format VARCHAR(32),
                    cell_count INT,
                    gene_count INT,
                    vector_dim INT,
                    embedding_key VARCHAR(128),
                    visualization_source VARCHAR(128),
                    index_type VARCHAR(32) NOT NULL,
                    distance_metric VARCHAR(32) NOT NULL,
                    effective_metric VARCHAR(32) NOT NULL,
                    quantization_config JSON NULL,
                    metadata_keys JSON NOT NULL,
                    hnsw_params JSON NOT NULL,
                    search_params JSON NOT NULL,
                    created_by INT NULL,
                    build_time_ms DOUBLE,
                    is_active TINYINT(1) NOT NULL DEFAULT 0,
                    status VARCHAR(32) NOT NULL DEFAULT 'ready',
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL,
                    UNIQUE KEY uq_user_index_name (user_id, index_name),
                    CONSTRAINT fk_user_indexes_user
                        FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_user_indexes_dataset
                        FOREIGN KEY (dataset_id) REFERENCES datasets(id)
                        ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_audit_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    actor_user_id INT NOT NULL,
                    actor_role VARCHAR(16) NOT NULL,
                    action_type VARCHAR(64) NOT NULL,
                    target_user_id INT NULL,
                    target_index_id INT NULL,
                    target_dataset_id INT NULL,
                    target_username VARCHAR(32) NULL,
                    detail_json JSON NULL,
                    ip_address VARCHAR(64) NULL,
                    created_at VARCHAR(40) NOT NULL,
                    INDEX idx_admin_audit_created (created_at),
                    INDEX idx_admin_audit_actor (actor_user_id, created_at),
                    INDEX idx_admin_audit_target_user (target_user_id, created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS index_build_jobs (
                    job_id VARCHAR(64) NOT NULL PRIMARY KEY,
                    user_id INT NOT NULL,
                    dataset_id INT NULL,
                    requested_by INT NULL,
                    data_path TEXT NOT NULL,
                    index_name VARCHAR(64) NOT NULL,
                    index_type VARCHAR(32) NOT NULL,
                    distance_metric VARCHAR(32) NOT NULL,
                    effective_metric VARCHAR(32) NOT NULL,
                    hnsw_params JSON NOT NULL,
                    search_params JSON NOT NULL,
                    quantization_config JSON NULL,
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
                    trigger_source VARCHAR(32) NOT NULL DEFAULT 'user_ui',
                    job_type VARCHAR(32) NOT NULL DEFAULT 'build_index',
                    created_at VARCHAR(40) NOT NULL,
                    updated_at VARCHAR(40) NOT NULL,
                    started_at VARCHAR(40) NULL,
                    finished_at VARCHAR(40) NULL,
                    INDEX idx_build_jobs_user_status (user_id, status, updated_at),
                    CONSTRAINT fk_build_jobs_user
                        FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE
                        ,
                    CONSTRAINT fk_build_jobs_dataset
                        FOREIGN KEY (dataset_id) REFERENCES datasets(id)
                        ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            self._migrate_schema(conn)

    def _migrate_schema(self, conn):
        self._drop_check_constraints(conn, "users")
        conn.execute(
            """
            ALTER TABLE users
            MODIFY COLUMN role ENUM('user', 'admin', 'super_admin') NOT NULL
            """
        )
        migration_columns = [
            ("users", "display_name", "VARCHAR(64) NULL"),
            ("users", "email", "VARCHAR(128) NULL"),
            ("users", "last_login_at", "VARCHAR(40) NULL"),
            ("users", "last_login_ip", "VARCHAR(64) NULL"),
            ("users", "created_by", "INT NULL"),
            ("users", "disabled_reason", "VARCHAR(255) NULL"),
            ("users", "token_version", "INT NOT NULL DEFAULT 1"),
            ("user_indexes", "index_type", "VARCHAR(32) NOT NULL DEFAULT 'hnsw'"),
            ("user_indexes", "distance_metric", "VARCHAR(32) NOT NULL DEFAULT 'cosine'"),
            ("user_indexes", "effective_metric", "VARCHAR(32) NOT NULL DEFAULT 'cosine'"),
            ("user_indexes", "quantization_config", "JSON NULL"),
            ("user_indexes", "dataset_id", "INT NULL"),
            ("user_indexes", "visualization_source", "VARCHAR(128) NULL"),
            ("user_indexes", "created_by", "INT NULL"),
            ("index_build_jobs", "index_type", "VARCHAR(32) NOT NULL DEFAULT 'hnsw'"),
            ("index_build_jobs", "distance_metric", "VARCHAR(32) NOT NULL DEFAULT 'cosine'"),
            ("index_build_jobs", "effective_metric", "VARCHAR(32) NOT NULL DEFAULT 'cosine'"),
            ("index_build_jobs", "quantization_config", "JSON NULL"),
            ("index_build_jobs", "dataset_id", "INT NULL"),
            ("index_build_jobs", "requested_by", "INT NULL"),
            ("index_build_jobs", "trigger_source", "VARCHAR(32) NOT NULL DEFAULT 'user_ui'"),
            ("index_build_jobs", "job_type", "VARCHAR(32) NOT NULL DEFAULT 'build_index'"),
        ]
        for table_name, column_name, column_sql in migration_columns:
            if not self._column_exists(conn, table_name, column_name):
                conn.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"
                )
        self._add_foreign_key_if_missing(
            conn,
            table_name="user_indexes",
            constraint_name="fk_user_indexes_dataset",
            column_name="dataset_id",
            ref_table="datasets",
            ref_column="id",
            on_delete="SET NULL",
        )
        self._add_foreign_key_if_missing(
            conn,
            table_name="index_build_jobs",
            constraint_name="fk_build_jobs_dataset",
            column_name="dataset_id",
            ref_table="datasets",
            ref_column="id",
            on_delete="SET NULL",
        )

        conn.execute(
            """
            UPDATE user_indexes
            SET index_type = 'hnsw'
            WHERE index_type IS NULL OR index_type = ''
            """
        )
        conn.execute(
            """
            UPDATE user_indexes
            SET distance_metric = 'cosine'
            WHERE distance_metric IS NULL OR distance_metric = ''
            """
        )
        conn.execute(
            """
            UPDATE user_indexes
            SET effective_metric = 'cosine'
            WHERE effective_metric IS NULL OR effective_metric = ''
            """
        )
        conn.execute(
            """
            UPDATE user_indexes
            SET quantization_config = JSON_OBJECT()
            WHERE quantization_config IS NULL
            """
        )
        conn.execute(
            """
            UPDATE users
            SET token_version = 1
            WHERE token_version IS NULL OR token_version < 1
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET index_type = 'hnsw'
            WHERE index_type IS NULL OR index_type = ''
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET distance_metric = 'cosine'
            WHERE distance_metric IS NULL OR distance_metric = ''
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET effective_metric = 'cosine'
            WHERE effective_metric IS NULL OR effective_metric = ''
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET quantization_config = JSON_OBJECT()
            WHERE quantization_config IS NULL
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET requested_by = user_id
            WHERE requested_by IS NULL
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET trigger_source = 'user_ui'
            WHERE trigger_source IS NULL OR trigger_source = ''
            """
        )
        conn.execute(
            """
            UPDATE index_build_jobs
            SET job_type = 'build_index'
            WHERE job_type IS NULL OR job_type = ''
            """
        )
        self._backfill_dataset_records(conn)

    def _column_exists(self, conn, table_name, column_name):
        row = conn.execute(
            f"SHOW COLUMNS FROM {table_name} LIKE ?",
            (column_name,),
        ).fetchone()
        return row is not None

    def _constraint_exists(self, conn, table_name, constraint_name):
        row = conn.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = ?
              AND CONSTRAINT_NAME = ?
            """,
            (table_name, constraint_name),
        ).fetchone()
        return row is not None

    def _drop_check_constraints(self, conn, table_name):
        rows = conn.execute(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = ?
              AND CONSTRAINT_TYPE = 'CHECK'
            """,
            (table_name,),
        ).fetchall()
        for row in rows:
            conn.execute(f"ALTER TABLE {table_name} DROP CHECK {row['CONSTRAINT_NAME']}")

    def _add_foreign_key_if_missing(
        self,
        conn,
        *,
        table_name,
        constraint_name,
        column_name,
        ref_table,
        ref_column,
        on_delete="CASCADE",
    ):
        if self._constraint_exists(conn, table_name, constraint_name):
            return
        conn.execute(
            f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {constraint_name}
            FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref_column})
            ON DELETE {on_delete}
            """
        )

    def _backfill_dataset_records(self, conn):
        rows = conn.execute(
            """
            SELECT
                user_id,
                data_path,
                source_format,
                cell_count,
                gene_count,
                vector_dim,
                embedding_key,
                visualization_source,
                MIN(created_at) AS created_at,
                MAX(updated_at) AS updated_at
            FROM user_indexes
            GROUP BY
                user_id,
                data_path,
                source_format,
                cell_count,
                gene_count,
                vector_dim,
                embedding_key,
                visualization_source
            """
        ).fetchall()
        for row in rows:
            dataset_id = self._ensure_dataset_row(
                conn,
                owner_user_id=row["user_id"],
                data_path=row["data_path"],
                dataset_name=None,
                source_format=row.get("source_format"),
                cell_count=row.get("cell_count"),
                gene_count=row.get("gene_count"),
                vector_dim=row.get("vector_dim"),
                embedding_key=row.get("embedding_key"),
                visualization_source=row.get("visualization_source"),
                metadata_summary=None,
                status="ready",
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
            )
            conn.execute(
                """
                UPDATE user_indexes
                SET dataset_id = ?
                WHERE user_id = ? AND data_path = ? AND dataset_id IS NULL
                """,
                (dataset_id, row["user_id"], row["data_path"]),
            )
            conn.execute(
                """
                UPDATE index_build_jobs
                SET dataset_id = ?
                WHERE user_id = ? AND data_path = ? AND dataset_id IS NULL
                """,
                (dataset_id, row["user_id"], row["data_path"]),
            )

    def _ensure_dataset_row(
        self,
        conn,
        *,
        owner_user_id,
        data_path,
        dataset_name=None,
        source_format=None,
        cell_count=None,
        gene_count=None,
        vector_dim=None,
        embedding_key=None,
        visualization_source=None,
        metadata_summary=None,
        status="ready",
        created_at=None,
        updated_at=None,
    ):
        normalized_path = str(data_path or "").strip()
        if not normalized_path:
            raise AuthError("data_path is required")
        dataset_name = (dataset_name or Path(normalized_path).stem or "dataset").strip()[:128] or "dataset"
        now = self._now()
        created_at = created_at or now
        updated_at = updated_at or now
        row = conn.execute(
            """
            SELECT id
            FROM datasets
            WHERE owner_user_id = ? AND data_path = ?
            LIMIT 1
            """,
            (owner_user_id, normalized_path),
        ).fetchone()
        metadata_summary_json = (
            json.dumps(metadata_summary, ensure_ascii=False) if metadata_summary is not None else None
        )
        if row:
            updates = ["dataset_name = ?", "status = ?", "updated_at = ?"]
            values = [dataset_name, status or "ready", updated_at]
            optional_fields = {
                "source_format": source_format,
                "cell_count": cell_count,
                "gene_count": gene_count,
                "vector_dim": vector_dim,
                "embedding_key": embedding_key,
                "visualization_source": visualization_source,
            }
            for field_name, field_value in optional_fields.items():
                if field_value is None:
                    continue
                updates.append(f"{field_name} = ?")
                values.append(field_value)
            if metadata_summary is not None:
                updates.append("metadata_summary = ?")
                values.append(metadata_summary_json)
            values.append(row["id"])
            conn.execute(
                f"UPDATE datasets SET {', '.join(updates)} WHERE id = ?",
                values,
            )
            return row["id"]

        cursor = conn.execute(
            """
            INSERT INTO datasets (
                owner_user_id, dataset_name, data_path, source_format,
                cell_count, gene_count, vector_dim, embedding_key,
                visualization_source, metadata_summary, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                owner_user_id,
                dataset_name,
                normalized_path,
                source_format,
                int(cell_count) if cell_count is not None else None,
                int(gene_count) if gene_count is not None else None,
                int(vector_dim) if vector_dim is not None else None,
                embedding_key,
                visualization_source,
                metadata_summary_json,
                status or "ready",
                created_at,
                updated_at,
            ),
        )
        return cursor.lastrowid

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

    def register(
        self,
        username,
        password,
        role="user",
        admin_key=None,
        expected_admin_key=None,
        *,
        created_by=None,
        display_name=None,
        email=None,
    ):
        username = self._normalize_username(username)
        self._validate_password(password)

        if role not in VALID_ROLES:
            raise AuthError("role must be user, admin or super_admin")

        now = self._now()
        password_hash = generate_password_hash(password)

        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (
                        username, password_hash, role, is_active,
                        display_name, email, created_by, token_version,
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, 1, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        username,
                        password_hash,
                        role,
                        (display_name or "").strip() or None,
                        (email or "").strip() or None,
                        created_by,
                        now,
                        now,
                    ),
                )
                user_id = cursor.lastrowid
        except pymysql.err.IntegrityError as exc:
            raise AuthError("username already exists") from exc

        return self.get_user(user_id)

    def login(self, username, password, ip_address=None):
        username = self._normalize_username(username)
        user = self.get_user_by_username(username, include_password=True)
        if not user or not check_password_hash(user["password_hash"], password or ""):
            raise AuthError("invalid username or password")
        if not user["is_active"]:
            raise AuthError("user is disabled")

        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET last_login_at = ?, last_login_ip = ?, updated_at = ?
                WHERE id = ?
                """,
                (now, (ip_address or "").strip() or None, now, user["id"]),
            )
        refreshed_user = self.get_user_by_username(username, include_password=True)
        public_user = self._public_user(refreshed_user)
        token = self.create_token(refreshed_user)
        return token, public_user

    def create_token(self, user):
        payload = {
            "user_id": user["id"],
            "token_version": int(user.get("token_version") or 1),
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
        if int(user.get("token_version") or 1) != int(payload.get("token_version") or 1):
            raise AuthError("authorization token expired")
        return user

    def list_users(self):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, username, role, is_active, display_name, email,
                    last_login_at, last_login_ip, created_by, disabled_reason,
                    token_version, created_at, updated_at
                FROM users
                ORDER BY id ASC
                """
            ).fetchall()
        return [self._public_user(dict(row)) for row in rows]

    def update_user(self, user_id, role=None, is_active=None, display_name=None, email=None, disabled_reason=None):
        user = self.get_user(user_id)
        if not user:
            raise AuthError("user not found")

        updates = []
        values = []
        invalidate_tokens = False
        if role is not None:
            if role not in VALID_ROLES:
                raise AuthError("role must be user, admin or super_admin")
            updates.append("role = ?")
            values.append(role)
            invalidate_tokens = invalidate_tokens or role != user["role"]
        if is_active is not None:
            updates.append("is_active = ?")
            values.append(1 if bool(is_active) else 0)
            if bool(is_active):
                updates.append("disabled_reason = ?")
                values.append(None)
            elif disabled_reason is not None:
                updates.append("disabled_reason = ?")
                values.append((disabled_reason or "").strip()[:255] or None)
            invalidate_tokens = True
        if display_name is not None:
            updates.append("display_name = ?")
            values.append((display_name or "").strip()[:64] or None)
        if email is not None:
            updates.append("email = ?")
            values.append((email or "").strip()[:128] or None)
        if disabled_reason is not None and is_active is None:
            updates.append("disabled_reason = ?")
            values.append((disabled_reason or "").strip()[:255] or None)

        if not updates:
            return user

        if invalidate_tokens:
            updates.append("token_version = token_version + 1")
        updates.append("updated_at = ?")
        values.append(self._now())
        values.append(user_id)

        with self._connect() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                values,
            )
        return self.get_user(user_id)

    def reset_user_password(self, user_id, new_password):
        user = self.get_user(user_id)
        if not user:
            raise AuthError("user not found")
        self._validate_password(new_password)
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?, token_version = token_version + 1, updated_at = ?
                WHERE id = ?
                """,
                (generate_password_hash(new_password), now, user_id),
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
                SELECT
                    id, username, role, is_active, display_name, email,
                    last_login_at, last_login_ip, created_by, disabled_reason,
                    token_version, created_at, updated_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
        return self._public_user(dict(row)) if row else None

    def get_user_by_username(self, username, include_password=False):
        fields = (
            "id, username, role, is_active, display_name, email, "
            "last_login_at, last_login_ip, created_by, disabled_reason, "
            "token_version, created_at, updated_at"
        )
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
                    id, user_id, dataset_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, visualization_source, created_by,
                    index_type, distance_metric, effective_metric, quantization_config, metadata_keys,
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
                    id, user_id, dataset_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, visualization_source, created_by,
                    index_type, distance_metric, effective_metric, quantization_config, metadata_keys,
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
                    id, user_id, dataset_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, visualization_source, created_by,
                    index_type, distance_metric, effective_metric, quantization_config, metadata_keys,
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
                    id, user_id, dataset_id, index_name, collection_name, data_path, source_format,
                    cell_count, gene_count, vector_dim, embedding_key, visualization_source, created_by,
                    index_type, distance_metric, effective_metric, quantization_config, metadata_keys,
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
        visualization_source,
        index_type,
        distance_metric,
        effective_metric,
        quantization_config,
        metadata_keys,
        hnsw_params,
        search_params,
        build_time_ms,
        dataset_id=None,
        created_by=None,
        is_active=True,
        status="ready",
    ):
        index_name = self._normalize_index_name(index_name)
        now = self._now()
        quantization_json = json.dumps(quantization_config or {}, ensure_ascii=False)
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
                        user_id, dataset_id, index_name, collection_name, data_path, source_format,
                        cell_count, gene_count, vector_dim, embedding_key, visualization_source,
                        index_type, distance_metric, effective_metric, quantization_config, metadata_keys,
                        hnsw_params, search_params, created_by, build_time_ms, is_active, status,
                        created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        dataset_id,
                        index_name,
                        collection_name,
                        str(data_path),
                        source_format,
                        int(cell_count),
                        int(gene_count),
                        int(vector_dim),
                        embedding_key,
                        visualization_source,
                        index_type,
                        distance_metric,
                        effective_metric,
                        quantization_json,
                        metadata_keys_json,
                        hnsw_params_json,
                        search_params_json,
                        created_by,
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

    def delete_user_index(self, user_id, index_id):
        index = self.get_user_index(user_id, index_id)
        if not index:
            raise AuthError("index not found")

        now = self._now()
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM index_build_jobs WHERE user_id = ? AND index_name = ?",
                (user_id, index["index_name"]),
            )
            conn.execute(
                "DELETE FROM user_indexes WHERE id = ? AND user_id = ?",
                (index_id, user_id),
            )
            if index["is_active"]:
                fallback = conn.execute(
                    """
                    SELECT id
                    FROM user_indexes
                    WHERE user_id = ? AND status = 'ready'
                    ORDER BY updated_at DESC, id DESC
                    LIMIT 1
                    """,
                    (user_id,),
                ).fetchone()
                if fallback:
                    conn.execute(
                        "UPDATE user_indexes SET is_active = 1, updated_at = ? WHERE id = ?",
                        (now, fallback["id"]),
                    )
        return index

    def find_reusable_user_index(
        self,
        user_id,
        data_path,
        index_type="hnsw",
        distance_metric="cosine",
        effective_metric="cosine",
        quantization_config=None,
        hnsw_params=None,
        search_params=None,
    ):
        normalized_path = str(data_path or "").strip()
        target_index_type = str(index_type or "hnsw").strip().lower()
        target_distance_metric = str(distance_metric or "cosine").strip().lower()
        target_effective_metric = str(effective_metric or "cosine").strip().lower()
        target_quantization = json.dumps(quantization_config or {}, ensure_ascii=False, sort_keys=True)
        target_hnsw = json.dumps(hnsw_params or {}, ensure_ascii=False, sort_keys=True)
        target_search = json.dumps(search_params or {}, ensure_ascii=False, sort_keys=True)
        indexes = self.list_user_indexes(user_id)
        for item in indexes:
            if item["status"] != "ready":
                continue
            if str(item.get("data_path") or "").strip() != normalized_path:
                continue
            if str(item.get("index_type") or "hnsw").strip().lower() != target_index_type:
                continue
            if str(item.get("distance_metric") or "cosine").strip().lower() != target_distance_metric:
                continue
            if str(item.get("effective_metric") or "cosine").strip().lower() != target_effective_metric:
                continue
            item_quantization = json.dumps(item.get("quantization_config") or {}, ensure_ascii=False, sort_keys=True)
            item_hnsw = json.dumps(item.get("hnsw_params") or {}, ensure_ascii=False, sort_keys=True)
            item_search = json.dumps(item.get("search_params") or {}, ensure_ascii=False, sort_keys=True)
            if item_quantization == target_quantization and item_hnsw == target_hnsw and item_search == target_search:
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
        dataset_id,
        requested_by,
        data_path,
        index_name,
        index_type,
        distance_metric,
        effective_metric,
        hnsw_params,
        search_params,
        quantization_config,
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
        trigger_source,
        job_type,
        created_at,
        updated_at,
        started_at,
        finished_at,
    ):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO index_build_jobs (
                    job_id, user_id, dataset_id, requested_by, data_path, index_name, index_type, distance_metric, effective_metric,
                    hnsw_params, search_params, quantization_config,
                    activate, status, stage, message, progress_pct, processed_cells, total_cells,
                    elapsed_seconds, rate_cells_per_second, eta_seconds, dataset_summary, history,
                    result_json, error_text, trigger_source, job_type, created_at, updated_at, started_at, finished_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    user_id,
                    dataset_id,
                    requested_by,
                    str(data_path),
                    index_name,
                    index_type,
                    distance_metric,
                    effective_metric,
                    json.dumps(hnsw_params or {}, ensure_ascii=False),
                    json.dumps(search_params or {}, ensure_ascii=False),
                    json.dumps(quantization_config or {}, ensure_ascii=False),
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
                    trigger_source,
                    job_type,
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
            "quantization_config",
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
            "display_name": user.get("display_name"),
            "email": user.get("email"),
            "last_login_at": user.get("last_login_at"),
            "last_login_ip": user.get("last_login_ip"),
            "created_by": user.get("created_by"),
            "disabled_reason": user.get("disabled_reason"),
            "token_version": int(user.get("token_version") or 1),
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }

    def _row_to_user_index(self, row):
        item = dict(row)
        item["is_active"] = bool(item["is_active"])
        item["dataset_id"] = int(item["dataset_id"]) if item.get("dataset_id") is not None else None
        item["created_by"] = int(item["created_by"]) if item.get("created_by") is not None else None
        item["index_type"] = item.get("index_type") or "hnsw"
        item["distance_metric"] = item.get("distance_metric") or "cosine"
        item["effective_metric"] = item.get("effective_metric") or "cosine"
        item["quantization_config"] = json.loads(item.get("quantization_config") or "{}")
        item["metadata_keys"] = json.loads(item.get("metadata_keys") or "[]")
        item["hnsw_params"] = json.loads(item.get("hnsw_params") or "{}")
        item["search_params"] = json.loads(item.get("search_params") or "{}")
        return item

    def _row_to_build_job(self, row):
        item = dict(row)
        item["activate"] = bool(item.get("activate"))
        item["dataset_id"] = int(item["dataset_id"]) if item.get("dataset_id") is not None else None
        item["requested_by"] = int(item["requested_by"]) if item.get("requested_by") is not None else None
        item["progress_pct"] = float(item.get("progress_pct") or 0)
        item["processed_cells"] = int(item.get("processed_cells") or 0)
        item["total_cells"] = int(item["total_cells"]) if item.get("total_cells") is not None else None
        item["elapsed_seconds"] = float(item.get("elapsed_seconds") or 0)
        item["rate_cells_per_second"] = (
            float(item["rate_cells_per_second"]) if item.get("rate_cells_per_second") is not None else None
        )
        item["eta_seconds"] = float(item["eta_seconds"]) if item.get("eta_seconds") is not None else None
        item["index_type"] = item.get("index_type") or "hnsw"
        item["distance_metric"] = item.get("distance_metric") or "cosine"
        item["effective_metric"] = item.get("effective_metric") or "cosine"
        item["quantization_config"] = json.loads(item.get("quantization_config") or "{}")
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
