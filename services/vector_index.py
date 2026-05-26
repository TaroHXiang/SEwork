from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterable

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    HnswConfigDiff,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    SearchParams,
    VectorParams,
)

from config import QDRANT_COLLECTION, QDRANT_PATH, QDRANT_URL
from services.data_loader import CellVectorDataset


DEFAULT_HNSW_PARAMS = {
    "m": 16,
    "ef_construct": 128,
}
DEFAULT_SEARCH_PARAMS = {
    "hnsw_ef": 128,
    "exact": False,
}


@dataclass
class SearchResult:
    results: list[dict]
    query_time_ms: float


class CellVectorIndex:
    def __init__(self, collection_name: str = QDRANT_COLLECTION):
        self.default_collection_name = collection_name
        self.client = _create_client()
        self.collection_name: str | None = None
        self.dataset_summary: dict | None = None
        self.vector_dim: int | None = None

    @property
    def is_ready(self) -> bool:
        return self.vector_dim is not None and self.collection_name is not None

    def build(
        self,
        dataset: CellVectorDataset,
        collection_name: str,
        hnsw_params: dict | None = None,
        search_params: dict | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict:
        collection_name = _normalize_collection_name(collection_name)
        resolved_hnsw = _resolve_hnsw_params(hnsw_params)
        resolved_search = _resolve_search_params(search_params)
        vector_dim = dataset.vector_dim

        self._reset_collection(collection_name, vector_dim, resolved_hnsw)
        if progress_callback is not None:
            progress_callback(0, dataset.cell_count)

        batch_size = 1000
        for start in range(0, dataset.cell_count, batch_size):
            points = [
                PointStruct(
                    id=index,
                    vector=vector.astype(float).tolist(),
                    payload={
                        "cell_id": cell_id,
                        "viz": {
                            "x": float(viz_point[0]),
                            "y": float(viz_point[1]),
                        },
                        "metadata": metadata,
                    },
                )
                for index, (cell_id, vector, metadata, viz_point) in enumerate(
                    zip(
                        dataset.cell_ids[start : start + batch_size],
                        dataset.vectors[start : start + batch_size],
                        dataset.metadata[start : start + batch_size],
                        dataset.visualization_points[start : start + batch_size],
                    ),
                    start=start,
                )
            ]
            self.client.upsert(
                collection_name=collection_name,
                points=points,
            )
            if progress_callback is not None:
                processed = min(start + len(points), dataset.cell_count)
                progress_callback(processed, dataset.cell_count)

        self._create_payload_indexes(collection_name, dataset.metadata_fields)
        self.set_active_collection(
            collection_name=collection_name,
            vector_dim=vector_dim,
            dataset_summary=dataset.summary(),
        )
        return {
            "collection": collection_name,
            "hnsw_params": resolved_hnsw,
            "search_params": resolved_search,
        }

    def get_visualization_points(
        self,
        collection_name: str,
        limit: int = 10000,
        filters: dict[str, str] | None = None,
    ) -> dict:
        if limit < 1 or limit > 100000:
            raise ValueError("limit must be between 1 and 100000")

        query_filter = _build_filter(filters)
        count_result = self.client.count(
            collection_name=collection_name,
            count_filter=query_filter,
            exact=False,
        )
        total_points = int(count_result.count)

        points = []
        offset = None
        batch_size = 1000
        while len(points) < limit:
            page_size = min(batch_size, limit - len(points))
            records, next_offset = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=query_filter,
                limit=page_size,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )
            if not records:
                break

            for record in records:
                payload = record.payload or {}
                viz = payload.get("viz") or {}
                metadata = payload.get("metadata") or {}
                if "x" in viz and "y" in viz:
                    x_axis = float(viz.get("x", 0.0))
                    y_axis = float(viz.get("y", 0.0))
                else:
                    raw_vector = record.vector
                    if isinstance(raw_vector, dict):
                        raw_vector = next(iter(raw_vector.values()), None)
                    if isinstance(raw_vector, list) and len(raw_vector) >= 2:
                        x_axis = float(raw_vector[0])
                        y_axis = float(raw_vector[1])
                    elif isinstance(raw_vector, list) and len(raw_vector) == 1:
                        x_axis = float(raw_vector[0])
                        y_axis = 0.0
                    else:
                        x_axis = 0.0
                        y_axis = 0.0
                points.append(
                    {
                        "cell_id": payload.get("cell_id"),
                        "x": x_axis,
                        "y": y_axis,
                        "metadata": metadata,
                    }
                )
                if len(points) >= limit:
                    break

            if next_offset is None:
                break
            offset = next_offset

        return {
            "total_points": total_points,
            "returned_points": len(points),
            "points": points,
        }

    def search_by_cell_id(
        self,
        collection_name: str,
        vector_dim: int,
        cell_id: str,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
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
        exact: bool | None = None,
    ) -> list[dict]:
        result = self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
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
        exact: bool | None = None,
    ) -> SearchResult:
        if top_k < 1 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        query_vector = np.asarray(list(vector), dtype=np.float32)
        if query_vector.ndim != 1:
            raise ValueError("query vector must be one-dimensional")
        if len(query_vector) != int(vector_dim):
            raise ValueError(f"vector dimension must be {vector_dim}")

        resolved_search = _resolve_search_params(search_params, exact=exact)
        start_time = perf_counter()
        hits = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector.astype(float).tolist(),
            query_filter=_build_filter(filters),
            search_params=SearchParams(
                hnsw_ef=int(resolved_search["hnsw_ef"]),
                exact=bool(resolved_search["exact"]),
            ),
            limit=top_k,
            with_payload=True,
        )
        elapsed_ms = round((perf_counter() - start_time) * 1000, 2)
        return SearchResult(
            results=[
                {
                    "cell_id": hit.payload.get("cell_id"),
                    "distance": round(1 - float(hit.score), 6),
                    "score": round(float(hit.score), 6),
                    "metadata": hit.payload.get("metadata", {}),
                }
                for hit in hits
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
        )

    def evaluate_query_by_vector(
        self,
        collection_name: str,
        vector_dim: int,
        vector: Iterable[float],
        top_k: int = 10,
        filters: dict[str, str] | None = None,
        search_params: dict | None = None,
    ) -> dict:
        ann = self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            exact=False,
        )
        exact = self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
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
            "ann_results": ann.results,
            "exact_results": exact.results,
        }

    def collection_exists(self, collection_name: str) -> bool:
        collection_names = {
            collection.name for collection in self.client.get_collections().collections
        }
        return collection_name in collection_names

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
        points, _ = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(key="cell_id", match=MatchValue(value=cell_id)),
                ]
            ),
            limit=1,
            with_payload=False,
            with_vectors=True,
        )
        if not points:
            return None
        vector = points[0].vector
        if isinstance(vector, dict):
            vector = next(iter(vector.values()), None)
        if vector is None:
            return None
        return list(vector)

    def _reset_collection(self, collection_name: str, vector_dim: int, hnsw_params: dict) -> None:
        collections = self.client.get_collections().collections
        collection_names = {collection.name for collection in collections}
        if collection_name in collection_names:
            self.client.delete_collection(collection_name=collection_name)

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            hnsw_config=HnswConfigDiff(
                m=int(hnsw_params["m"]),
                ef_construct=int(hnsw_params["ef_construct"]),
            ),
        )

    def _create_payload_indexes(self, collection_name: str, metadata_fields: list[str]) -> None:
        # Best-effort optimization for metadata filtering; skip failures silently.
        fields = ["cell_id"] + [f"metadata.{field}" for field in metadata_fields]
        for field in fields:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )
            except Exception:
                pass


def _create_client() -> QdrantClient:
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL)
    storage_path = Path(QDRANT_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    try:
        return QdrantClient(path=str(storage_path))
    except TypeError:
        return QdrantClient(location=str(storage_path))


def _normalize_collection_name(raw_name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", (raw_name or "").strip())
    normalized = normalized.strip("_").lower()
    if len(normalized) < 3 or len(normalized) > 64:
        raise ValueError("collection name length must be between 3 and 64 after normalization")
    return normalized


def _resolve_hnsw_params(hnsw_params: dict | None) -> dict:
    resolved = dict(DEFAULT_HNSW_PARAMS)
    if hnsw_params:
        for key in ("m", "ef_construct"):
            if key in hnsw_params and hnsw_params[key] is not None:
                resolved[key] = int(hnsw_params[key])
    if resolved["m"] < 4 or resolved["m"] > 128:
        raise ValueError("hnsw_params.m must be between 4 and 128")
    if resolved["ef_construct"] < 16 or resolved["ef_construct"] > 4096:
        raise ValueError("hnsw_params.ef_construct must be between 16 and 4096")
    return resolved


def _resolve_search_params(search_params: dict | None, exact: bool | None = None) -> dict:
    resolved = dict(DEFAULT_SEARCH_PARAMS)
    if search_params:
        if search_params.get("hnsw_ef") is not None:
            resolved["hnsw_ef"] = int(search_params["hnsw_ef"])
        if search_params.get("exact") is not None:
            resolved["exact"] = bool(search_params["exact"])
    if exact is not None:
        resolved["exact"] = bool(exact)
    if resolved["hnsw_ef"] < 16 or resolved["hnsw_ef"] > 4096:
        raise ValueError("search_params.hnsw_ef must be between 16 and 4096")
    return resolved


def _build_filter(filters: dict[str, str] | None) -> Filter | None:
    if not filters:
        return None

    conditions = [
        FieldCondition(key=f"metadata.{key}", match=MatchValue(value=value))
        for key, value in filters.items()
        if value
    ]
    if not conditions:
        return None
    return Filter(must=conditions)


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
