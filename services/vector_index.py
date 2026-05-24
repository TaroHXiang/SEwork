from __future__ import annotations

from typing import Iterable

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from config import QDRANT_COLLECTION, QDRANT_PATH, QDRANT_URL
from services.data_loader import CellVectorDataset


class CellVectorIndex:
    def __init__(self, collection_name: str = QDRANT_COLLECTION):
        self.collection_name = collection_name
        self.client = _create_client()
        self.cell_id_to_vector: dict[str, list[float]] = {}
        self.vector_dim: int | None = None

    @property
    def is_ready(self) -> bool:
        return self.vector_dim is not None

    def build(self, dataset: CellVectorDataset) -> None:
        self.vector_dim = dataset.vector_dim
        self.cell_id_to_vector = {
            cell_id: vector.astype(float).tolist()
            for cell_id, vector in zip(dataset.cell_ids, dataset.vectors)
        }

        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=dataset.vector_dim, distance=Distance.COSINE),
        )

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
                zip(dataset.cell_ids, dataset.vectors, dataset.metadata)
            )
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search_by_cell_id(self, cell_id: str, top_k: int = 5) -> list[dict]:
        self._ensure_ready()
        vector = self.cell_id_to_vector.get(cell_id)
        if vector is None:
            raise ValueError(f"unknown cell_id: {cell_id}")
        return self.search_by_vector(vector, top_k=top_k)

    def search_by_vector(self, vector: Iterable[float], top_k: int = 5) -> list[dict]:
        self._ensure_ready()
        query_vector = np.asarray(list(vector), dtype=np.float32)
        if query_vector.ndim != 1:
            raise ValueError("query vector must be one-dimensional")
        if len(query_vector) != self.vector_dim:
            raise ValueError(f"vector dimension must be {self.vector_dim}")

        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.astype(float).tolist(),
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


def _create_client() -> QdrantClient:
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL)
    QDRANT_PATH.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(QDRANT_PATH))
