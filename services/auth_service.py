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
        return [dict(row) for row in rows]

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
        return dict(row) if row else None

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

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _normalize_username(self, username):
        username = (username or "").strip()
        if len(username) < 3 or len(username) > 32:
            raise AuthError("username length must be 3-32 characters")
        return username

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

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
