from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

from config import BASE_DIR, FAISS_SERVICE_URL, VECTOR_INDEX_COLLECTION
from services.data_loader import CellVectorDataset
from services.faiss_engine import (
    DEFAULT_DISTANCE_METRIC,
    DEFAULT_INDEX_TYPE,
    SearchResult,
    build_collection_name,
    normalize_requested_build_options,
)


DEFAULT_HTTP_TIMEOUT_SECONDS = 30
DEFAULT_BUILD_TIMEOUT_SECONDS = 1800


class CellVectorIndex:
    def __init__(self, collection_name: str = VECTOR_INDEX_COLLECTION):
        self.default_collection_name = collection_name
        self.base_url = str(FAISS_SERVICE_URL or "").rstrip("/")
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
        index_type: str = DEFAULT_INDEX_TYPE,
        distance_metric: str = DEFAULT_DISTANCE_METRIC,
        quantization_config: dict | None = None,
        hnsw_params: dict | None = None,
        search_params: dict | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict:
        requested_options = normalize_requested_build_options(
            index_type=index_type,
            distance_metric=distance_metric,
            quantization_config=quantization_config,
            hnsw_params=hnsw_params,
            search_params=search_params,
        )
        service_data_path = _resolve_service_data_path(dataset.source_path)

        if progress_callback is not None:
            progress_callback(0, dataset.cell_count)

        payload = {
            "collection_name": collection_name,
            "data_path": service_data_path,
            "index_type": requested_options["index_type"],
            "distance_metric": requested_options["distance_metric"],
            "quantization_config": requested_options["quantization_config"],
            "hnsw_params": requested_options["hnsw_params"],
            "search_params": requested_options["search_params"],
        }
        response = self._request_json(
            method="POST",
            path="/collections/build",
            payload=payload,
            timeout=DEFAULT_BUILD_TIMEOUT_SECONDS,
        )

        if progress_callback is not None:
            progress_callback(dataset.cell_count, dataset.cell_count)

        dataset_summary = response.get("dataset_summary") or {}
        self.set_active_collection(
            collection_name=response["collection"],
            vector_dim=int(dataset_summary.get("vector_dim") or dataset.vector_dim),
            dataset_summary=dataset_summary,
        )
        return {
            "collection": response["collection"],
            "index_type": response["index_type"],
            "distance_metric": response["distance_metric"],
            "effective_metric": response["effective_metric"],
            "quantization_config": response.get("quantization_config") or {},
            "resolved_quantization_config": response.get("resolved_quantization_config") or {},
            "hnsw_params": response.get("hnsw_params") or {},
            "search_params": response.get("search_params") or {},
        }

    def get_visualization_points(
        self,
        collection_name: str,
        limit: int = 10000,
        filters: dict[str, str] | None = None,
    ) -> dict:
        return self._request_json(
            method="POST",
            path=f"/collections/{quote(collection_name)}/visualization",
            payload={
                "limit": limit,
                "filters": filters or {},
            },
        )

    def get_metadata_options(
        self,
        collection_name: str,
        fields: list[str],
        max_values_per_field: int = 200,
        scan_limit: int = 300000,
    ) -> dict:
        return self._request_json(
            method="POST",
            path=f"/collections/{quote(collection_name)}/metadata-options",
            payload={
                "fields": fields,
                "max_values_per_field": max_values_per_field,
                "scan_limit": scan_limit,
            },
        )

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
        response = self._request_json(
            method="POST",
            path=f"/collections/{quote(collection_name)}/search/by-id",
            payload={
                "vector_dim": vector_dim,
                "cell_id": cell_id,
                "top_k": top_k,
                "filters": filters or {},
                "search_params": search_params or {},
                "distance_metric": distance_metric,
                "exact": exact,
            },
        )
        return response["results"]

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
        return self.search_by_vector_with_timing(
            collection_name=collection_name,
            vector_dim=vector_dim,
            vector=vector,
            top_k=top_k,
            filters=filters,
            search_params=search_params,
            distance_metric=distance_metric,
            vector_is_prepared=vector_is_prepared,
            exact=exact,
        ).results

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
        response = self._request_json(
            method="POST",
            path=f"/collections/{quote(collection_name)}/search/by-vector",
            payload={
                "vector_dim": vector_dim,
                "vector": list(vector),
                "top_k": top_k,
                "filters": filters or {},
                "search_params": search_params or {},
                "distance_metric": distance_metric,
                "vector_is_prepared": vector_is_prepared,
                "exact": exact,
            },
        )
        return SearchResult(
            results=response["results"],
            query_time_ms=float(response["query_time_ms"]),
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
        return self._request_json(
            method="POST",
            path=f"/collections/{quote(collection_name)}/evaluate/by-id",
            payload={
                "vector_dim": vector_dim,
                "cell_id": cell_id,
                "top_k": top_k,
                "filters": filters or {},
                "search_params": search_params or {},
                "distance_metric": distance_metric,
            },
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
        return self._request_json(
            method="POST",
            path=f"/collections/{quote(collection_name)}/evaluate/by-vector",
            payload={
                "vector_dim": vector_dim,
                "vector": list(vector),
                "top_k": top_k,
                "filters": filters or {},
                "search_params": search_params or {},
                "distance_metric": distance_metric,
                "vector_is_prepared": vector_is_prepared,
            },
        )

    def collection_exists(self, collection_name: str) -> bool:
        response = self._request_json(
            method="GET",
            path=f"/collections/{quote(collection_name)}/exists",
        )
        return bool(response.get("exists"))

    def delete_collection(self, collection_name: str) -> bool:
        response = self._request_json(
            method="DELETE",
            path=f"/collections/{quote(collection_name)}",
        )
        deleted = bool(response.get("deleted"))
        if deleted and self.collection_name == collection_name:
            self.clear_active_collection()
        return deleted

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

    def clear_active_collection(self) -> None:
        self.collection_name = None
        self.vector_dim = None
        self.dataset_summary = None

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        payload: dict | None = None,
        timeout: int = DEFAULT_HTTP_TIMEOUT_SECONDS,
    ) -> dict:
        if not self.base_url:
            raise RuntimeError("FAISS_SERVICE_URL is not configured")

        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(
            url=urljoin(f"{self.base_url}/", path.lstrip("/")),
            data=body,
            headers=headers,
            method=method.upper(),
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                content = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            try:
                payload = json.loads(detail) if detail else {}
            except Exception:
                payload = {}
            message = payload.get("error") or detail or f"FAISS service request failed with {exc.code}"
            raise RuntimeError(message) from exc
        except URLError as exc:
            raise RuntimeError(
                f"Cannot reach FAISS service at {self.base_url}. "
                "Start it with `docker compose up -d faiss`."
            ) from exc

        if not content:
            return {}
        try:
            return json.loads(content)
        except Exception as exc:
            raise RuntimeError("FAISS service returned invalid JSON") from exc


def _resolve_service_data_path(source_path: str) -> str:
    candidate = Path(source_path)
    if not candidate.is_absolute():
        return str(candidate).replace("\\", "/")
    try:
        relative = candidate.resolve().relative_to(BASE_DIR.resolve())
    except Exception as exc:
        raise ValueError(
            "Dockerized FAISS service can only access datasets under the project workspace. "
            "Use a path inside this repo or add an explicit bind mount for that dataset."
        ) from exc
    return str(relative).replace("\\", "/")
