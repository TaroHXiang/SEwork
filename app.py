from __future__ import annotations

from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from time import perf_counter
from threading import Lock, Thread
from uuid import uuid4

from flask import Flask, jsonify, render_template, request

from config import DEFAULT_SAMPLE_DATA, SECRET_KEY, USER_DB_PATH
from services.auth_service import AuthError, UserStore
from services.data_loader import (
    inspect_cell_dataset,
    load_cell_vectors,
    load_dataset_visualization_preview,
)
from services.vector_index import CellVectorIndex, build_collection_name


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
index = CellVectorIndex()
user_store = UserStore(USER_DB_PATH, SECRET_KEY)
user_store.init_db()
INDEX_BUILD_JOBS: dict[str, dict] = {}
INDEX_BUILD_JOBS_LOCK = Lock()
MAX_INDEX_BUILD_JOBS = 200


def _get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ").strip()
    return None


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _parse_top_k(raw_value, default=5):
    try:
        top_k = int(raw_value if raw_value is not None else default)
    except Exception as exc:
        raise ValueError("top_k must be an integer") from exc
    if top_k < 1 or top_k > 100:
        raise ValueError("top_k must be between 1 and 100")
    return top_k


def _index_summary_from_record(index_record):
    return {
        "source_path": index_record.get("data_path"),
        "format": index_record.get("source_format"),
        "cell_count": index_record.get("cell_count"),
        "gene_count": index_record.get("gene_count"),
        "vector_dim": index_record.get("vector_dim"),
        "embedding_key": index_record.get("embedding_key"),
        "visualization_source": index_record.get("visualization_source"),
        "metadata_fields": index_record.get("metadata_keys", []),
    }


def _require_collection_exists(collection_name):
    if not index.collection_exists(collection_name):
        raise RuntimeError(
            f"collection not found in Qdrant: {collection_name}. "
            "Please rebuild or import this index."
        )


def _resolve_target_index(payload=None, required=True):
    payload = payload or {}
    user_id = request.current_user["id"]
    raw_index_id = payload.get("index_id")

    if raw_index_id is not None:
        try:
            index_id = int(raw_index_id)
        except Exception as exc:
            raise ValueError("index_id must be an integer") from exc
        index_record = user_store.get_user_index(user_id, index_id)
        if not index_record:
            raise ValueError("index not found for current user")
        if not index_record["is_active"]:
            index_record = user_store.set_active_user_index(user_id, index_id)
    else:
        index_record = user_store.get_active_user_index(user_id)

    if not index_record and required:
        raise ValueError("no active index. build a new index or activate a history index first")
    if not index_record:
        return None

    _require_collection_exists(index_record["collection_name"])
    index.set_active_collection(
        collection_name=index_record["collection_name"],
        vector_dim=index_record["vector_dim"],
        dataset_summary=_index_summary_from_record(index_record),
    )
    return index_record


def _default_index_name(data_path: str):
    stem = Path(data_path).stem or "dataset"
    safe_stem = "".join(ch if ch.isalnum() else "_" for ch in stem).strip("_").lower()
    safe_stem = safe_stem or "dataset"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"{safe_stem}_{timestamp}"


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def _build_index_response(index_record: dict, dataset, elapsed_ms: float) -> dict:
    return {
        "message": "index built",
        "index_id": index_record["id"],
        "index_name": index_record["index_name"],
        "collection": index_record["collection_name"],
        "cell_count": dataset.cell_count,
        "gene_count": dataset.gene_count,
        "vector_dim": dataset.vector_dim,
        "embedding_key": dataset.embedding_key,
        "visualization_source": dataset.visualization_source,
        "metadata_fields": dataset.metadata_fields,
        "hnsw_params": index_record["hnsw_params"],
        "search_params": index_record["search_params"],
        "build_time_ms": elapsed_ms,
        "is_active": index_record["is_active"],
    }


def _perform_index_build(
    *,
    user_id: int,
    data_path: str,
    index_name: str,
    hnsw_params: dict,
    search_params: dict,
    activate: bool,
    progress_callback=None,
):
    collection_name = build_collection_name(user_id, index_name)
    start_time = perf_counter()
    dataset = load_cell_vectors(data_path)
    build_meta = index.build(
        dataset=dataset,
        collection_name=collection_name,
        hnsw_params=hnsw_params,
        search_params=search_params,
        progress_callback=progress_callback,
    )
    elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
    index_record = user_store.create_user_index(
        user_id=user_id,
        index_name=index_name,
        collection_name=build_meta["collection"],
        data_path=dataset.source_path,
        source_format=dataset.source_format,
        cell_count=dataset.cell_count,
        gene_count=dataset.gene_count,
        vector_dim=dataset.vector_dim,
        embedding_key=dataset.embedding_key,
        metadata_keys=dataset.metadata_fields,
        hnsw_params=build_meta["hnsw_params"],
        search_params=build_meta["search_params"],
        build_time_ms=elapsed_ms,
        is_active=activate,
        status="ready",
    )
    return _build_index_response(index_record=index_record, dataset=dataset, elapsed_ms=elapsed_ms)


def _trim_index_build_jobs_locked():
    overflow = len(INDEX_BUILD_JOBS) - MAX_INDEX_BUILD_JOBS
    if overflow <= 0:
        return
    old_job_ids = sorted(
        INDEX_BUILD_JOBS.keys(),
        key=lambda item: INDEX_BUILD_JOBS[item].get("updated_at", ""),
    )[:overflow]
    for job_id in old_job_ids:
        INDEX_BUILD_JOBS.pop(job_id, None)


def _create_index_build_job(
    *,
    user_id: int,
    data_path: str,
    index_name: str,
    hnsw_params: dict,
    search_params: dict,
    activate: bool,
):
    now = _utc_now_iso()
    job_id = uuid4().hex
    job = {
        "job_id": job_id,
        "user_id": user_id,
        "data_path": data_path,
        "index_name": index_name,
        "hnsw_params": hnsw_params,
        "search_params": search_params,
        "activate": bool(activate),
        "status": "queued",
        "stage": "queued",
        "message": "构建任务已创建，等待执行",
        "progress_pct": 0.0,
        "processed_cells": 0,
        "total_cells": None,
        "eta_seconds": None,
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "finished_at": None,
    }
    with INDEX_BUILD_JOBS_LOCK:
        for running_job in INDEX_BUILD_JOBS.values():
            if running_job["user_id"] == user_id and running_job["status"] in {"queued", "running"}:
                raise ValueError("another index build task is already running for this user")
        INDEX_BUILD_JOBS[job_id] = job
        _trim_index_build_jobs_locked()
    return job


def _get_index_build_job(job_id: str) -> dict | None:
    with INDEX_BUILD_JOBS_LOCK:
        job = INDEX_BUILD_JOBS.get(job_id)
        if not job:
            return None
        return dict(job)


def _update_index_build_job(job_id: str, **fields):
    with INDEX_BUILD_JOBS_LOCK:
        job = INDEX_BUILD_JOBS.get(job_id)
        if not job:
            return None
        job.update(fields)
        job["updated_at"] = _utc_now_iso()
        return dict(job)


def _run_index_build_job(job_id: str):
    job = _get_index_build_job(job_id)
    if not job:
        return

    user_id = job["user_id"]
    data_path = job["data_path"]
    index_name = job["index_name"]
    hnsw_params = job["hnsw_params"]
    search_params = job["search_params"]
    activate = bool(job["activate"])

    _update_index_build_job(
        job_id,
        status="running",
        stage="loading_dataset",
        message="正在加载数据集...",
        started_at=_utc_now_iso(),
        progress_pct=1.0,
    )

    progress_start = perf_counter()

    def on_progress(processed_cells: int, total_cells: int):
        progress_ratio = (processed_cells / total_cells) if total_cells else 0.0
        progress_pct = round(min(95.0, 5.0 + progress_ratio * 90.0), 2)
        elapsed_seconds = max(perf_counter() - progress_start, 0.001)
        eta_seconds = None
        if processed_cells > 0 and total_cells and processed_cells < total_cells:
            process_rate = processed_cells / elapsed_seconds
            remaining = max(total_cells - processed_cells, 0)
            eta_seconds = round(remaining / process_rate, 1) if process_rate > 0 else None

        _update_index_build_job(
            job_id,
            status="running",
            stage="building_hnsw",
            message=f"正在写入向量并构建 HNSW 索引（{processed_cells}/{total_cells}）",
            progress_pct=progress_pct,
            processed_cells=processed_cells,
            total_cells=total_cells,
            eta_seconds=eta_seconds,
        )

    try:
        result = _perform_index_build(
            user_id=user_id,
            data_path=data_path,
            index_name=index_name,
            hnsw_params=hnsw_params,
            search_params=search_params,
            activate=activate,
            progress_callback=on_progress,
        )
    except Exception as exc:
        _update_index_build_job(
            job_id,
            status="failed",
            stage="failed",
            message="索引构建失败",
            error=str(exc),
            progress_pct=100.0,
            finished_at=_utc_now_iso(),
            eta_seconds=None,
        )
        return

    _update_index_build_job(
        job_id,
        status="completed",
        stage="completed",
        message="索引构建完成",
        progress_pct=100.0,
        processed_cells=result["cell_count"],
        total_cells=result["cell_count"],
        result=result,
        finished_at=_utc_now_iso(),
        eta_seconds=0.0,
    )


def _start_index_build_job(job_id: str):
    worker = Thread(target=_run_index_build_job, args=(job_id,), daemon=True)
    worker.start()


def _public_index_build_job(job: dict) -> dict:
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "stage": job["stage"],
        "message": job["message"],
        "progress_pct": job["progress_pct"],
        "processed_cells": job["processed_cells"],
        "total_cells": job["total_cells"],
        "eta_seconds": job["eta_seconds"],
        "error": job["error"],
        "result": job["result"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "started_at": job["started_at"],
        "finished_at": job["finished_at"],
    }


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
    token = _get_bearer_token()
    if not token:
        return jsonify(
            {
                "status": "ok",
                "indexed": index.is_ready,
                "dataset": index.dataset_summary,
                "active_index": None,
            }
        )

    try:
        user = user_store.verify_token(token)
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 401

    active_index = user_store.get_active_user_index(user["id"])
    if active_index:
        try:
            _require_collection_exists(active_index["collection_name"])
            index.set_active_collection(
                collection_name=active_index["collection_name"],
                vector_dim=active_index["vector_dim"],
                dataset_summary=_index_summary_from_record(active_index),
            )
            indexed = True
            dataset = index.dataset_summary
        except Exception:
            indexed = False
            dataset = None
    else:
        indexed = False
        dataset = None

    return jsonify(
        {
            "status": "ok",
            "indexed": indexed,
            "dataset": dataset,
            "active_index": active_index,
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
@require_auth
def inspect_dataset():
    payload = request.get_json(silent=True) or {}
    data_path = payload.get("data_path") or str(DEFAULT_SAMPLE_DATA)

    try:
        dataset_info = inspect_cell_dataset(data_path)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(dataset_info)


@app.post("/api/index/build")
@require_auth
def build_index():
    payload = request.get_json(silent=True) or {}
    user_id = request.current_user["id"]
    data_path = payload.get("data_path") or str(DEFAULT_SAMPLE_DATA)
    index_name = payload.get("index_name") or _default_index_name(data_path)
    hnsw_params = payload.get("hnsw_params") or {}
    search_params = payload.get("search_params") or {}
    activate = _to_bool(payload.get("activate"), default=True)
    run_async = _to_bool(payload.get("async"), default=False)

    if run_async:
        try:
            job = _create_index_build_job(
                user_id=user_id,
                data_path=data_path,
                index_name=index_name,
                hnsw_params=hnsw_params,
                search_params=search_params,
                activate=activate,
            )
            _start_index_build_job(job["job_id"])
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

        return (
            jsonify(
                {
                    "message": "index build started",
                    "job_id": job["job_id"],
                    "status": job["status"],
                    "stage": job["stage"],
                }
            ),
            202,
        )

    try:
        result = _perform_index_build(
            user_id=user_id,
            data_path=data_path,
            index_name=index_name,
            hnsw_params=hnsw_params,
            search_params=search_params,
            activate=activate,
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


@app.get("/api/index/build/jobs/<job_id>")
@require_auth
def index_build_job_status(job_id):
    job = _get_index_build_job(job_id)
    if not job:
        return jsonify({"error": "build job not found"}), 404

    current_user = request.current_user
    if job["user_id"] != current_user["id"] and current_user["role"] != "admin":
        return jsonify({"error": "forbidden"}), 403

    return jsonify({"job": _public_index_build_job(job)})


@app.get("/api/visualization/umap")
@require_auth
def visualization_umap():
    payload = {}
    raw_index_id = request.args.get("index_id")
    if raw_index_id:
        payload["index_id"] = raw_index_id

    try:
        limit = int(request.args.get("limit", 10000))
    except Exception as exc:
        return jsonify({"error": f"invalid limit: {exc}"}), 400

    if limit < 1 or limit > 100000:
        return jsonify({"error": "limit must be between 1 and 100000"}), 400

    filters = {}
    for key in ["cell_type", "disease", "AgeGroup", "sex", "tissue", "donor_id"]:
        value = request.args.get(key)
        if value:
            filters[key] = value

    try:
        index_record = _resolve_target_index(payload=payload, required=True)
        viz_data = index.get_visualization_points(
            collection_name=index_record["collection_name"],
            limit=limit,
            filters=filters or None,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "index_id": index_record["id"],
            "collection": index_record["collection_name"],
            "visualization_source": (index.dataset_summary or {}).get("visualization_source")
            or "payload.viz",
            "filters": filters,
            **viz_data,
        }
    )


@app.get("/api/dataset/umap-preview")
@require_auth
def dataset_umap_preview():
    data_path = request.args.get("data_path")
    if not data_path:
        return jsonify({"error": "data_path is required"}), 400

    try:
        limit = int(request.args.get("limit", 10000))
    except Exception as exc:
        return jsonify({"error": f"invalid limit: {exc}"}), 400

    try:
        preview = load_dataset_visualization_preview(
            data_path=data_path,
            limit=limit,
            seed=42,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(preview)


@app.get("/api/indexes")
@require_auth
def list_indexes():
    user_id = request.current_user["id"]
    indexes = user_store.list_user_indexes(user_id)
    return jsonify({"indexes": indexes})


@app.get("/api/indexes/active")
@require_auth
def active_index():
    user_id = request.current_user["id"]
    index_record = user_store.get_active_user_index(user_id)
    if not index_record:
        return jsonify({"index": None})

    try:
        _require_collection_exists(index_record["collection_name"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"index": index_record})


@app.post("/api/indexes/<int:index_id>/activate")
@require_auth
def activate_index(index_id):
    user_id = request.current_user["id"]

    try:
        index_record = user_store.set_active_user_index(user_id, index_id)
        _require_collection_exists(index_record["collection_name"])
        index.set_active_collection(
            collection_name=index_record["collection_name"],
            vector_dim=index_record["vector_dim"],
            dataset_summary=_index_summary_from_record(index_record),
        )
    except (AuthError, ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "index activated", "index": index_record})


@app.post("/api/index/import")
@require_auth
def import_index():
    payload = request.get_json(silent=True) or {}
    user_id = request.current_user["id"]

    index_name = payload.get("index_name")
    collection_name = payload.get("collection_name")
    vector_dim = payload.get("vector_dim")
    if not index_name:
        return jsonify({"error": "index_name is required"}), 400
    if not collection_name:
        return jsonify({"error": "collection_name is required"}), 400
    if not vector_dim:
        return jsonify({"error": "vector_dim is required"}), 400

    try:
        vector_dim = int(vector_dim)
        if vector_dim <= 0:
            raise ValueError("vector_dim must be greater than 0")
        _require_collection_exists(collection_name)
        index_record = user_store.create_user_index(
            user_id=user_id,
            index_name=index_name,
            collection_name=collection_name,
            data_path=payload.get("data_path") or "imported",
            source_format=payload.get("source_format") or "imported",
            cell_count=int(payload.get("cell_count") or 0),
            gene_count=int(payload.get("gene_count") or 0),
            vector_dim=vector_dim,
            embedding_key=payload.get("embedding_key") or "imported",
            metadata_keys=payload.get("metadata_fields") or [],
            hnsw_params=payload.get("hnsw_params") or {},
            search_params=payload.get("search_params") or {},
            build_time_ms=float(payload.get("build_time_ms") or 0.0),
            is_active=_to_bool(payload.get("activate"), default=True),
            status="ready",
        )
    except (AuthError, ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "index imported", "index": index_record}), 201


@app.post("/api/search/by-id")
@require_auth
def search_by_id():
    payload = request.get_json(silent=True) or {}
    cell_id = payload.get("cell_id")
    top_k = payload.get("top_k", 5)
    filters = payload.get("filters") or {}
    evaluate = _to_bool(payload.get("evaluate"), default=False)

    if not cell_id:
        return jsonify({"error": "cell_id is required"}), 400

    try:
        top_k = _parse_top_k(top_k)
        index_record = _resolve_target_index(payload)
        search_params = payload.get("search_params") or index_record.get("search_params") or {}

        if evaluate:
            evaluation = index.evaluate_query_by_cell_id(
                collection_name=index_record["collection_name"],
                vector_dim=index_record["vector_dim"],
                cell_id=cell_id,
                top_k=top_k,
                filters=filters,
                search_params=search_params,
            )
            return jsonify(
                {
                    "query": {
                        "cell_id": cell_id,
                        "top_k": top_k,
                        "filters": filters,
                        "index_id": index_record["id"],
                    },
                    "query_time_ms": evaluation["ann_query_time_ms"],
                    "results": evaluation["ann_results"],
                    "evaluation": {
                        "precision_at_k": evaluation["precision_at_k"],
                        "recall_at_k": evaluation["recall_at_k"],
                        "overlap_count": evaluation["overlap_count"],
                        "ann_query_time_ms": evaluation["ann_query_time_ms"],
                        "exact_query_time_ms": evaluation["exact_query_time_ms"],
                    },
                }
            )

        start_time = perf_counter()
        results = index.search_by_cell_id(
            collection_name=index_record["collection_name"],
            vector_dim=index_record["vector_dim"],
            cell_id=cell_id,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
        )
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "query": {
                "cell_id": cell_id,
                "top_k": top_k,
                "filters": filters,
                "index_id": index_record["id"],
            },
            "query_time_ms": elapsed_ms,
            "results": results,
        }
    )


@app.post("/api/search/by-vector")
@require_auth
def search_by_vector():
    payload = request.get_json(silent=True) or {}
    vector = payload.get("vector")
    top_k = payload.get("top_k", 5)
    filters = payload.get("filters") or {}
    evaluate = _to_bool(payload.get("evaluate"), default=False)

    if not vector:
        return jsonify({"error": "vector is required"}), 400

    try:
        top_k = _parse_top_k(top_k)
        index_record = _resolve_target_index(payload)
        search_params = payload.get("search_params") or index_record.get("search_params") or {}

        if evaluate:
            evaluation = index.evaluate_query_by_vector(
                collection_name=index_record["collection_name"],
                vector_dim=index_record["vector_dim"],
                vector=vector,
                top_k=top_k,
                filters=filters,
                search_params=search_params,
            )
            return jsonify(
                {
                    "query": {
                        "top_k": top_k,
                        "filters": filters,
                        "index_id": index_record["id"],
                    },
                    "query_time_ms": evaluation["ann_query_time_ms"],
                    "results": evaluation["ann_results"],
                    "evaluation": {
                        "precision_at_k": evaluation["precision_at_k"],
                        "recall_at_k": evaluation["recall_at_k"],
                        "overlap_count": evaluation["overlap_count"],
                        "ann_query_time_ms": evaluation["ann_query_time_ms"],
                        "exact_query_time_ms": evaluation["exact_query_time_ms"],
                    },
                }
            )

        search_output = index.search_by_vector_with_timing(
            collection_name=index_record["collection_name"],
            vector_dim=index_record["vector_dim"],
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "query": {
                "top_k": top_k,
                "filters": filters,
                "index_id": index_record["id"],
            },
            "query_time_ms": search_output.query_time_ms,
            "results": search_output.results,
        }
    )


@app.post("/api/search/evaluate/by-id")
@require_auth
def evaluate_by_id():
    payload = request.get_json(silent=True) or {}
    cell_id = payload.get("cell_id")
    top_k = payload.get("top_k", 10)
    filters = payload.get("filters") or {}

    if not cell_id:
        return jsonify({"error": "cell_id is required"}), 400

    try:
        top_k = _parse_top_k(top_k, default=10)
        index_record = _resolve_target_index(payload)
        search_params = payload.get("search_params") or index_record.get("search_params") or {}
        evaluation = index.evaluate_query_by_cell_id(
            collection_name=index_record["collection_name"],
            vector_dim=index_record["vector_dim"],
            cell_id=cell_id,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "query": {
                "cell_id": cell_id,
                "top_k": top_k,
                "filters": filters,
                "index_id": index_record["id"],
            },
            "evaluation": evaluation,
        }
    )


@app.post("/api/search/evaluate/by-vector")
@require_auth
def evaluate_by_vector():
    payload = request.get_json(silent=True) or {}
    vector = payload.get("vector")
    top_k = payload.get("top_k", 10)
    filters = payload.get("filters") or {}

    if not vector:
        return jsonify({"error": "vector is required"}), 400

    try:
        top_k = _parse_top_k(top_k, default=10)
        index_record = _resolve_target_index(payload)
        search_params = payload.get("search_params") or index_record.get("search_params") or {}
        evaluation = index.evaluate_query_by_vector(
            collection_name=index_record["collection_name"],
            vector_dim=index_record["vector_dim"],
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "query": {
                "top_k": top_k,
                "filters": filters,
                "index_id": index_record["id"],
            },
            "evaluation": evaluation,
        }
    )


@app.get("/api/contracts/upstream")
@require_auth
def upstream_contract():
    return jsonify(
        {
            "description": "Upstream preprocessor must output either CSV or h5ad for index build.",
            "accepted_formats": [".csv", ".h5ad"],
            "csv_contract": {
                "required_columns": ["cell_id", "v1", "v2", "..."],
                "vector_column_rule": "All vector columns must start with 'v' and have equal numeric dimension.",
                "optional_metadata_columns": ["cell_type", "disease", "AgeGroup", "sex", "tissue", "donor_id"],
            },
            "h5ad_contract": {
                "required": ["obs_names as cell_id", "X or obsm['X_pca']"],
                "vector_priority": ["obsm.X_pca", "X"],
                "optional_obs_metadata": ["cell_type", "disease", "AgeGroup", "sex", "tissue", "donor_id"],
            },
            "api_example": {
                "endpoint": "/api/index/build",
                "method": "POST",
                "payload": {
                    "data_path": "data/liver.h5ad",
                    "index_name": "liver_pca_v1",
                    "async": True,
                    "hnsw_params": {"m": 16, "ef_construct": 128},
                    "search_params": {"hnsw_ef": 128},
                },
                "progress_endpoint": "/api/index/build/jobs/<job_id>",
            },
        }
    )


@app.get("/api/contracts/downstream")
@require_auth
def downstream_contract():
    return jsonify(
        {
            "description": "Downstream visualization can consume search and evaluation responses directly.",
            "visualization_endpoint": {
                "endpoint": "/api/visualization/umap",
                "method": "GET",
                "params": {"limit": 10000, "index_id": "optional", "cell_type": "optional"},
                "response_fields": ["points[].cell_id", "points[].x", "points[].y", "points[].metadata"],
            },
            "search_response_fields": {
                "query": "query context",
                "query_time_ms": "ANN retrieval time in ms",
                "results": [
                    {
                        "cell_id": "string",
                        "distance": "float (1-score for cosine)",
                        "score": "float",
                        "metadata": {
                            "cell_type": "string|optional",
                            "disease": "string|optional",
                            "AgeGroup": "string|optional",
                            "sex": "string|optional",
                        },
                    }
                ],
                "evaluation": {
                    "precision_at_k": "float",
                    "recall_at_k": "float",
                    "overlap_count": "int",
                    "ann_query_time_ms": "float",
                    "exact_query_time_ms": "float",
                },
            },
            "recommended_endpoints": [
                "/api/search/by-id",
                "/api/search/by-vector",
                "/api/search/evaluate/by-id",
                "/api/search/evaluate/by-vector",
            ],
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
