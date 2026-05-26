from time import perf_counter
from functools import wraps

from flask import Flask, jsonify, render_template, request

from config import DEFAULT_SAMPLE_DATA, SECRET_KEY, USER_DB_PATH
from services.auth_service import AuthError, UserStore
from services.data_loader import inspect_cell_dataset, load_cell_vectors
from services.vector_index import CellVectorIndex


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
index = CellVectorIndex()
user_store = UserStore(USER_DB_PATH, SECRET_KEY)
user_store.init_db()


def _get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ").strip()
    return None


def require_auth(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            request.current_user = user_store.verify_token(_get_bearer_token())
        except AuthError as exc:
            return jsonify({"error": str(exc)}), 401
        return view_func(*args, **kwargs)

    return wrapper


def require_admin(view_func):
    @wraps(view_func)
    @require_auth
    def wrapper(*args, **kwargs):
        if request.current_user["role"] != "admin":
            return jsonify({"error": "admin role required"}), 403
        return view_func(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "indexed": index.is_ready,
            "dataset": index.dataset_summary,
        }
    )


@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}

    try:
        user = user_store.register(
            username=payload.get("username"),
            password=payload.get("password"),
            role=payload.get("role", "user"),
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "registered", "user": user}), 201


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        start_time = perf_counter()
        token, user = user_store.login(
            username=payload.get("username"),
            password=payload.get("password"),
        )
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 401

    return jsonify(
        {
            "message": "login successful",
            "token": token,
            "token_type": "Bearer",
            "login_time_ms": elapsed_ms,
            "user": user,
        }
    )


@app.get("/api/auth/me")
@require_auth
def current_user():
    return jsonify({"user": request.current_user})


@app.get("/api/admin/users")
@require_admin
def list_users():
    return jsonify({"users": user_store.list_users()})


@app.post("/api/admin/users")
@require_admin
def create_user():
    payload = request.get_json(silent=True) or {}

    try:
        user = user_store.register(
            username=payload.get("username"),
            password=payload.get("password"),
            role=payload.get("role", "user"),
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "user created", "user": user}), 201


@app.patch("/api/admin/users/<int:user_id>")
@require_admin
def update_user(user_id):
    payload = request.get_json(silent=True) or {}

    try:
        user = user_store.update_user(
            user_id,
            role=payload.get("role"),
            is_active=payload.get("is_active"),
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "user updated", "user": user})


@app.delete("/api/admin/users/<int:user_id>")
@require_admin
def delete_user(user_id):
    if request.current_user["id"] == user_id:
        return jsonify({"error": "cannot delete current logged-in user"}), 400

    try:
        user = user_store.delete_user(user_id)
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "user deleted", "user": user})


@app.post("/api/dataset/inspect")
def inspect_dataset():
    payload = request.get_json(silent=True) or {}
    data_path = payload.get("data_path") or str(DEFAULT_SAMPLE_DATA)

    try:
        dataset_info = inspect_cell_dataset(data_path)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(dataset_info)


@app.post("/api/index/build")
def build_index():
    payload = request.get_json(silent=True) or {}
    data_path = payload.get("data_path") or str(DEFAULT_SAMPLE_DATA)

    try:
        start_time = perf_counter()
        dataset = load_cell_vectors(data_path)
        index.build(dataset)
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "message": "index built",
            "collection": index.collection_name,
            "cell_count": len(dataset.cell_ids),
            "gene_count": dataset.gene_count,
            "vector_dim": dataset.vector_dim,
            "embedding_key": dataset.embedding_key,
            "build_time_ms": elapsed_ms,
        }
    )


@app.post("/api/search/by-id")
def search_by_id():
    payload = request.get_json(silent=True) or {}
    cell_id = payload.get("cell_id")
    top_k = int(payload.get("top_k", 5))
    filters = payload.get("filters") or {}

    if not cell_id:
        return jsonify({"error": "cell_id is required"}), 400

    try:
        start_time = perf_counter()
        results = index.search_by_cell_id(cell_id, top_k=top_k, filters=filters)
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "query": {"cell_id": cell_id, "top_k": top_k, "filters": filters},
            "query_time_ms": elapsed_ms,
            "results": results,
        }
    )


@app.post("/api/search/by-vector")
def search_by_vector():
    payload = request.get_json(silent=True) or {}
    vector = payload.get("vector")
    top_k = int(payload.get("top_k", 5))
    filters = payload.get("filters") or {}

    if not vector:
        return jsonify({"error": "vector is required"}), 400

    try:
        start_time = perf_counter()
        results = index.search_by_vector(vector, top_k=top_k, filters=filters)
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "query": {"top_k": top_k, "filters": filters},
            "query_time_ms": elapsed_ms,
            "results": results,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
