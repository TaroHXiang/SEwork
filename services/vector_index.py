from __future__ import annotations

from typing import Iterable

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from config import QDRANT_COLLECTION, QDRANT_URL
from services.data_loader import CellVectorDataset


class CellVectorIndex:
    def __init__(self, collection_name: str = QDRANT_COLLECTION):
        self.collection_name = collection_name
        self.client = _create_client()
        self.cell_id_to_vector: dict[str, list[float]] = {}
        self.dataset_summary: dict | None = None
        self.vector_dim: int | None = None

    @property
    def is_ready(self) -> bool:
        return self.vector_dim is not None

    def build(self, dataset: CellVectorDataset) -> None:
        vector_dim = dataset.vector_dim
        cell_id_to_vector = {
            cell_id: vector.astype(float).tolist()
            for cell_id, vector in zip(dataset.cell_ids, dataset.vectors)
        }

        self._reset_collection(vector_dim)

        batch_size = 1000
        for start in range(0, dataset.cell_count, batch_size):
            points = [
                PointStruct(
                    id=index,
                    vector=vector.astype(float).tolist(),
                    payload={
                        "cell_id": cell_id,
                        "metadata": metadata,
                    },
                )
                for index, (cell_id, vector, metadata) in enumerate(
                    zip(
                        dataset.cell_ids[start : start + batch_size],
                        dataset.vectors[start : start + batch_size],
                        dataset.metadata[start : start + batch_size],
                    ),
                    start=start,
                )
            ]
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

        self.vector_dim = vector_dim
        self.cell_id_to_vector = cell_id_to_vector
        self.dataset_summary = dataset.summary()

    def search_by_cell_id(
        self, cell_id: str, top_k: int = 5, filters: dict[str, str] | None = None
    ) -> list[dict]:
        self._ensure_ready()
        vector = self.cell_id_to_vector.get(cell_id)
        if vector is None:
            raise ValueError(f"unknown cell_id: {cell_id}")
        return self.search_by_vector(vector, top_k=top_k, filters=filters)

    def search_by_vector(
        self, vector: Iterable[float], top_k: int = 5, filters: dict[str, str] | None = None
    ) -> list[dict]:
        self._ensure_ready()
        if top_k < 1 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        query_vector = np.asarray(list(vector), dtype=np.float32)
        if query_vector.ndim != 1:
            raise ValueError("query vector must be one-dimensional")
        if len(query_vector) != self.vector_dim:
            raise ValueError(f"vector dimension must be {self.vector_dim}")

        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.astype(float).tolist(),
            query_filter=_build_filter(filters),
            limit=top_k,
            with_payload=True,
        )
        return [
            {
                "cell_id": hit.payload.get("cell_id"),
                "distance": round(1 - float(hit.score), 6),
                "score": round(float(hit.score), 6),
                "metadata": hit.payload.get("metadata", {}),
            }
            for hit in hits
        ]

    def _ensure_ready(self) -> None:
        if not self.is_ready:
            raise RuntimeError("index is not built yet")

    def _reset_collection(self, vector_dim: int) -> None:
        collections = self.client.get_collections().collections
        collection_names = {collection.name for collection in collections}
        if self.collection_name in collection_names:
            self.client.delete_collection(collection_name=self.collection_name)

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )


def _create_client() -> QdrantClient:
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL)
    return QdrantClient(location=":memory:")


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
