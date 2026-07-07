from __future__ import annotations

import json
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterable

import numpy as np

from config import FAISS_INDEX_PATH, VECTOR_INDEX_COLLECTION
from services.data_loader import CellVectorDataset


DEFAULT_HNSW_PARAMS = {
    "m": 16,
    "ef_construct": 128,
}
DEFAULT_SEARCH_PARAMS = {
    "hnsw_ef": 128,
    "nprobe": 8,
    "exact": False,
    "rerank_k": 50,
    "filter_candidate_multiplier": 20,
}
DEFAULT_INDEX_TYPE = "hnsw"
DEFAULT_DISTANCE_METRIC = "cosine"
DEFAULT_PQ_CONFIG = {
    "compression": "x16",
    "nbits": 8,
}
SUPPORTED_INDEX_TYPES = {"hnsw", "ivf", "pq"}
SUPPORTED_DISTANCE_METRICS = {"cosine", "ip", "l2", "pearson"}
FAISS_DISTANCE_NAMES = {
    "cosine": "inner_product",
    "ip": "inner_product",
    "l2": "l2",
    "pearson": "inner_product",
}
PQ_COMPRESSION_FACTORS = {
    "x4": 4,
    "x8": 8,
    "x16": 16,
    "x32": 32,
    "x64": 64,
}


@dataclass
class SearchResult:
    results: list[dict]
    query_time_ms: float


@dataclass
class _StoredCollection:
    name: str
    index: object
    vectors: np.ndarray
    cell_ids: list[str]
    metadata: list[dict]
    visualization_points: np.ndarray
    cell_id_to_offset: dict[str, int]
    manifest: dict
    vector_transform: dict | None = None


class CellVectorIndex:
    def __init__(self, collection_name: str = VECTOR_INDEX_COLLECTION):
        self.default_collection_name = collection_name
        self.storage_path = Path(FAISS_INDEX_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.collection_name: str | None = None
        self.dataset_summary: dict | None = None
        self.vector_dim: int | None = None
        self._collection_cache: dict[str, _StoredCollection] = {}

    @property
    def is_ready(self) -> bool:
        return self.vector_dim is not None and self.collection_name is not None

    def build(
        self,
        dataset: CellVectorDataset,
        collection_name: str,
        index_type: str = DEFAULT_INDEX_TYPE,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
        quantization_config: dict | None = None,
        hnsw_params: dict | None = None,
        search_params: dict | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict:
        if dataset.cell_count < 1:
            raise ValueError("dataset must contain at least one vector")

        collection_name = _normalize_collection_name(collection_name)
        requested_options = normalize_requested_build_options(
            index_type=index_type,
            distance_metric=distance_metric,
            quantization_config=quantization_config,
            hnsw_params=hnsw_params,
            search_params=search_params,
        )
        resolved_index = resolve_index_build_config(
            index_type=requested_options["index_type"],
            distance_metric=requested_options["distance_metric"],
            quantization_config=requested_options["quantization_config"],
            vector_dim=dataset.vector_dim,
            cell_count=dataset.cell_count,
        )
        indexed_vectors = _prepare_vectors_for_metric(dataset.vectors, resolved_index["distance_metric"])

        faiss_index = _build_faiss_index(
            vectors=indexed_vectors,
            vector_dim=dataset.vector_dim,
            index_type=resolved_index["index_type"],
            distance_metric=resolved_index["distance_metric"],
            hnsw_params=requested_options["hnsw_params"],
            quantization_config=resolved_index["quantization_config"],
        )
        if progress_callback is not None:
            progress_callback(0, dataset.cell_count)

        batch_size = 1000
        for start in range(0, dataset.cell_count, batch_size):
            batch = np.ascontiguousarray(indexed_vectors[start : start + batch_size], dtype=np.float32)
            faiss_index.add(batch)
            if progress_callback is not None:
                processed = min(start + len(batch), dataset.cell_count)
                progress_callback(processed, dataset.cell_count)

        manifest = {
            "collection_name": collection_name,
            "cell_count": dataset.cell_count,
            "vector_dim": dataset.vector_dim,
            "index_type": resolved_index["index_type"],
            "distance_metric": resolved_index["distance_metric"],
            "effective_metric": resolved_index["effective_metric"],
            "request_quantization_config": requested_options["quantization_config"],
            "resolved_quantization_config": resolved_index["quantization_config"],
            "hnsw_params": requested_options["hnsw_params"],
            "search_params": requested_options["search_params"],
            "metadata_fields": dataset.metadata_fields,
            "source_path": dataset.source_path,
            "source_format": dataset.source_format,
            "gene_count": dataset.gene_count,
            "embedding_key": dataset.embedding_key,
            "visualization_source": dataset.visualization_source,
            "vector_transform": _vector_transform_metadata(dataset.vector_transform),
        }
        self._persist_collection(
            collection_name=collection_name,
            index=faiss_index,
            vectors=indexed_vectors,
            cell_ids=dataset.cell_ids,
            metadata=dataset.metadata,
            visualization_points=dataset.visualization_points,
            manifest=manifest,
            vector_transform=dataset.vector_transform,
        )

        dataset_summary = {
            **dataset.summary(),
            "index_type": resolved_index["index_type"],
            "distance_metric": resolved_index["distance_metric"],
            "effective_metric": resolved_index["effective_metric"],
            "quantization_config": requested_options["quantization_config"],
            "resolved_quantization_config": resolved_index["quantization_config"],
        }
        self.set_active_collection(
            collection_name=collection_name,
            vector_dim=dataset.vector_dim,
            dataset_summary=dataset_summary,
        )
        return {
            "collection": collection_name,
            "index_type": resolved_index["index_type"],
            "distance_metric": resolved_index["distance_metric"],
            "effective_metric": resolved_index["effective_metric"],
            "quantization_config": requested_options["quantization_config"],
            "resolved_quantization_config": resolved_index["quantization_config"],
            "hnsw_params": requested_options["hnsw_params"],
            "search_params": requested_options["search_params"],
        }

    def get_visualization_points(
        self,
        collection_name: str,
        limit: int = 10000,
        filters: dict[str, str] | None = None,
    ) -> dict:
        if limit < 1 or limit > 100000:
            raise ValueError("limit must be between 1 and 100000")

        collection = self._load_collection(collection_name)
        candidate_offsets = _matching_offsets(collection.metadata, filters)
        total_points = int(len(candidate_offsets))
        selected_offsets = candidate_offsets[:limit]
        points = [
            {
                "cell_id": collection.cell_ids[offset],
                "x": float(collection.visualization_points[offset][0]),
                "y": float(collection.visualization_points[offset][1]),
                "metadata": collection.metadata[offset] or {},
            }
            for offset in selected_offsets
        ]
        return {
            "total_points": total_points,
            "returned_points": len(points),
            "points": points,
        }

    def get_metadata_options(
        self,
        collection_name: str,
        fields: list[str],
        max_values_per_field: int = 200,
        scan_limit: int = 300000,
    ) -> dict:
        if max_values_per_field < 1:
            raise ValueError("max_values_per_field must be greater than 0")
        if scan_limit < 1:
            raise ValueError("scan_limit must be greater than 0")

        target_fields = [field for field in (fields or []) if field]
        if not target_fields:
            return {
                "available_fields": [],
                "options": {},
                "unique_counts": {},
                "truncated_fields": [],
                "scanned_points": 0,
            }

        collection = self._load_collection(collection_name)
        scanned_points = min(len(collection.metadata), scan_limit)
        value_sets: dict[str, set[str]] = {field: set() for field in target_fields}
        for metadata in collection.metadata[:scanned_points]:
            metadata = metadata or {}
            for field in target_fields:
                current_values = value_sets[field]
                if len(current_values) >= max_values_per_field:
                    continue
                value = metadata.get(field)
                if value is None:
                    continue
                value_text = str(value).strip()
                if not value_text or value_text.lower() in {"nan", "none", "null"}:
                    continue
                current_values.add(value_text)

        options: dict[str, list[str]] = {}
        unique_counts: dict[str, int] = {}
        truncated_fields: list[str] = []
        scan_truncated = len(collection.metadata) > scan_limit
        for field in target_fields:
            values = sorted(value_sets[field])
            options[field] = values[:max_values_per_field]
            unique_counts[field] = len(values)
            if scan_truncated and len(values) >= max_values_per_field:
                truncated_fields.append(field)

        available_fields = [field for field in target_fields if options.get(field)]
        return {
            "available_fields": available_fields,
            "options": options,
            "unique_counts": unique_counts,
            "truncated_fields": truncated_fields,
            "scanned_points": scanned_points,
        }

    def search_by_cell_id(
        self,
        collection_name: str,
        vector_dim: int,
        cell_id: str,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
        exact: bool | None = None,
    ) -> list[dict]:
        vector = self._fetch_vector_by_cell_id(collection_name=collection_name, cell_id=cell_id)
        if not vector:
            raise ValueError(f"unknown cell_id: {cell_id}")
        return self.search_by_vector(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            distance_metric=distance_metric,
            vector_is_prepared=True,
            exact=exact,
        )

    def search_by_vector(
        self,
        collection_name: str,
        vector_dim: int,
        vector: Iterable[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
        vector_is_prepared: bool = False,
        exact: bool | None = None,
    ) -> list[dict]:
        result = self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            distance_metric=distance_metric,
            vector_is_prepared=vector_is_prepared,
            exact=exact,
        )
        return result.results

    def search_by_vector_with_timing(
        self,
        collection_name: str,
        vector_dim: int,
        vector: Iterable[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
        vector_is_prepared: bool = False,
        exact: bool | None = None,
    ) -> SearchResult:
        if top_k < 1 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        collection = self._load_collection(collection_name)
        manifest = collection.manifest
        resolved_distance_metric = str(manifest.get("distance_metric") or distance_metric).strip().lower()
        query_input = list(vector)
        if not vector_is_prepared:
            query_input = _transform_query_vector_if_needed(query_input, collection)
        query_vector = _prepare_query_vector_for_metric(
            vector=query_input,
            vector_dim=vector_dim,
            distance_metric=resolved_distance_metric,
            vector_is_prepared=vector_is_prepared,
        )
        resolved_search = _resolve_search_params(
            search_params or manifest.get("search_params"),
            exact=exact,
            index_type=manifest.get("index_type") or DEFAULT_INDEX_TYPE,
        )
        candidate_offsets = _matching_offsets(collection.metadata, filters)

        start_time = perf_counter()
        if resolved_search["exact"]:
            raw_hits = _exact_search(
                vectors=collection.vectors,
                query_vector=query_vector,
                candidate_offsets=candidate_offsets,
                top_k=top_k,
                distance_metric=resolved_distance_metric,
            )
        elif filters:
            raw_hits = _ann_filtered_rerank_search(
                collection=collection,
                query_vector=query_vector,
                top_k=top_k,
                search_params=resolved_search,
                distance_metric=resolved_distance_metric,
                candidate_offsets=candidate_offsets,
            )
        else:
            ann_top_k = max(top_k, int(resolved_search["rerank_k"]))
            ann_hits = _ann_search(
                collection=collection,
                query_vector=query_vector,
                top_k=ann_top_k,
                search_params=resolved_search,
                distance_metric=resolved_distance_metric,
            )
            raw_hits = _rerank_ann_hits(
                vectors=collection.vectors,
                query_vector=query_vector,
                ann_hits=ann_hits,
                top_k=top_k,
                distance_metric=resolved_distance_metric,
            )
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
        return SearchResult(
            results=[
                _build_search_result(
                    collection=collection,
                    offset=offset,
                    raw_value=raw_value,
                    distance_metric=resolved_distance_metric,
                    squared_l2=squared_l2,
                )
                for offset, raw_value, squared_l2 in raw_hits
            ],
            query_time_ms=elapsed_ms,
        )

    def evaluate_query_by_cell_id(
        self,
        collection_name: str,
        vector_dim: int,
        cell_id: str,
        top_k: int = 10,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
    ) -> dict:
        vector = self._fetch_vector_by_cell_id(collection_name=collection_name, cell_id=cell_id)
        if not vector:
            raise ValueError(f"unknown cell_id: {cell_id}")
        return self.evaluate_query_by_vector(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            distance_metric=distance_metric,
            vector_is_prepared=True,
        )

    def evaluate_query_by_vector(
        self,
        collection_name: str,
        vector_dim: int,
        vector: Iterable[float],
        top_k: int = 10,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
        vector_is_prepared: bool = False,
    ) -> dict:
        ann = self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            distance_metric=distance_metric,
            vector_is_prepared=vector_is_prepared,
            exact=False,
        )
        exact = self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            distance_metric=distance_metric,
            vector_is_prepared=vector_is_prepared,
            exact=True,
        )
        ann_ids = [item["cell_id"] for item in ann.results]
        exact_ids = [item["cell_id"] for item in exact.results]
        ann_set = set(ann_ids)
        exact_set = set(exact_ids)
        overlap_count = len(ann_set & exact_set)
        precision = overlap_count / len(ann_set) if ann_set else 0.0
        recall = overlap_count / len(exact_set) if exact_set else 0.0
        return {
            "top_k": top_k,
            "ann_query_time_ms": ann.query_time_ms,
            "exact_query_time_ms": exact.query_time_ms,
            "precision_at_k": round(precision, 6),
            "recall_at_k": round(recall, 6),
            "overlap_count": overlap_count,
            "distance_metric": distance_metric,
            "ann_results": ann.results,
            "exact_results": exact.results,
        }

    def collection_exists(self, collection_name: str) -> bool:
        collection_dir = self._collection_dir(collection_name)
        required_files = [
            collection_dir / "index.faiss",
            collection_dir / "manifest.json",
            collection_dir / "vectors.npy",
            collection_dir / "cell_ids.json",
            collection_dir / "metadata.json",
            collection_dir / "visualization.npy",
        ]
        return all(path.exists() for path in required_files)

    def delete_collection(self, collection_name: str) -> bool:
        collection_dir = self._collection_dir(collection_name)
        existed = collection_dir.exists()
        self._collection_cache.pop(collection_name, None)
        if existed:
            shutil.rmtree(collection_dir)
        if self.collection_name == collection_name:
            self.collection_name = None
            self.vector_dim = None
            self.dataset_summary = None
        return existed

    def set_active_collection(
        self,
        collection_name: str,
        vector_dim: int | None = None,
        dataset_summary: dict | None = None,
    ) -> None:
        self.collection_name = collection_name
        if vector_dim is not None:
            self.vector_dim = int(vector_dim)
        if dataset_summary is not None:
            self.dataset_summary = dataset_summary

    def _fetch_vector_by_cell_id(self, collection_name: str, cell_id: str) -> list[float] | None:
        collection = self._load_collection(collection_name)
        offset = collection.cell_id_to_offset.get(cell_id)
        if offset is None:
            return None
        return collection.vectors[offset].astype(float).tolist()

    def _collection_dir(self, collection_name: str) -> Path:
        return self.storage_path / collection_name

    def _persist_collection(
        self,
        *,
        collection_name: str,
        index: object,
        vectors: np.ndarray,
        cell_ids: list[str],
        metadata: list[dict],
        visualization_points: np.ndarray,
        manifest: dict,
        vector_transform: dict | None = None,
    ) -> None:
        faiss = _require_faiss()
        collection_dir = self._collection_dir(collection_name)
        temp_dir = self._collection_dir(f"{collection_name}__tmp")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(index, str(temp_dir / "index.faiss"))
        np.save(str(temp_dir / "vectors.npy"), np.ascontiguousarray(vectors, dtype=np.float32))
        np.save(
            str(temp_dir / "visualization.npy"),
            np.ascontiguousarray(visualization_points, dtype=np.float32),
        )
        _persist_vector_transform(temp_dir, vector_transform)
        (temp_dir / "cell_ids.json").write_text(
            json.dumps([str(item) for item in cell_ids], ensure_ascii=False),
            encoding="utf-8",
        )
        (temp_dir / "metadata.json").write_text(
            json.dumps(list(metadata or []), ensure_ascii=False),
            encoding="utf-8",
        )
        (temp_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if collection_dir.exists():
            shutil.rmtree(collection_dir)
        temp_dir.rename(collection_dir)
        self._collection_cache.pop(collection_name, None)

    def _load_collection(self, collection_name: str) -> _StoredCollection:
        if collection_name in self._collection_cache:
            return self._collection_cache[collection_name]
        if not self.collection_exists(collection_name):
            raise RuntimeError(f"collection not found in local FAISS storage: {collection_name}")

        faiss = _require_faiss()
        collection_dir = self._collection_dir(collection_name)
        manifest = json.loads((collection_dir / "manifest.json").read_text(encoding="utf-8"))
        index = faiss.read_index(str(collection_dir / "index.faiss"))
        vectors = np.load(str(collection_dir / "vectors.npy"), allow_pickle=False)
        visualization_points = np.load(str(collection_dir / "visualization.npy"), allow_pickle=False)
        cell_ids = json.loads((collection_dir / "cell_ids.json").read_text(encoding="utf-8"))
        metadata = json.loads((collection_dir / "metadata.json").read_text(encoding="utf-8"))
        vector_transform = _load_vector_transform(collection_dir)
        loaded = _StoredCollection(
            name=collection_name,
            index=index,
            vectors=np.asarray(vectors, dtype=np.float32),
            cell_ids=[str(item) for item in cell_ids],
            metadata=list(metadata or []),
            visualization_points=_ensure_two_dim_points(visualization_points),
            cell_id_to_offset={str(cell_id): offset for offset, cell_id in enumerate(cell_ids)},
            manifest=dict(manifest),
            vector_transform=vector_transform,
        )
        self._collection_cache[collection_name] = loaded
        return loaded


def _vector_transform_metadata(vector_transform: dict | None) -> dict | None:
    if not vector_transform:
        return None
    return {
        key: value
        for key, value in vector_transform.items()
        if key not in {"mean", "components"}
    }


def _persist_vector_transform(collection_dir: Path, vector_transform: dict | None) -> None:
    if not vector_transform:
        return

    metadata = _vector_transform_metadata(vector_transform) or {}
    arrays = {}
    for key in ("mean", "components"):
        if key in vector_transform and vector_transform[key] is not None:
            arrays[key] = np.asarray(vector_transform[key], dtype=np.float32)

    (collection_dir / "vector_transform.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if arrays:
        np.savez_compressed(collection_dir / "vector_transform.npz", **arrays)


def _load_vector_transform(collection_dir: Path) -> dict | None:
    metadata_path = collection_dir / "vector_transform.json"
    if not metadata_path.exists():
        return None

    vector_transform = json.loads(metadata_path.read_text(encoding="utf-8"))
    arrays_path = collection_dir / "vector_transform.npz"
    if arrays_path.exists():
        with np.load(str(arrays_path), allow_pickle=False) as arrays:
            for key in arrays.files:
                vector_transform[key] = np.asarray(arrays[key], dtype=np.float32)
    return vector_transform


def _transform_query_vector_if_needed(vector: Iterable[float], collection: _StoredCollection) -> list[float]:
    query_vector = np.asarray(list(vector), dtype=np.float32)
    if query_vector.ndim != 1:
        raise ValueError("query vector must be one-dimensional")

    index_dim = int(collection.manifest.get("vector_dim") or collection.vectors.shape[1])
    if len(query_vector) == index_dim:
        return query_vector.astype(float).tolist()

    vector_transform = collection.vector_transform
    if not vector_transform:
        raise ValueError(
            f"vector dimension must be {index_dim}. "
            "This index does not contain the raw-vector transform needed for high-dimensional CSV queries; "
            "rebuild the index with the current code, or provide an already processed query vector."
        )

    input_dim = int(vector_transform.get("input_dim") or 0)
    output_dim = int(vector_transform.get("output_dim") or index_dim)
    if len(query_vector) != input_dim:
        raise ValueError(
            f"vector dimension must be {index_dim}; raw-vector transform expects {input_dim} dimensions"
        )

    transform_type = str(vector_transform.get("type") or "").strip().lower()
    if transform_type == "slice":
        transformed = query_vector[:output_dim]
    elif transform_type in {"pca", "incremental_pca"}:
        components = np.asarray(vector_transform.get("components"), dtype=np.float32)
        mean = np.asarray(vector_transform.get("mean"), dtype=np.float32)
        transformed = (query_vector - mean) @ components.T
    elif transform_type == "truncated_svd":
        components = np.asarray(vector_transform.get("components"), dtype=np.float32)
        transformed = query_vector @ components.T
    else:
        raise ValueError(f"unsupported vector transform: {transform_type or 'unknown'}")

    if transformed.shape[0] != index_dim:
        raise ValueError(f"transformed query vector dimension must be {index_dim}")
    return np.asarray(transformed, dtype=np.float32).astype(float).tolist()


def normalize_requested_build_options(
    *,
    index_type: str | None = None,
    distance_metric: str | None = None,
    quantization_config: dict | None = None,
    hnsw_params: dict | None = None,
    search_params: dict | None = None,
) -> dict:
    normalized_index_type = _normalize_choice(index_type or DEFAULT_INDEX_TYPE, SUPPORTED_INDEX_TYPES, "index_type")
    normalized_distance_metric = _normalize_choice(
        distance_metric or DEFAULT_DISTANCE_METRIC,
        SUPPORTED_DISTANCE_METRICS,
        "distance_metric",
    )
    return {
        "index_type": normalized_index_type,
        "distance_metric": normalized_distance_metric,
        "effective_metric": FAISS_DISTANCE_NAMES[normalized_distance_metric],
        "quantization_config": _normalize_request_quantization_config(
            normalized_index_type,
            quantization_config,
        ),
        "hnsw_params": _resolve_hnsw_params(hnsw_params) if normalized_index_type == "hnsw" else {},
        "search_params": _resolve_search_params(search_params, index_type=normalized_index_type),
    }


def build_collection_name(user_id: int, index_name: str) -> str:
    normalized_name = _normalize_collection_name(index_name)
    prefix = f"user_{user_id}_"
    max_len = 64
    available = max_len - len(prefix)
    if available < 3:
        raise ValueError("user-specific collection prefix is too long")
    if len(normalized_name) > available:
        normalized_name = normalized_name[:available]
    return f"{prefix}{normalized_name}"


def resolve_index_build_config(
    index_type: str | None = None,
    distance_metric: str | None = None,
    quantization_config: dict | None = None,
    *,
    vector_dim: int,
    cell_count: int,
) -> dict:
    normalized_index_type = _normalize_choice(index_type or DEFAULT_INDEX_TYPE, SUPPORTED_INDEX_TYPES, "index_type")
    normalized_distance_metric = _normalize_choice(
        distance_metric or DEFAULT_DISTANCE_METRIC,
        SUPPORTED_DISTANCE_METRICS,
        "distance_metric",
    )
    normalized_quantization = _normalize_request_quantization_config(
        normalized_index_type,
        quantization_config,
    )
    if normalized_index_type == "ivf":
        resolved_quantization = _resolve_ivf_config(normalized_quantization, cell_count)
    elif normalized_index_type == "pq":
        resolved_quantization = _resolve_pq_config(normalized_quantization, vector_dim)
    else:
        resolved_quantization = {}
    return {
        "index_type": normalized_index_type,
        "distance_metric": normalized_distance_metric,
        "effective_metric": FAISS_DISTANCE_NAMES[normalized_distance_metric],
        "quantization_config": resolved_quantization,
    }


def _normalize_collection_name(raw_name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", (raw_name or "").strip())
    normalized = normalized.strip("_").lower()
    if len(normalized) < 3 or len(normalized) > 64:
        raise ValueError("collection name length must be between 3 and 64 after normalization")
    return normalized


def _normalize_choice(value: str, allowed: set[str], field_name: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"{field_name} must be one of: {allowed_text}")
    return normalized


def _resolve_hnsw_params(hnsw_params: dict | None) -> dict:
    resolved = dict(DEFAULT_HNSW_PARAMS)
    if hnsw_params:
        for key in ("m", "ef_construct"):
            if hnsw_params.get(key) is not None:
                resolved[key] = int(hnsw_params[key])
    if resolved["m"] < 4 or resolved["m"] > 128:
        raise ValueError("hnsw_params.m must be between 4 and 128")
    if resolved["ef_construct"] < 16 or resolved["ef_construct"] > 4096:
        raise ValueError("hnsw_params.ef_construct must be between 16 and 4096")
    return resolved


def _resolve_search_params(
    search_params: dict | None,
    exact: bool | None = None,
    index_type: str = DEFAULT_INDEX_TYPE,
) -> dict:
    resolved = dict(DEFAULT_SEARCH_PARAMS)
    if search_params:
        if search_params.get("hnsw_ef") is not None:
            resolved["hnsw_ef"] = int(search_params["hnsw_ef"])
        if search_params.get("nprobe") is not None:
            resolved["nprobe"] = int(search_params["nprobe"])
        if search_params.get("exact") is not None:
            resolved["exact"] = bool(search_params["exact"])
        if search_params.get("rerank_k") is not None:
            resolved["rerank_k"] = int(search_params["rerank_k"])
        if search_params.get("filter_candidate_multiplier") is not None:
            resolved["filter_candidate_multiplier"] = int(search_params["filter_candidate_multiplier"])
    if exact is not None:
        resolved["exact"] = bool(exact)
    if resolved["hnsw_ef"] < 16 or resolved["hnsw_ef"] > 4096:
        raise ValueError("search_params.hnsw_ef must be between 16 and 4096")
    if resolved["nprobe"] < 1 or resolved["nprobe"] > 4096:
        raise ValueError("search_params.nprobe must be between 1 and 4096")
    if resolved["rerank_k"] < 1 or resolved["rerank_k"] > 10000:
        raise ValueError("search_params.rerank_k must be between 1 and 10000")
    if resolved["filter_candidate_multiplier"] < 1 or resolved["filter_candidate_multiplier"] > 1000:
        raise ValueError("search_params.filter_candidate_multiplier must be between 1 and 1000")
    if index_type not in SUPPORTED_INDEX_TYPES:
        raise ValueError(f"unsupported index_type: {index_type}")
    return resolved


def _normalize_request_quantization_config(index_type: str, quantization_config: dict | None) -> dict:
    raw_config = dict(quantization_config or {})
    if index_type == "hnsw":
        return {}
    if index_type == "ivf":
        if raw_config.get("nlist") is None:
            return {}
        nlist = int(raw_config["nlist"])
        if nlist < 1 or nlist > 65536:
            raise ValueError("quantization_config.nlist must be between 1 and 65536")
        return {"nlist": nlist}

    raw_pq = dict(DEFAULT_PQ_CONFIG)
    raw_pq.update({key: value for key, value in raw_config.items() if value is not None})
    compression = str(raw_pq.get("compression") or DEFAULT_PQ_CONFIG["compression"]).strip().lower()
    if compression not in PQ_COMPRESSION_FACTORS:
        allowed = ", ".join(sorted(PQ_COMPRESSION_FACTORS))
        raise ValueError(f"quantization_config.compression must be one of: {allowed}")
    nbits = int(raw_pq.get("nbits") or DEFAULT_PQ_CONFIG["nbits"])
    if nbits < 4 or nbits > 16:
        raise ValueError("quantization_config.nbits must be between 4 and 16")

    normalized = {
        "compression": compression,
        "nbits": nbits,
    }
    if raw_pq.get("subquantizers") is not None:
        subquantizers = int(raw_pq["subquantizers"])
        if subquantizers < 1 or subquantizers > 1024:
            raise ValueError("quantization_config.subquantizers must be between 1 and 1024")
        normalized["subquantizers"] = subquantizers
    return normalized


def _resolve_ivf_config(config: dict, cell_count: int) -> dict:
    nlist = int(config.get("nlist") or _default_ivf_nlist(cell_count))
    nlist = max(1, min(nlist, max(cell_count, 1)))
    return {"nlist": nlist}


def _resolve_pq_config(config: dict, vector_dim: int) -> dict:
    compression = str(config.get("compression") or DEFAULT_PQ_CONFIG["compression"]).strip().lower()
    nbits = int(config.get("nbits") or DEFAULT_PQ_CONFIG["nbits"])
    requested_subquantizers = config.get("subquantizers")
    if requested_subquantizers is not None:
        subquantizers = int(requested_subquantizers)
        if vector_dim % subquantizers != 0:
            raise ValueError("quantization_config.subquantizers must divide vector_dim exactly")
    else:
        subquantizers = _choose_pq_subquantizers(
            vector_dim=vector_dim,
            compression=compression,
            nbits=nbits,
        )
    return {
        "compression": compression,
        "nbits": nbits,
        "subquantizers": subquantizers,
    }


def _default_ivf_nlist(cell_count: int) -> int:
    if cell_count <= 1:
        return 1
    suggested = int(round(math.sqrt(cell_count)))
    return max(4, min(suggested, cell_count))


def _choose_pq_subquantizers(vector_dim: int, compression: str, nbits: int) -> int:
    target_ratio = PQ_COMPRESSION_FACTORS[compression]
    target_subquantizers = max(1, int(round((32 * vector_dim) / (target_ratio * nbits))))
    divisors = [value for value in range(1, min(vector_dim, 256) + 1) if vector_dim % value == 0]
    if not divisors:
        return 1
    return min(divisors, key=lambda item: (abs(item - target_subquantizers), item))


def _prepare_vectors_for_metric(vectors: np.ndarray, distance_metric: str) -> np.ndarray:
    raw_vectors = np.asarray(vectors, dtype=np.float32)
    if distance_metric == "pearson":
        return _pearson_normalize_vectors(raw_vectors)
    if distance_metric == "cosine":
        return _l2_normalize_vectors(raw_vectors)
    return raw_vectors


def _prepare_query_vector_for_metric(
    *,
    vector: Iterable[float],
    vector_dim: int,
    distance_metric: str,
    vector_is_prepared: bool = False,
) -> np.ndarray:
    query_vector = np.asarray(list(vector), dtype=np.float32)
    if query_vector.ndim != 1:
        raise ValueError("query vector must be one-dimensional")
    if len(query_vector) != int(vector_dim):
        raise ValueError(f"vector dimension must be {vector_dim}")
    if vector_is_prepared:
        return query_vector
    if distance_metric == "pearson":
        return _pearson_normalize_vectors(query_vector.reshape(1, -1))[0]
    if distance_metric == "cosine":
        return _l2_normalize_vectors(query_vector.reshape(1, -1))[0]
    return query_vector


def _pearson_normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    normalized = np.asarray(vectors, dtype=np.float32).copy()
    means = normalized.mean(axis=1, keepdims=True)
    normalized -= means
    return _l2_normalize_vectors(normalized)


def _l2_normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    normalized = np.asarray(vectors, dtype=np.float32).copy()
    norms = np.linalg.norm(normalized, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized /= norms
    return normalized


def _build_faiss_index(
    *,
    vectors: np.ndarray,
    vector_dim: int,
    index_type: str,
    distance_metric: str,
    hnsw_params: dict,
    quantization_config: dict,
):
    faiss = _require_faiss()
    metric_type = _faiss_metric_type(distance_metric)
    if index_type == "hnsw":
        index = faiss.IndexHNSWFlat(vector_dim, int(hnsw_params["m"]), metric_type)
        index.hnsw.efConstruction = int(hnsw_params["ef_construct"])
        return index

    if index_type == "ivf":
        quantizer = _build_flat_quantizer(faiss, vector_dim, metric_type)
        index = faiss.IndexIVFFlat(
            quantizer,
            vector_dim,
            int(quantization_config["nlist"]),
            metric_type,
        )
        index.train(np.ascontiguousarray(vectors, dtype=np.float32))
        return index

    factory_spec = f"PQ{int(quantization_config['subquantizers'])}x{int(quantization_config['nbits'])}"
    index = faiss.index_factory(vector_dim, factory_spec, metric_type)
    index.train(np.ascontiguousarray(vectors, dtype=np.float32))
    return index


def _build_flat_quantizer(faiss, vector_dim: int, metric_type: int):
    if metric_type == faiss.METRIC_L2:
        return faiss.IndexFlatL2(vector_dim)
    return faiss.IndexFlatIP(vector_dim)


def _faiss_metric_type(distance_metric: str) -> int:
    faiss = _require_faiss()
    if distance_metric == "l2":
        return faiss.METRIC_L2
    return faiss.METRIC_INNER_PRODUCT


def _ann_search(
    *,
    collection: _StoredCollection,
    query_vector: np.ndarray,
    top_k: int,
    search_params: dict,
    distance_metric: str,
) -> list[tuple[int, float, bool]]:
    index = collection.index
    manifest = collection.manifest
    index_type = manifest.get("index_type") or DEFAULT_INDEX_TYPE
    if index_type == "hnsw" and hasattr(index, "hnsw"):
        index.hnsw.efSearch = int(search_params["hnsw_ef"])
    if index_type == "ivf" and hasattr(index, "nprobe"):
        index.nprobe = int(search_params["nprobe"])

    distances, labels = index.search(
        np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32),
        top_k,
    )
    hits: list[tuple[int, float, bool]] = []
    squared_l2 = distance_metric == "l2"
    for raw_value, label in zip(distances[0].tolist(), labels[0].tolist()):
        if label is None or int(label) < 0:
            continue
        hits.append((int(label), float(raw_value), squared_l2))
    return hits


def _ann_filtered_rerank_search(
    *,
    collection: _StoredCollection,
    query_vector: np.ndarray,
    top_k: int,
    search_params: dict,
    distance_metric: str,
    candidate_offsets: np.ndarray,
) -> list[tuple[int, float, bool]]:
    if len(candidate_offsets) == 0:
        return []

    ann_top_k = max(
        top_k,
        int(search_params["rerank_k"]),
        top_k * int(search_params["filter_candidate_multiplier"]),
    )
    ntotal = int(getattr(collection.index, "ntotal", len(collection.vectors)) or len(collection.vectors))
    ann_top_k = min(max(1, ann_top_k), ntotal)
    ann_hits = _ann_search(
        collection=collection,
        query_vector=query_vector,
        top_k=ann_top_k,
        search_params=search_params,
        distance_metric=distance_metric,
    )
    allowed_offsets = set(int(offset) for offset in candidate_offsets.tolist())
    filtered_offsets = _unique_offsets(offset for offset, _, _ in ann_hits if offset in allowed_offsets)
    if len(filtered_offsets) >= top_k:
        return _exact_search(
            vectors=collection.vectors,
            query_vector=query_vector,
            candidate_offsets=np.asarray(filtered_offsets, dtype=np.int64),
            top_k=top_k,
            distance_metric=distance_metric,
        )

    return _exact_search(
        vectors=collection.vectors,
        query_vector=query_vector,
        candidate_offsets=candidate_offsets,
        top_k=top_k,
        distance_metric=distance_metric,
    )


def _rerank_ann_hits(
    *,
    vectors: np.ndarray,
    query_vector: np.ndarray,
    ann_hits: list[tuple[int, float, bool]],
    top_k: int,
    distance_metric: str,
) -> list[tuple[int, float, bool]]:
    candidate_offsets = _unique_offsets(offset for offset, _, _ in ann_hits)
    if not candidate_offsets:
        return []
    return _exact_search(
        vectors=vectors,
        query_vector=query_vector,
        candidate_offsets=np.asarray(candidate_offsets, dtype=np.int64),
        top_k=top_k,
        distance_metric=distance_metric,
    )


def _unique_offsets(offsets: Iterable[int]) -> list[int]:
    seen: set[int] = set()
    unique: list[int] = []
    for offset in offsets:
        normalized = int(offset)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return unique


def _exact_search(
    *,
    vectors: np.ndarray,
    query_vector: np.ndarray,
    candidate_offsets: np.ndarray,
    top_k: int,
    distance_metric: str,
) -> list[tuple[int, float, bool]]:
    if len(candidate_offsets) == 0:
        return []
    candidates = vectors[candidate_offsets]
    if distance_metric == "l2":
        distances = np.sum((candidates - query_vector) ** 2, axis=1)
        order = np.argsort(distances)[:top_k]
        return [
            (int(candidate_offsets[position]), float(distances[position]), True)
            for position in order.tolist()
        ]
    scores = candidates @ query_vector
    order = np.argsort(-scores)[:top_k]
    return [
        (int(candidate_offsets[position]), float(scores[position]), False)
        for position in order.tolist()
    ]


def _build_search_result(
    *,
    collection: _StoredCollection,
    offset: int,
    raw_value: float,
    distance_metric: str,
    squared_l2: bool,
) -> dict:
    result = {
        "cell_id": collection.cell_ids[offset],
        "viz": {
            "x": float(collection.visualization_points[offset][0]),
            "y": float(collection.visualization_points[offset][1]),
        },
        "metadata": collection.metadata[offset] or {},
        "distance_metric": distance_metric,
    }
    result.update(_score_payload_from_hit(raw_value, distance_metric, squared_l2=squared_l2))
    return result


def _score_payload_from_hit(raw_score: float, distance_metric: str, *, squared_l2: bool = False) -> dict:
    if distance_metric == "l2":
        value = max(float(raw_score), 0.0)
        if squared_l2:
            value = math.sqrt(value)
        distance = round(value, 6)
        return {
            "distance": distance,
            "score": None,
            "score_semantics": "euclidean_distance",
        }

    score = round(float(raw_score), 6)
    if distance_metric == "ip":
        return {
            "distance": None,
            "score": score,
            "score_semantics": "inner_product",
        }
    if distance_metric == "pearson":
        return {
            "distance": round(1 - score, 6),
            "score": score,
            "score_semantics": "pearson_correlation",
        }
    return {
        "distance": round(1 - score, 6),
        "score": score,
        "score_semantics": "cosine_similarity",
    }


def _matching_offsets(metadata_rows: list[dict], filters: dict[str, str] | None) -> np.ndarray:
    if not filters:
        return np.arange(len(metadata_rows), dtype=np.int64)

    normalized_filters = {
        str(key): str(value).strip()
        for key, value in filters.items()
        if value is not None and str(value).strip()
    }
    if not normalized_filters:
        return np.arange(len(metadata_rows), dtype=np.int64)

    matched: list[int] = []
    for offset, metadata in enumerate(metadata_rows):
        payload = metadata or {}
        if all(str(payload.get(key, "")).strip() == value for key, value in normalized_filters.items()):
            matched.append(offset)
    return np.asarray(matched, dtype=np.int64)


def _ensure_two_dim_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float32)
    if array.ndim == 2 and array.shape[1] >= 2:
        return array[:, :2]
    if array.ndim == 2 and array.shape[1] == 1:
        axis = array[:, 0]
        return np.column_stack([axis, np.zeros_like(axis)]).astype(np.float32)
    if array.ndim == 1:
        return np.column_stack([array, np.zeros_like(array)]).astype(np.float32)
    return np.zeros((len(array), 2), dtype=np.float32)


def _require_faiss():
    try:
        import faiss
    except Exception as exc:
        raise ImportError(
            "FAISS backend is selected but the faiss package is unavailable. "
            "Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return faiss
