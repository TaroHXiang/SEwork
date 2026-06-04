from __future__ import annotations

from pathlib import Path
from time import perf_counter

from flask import Flask, jsonify, request

from config import FAISS_DATA_ROOT
from services.data_loader import load_cell_vectors
from services.faiss_engine import CellVectorIndex


app = Flask(__name__)
engine = CellVectorIndex()


@app.errorhandler(FileNotFoundError)
def handle_not_found(exc):
    return jsonify({"error": str(exc)}), 404


@app.errorhandler(ValueError)
def handle_value_error(exc):
    return jsonify({"error": str(exc)}), 400


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    app.logger.exception("Unhandled FAISS service error")
    return jsonify({"error": str(exc)}), 500


def _resolve_data_path(raw_path: str) -> str:
    if not raw_path:
        raise ValueError("data_path is required")
    candidate = Path(raw_path)
    if candidate.is_absolute():
        if candidate.exists():
            return str(candidate)
        raise FileNotFoundError(f"data file not found inside container: {candidate}")
    resolved = (FAISS_DATA_ROOT / candidate).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"data file not found inside container: {resolved}")
    return str(resolved)


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "faiss_data_root": str(FAISS_DATA_ROOT),
            "faiss_index_path": str(engine.storage_path),
        }
    )


@app.get("/collections/<collection_name>/exists")
def collection_exists(collection_name: str):
    return jsonify({"exists": engine.collection_exists(collection_name)})


@app.post("/collections/build")
def build_collection():
    payload = request.get_json(silent=True) or {}
    data_path = _resolve_data_path(payload.get("data_path"))
    dataset = load_cell_vectors(data_path)
    build_meta = engine.build(
        dataset=dataset,
        collection_name=payload.get("collection_name") or engine.default_collection_name,
        index_type=payload.get("index_type"),
        distance_metric=payload.get("distance_metric"),
        quantization_config=payload.get("quantization_config"),
        hnsw_params=payload.get("hnsw_params"),
        search_params=payload.get("search_params"),
    )
    return jsonify(
        {
            **build_meta,
            "dataset_summary": {
                **dataset.summary(),
                "index_type": build_meta["index_type"],
                "distance_metric": build_meta["distance_metric"],
                "effective_metric": build_meta["effective_metric"],
                "quantization_config": build_meta.get("quantization_config") or {},
                "resolved_quantization_config": build_meta.get("resolved_quantization_config") or {},
            },
        }
    )


@app.post("/collections/<collection_name>/visualization")
def visualization(collection_name: str):
    payload = request.get_json(silent=True) or {}
    result = engine.get_visualization_points(
        collection_name=collection_name,
        limit=int(payload.get("limit") or 10000),
        filters=payload.get("filters") or None,
    )
    return jsonify(result)


@app.post("/collections/<collection_name>/metadata-options")
def metadata_options(collection_name: str):
    payload = request.get_json(silent=True) or {}
    result = engine.get_metadata_options(
        collection_name=collection_name,
        fields=payload.get("fields") or [],
        max_values_per_field=int(payload.get("max_values_per_field") or 200),
        scan_limit=int(payload.get("scan_limit") or 300000),
    )
    return jsonify(result)


@app.post("/collections/<collection_name>/search/by-id")
def search_by_id(collection_name: str):
    payload = request.get_json(silent=True) or {}
    start = perf_counter()
    results = engine.search_by_cell_id(
        collection_name=collection_name,
        vector_dim=int(payload.get("vector_dim") or 0),
        cell_id=payload.get("cell_id") or "",
        top_k=int(payload.get("top_k") or 5),
        filters=payload.get("filters") or None,
        search_params=payload.get("search_params") or None,
        distance_metric=payload.get("distance_metric") or "cosine",
        exact=payload.get("exact"),
    )
    return jsonify(
        {
            "results": results,
            "query_time_ms": round((perf_counter() - start) * 1000, 2),
        }
    )


@app.post("/collections/<collection_name>/search/by-vector")
def search_by_vector(collection_name: str):
    payload = request.get_json(silent=True) or {}
    result = engine.search_by_vector_with_timing(
        collection_name=collection_name,
        vector_dim=int(payload.get("vector_dim") or 0),
        vector=payload.get("vector") or [],
        top_k=int(payload.get("top_k") or 5),
        filters=payload.get("filters") or None,
        search_params=payload.get("search_params") or None,
        distance_metric=payload.get("distance_metric") or "cosine",
        vector_is_prepared=bool(payload.get("vector_is_prepared")),
        exact=payload.get("exact"),
    )
    return jsonify(
        {
            "results": result.results,
            "query_time_ms": result.query_time_ms,
        }
    )


@app.post("/collections/<collection_name>/evaluate/by-id")
def evaluate_by_id(collection_name: str):
    payload = request.get_json(silent=True) or {}
    result = engine.evaluate_query_by_cell_id(
        collection_name=collection_name,
        vector_dim=int(payload.get("vector_dim") or 0),
        cell_id=payload.get("cell_id") or "",
        top_k=int(payload.get("top_k") or 10),
        filters=payload.get("filters") or None,
        search_params=payload.get("search_params") or None,
        distance_metric=payload.get("distance_metric") or "cosine",
    )
    return jsonify(result)


@app.post("/collections/<collection_name>/evaluate/by-vector")
def evaluate_by_vector(collection_name: str):
    payload = request.get_json(silent=True) or {}
    result = engine.evaluate_query_by_vector(
        collection_name=collection_name,
        vector_dim=int(payload.get("vector_dim") or 0),
        vector=payload.get("vector") or [],
        top_k=int(payload.get("top_k") or 10),
        filters=payload.get("filters") or None,
        search_params=payload.get("search_params") or None,
        distance_metric=payload.get("distance_metric") or "cosine",
        vector_is_prepared=bool(payload.get("vector_is_prepared")),
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
