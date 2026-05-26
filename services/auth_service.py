import json
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


VALID_ROLES = {"user", "admin"}


class AuthError(Exception):
    pass


class UserStore:
    def __init__(self, db_path, secret_key, token_max_age=7 * 24 * 60 * 60):
        self.db_path = Path(db_path)
        self.secret_key = secret_key
        self.token_max_age = token_max_age
        self.serializer = URLSafeTimedSerializer(secret_key)

    def init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_indexes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    index_name TEXT NOT NULL,
                    collection_name TEXT NOT NULL UNIQUE,
                    data_path TEXT NOT NULL,
                    source_format TEXT,
                    cell_count INTEGER,
                    gene_count INTEGER,
                    vector_dim INTEGER,
                    embedding_key TEXT,
                    metadata_keys TEXT NOT NULL DEFAULT '[]',
                    hnsw_params TEXT NOT NULL DEFAULT '{}',
                    search_params TEXT NOT NULL DEFAULT '{}',
                    build_time_ms REAL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'ready',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, index_name),
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
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
        except sqlite3.IntegrityError as exc:
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
        except sqlite3.IntegrityError as exc:
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

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

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

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
