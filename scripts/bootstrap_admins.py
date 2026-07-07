import json
import os
import secrets
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

from config import BASE_DIR, DATABASE_URL, SECRET_KEY
from services.auth_service import AuthError, UserStore


DEFAULT_ADMIN_USERS = ["admin01", "admin02", "admin03", "admin04"]


def parse_admin_users():
    raw = (os.getenv("BOOTSTRAP_ADMIN_USERS") or "").strip()
    if not raw:
        return list(DEFAULT_ADMIN_USERS)
    users = [item.strip() for item in raw.split(",") if item.strip()]
    return users or list(DEFAULT_ADMIN_USERS)


def parse_passwords():
    raw = (os.getenv("BOOTSTRAP_ADMIN_PASSWORDS_JSON") or "").strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORDS_JSON must be a JSON object")
    return {str(key).strip(): str(value) for key, value in parsed.items() if str(key).strip()}


def ensure_store():
    store = UserStore(DATABASE_URL, SECRET_KEY)
    store.init_db()
    return store


def main():
    load_dotenv(BASE_DIR / ".env")
    store = ensure_store()
    usernames = parse_admin_users()
    super_admin_username = (os.getenv("BOOTSTRAP_SUPER_ADMIN") or usernames[0]).strip()
    provided_passwords = parse_passwords()

    created_credentials = []
    updated_users = []

    for username in usernames:
        role = "super_admin" if username == super_admin_username else "admin"
        user = store.get_user_by_username(username, include_password=True)
        provided_password = provided_passwords.get(username)

        if user:
            store.update_user(user["id"], role=role, is_active=True)
            if provided_password:
                store.reset_user_password(user["id"], provided_password)
            updated_users.append((username, role, bool(provided_password)))
            continue

        password = provided_password or secrets.token_urlsafe(10)
        try:
            store.register(username=username, password=password, role=role)
        except AuthError as exc:
            raise RuntimeError(f"failed to create bootstrap admin {username}: {exc}") from exc
        created_credentials.append((username, role, password))

    print("Bootstrap complete.")
    print(f"Configured admins: {', '.join(usernames)}")
    print(f"Super admin: {super_admin_username}")
    if updated_users:
        print("Updated existing users:")
        for username, role, password_reset in updated_users:
            suffix = " (password reset)" if password_reset else ""
            print(f"  - {username}: {role}{suffix}")
    if created_credentials:
        print("Created users:")
        for username, role, password in created_credentials:
            print(f"  - {username}: {role} | password={password}")
    elif not updated_users:
        print("No admin users were created or updated.")


if __name__ == "__main__":
    main()
