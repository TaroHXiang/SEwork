from __future__ import annotations

from datetime import datetime, timezone
from functools import wraps
import json
import mimetypes
from pathlib import Path
from time import perf_counter
from threading import Lock, Thread
from uuid import uuid4

from flask import Flask, g, jsonify, render_template, request
import pandas as pd
from werkzeug.utils import secure_filename

from config import (
    API_METADATA_VALUES_MAX,
    API_TOP_K_MAX,
    API_UMAP_LIMIT_MAX,
    BASE_DIR,
    DATABASE_URL,
    DATA_DIR,
    DEFAULT_SAMPLE_DATA,
    MAX_INDEX_BUILD_JOBS,
    SECRET_KEY,
    ZHIPU_API_KEY,
    ZHIPU_API_URL,
    ZHIPU_MODEL,
)
from services.admin_service import AdminStore
from services.ai_advisor import AIAdvisorError, DEFAULT_SUGGESTED_QUESTION, build_dataset_context, request_ai_chat
from services.cell_analysis_agent import analyze_cell_query
from services.auth_service import AuthError, UserStore
from services.data_loader import (
    DEFAULT_METADATA_FILTER_FIELDS,
    inspect_cell_dataset,
    load_cell_vectors,
    load_dataset_analytics,
    load_dataset_metadata_options,
    load_dataset_visualization_preview,
)
from services.vector_index import (
    CellVectorIndex,
    build_collection_name,
    normalize_requested_build_options,
)


mimetypes.add_type("text/css", ".css")
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
index = CellVectorIndex()
user_store = UserStore(DATABASE_URL, SECRET_KEY)
admin_store = AdminStore(DATABASE_URL)
user_store.init_db()
user_store.mark_unfinished_build_jobs_failed()
INDEX_BUILD_JOBS: dict[str, dict] = {}
INDEX_BUILD_JOBS_LOCK = Lock()
ADMIN_ROLES = {"admin", "super_admin"}
ALLOWED_DATASET_UPLOAD_EXTENSIONS = {".csv", ".h5ad"}


@app.before_request
def mark_request_start():
    g.request_start_time = perf_counter()
    g.request_id = request.headers.get("X-Request-Id") or uuid4().hex[:12]


@app.after_request
def add_timing_headers(response):
    if hasattr(g, "request_start_time"):
        response.headers["X-Request-Time-Ms"] = str(_elapsed_ms(g.request_start_time))
    if hasattr(g, "request_id"):
        response.headers["X-Request-Id"] = g.request_id
    return response


@app.errorhandler(404)
def not_found(_exc):
    return _api_error("endpoint not found", 404, code="not_found")


@app.errorhandler(405)
def method_not_allowed(_exc):
    return _api_error("method not allowed", 405, code="method_not_allowed")


@app.errorhandler(Exception)
def unhandled_exception(exc):
    app.logger.exception("Unhandled API error")
    return _api_error(str(exc), 500, code="internal_error")


def _elapsed_ms(start_time: float) -> float:
    return round((perf_counter() - start_time) * 1000, 2)


def _api_error(message: str, status_code: int = 400, *, code: str | None = None, **extra):
    payload = {
        "ok": False,
        "error": message,
        "code": code or "request_error",
        "timestamp": _utc_now_iso(),
    }
    if hasattr(g, "request_id"):
        payload["request_id"] = g.request_id
    if hasattr(g, "request_start_time"):
        payload["request_time_ms"] = _elapsed_ms(g.request_start_time)
    payload.update(extra)
    return jsonify(payload), status_code


def _api_ok(payload: dict | None = None, status_code: int = 200):
    payload = dict(payload or {})
    payload.setdefault("ok", True)
    if hasattr(g, "request_id"):
        payload.setdefault("request_id", g.request_id)
    if hasattr(g, "request_start_time"):
        payload.setdefault("request_time_ms", _elapsed_ms(g.request_start_time))
    return jsonify(payload), status_code


def _get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ").strip()
    return None


def _client_ip():
    forwarded = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    real_ip = (request.headers.get("X-Real-IP") or "").strip()
    return forwarded or real_ip or (request.remote_addr or "")


def _is_admin_role(role: str | None):
    return str(role or "").strip().lower() in ADMIN_ROLES


def _is_admin_user(user: dict | None):
    return _is_admin_role((user or {}).get("role"))


def _is_super_admin_user(user: dict | None):
    return str((user or {}).get("role") or "").strip().lower() == "super_admin"


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
    if top_k < 1 or top_k > API_TOP_K_MAX:
        raise ValueError(f"top_k must be between 1 and {API_TOP_K_MAX}")
    return top_k


def _benchmark_from_evaluation(evaluation: dict, top_k: int) -> dict:
    after = {
        "query_time_ms": evaluation.get("ann_query_time_ms"),
        "precision_at_k": evaluation.get("precision_at_k"),
        "recall_at_k": evaluation.get("recall_at_k"),
        "overlap_count": evaluation.get("overlap_count"),
        "result_count": len(evaluation.get("ann_results") or []),
        "extra_persistent_memory_mb": 0.0,
    }
    return {
        "top_k": top_k,
        "distance_metric": evaluation.get("distance_metric"),
        "before": {
            "query_time_ms": None,
            "precision_at_k": None,
            "recall_at_k": None,
            "overlap_count": None,
            "result_count": None,
            "extra_persistent_memory_mb": 0.0,
        },
        "after": after,
        "exact": {
            "query_time_ms": evaluation.get("exact_query_time_ms"),
            "result_count": len(evaluation.get("exact_results") or []),
        },
        "delta": {
            "query_time_ms": None,
            "precision_at_k": None,
            "recall_at_k": None,
            "overlap_count": None,
            "extra_persistent_memory_mb": 0.0,
        },
        "params": {
            "method": "当前后端未暴露改进前 ANN 基线，已展示 ANN 与 Exact 的评估结果。",
            "fallback": True,
        },
        "ann_results": evaluation.get("ann_results") or [],
        "exact_results": evaluation.get("exact_results") or [],
    }


def _build_ann_improvement_benchmark_from_vector(
    *,
    collection_name: str,
    vector_dim: int,
    vector,
    top_k: int,
    filters: dict | None,
    search_params: dict | None,
    vector_is_prepared: bool = False,
) -> dict:
    old_params = dict(search_params or {})
    old_params["rerank_k"] = top_k
    old_params["filter_candidate_multiplier"] = 1

    old_ann = index.search_by_vector_with_timing(
        collection_name=collection_name,
        vector_dim=vector_dim,
        vector=vector,
        top_k=top_k,
        filters=filters,
        search_params=old_params,
        vector_is_prepared=vector_is_prepared,
        exact=False,
    )
    improved_ann = index.search_by_vector_with_timing(
        collection_name=collection_name,
        vector_dim=vector_dim,
        vector=vector,
        top_k=top_k,
        filters=filters,
        search_params=search_params,
        vector_is_prepared=vector_is_prepared,
        exact=False,
    )
    exact = index.search_by_vector_with_timing(
        collection_name=collection_name,
        vector_dim=vector_dim,
        vector=vector,
        top_k=top_k,
        filters=filters,
        search_params=search_params,
        vector_is_prepared=vector_is_prepared,
        exact=True,
    )
    exact_ids = [item["cell_id"] for item in exact.results]

    def summarize(label: str, output, *, is_exact: bool = False) -> dict:
        ids = [item["cell_id"] for item in output.results]
        overlap_count = len(set(ids) & set(exact_ids))
        precision = overlap_count / len(ids) if ids else 0.0
        recall = overlap_count / len(exact_ids) if exact_ids else 0.0
        return {
            "label": label,
            "query_time_ms": output.query_time_ms,
            "precision_at_k": 1.0 if is_exact else round(precision, 6),
            "recall_at_k": 1.0 if is_exact else round(recall, 6),
            "overlap_count": len(exact_ids) if is_exact else overlap_count,
            "result_count": len(ids),
            "extra_persistent_memory_mb": 0.0,
        }

    before = summarize("before", old_ann)
    after = summarize("after", improved_ann)
    exact_summary = summarize("exact", exact, is_exact=True)
    return {
        "top_k": top_k,
        "before": before,
        "after": after,
        "exact": exact_summary,
        "delta": {
            "query_time_ms": round(before["query_time_ms"] - after["query_time_ms"], 2),
            "precision_at_k": round(after["precision_at_k"] - before["precision_at_k"], 6),
            "recall_at_k": round(after["recall_at_k"] - before["recall_at_k"], 6),
            "overlap_count": after["overlap_count"] - before["overlap_count"],
            "extra_persistent_memory_mb": 0.0,
        },
        "params": {
            "before": old_params,
            "after": dict(search_params or {}),
            "method": "ANN coarse retrieval + exact rerank on candidates",
        },
        "ann_results": improved_ann.results,
        "exact_results": exact.results,
    }


def _fetch_query_vector_for_benchmark(collection_name: str, cell_id: str):
    fetch_vector = getattr(index, "_fetch_vector_by_cell_id", None)
    if callable(fetch_vector):
        return fetch_vector(collection_name=collection_name, cell_id=cell_id)

    load_collection = getattr(index, "_load_collection", None)
    if callable(load_collection):
        collection = load_collection(collection_name)
        offset = getattr(collection, "cell_id_to_offset", {}).get(cell_id)
        if offset is not None:
            return collection.vectors[offset].astype(float).tolist()

    return None


def _compare_ann_improvement_by_cell_id(**kwargs) -> dict:
    compare = getattr(index, "compare_ann_improvement_by_cell_id", None)
    if callable(compare):
        return compare(**kwargs)
    vector = _fetch_query_vector_for_benchmark(
        collection_name=kwargs["collection_name"],
        cell_id=kwargs["cell_id"],
    )
    if not vector:
        evaluation = index.evaluate_query_by_cell_id(**kwargs)
        return _benchmark_from_evaluation(evaluation, kwargs.get("top_k", 10))
    return _build_ann_improvement_benchmark_from_vector(
        collection_name=kwargs["collection_name"],
        vector_dim=kwargs["vector_dim"],
        vector=vector,
        top_k=kwargs.get("top_k", 10),
        filters=kwargs.get("filters"),
        search_params=kwargs.get("search_params"),
        vector_is_prepared=True,
    )


def _compare_ann_improvement_by_vector(**kwargs) -> dict:
    compare = getattr(index, "compare_ann_improvement_by_vector", None)
    if callable(compare):
        return compare(**kwargs)
    if not callable(getattr(index, "search_by_vector_with_timing", None)):
        evaluation = index.evaluate_query_by_vector(**kwargs)
        return _benchmark_from_evaluation(evaluation, kwargs.get("top_k", 10))
    return _build_ann_improvement_benchmark_from_vector(
        collection_name=kwargs["collection_name"],
        vector_dim=kwargs["vector_dim"],
        vector=kwargs["vector"],
        top_k=kwargs.get("top_k", 10),
        filters=kwargs.get("filters"),
        search_params=kwargs.get("search_params"),
        vector_is_prepared=kwargs.get("vector_is_prepared", False),
    )



def _index_summary_from_record(index_record):
    return {
        "source_path": index_record.get("data_path"),
        "format": index_record.get("source_format"),
        "cell_count": index_record.get("cell_count"),
        "gene_count": index_record.get("gene_count"),
        "vector_dim": index_record.get("vector_dim"),
        "embedding_key": index_record.get("embedding_key"),
        "visualization_source": index_record.get("visualization_source"),
        "index_type": index_record.get("index_type"),
        "distance_metric": index_record.get("distance_metric"),
        "effective_metric": index_record.get("effective_metric"),
        "quantization_config": index_record.get("quantization_config", {}),
        "metadata_fields": index_record.get("metadata_keys", []),
    }


def _require_collection_exists(collection_name):
    if not index.collection_exists(collection_name):
        raise RuntimeError(
            f"collection not found in FAISS service: {collection_name}. "
            "Please rebuild this index or make sure the FAISS Docker service is running."
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


def _remove_cached_index_build_jobs(user_id: int, index_name: str) -> None:
    with INDEX_BUILD_JOBS_LOCK:
        stale_job_ids = [
            job_id
            for job_id, job in INDEX_BUILD_JOBS.items()
            if job.get("user_id") == user_id and job.get("index_name") == index_name
        ]
        for job_id in stale_job_ids:
            INDEX_BUILD_JOBS.pop(job_id, None)


def _default_index_name(data_path: str):
    stem = Path(data_path).stem or "dataset"
    safe_stem = "".join(ch if ch.isalnum() else "_" for ch in stem).strip("_").lower()
    safe_stem = safe_stem or "dataset"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"{safe_stem}_{timestamp}"


def _workspace_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(BASE_DIR.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def _save_uploaded_dataset(file_storage, user_id: int) -> dict:
    original_name = secure_filename(file_storage.filename or "")
    if not original_name:
        raise ValueError("uploaded file must have a filename")

    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_DATASET_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_DATASET_UPLOAD_EXTENSIONS))
        raise ValueError(f"unsupported upload format, expected one of: {allowed}")

    upload_dir = DATA_DIR / "uploads" / f"user_{user_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(original_name).stem or "dataset"
    target_path = upload_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}_{stem}{suffix}"
    file_storage.save(target_path)
    return {
        "filename": original_name,
        "data_path": _workspace_relative_path(target_path),
        "size_bytes": int(target_path.stat().st_size),
    }


def _vector_column_sort_key(column_name: str):
    normalized = str(column_name).strip().lower()
    match = None
    if normalized.startswith("dim_"):
        match = normalized.removeprefix("dim_")
    elif normalized.startswith("dim"):
        match = normalized.removeprefix("dim")
    elif normalized.startswith("v"):
        match = normalized.removeprefix("v")
    if match and match.isdigit():
        return int(match)
    return normalized


def _extract_query_vector_from_csv_upload(file_storage, row_index: int = 0) -> tuple[list[float], dict]:
    filename = secure_filename(file_storage.filename or "")
    if Path(filename).suffix.lower() != ".csv":
        raise ValueError("query vector upload must be a .csv file")

    df = pd.read_csv(file_storage)
    if df.empty:
        raise ValueError("query vector CSV must contain at least one row")
    if row_index < 0 or row_index >= len(df):
        raise ValueError(f"row_index must be between 0 and {len(df) - 1}")

    columns = list(df.columns)
    vector_columns = [
        column
        for column in columns
        if re_match_vector_column(column)
    ]
    if vector_columns:
        vector_columns = sorted(vector_columns, key=_vector_column_sort_key)
    else:
        excluded = {"cell_id", "id", "barcode"}
        numeric_df = df.drop(columns=[column for column in columns if str(column).strip().lower() in excluded], errors="ignore")
        vector_columns = [
            column
            for column in numeric_df.columns
            if pd.api.types.is_numeric_dtype(numeric_df[column])
        ]

    if not vector_columns:
        raise ValueError("query vector CSV must contain vector columns such as v1,v2,... or numeric columns")

    values = pd.to_numeric(df.iloc[row_index][vector_columns], errors="coerce")
    if values.isna().any():
        raise ValueError("query vector CSV contains non-numeric vector values")

    cell_id = None
    for candidate in ("cell_id", "id", "barcode"):
        if candidate in df.columns:
            cell_id = str(df.iloc[row_index][candidate])
            break

    return values.astype(float).tolist(), {
        "filename": filename,
        "row_index": row_index,
        "cell_id": cell_id,
        "vector_columns": [str(column) for column in vector_columns],
        "input_dim": len(vector_columns),
        "row_count": len(df),
    }


def re_match_vector_column(column_name: str) -> bool:
    normalized = str(column_name).strip().lower()
    if normalized.startswith("dim_"):
        return normalized.removeprefix("dim_").isdigit()
    if normalized.startswith("dim"):
        return normalized.removeprefix("dim").isdigit()
    if normalized.startswith("v"):
        return normalized.removeprefix("v").isdigit()
    return False


def _seed_dataset_info(data_path: str):
    data_path = str(data_path or "").strip()
    return {
        "source_path": data_path,
        "dataset_name": Path(data_path).stem or "dataset",
    }


def _ensure_dataset_record(user_id: int, data_path: str, dataset_info: dict | None = None, status: str = "ready"):
    payload = dict(dataset_info or {})
    payload.setdefault("source_path", str(data_path or "").strip())
    payload.setdefault("dataset_name", Path(str(data_path or "").strip()).stem or "dataset")
    return admin_store.upsert_dataset(user_id, data_path, dataset_info=payload, status=status)


def _delete_collection_if_present(collection_name: str):
    if not collection_name:
        return False
    try:
        if not index.collection_exists(collection_name):
            return False
        return index.delete_collection(collection_name)
    except RuntimeError as exc:
        message = str(exc).lower()
        if "collection not found" in message:
            return False
        raise


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def _build_index_response(index_record: dict, dataset, elapsed_ms: float) -> dict:
    return {
        "message": "index built",
        "index_id": index_record["id"],
        "index_name": index_record["index_name"],
        "collection": index_record["collection_name"],
        "index_type": index_record["index_type"],
        "distance_metric": index_record["distance_metric"],
        "effective_metric": index_record["effective_metric"],
        "quantization_config": index_record["quantization_config"],
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
    dataset_id: int | None,
    index_type: str,
    distance_metric: str,
    quantization_config: dict,
    hnsw_params: dict,
    search_params: dict,
    activate: bool,
    created_by: int | None = None,
    progress_callback=None,
    status_callback=None,
):
    collection_name = build_collection_name(user_id, index_name)
    start_time = perf_counter()
    dataset = load_cell_vectors(data_path)
    if status_callback is not None:
        status_callback(
            "dataset_loaded",
            {
                "cell_count": dataset.cell_count,
                "gene_count": dataset.gene_count,
                "vector_dim": dataset.vector_dim,
                "embedding_key": dataset.embedding_key,
                "source_path": dataset.source_path,
                "source_format": dataset.source_format,
            },
        )
    build_meta = index.build(
        dataset=dataset,
        collection_name=collection_name,
        index_type=index_type,
        distance_metric=distance_metric,
        quantization_config=quantization_config,
        hnsw_params=hnsw_params,
        search_params=search_params,
        progress_callback=progress_callback,
    )
    dataset_record = _ensure_dataset_record(
        user_id,
        dataset.source_path,
        dataset_info={
            "source_path": dataset.source_path,
            "format": dataset.source_format,
            "cell_count": dataset.cell_count,
            "gene_count": dataset.gene_count,
            "vector_dim": dataset.vector_dim,
            "embedding_key": dataset.embedding_key,
            "visualization_source": dataset.visualization_source,
            "metadata_fields": dataset.metadata_fields,
            "dataset_name": Path(dataset.source_path).stem or "dataset",
        },
        status="ready",
    )
    if status_callback is not None:
        status_callback(
            "persisting_index",
            {
                "cell_count": dataset.cell_count,
                "collection_name": build_meta["collection"],
            },
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
        visualization_source=dataset.visualization_source,
        index_type=build_meta["index_type"],
        distance_metric=build_meta["distance_metric"],
        effective_metric=build_meta["effective_metric"],
        quantization_config=build_meta["quantization_config"],
        metadata_keys=dataset.metadata_fields,
        hnsw_params=build_meta["hnsw_params"],
        search_params=build_meta["search_params"],
        dataset_id=dataset_record["id"] if dataset_record else dataset_id,
        created_by=created_by,
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
    dataset_id: int | None,
    data_path: str,
    index_name: str,
    index_type: str,
    distance_metric: str,
    effective_metric: str,
    quantization_config: dict,
    hnsw_params: dict,
    search_params: dict,
    activate: bool,
):
    existing_job = user_store.get_latest_running_build_job(user_id)
    if existing_job:
        raise ValueError("another index build task is already running for this user")

    now = _utc_now_iso()
    job_id = uuid4().hex
    job = {
        "job_id": job_id,
        "user_id": user_id,
        "dataset_id": dataset_id,
        "requested_by": user_id,
        "data_path": data_path,
        "index_name": index_name,
        "index_type": index_type,
        "distance_metric": distance_metric,
        "effective_metric": effective_metric,
        "quantization_config": quantization_config,
        "hnsw_params": hnsw_params,
        "search_params": search_params,
        "activate": bool(activate),
        "status": "queued",
        "stage": "queued",
        "message": "构建任务已创建，等待执行",
        "progress_pct": 0.0,
        "processed_cells": 0,
        "total_cells": None,
        "elapsed_seconds": 0.0,
        "rate_cells_per_second": None,
        "eta_seconds": None,
        "dataset_summary": None,
        "history": [
            {
                "time": now,
                "stage": "queued",
                "text": "构建任务已创建，等待执行",
            }
        ],
        "result": None,
        "error": None,
        "trigger_source": "user_ui",
        "job_type": "build_index",
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
    user_store.create_index_build_job(**job)
    return job


def _get_index_build_job(job_id: str) -> dict | None:
    with INDEX_BUILD_JOBS_LOCK:
        job = INDEX_BUILD_JOBS.get(job_id)
    if job:
        return dict(job)
    db_job = user_store.get_index_build_job(job_id)
    if db_job:
        with INDEX_BUILD_JOBS_LOCK:
            INDEX_BUILD_JOBS[job_id] = dict(db_job)
        return db_job
    return None


def _update_index_build_job(job_id: str, **fields):
    persisted_job = user_store.update_index_build_job(job_id, **fields)
    with INDEX_BUILD_JOBS_LOCK:
        job = INDEX_BUILD_JOBS.get(job_id)
        if job:
            job.update(fields)
            job["updated_at"] = persisted_job["updated_at"] if persisted_job else _utc_now_iso()
            return dict(job)
    if persisted_job:
        with INDEX_BUILD_JOBS_LOCK:
            INDEX_BUILD_JOBS[job_id] = dict(persisted_job)
        return persisted_job
    return None


def _append_index_build_history(job_id: str, *, stage: str, text: str):
    job = _get_index_build_job(job_id)
    if not job:
        return None
    history = list(job.get("history") or [])
    history.append(
        {
            "time": _utc_now_iso(),
            "stage": stage,
            "text": text,
        }
    )
    return _update_index_build_job(job_id, history=history[-12:])


def _run_index_build_job_legacy(job_id: str):
    job = _get_index_build_job(job_id)
    if not job:
        return

    user_id = job["user_id"]
    data_path = job["data_path"]
    index_name = job["index_name"]
    index_type = job["index_type"]
    distance_metric = job["distance_metric"]
    quantization_config = job.get("quantization_config") or {}
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
        elapsed_seconds=0.0,
    )
    _append_index_build_history(job_id, stage="loading_dataset", text="开始读取数据集并提取向量")

    progress_start = perf_counter()

    def on_status(stage: str, payload: dict):
        elapsed_seconds = round(max(perf_counter() - progress_start, 0.0), 1)
        if stage == "dataset_loaded":
            cell_count = payload.get("cell_count")
            gene_count = payload.get("gene_count")
            vector_dim = payload.get("vector_dim")
            summary = {
                "cell_count": cell_count,
                "gene_count": gene_count,
                "vector_dim": vector_dim,
                "embedding_key": payload.get("embedding_key"),
                "source_path": payload.get("source_path"),
                "source_format": payload.get("source_format"),
            }
            _update_index_build_job(
                job_id,
                status="running",
                stage="dataset_loaded",
                message=f"数据集加载完成，共 {cell_count} 个细胞，开始构建向量索引",
                progress_pct=5.0,
                processed_cells=0,
                total_cells=cell_count,
                elapsed_seconds=elapsed_seconds,
                dataset_summary=summary,
            )
            _append_index_build_history(
                job_id,
                stage="dataset_loaded",
                text=f"数据集加载完成：{cell_count} 个细胞，{gene_count} 个基因，向量维度 {vector_dim}",
            )
        elif stage == "persisting_index":
            _update_index_build_job(
                job_id,
                status="running",
                stage="persisting_index",
                message="向量写入完成，正在保存索引元数据并激活索引",
                progress_pct=97.0,
                processed_cells=payload.get("cell_count"),
                total_cells=payload.get("cell_count"),
                elapsed_seconds=elapsed_seconds,
                eta_seconds=1.0,
            )
            _append_index_build_history(
                job_id,
                stage="persisting_index",
                text=f"向量写入完成，正在登记索引集合 {payload.get('collection_name')}",
            )

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
            elapsed_seconds=round(elapsed_seconds, 1),
            rate_cells_per_second=round(processed_cells / elapsed_seconds, 1) if processed_cells > 0 else None,
            eta_seconds=eta_seconds,
        )

    try:
        result = _perform_index_build(
            user_id=user_id,
            data_path=data_path,
            index_name=index_name,
            dataset_id=job.get("dataset_id"),
            index_type=index_type,
            distance_metric=distance_metric,
            quantization_config=quantization_config,
            hnsw_params=hnsw_params,
            search_params=search_params,
            activate=activate,
            created_by=user_id,
            progress_callback=on_progress,
            status_callback=on_status,
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
            elapsed_seconds=round(max(perf_counter() - progress_start, 0.0), 1),
            eta_seconds=None,
        )
        _append_index_build_history(job_id, stage="failed", text=f"索引构建失败：{exc}")
        return

    _update_index_build_job(
        job_id,
        status="completed",
        stage="completed",
        message="索引构建完成",
        progress_pct=100.0,
        processed_cells=result["cell_count"],
        total_cells=result["cell_count"],
        elapsed_seconds=round(max(perf_counter() - progress_start, 0.0), 1),
        rate_cells_per_second=round(
            result["cell_count"] / max(perf_counter() - progress_start, 0.001),
            1,
        ),
        result=result,
        finished_at=_utc_now_iso(),
        eta_seconds=0.0,
    )
    _append_index_build_history(job_id, stage="completed", text="索引构建完成，可进行 Top-K 检索")


def _start_index_build_job(job_id: str):
    worker = Thread(target=_run_index_build_job_guarded, args=(job_id,), daemon=True)
    worker.start()


def _run_index_build_job_guarded(job_id: str):
    try:
        _run_index_build_job(job_id)
    except Exception as exc:
        app.logger.exception("Background index build job crashed: %s", job_id)
        try:
            _update_index_build_job(
                job_id,
                status="failed",
                stage="failed",
                message="index build worker crashed",
                error=str(exc),
                finished_at=_utc_now_iso(),
            )
            _append_index_build_history(job_id, stage="failed", text=f"build worker crashed: {exc}")
        except Exception:
            app.logger.exception("Failed to persist build crash state: %s", job_id)


def _public_index_build_job(job: dict) -> dict:
    return {
        "job_id": job["job_id"],
        "dataset_id": job.get("dataset_id"),
        "status": job["status"],
        "stage": job["stage"],
        "index_type": job.get("index_type"),
        "distance_metric": job.get("distance_metric"),
        "effective_metric": job.get("effective_metric"),
        "quantization_config": job.get("quantization_config") or {},
        "message": job["message"],
        "progress_pct": job["progress_pct"],
        "processed_cells": job["processed_cells"],
        "total_cells": job["total_cells"],
        "elapsed_seconds": job.get("elapsed_seconds"),
        "rate_cells_per_second": job.get("rate_cells_per_second"),
        "eta_seconds": job["eta_seconds"],
        "dataset_summary": job.get("dataset_summary"),
        "history": job.get("history") or [],
        "error": job["error"],
        "result": job["result"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "started_at": job["started_at"],
        "finished_at": job["finished_at"],
    }


def _assert_manageable_target_user(actor: dict, target: dict, *, allow_self: bool = False):
    if not target:
        raise AuthError("user not found")
    if not allow_self and int(actor["id"]) == int(target["id"]):
        raise AuthError("cannot modify current logged-in user")
    if target["role"] == "super_admin":
        raise AuthError("super_admin account cannot be modified from this interface")
    if _is_super_admin_user(actor):
        return
    if target["role"] != "user":
        raise AuthError("only super_admin can manage admin accounts")


def _assert_assignable_role(actor: dict, role: str):
    normalized_role = str(role or "user").strip().lower()
    if normalized_role not in {"user", "admin"}:
        raise AuthError("only user or admin role can be assigned from this interface")
    if normalized_role == "admin" and not _is_super_admin_user(actor):
        raise AuthError("only super_admin can create or promote admin accounts")
    return normalized_role


def _record_admin_audit(action_type: str, *, detail=None, target_user=None, target_index=None, target_dataset=None):
    actor = request.current_user
    admin_store.create_audit_log(
        actor_user_id=actor["id"],
        actor_role=actor["role"],
        action_type=action_type,
        target_user_id=target_user.get("id") if target_user else None,
        target_index_id=target_index.get("id") if target_index else None,
        target_dataset_id=target_dataset.get("id") if target_dataset else None,
        target_username=target_user.get("username") if target_user else None,
        detail=detail or {},
        ip_address=_client_ip(),
    )


def _delete_index_record(index_record: dict):
    owner_user_id = index_record["user_id"]
    collection_name = index_record["collection_name"]
    _delete_collection_if_present(collection_name)
    deleted_index = user_store.delete_user_index(owner_user_id, index_record["id"])
    _remove_cached_index_build_jobs(owner_user_id, deleted_index["index_name"])

    next_active_index = user_store.get_active_user_index(owner_user_id)
    if deleted_index.get("is_active") or index.collection_name == collection_name:
        try:
            if next_active_index and index.collection_exists(next_active_index["collection_name"]):
                index.set_active_collection(
                    collection_name=next_active_index["collection_name"],
                    vector_dim=next_active_index["vector_dim"],
                    dataset_summary=_index_summary_from_record(next_active_index),
                )
            else:
                index.clear_active_collection()
        except RuntimeError:
            index.clear_active_collection()
    return deleted_index, next_active_index


def _find_reusable_index_for_request(
    user_id: int,
    data_path: str,
    index_type: str,
    distance_metric: str,
    effective_metric: str,
    quantization_config: dict,
    hnsw_params: dict,
    search_params: dict,
):
    index_record = user_store.find_reusable_user_index(
        user_id,
        data_path=data_path,
        index_type=index_type,
        distance_metric=distance_metric,
        effective_metric=effective_metric,
        quantization_config=quantization_config,
        hnsw_params=hnsw_params,
        search_params=search_params,
    )
    if not index_record:
        return None
    try:
        _require_collection_exists(index_record["collection_name"])
    except Exception:
        return None
    return index_record


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
        if not _is_admin_user(request.current_user):
            return jsonify({"error": "admin role required"}), 403
        return view_func(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/docs/user-manual")
def user_manual():
    return render_template("user_manual.html")


@app.route("/docs/admin-manual")
def admin_manual():
    return render_template("admin_manual.html")


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
    requested_role = payload.get("role", "user")

    if requested_role != "user":
        return jsonify({"error": "管理员账号不开放自助注册，请联系项目团队处理"}), 403

    try:
        user = user_store.register(
            username=payload.get("username"),
            password=payload.get("password"),
            role="user",
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
            ip_address=_client_ip(),
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


@app.get("/api/admin/overview")
@require_admin
def admin_overview():
    return jsonify({"overview": admin_store.get_overview()})


@app.get("/api/admin/users")
@require_admin
def list_users():
    return jsonify({"users": admin_store.list_users_with_stats()})


@app.get("/api/admin/users/<int:user_id>")
@require_admin
def admin_user_detail(user_id):
    try:
        detail = admin_store.get_user_detail(user_id)
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(detail)


@app.post("/api/admin/users")
@require_admin
def create_user():
    payload = request.get_json(silent=True) or {}
    actor = request.current_user

    try:
        requested_role = _assert_assignable_role(actor, payload.get("role", "user"))
        user = user_store.register(
            username=payload.get("username"),
            password=payload.get("password"),
            role=requested_role,
            created_by=actor["id"],
            display_name=payload.get("display_name"),
            email=payload.get("email"),
        )
        _record_admin_audit(
            "user_create",
            target_user=user,
            detail={"assigned_role": requested_role},
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "user created", "user": user}), 201


@app.patch("/api/admin/users/<int:user_id>")
@require_admin
def update_user(user_id):
    payload = request.get_json(silent=True) or {}
    actor = request.current_user

    try:
        target_user = user_store.get_user(user_id)
        _assert_manageable_target_user(actor, target_user)
        next_role = payload.get("role")
        if next_role is not None:
            next_role = _assert_assignable_role(actor, next_role)
        user = user_store.update_user(
            user_id,
            role=next_role,
            is_active=payload.get("is_active"),
            display_name=payload.get("display_name"),
            email=payload.get("email"),
            disabled_reason=payload.get("disabled_reason"),
        )
        action_type = "user_update"
        if next_role is not None and next_role != target_user["role"]:
            action_type = "user_change_role"
        elif payload.get("is_active") is not None:
            action_type = "user_enable" if bool(payload.get("is_active")) else "user_disable"
        _record_admin_audit(
            action_type,
            target_user=user,
            detail={
                "role": next_role,
                "is_active": payload.get("is_active"),
                "display_name": payload.get("display_name"),
                "email": payload.get("email"),
            },
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "user updated", "user": user})


@app.post("/api/admin/users/<int:user_id>/reset-password")
@require_admin
def reset_admin_user_password(user_id):
    payload = request.get_json(silent=True) or {}
    actor = request.current_user
    try:
        target_user = user_store.get_user(user_id)
        _assert_manageable_target_user(actor, target_user)
        user = user_store.reset_user_password(user_id, payload.get("password"))
        _record_admin_audit(
            "user_reset_password",
            target_user=user,
            detail={"password_reset": True},
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"message": "password reset", "user": user})


@app.delete("/api/admin/users/<int:user_id>")
@require_admin
def delete_user(user_id):
    actor = request.current_user
    try:
        target_user = user_store.get_user(user_id)
        _assert_manageable_target_user(actor, target_user)
        indexes = user_store.list_user_indexes(user_id)
        for index_record in indexes:
            _delete_collection_if_present(index_record["collection_name"])
        user = user_store.delete_user(user_id)
        _record_admin_audit(
            "user_delete",
            target_user=target_user,
            detail={"deleted_index_count": len(indexes)},
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "user deleted", "user": user})


@app.get("/api/admin/datasets")
@require_admin
def admin_datasets():
    raw_owner_user_id = request.args.get("owner_user_id")
    owner_user_id = None
    if raw_owner_user_id not in (None, ""):
        try:
            owner_user_id = int(raw_owner_user_id)
        except Exception as exc:
            return jsonify({"error": f"invalid owner_user_id: {exc}"}), 400
    return jsonify({"datasets": admin_store.list_datasets(owner_user_id=owner_user_id)})


@app.delete("/api/admin/datasets/<int:dataset_id>")
@require_admin
def admin_delete_dataset(dataset_id):
    try:
        dataset = admin_store.get_dataset(dataset_id)
        if not dataset:
            raise AuthError("dataset not found")
        _assert_manageable_target_user(
            request.current_user,
            {
                "id": dataset["owner_user_id"],
                "role": dataset.get("owner_role"),
                "username": dataset.get("owner_username"),
            },
            allow_self=True,
        )
        related_indexes = admin_store.list_indexes(dataset_id=dataset_id)
        for index_record in related_indexes:
            target_user = {
                "id": index_record["user_id"],
                "role": index_record.get("owner_role"),
                "username": index_record.get("owner_username"),
            }
            _assert_manageable_target_user(request.current_user, target_user, allow_self=True)
            _delete_index_record(index_record)
        deleted_dataset = admin_store.delete_dataset(dataset_id)
        _record_admin_audit(
            "dataset_delete",
            target_dataset=deleted_dataset,
            detail={"deleted_index_count": len(related_indexes)},
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "dataset deleted", "dataset": deleted_dataset})


@app.get("/api/admin/indexes")
@require_admin
def admin_indexes():
    raw_user_id = request.args.get("user_id")
    raw_dataset_id = request.args.get("dataset_id")
    user_id = None
    dataset_id = None
    try:
        if raw_user_id not in (None, ""):
            user_id = int(raw_user_id)
        if raw_dataset_id not in (None, ""):
            dataset_id = int(raw_dataset_id)
    except Exception as exc:
        return jsonify({"error": f"invalid filter: {exc}"}), 400
    return jsonify({"indexes": admin_store.list_indexes(user_id=user_id, dataset_id=dataset_id)})


@app.post("/api/admin/indexes/<int:index_id>/activate")
@require_admin
def admin_activate_index(index_id):
    try:
        index_record = admin_store.get_index(index_id)
        if not index_record:
            raise AuthError("index not found")
        _assert_manageable_target_user(
            request.current_user,
            {
                "id": index_record["user_id"],
                "role": index_record.get("owner_role"),
                "username": index_record.get("owner_username"),
            },
            allow_self=True,
        )
        _require_collection_exists(index_record["collection_name"])
        activated = user_store.set_active_user_index(index_record["user_id"], index_id)
        _record_admin_audit(
            "index_force_activate",
            target_index=activated,
            detail={"owner_user_id": index_record["user_id"]},
        )
    except (AuthError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"message": "index activated", "index": activated})


@app.delete("/api/admin/indexes/<int:index_id>")
@require_admin
def admin_delete_index(index_id):
    try:
        index_record = admin_store.get_index(index_id)
        if not index_record:
            raise AuthError("index not found")
        _assert_manageable_target_user(
            request.current_user,
            {
                "id": index_record["user_id"],
                "role": index_record.get("owner_role"),
                "username": index_record.get("owner_username"),
            },
            allow_self=True,
        )
        deleted_index, next_active_index = _delete_index_record(index_record)
        _record_admin_audit(
            "index_delete",
            target_index=deleted_index,
            detail={"owner_user_id": index_record["user_id"]},
        )
    except (AuthError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "message": "index deleted",
            "index": deleted_index,
            "next_active_index": next_active_index,
        }
    )


@app.get("/api/admin/build-jobs")
@require_admin
def admin_build_jobs():
    try:
        limit = int(request.args.get("limit", 120))
    except Exception as exc:
        return jsonify({"error": f"invalid limit: {exc}"}), 400
    return jsonify({"jobs": admin_store.list_build_jobs(limit=limit)})


@app.get("/api/admin/audit-logs")
@require_admin
def admin_audit_logs():
    try:
        limit = int(request.args.get("limit", 120))
    except Exception as exc:
        return jsonify({"error": f"invalid limit: {exc}"}), 400
    return jsonify({"logs": admin_store.list_audit_logs(limit=limit)})


@app.post("/api/dataset/upload")
@require_auth
def upload_dataset():
    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return jsonify({"error": "file is required"}), 400

    user_id = request.current_user["id"]
    try:
        upload_info = _save_uploaded_dataset(uploaded_file, user_id)
        dataset_info = inspect_cell_dataset(upload_info["data_path"])
        dataset_record = _ensure_dataset_record(
            user_id,
            upload_info["data_path"],
            dataset_info={
                **dataset_info,
                "dataset_name": Path(upload_info["data_path"]).stem or "dataset",
                "uploaded_filename": upload_info["filename"],
                "size_bytes": upload_info["size_bytes"],
            },
            status="ready",
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "message": "dataset uploaded",
            **upload_info,
            "dataset": dataset_info,
            "dataset_record": dataset_record,
        }
    )


@app.post("/api/dataset/inspect")
@require_auth
def inspect_dataset():
    payload = request.get_json(silent=True) or {}
    data_path = payload.get("data_path") or str(DEFAULT_SAMPLE_DATA)
    user_id = request.current_user["id"]

    try:
        dataset_info = inspect_cell_dataset(data_path)
        _ensure_dataset_record(user_id, data_path, dataset_info=dataset_info, status="ready")
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
    activate = _to_bool(payload.get("activate"), default=True)
    run_async = _to_bool(payload.get("async"), default=False)
    reuse_if_available = _to_bool(payload.get("reuse_if_available"), default=True)

    try:
        requested_options = normalize_requested_build_options(
            index_type=payload.get("index_type"),
            distance_metric=payload.get("distance_metric"),
            quantization_config=payload.get("quantization_config"),
            hnsw_params=payload.get("hnsw_params"),
            search_params=payload.get("search_params"),
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    index_type = requested_options["index_type"]
    distance_metric = requested_options["distance_metric"]
    effective_metric = requested_options["effective_metric"]
    quantization_config = requested_options["quantization_config"]
    hnsw_params = requested_options["hnsw_params"]
    search_params = requested_options["search_params"]

    if reuse_if_available:
        reusable_index = _find_reusable_index_for_request(
            user_id,
            data_path,
            index_type,
            distance_metric,
            effective_metric,
            quantization_config,
            hnsw_params,
            search_params,
        )
        if reusable_index:
            if activate and not reusable_index["is_active"]:
                reusable_index = user_store.set_active_user_index(user_id, reusable_index["id"])
            return (
                jsonify(
                    {
                        "message": "reused existing index",
                        "reused": True,
                        "index": reusable_index,
                    }
                ),
                200,
            )

    dataset_record = _ensure_dataset_record(
        user_id,
        data_path,
        dataset_info=_seed_dataset_info(data_path),
        status="indexing" if run_async else "ready",
    )

    if run_async:
        existing_job = user_store.get_latest_running_build_job(user_id, data_path=data_path)
        if (
            existing_job
            and existing_job.get("index_type") == index_type
            and existing_job.get("distance_metric") == distance_metric
            and (existing_job.get("quantization_config") or {}) == quantization_config
            and existing_job.get("hnsw_params") == hnsw_params
            and existing_job.get("search_params") == search_params
        ):
            with INDEX_BUILD_JOBS_LOCK:
                INDEX_BUILD_JOBS[existing_job["job_id"]] = dict(existing_job)
            return (
                jsonify(
                    {
                        "message": "existing build job resumed",
                        "job_id": existing_job["job_id"],
                        "status": existing_job["status"],
                        "stage": existing_job["stage"],
                        "resumed": True,
                    }
                ),
                202,
            )
        try:
            job = _create_index_build_job(
                user_id=user_id,
                dataset_id=dataset_record["id"] if dataset_record else None,
                data_path=data_path,
                index_name=index_name,
                index_type=index_type,
                distance_metric=distance_metric,
                effective_metric=effective_metric,
                quantization_config=quantization_config,
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
            dataset_id=dataset_record["id"] if dataset_record else None,
            index_type=index_type,
            distance_metric=distance_metric,
            quantization_config=quantization_config,
            hnsw_params=hnsw_params,
            search_params=search_params,
            activate=activate,
            created_by=user_id,
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
    if job["user_id"] != current_user["id"] and not _is_admin_user(current_user):
        return jsonify({"error": "forbidden"}), 403

    return jsonify({"job": _public_index_build_job(job)})


@app.get("/api/index/build/jobs/latest-running")
@require_auth
def latest_running_index_build_job():
    user_id = request.current_user["id"]
    data_path = request.args.get("data_path")
    job = user_store.get_latest_running_build_job(user_id, data_path=data_path)
    if not job:
        return jsonify({"job": None})
    with INDEX_BUILD_JOBS_LOCK:
        INDEX_BUILD_JOBS[job["job_id"]] = dict(job)
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

    raw_limit = request.args.get("limit")
    limit = None
    if raw_limit not in (None, ""):
        try:
            limit = int(raw_limit)
        except Exception as exc:
            return jsonify({"error": f"invalid limit: {exc}"}), 400

    level = request.args.get("level", "preview")

    try:
        preview = load_dataset_visualization_preview(
            data_path=data_path,
            limit=limit,
            seed=42,
            level=level,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(preview)


@app.get("/api/dataset/umap-stats")
@require_auth
def dataset_umap_stats():
    data_path = request.args.get("data_path")
    if not data_path:
        return jsonify({"error": "data_path is required"}), 400

    try:
        stats = load_dataset_analytics(data_path=data_path)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(stats)


@app.get("/api/dataset/metadata-options")
@require_auth
def dataset_metadata_options():
    data_path = request.args.get("data_path")
    raw_index_id = request.args.get("index_id")
    if not data_path and not raw_index_id:
        return jsonify({"error": "data_path or index_id is required"}), 400

    try:
        max_values = int(request.args.get("max_values", 200))
    except Exception as exc:
        return jsonify({"error": f"invalid max_values: {exc}"}), 400

    raw_fields = request.args.get("fields", "")
    fields = [item.strip() for item in raw_fields.split(",") if item.strip()]
    if not fields:
        fields = list(DEFAULT_METADATA_FILTER_FIELDS)

    dataset_error = None
    try:
        if data_path:
            options = load_dataset_metadata_options(
                data_path=data_path,
                fields=fields or None,
                max_values_per_field=max_values,
            )
            options["source"] = "dataset_file"
            return jsonify(options)
    except Exception as exc:
        dataset_error = str(exc)

    payload = {}
    if raw_index_id:
        payload["index_id"] = raw_index_id

    try:
        index_record = _resolve_target_index(payload=payload, required=True)
        options = index.get_metadata_options(
            collection_name=index_record["collection_name"],
            fields=fields,
            max_values_per_field=max_values,
        )
        options.update(
            {
                "source": "index_payload",
                "index_id": index_record["id"],
                "collection": index_record["collection_name"],
            }
        )
        if data_path:
            options["source_path"] = data_path
        if dataset_error:
            options["dataset_error"] = dataset_error
        return jsonify(options)
    except Exception as exc:
        if dataset_error:
            return jsonify({"error": dataset_error, "fallback_error": str(exc)}), 400
        return jsonify({"error": str(exc)}), 400


def _metadata_options_for_ai(data_path: str) -> dict:
    return load_dataset_metadata_options(
        data_path=data_path,
        fields=list(DEFAULT_METADATA_FILTER_FIELDS),
        max_values_per_field=min(API_METADATA_VALUES_MAX, 120),
    )


@app.post("/api/ai/chat")
@app.post("/api/ai/index-advice")
@require_auth
def ai_chat():
    payload = request.get_json(silent=True) or {}
    data_path = str(payload.get("data_path") or "").strip()
    if not data_path:
        return jsonify({"error": "data_path is required"}), 400

    raw_dataset_info = payload.get("dataset_info")
    dataset_info = raw_dataset_info if isinstance(raw_dataset_info, dict) else None

    raw_build_options = payload.get("current_build_options")
    current_build_options = raw_build_options if isinstance(raw_build_options, dict) else None

    user_question = str(payload.get("user_question") or "").strip()[:2000]
    raw_conversation_history = payload.get("conversation_history")
    conversation_history = raw_conversation_history if isinstance(raw_conversation_history, list) else []

    try:
        if not dataset_info:
            dataset_info = inspect_cell_dataset(data_path)
        dataset_context = build_dataset_context(
            data_path=data_path,
            dataset_info=dataset_info,
            current_build_options=current_build_options,
        )
        ai_result = request_ai_chat(
            api_key=ZHIPU_API_KEY,
            model=ZHIPU_MODEL,
            api_url=ZHIPU_API_URL,
            dataset_context=dataset_context,
            user_question=user_question,
            conversation_history=conversation_history,
        )
    except AIAdvisorError as exc:
        error_text = str(exc)
        status_code = 503 if "not configured" in error_text or "connection failed" in error_text else 400
        return jsonify({"error": error_text}), status_code
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return _api_ok(
        {
            "message": "AI chat response ready",
            "model": ai_result["model"],
            "dataset_summary": dataset_context,
            "answer": ai_result["answer"],
            "suggested_question": ai_result.get("suggested_question") or DEFAULT_SUGGESTED_QUESTION,
        }
    )


@app.post("/api/ai/cell-query")
@require_auth
def ai_cell_query():
    payload = request.get_json(silent=True) or {}
    data_path = str(payload.get("data_path") or "").strip()
    if not data_path:
        return jsonify({"error": "data_path is required"}), 400

    raw_dataset_info = payload.get("dataset_info")
    dataset_info = raw_dataset_info if isinstance(raw_dataset_info, dict) else None
    raw_build_options = payload.get("current_build_options")
    current_build_options = raw_build_options if isinstance(raw_build_options, dict) else None
    raw_index_id = payload.get("index_id")
    user_question = str(payload.get("user_question") or "").strip()[:2000]
    if not user_question:
        return jsonify({"error": "user_question is required"}), 400
    raw_conversation_history = payload.get("conversation_history")
    conversation_history = raw_conversation_history if isinstance(raw_conversation_history, list) else []
    raw_current_results = payload.get("current_results")
    current_results = raw_current_results if isinstance(raw_current_results, list) else []
    selected_cell_id = str(payload.get("selected_cell_id") or "").strip()
    raw_query_context = payload.get("query_context")
    query_context = raw_query_context if isinstance(raw_query_context, dict) else {}

    try:
        if not dataset_info:
            dataset_info = inspect_cell_dataset(data_path)
        dataset_context = build_dataset_context(
            data_path=data_path,
            dataset_info=dataset_info,
            current_build_options=current_build_options,
        )
        metadata_options = _metadata_options_for_ai(data_path)
        index_payload = {"index_id": raw_index_id} if raw_index_id not in (None, "") else {}
        active_index_record = _resolve_target_index(payload=index_payload, required=False)
        analysis = analyze_cell_query(
            question=user_question,
            data_path=data_path,
            dataset_context=dataset_context,
            metadata_options=metadata_options,
            active_index_record=active_index_record,
            vector_index=index,
            api_key=ZHIPU_API_KEY,
            api_url=ZHIPU_API_URL,
            model=ZHIPU_MODEL,
            conversation_history=conversation_history,
            current_results=current_results,
            selected_cell_id=selected_cell_id,
            query_context=query_context,
        )
    except AIAdvisorError as exc:
        error_text = str(exc)
        status_code = 503 if "not configured" in error_text or "connection failed" in error_text else 400
        return jsonify({"error": error_text}), status_code
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return _api_ok(
        {
            "message": "AI cell analysis ready",
            "model": analysis["model"],
            "dataset_summary": dataset_context,
            "answer": analysis["answer"],
            "intent": analysis["intent"],
            "applied_filters": analysis["applied_filters"],
            "knowledge_hits": analysis["knowledge_hits"],
            "cell_hits": analysis["cell_hits"],
            "cell_summary": analysis["cell_summary"],
            "next_steps": analysis["next_steps"],
            "retrieval_source": analysis["retrieval_source"],
            "query_context": analysis.get("query_context") or {},
        }
    )


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


@app.delete("/api/indexes/<int:index_id>")
@require_auth
def delete_index(index_id):
    user_id = request.current_user["id"]

    try:
        index_record = user_store.get_user_index(user_id, index_id)
        if not index_record:
            raise AuthError("index not found")
        deleted_index, next_active_index = _delete_index_record(index_record)
    except (AuthError, ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "message": "index deleted",
            "index": deleted_index,
            "next_active_index": next_active_index,
        }
    )


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
        requested_options = normalize_requested_build_options(
            index_type=payload.get("index_type"),
            distance_metric=payload.get("distance_metric"),
            quantization_config=payload.get("quantization_config"),
            hnsw_params=payload.get("hnsw_params"),
            search_params=payload.get("search_params"),
        )
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
            index_type=requested_options["index_type"],
            distance_metric=requested_options["distance_metric"],
            effective_metric=requested_options["effective_metric"],
            quantization_config=requested_options["quantization_config"],
            metadata_keys=payload.get("metadata_fields") or [],
            hnsw_params=requested_options["hnsw_params"],
            search_params=requested_options["search_params"],
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
            benchmark = _compare_ann_improvement_by_cell_id(
                collection_name=index_record["collection_name"],
                vector_dim=index_record["vector_dim"],
                cell_id=cell_id,
                top_k=top_k,
                filters=filters,
                search_params=search_params,
            )
            after = benchmark["after"]
            return jsonify(
                {
                    "query": {
                        "cell_id": cell_id,
                        "top_k": top_k,
                        "filters": filters,
                        "index_id": index_record["id"],
                    },
                    "query_time_ms": after["query_time_ms"],
                    "results": benchmark["ann_results"],
                    "evaluation": {
                        "precision_at_k": after["precision_at_k"],
                        "recall_at_k": after["recall_at_k"],
                        "overlap_count": after["overlap_count"],
                        "ann_query_time_ms": after["query_time_ms"],
                        "exact_query_time_ms": benchmark["exact"]["query_time_ms"],
                    },
                    "improvement_benchmark": benchmark,
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
            benchmark = _compare_ann_improvement_by_vector(
                collection_name=index_record["collection_name"],
                vector_dim=index_record["vector_dim"],
                vector=vector,
                top_k=top_k,
                filters=filters,
                search_params=search_params,
            )
            after = benchmark["after"]
            return jsonify(
                {
                    "query": {
                        "top_k": top_k,
                        "filters": filters,
                        "index_id": index_record["id"],
                    },
                    "query_time_ms": after["query_time_ms"],
                    "results": benchmark["ann_results"],
                    "evaluation": {
                        "precision_at_k": after["precision_at_k"],
                        "recall_at_k": after["recall_at_k"],
                        "overlap_count": after["overlap_count"],
                        "ann_query_time_ms": after["query_time_ms"],
                        "exact_query_time_ms": benchmark["exact"]["query_time_ms"],
                    },
                    "improvement_benchmark": benchmark,
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


@app.post("/api/search/by-vector-csv")
@require_auth
def search_by_vector_csv():
    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return jsonify({"error": "file is required"}), 400

    try:
        top_k = _parse_top_k(request.form.get("top_k", 5))
        row_index = int(request.form.get("row_index", 0))
        evaluate = _to_bool(request.form.get("evaluate"), default=False)
        filters = json.loads(request.form.get("filters") or "{}")
        if not isinstance(filters, dict):
            raise ValueError("filters must be a JSON object")
        index_record = _resolve_target_index({"index_id": request.form.get("index_id")})
        search_params = index_record.get("search_params") or {}
        vector, csv_info = _extract_query_vector_from_csv_upload(uploaded_file, row_index=row_index)

        if evaluate:
            benchmark = _compare_ann_improvement_by_vector(
                collection_name=index_record["collection_name"],
                vector_dim=index_record["vector_dim"],
                vector=vector,
                top_k=top_k,
                filters=filters,
                search_params=search_params,
            )
            after = benchmark["after"]
            return jsonify(
                {
                    "query": {
                        "top_k": top_k,
                        "filters": filters,
                        "index_id": index_record["id"],
                        "csv": csv_info,
                    },
                    "query_time_ms": after["query_time_ms"],
                    "results": benchmark["ann_results"],
                    "evaluation": {
                        "precision_at_k": after["precision_at_k"],
                        "recall_at_k": after["recall_at_k"],
                        "overlap_count": after["overlap_count"],
                        "ann_query_time_ms": after["query_time_ms"],
                        "exact_query_time_ms": benchmark["exact"]["query_time_ms"],
                    },
                    "improvement_benchmark": benchmark,
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
                "csv": csv_info,
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
                    "index_type": "ivf",
                    "distance_metric": "cosine",
                    "async": True,
                    "quantization_config": {"nlist": 128},
                    "search_params": {"nprobe": 8},
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


def _run_index_build_job(job_id: str):
    job = _get_index_build_job(job_id)
    if not job:
        return

    user_id = job["user_id"]
    data_path = job["data_path"]
    index_name = job["index_name"]
    index_type = job["index_type"]
    distance_metric = job["distance_metric"]
    quantization_config = job.get("quantization_config") or {}
    hnsw_params = job["hnsw_params"]
    search_params = job["search_params"]
    activate = bool(job["activate"])

    _update_index_build_job(
        job_id,
        status="running",
        stage="loading_dataset",
        message="loading dataset",
        started_at=_utc_now_iso(),
        progress_pct=1.0,
        elapsed_seconds=0.0,
    )
    _append_index_build_history(job_id, stage="loading_dataset", text="loading dataset and extracting vectors")

    progress_start = perf_counter()

    def on_status(stage: str, payload: dict):
        elapsed_seconds = round(max(perf_counter() - progress_start, 0.0), 1)
        if stage == "dataset_loaded":
            cell_count = payload.get("cell_count")
            gene_count = payload.get("gene_count")
            vector_dim = payload.get("vector_dim")
            summary = {
                "cell_count": cell_count,
                "gene_count": gene_count,
                "vector_dim": vector_dim,
                "embedding_key": payload.get("embedding_key"),
                "source_path": payload.get("source_path"),
                "source_format": payload.get("source_format"),
            }
            _update_index_build_job(
                job_id,
                status="running",
                stage="dataset_loaded",
                message=f"dataset loaded, start building FAISS {index_type}",
                progress_pct=5.0,
                processed_cells=0,
                total_cells=cell_count,
                elapsed_seconds=elapsed_seconds,
                dataset_summary=summary,
            )
            _append_index_build_history(
                job_id,
                stage="dataset_loaded",
                text=(
                    f"dataset loaded: {cell_count} cells, {gene_count} genes, "
                    f"dim {vector_dim}, index_type={index_type}"
                ),
            )
        elif stage == "persisting_index":
            _update_index_build_job(
                job_id,
                status="running",
                stage="persisting_index",
                message="persisting index metadata",
                progress_pct=97.0,
                processed_cells=payload.get("cell_count"),
                total_cells=payload.get("cell_count"),
                elapsed_seconds=elapsed_seconds,
                eta_seconds=1.0,
            )
            _append_index_build_history(
                job_id,
                stage="persisting_index",
                text=f"persisting index metadata for {payload.get('collection_name')}",
            )

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
            message=f"building FAISS {index_type} index ({processed_cells}/{total_cells})",
            progress_pct=progress_pct,
            processed_cells=processed_cells,
            total_cells=total_cells,
            elapsed_seconds=round(elapsed_seconds, 1),
            rate_cells_per_second=round(processed_cells / elapsed_seconds, 1) if processed_cells > 0 else None,
            eta_seconds=eta_seconds,
        )

    try:
        result = _perform_index_build(
            user_id=user_id,
            data_path=data_path,
            index_name=index_name,
            dataset_id=job.get("dataset_id"),
            index_type=index_type,
            distance_metric=distance_metric,
            quantization_config=quantization_config,
            hnsw_params=hnsw_params,
            search_params=search_params,
            activate=activate,
            created_by=user_id,
            progress_callback=on_progress,
            status_callback=on_status,
        )
    except Exception as exc:
        _update_index_build_job(
            job_id,
            status="failed",
            stage="failed",
            message="index build failed",
            error=str(exc),
            progress_pct=100.0,
            finished_at=_utc_now_iso(),
            elapsed_seconds=round(max(perf_counter() - progress_start, 0.0), 1),
            eta_seconds=None,
        )
        _append_index_build_history(job_id, stage="failed", text=f"build failed: {exc}")
        return

    _update_index_build_job(
        job_id,
        status="completed",
        stage="completed",
        message="index build completed",
        progress_pct=100.0,
        processed_cells=result["cell_count"],
        total_cells=result["cell_count"],
        elapsed_seconds=round(max(perf_counter() - progress_start, 0.0), 1),
        rate_cells_per_second=round(
            result["cell_count"] / max(perf_counter() - progress_start, 0.001),
            1,
        ),
        result=result,
        finished_at=_utc_now_iso(),
        eta_seconds=0.0,
    )
    _append_index_build_history(job_id, stage="completed", text="index build completed")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
