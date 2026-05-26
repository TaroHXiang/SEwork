from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class CellVectorDataset:
    cell_ids: list[str]
    vectors: np.ndarray
    metadata: list[dict]
    visualization_points: np.ndarray
    visualization_source: str
    metadata_fields: list[str]
    source_path: str
    source_format: str
    gene_count: int
    embedding_key: str

    @property
    def vector_dim(self) -> int:
        return int(self.vectors.shape[1])

    @property
    def cell_count(self) -> int:
        return len(self.cell_ids)

    def summary(self) -> dict:
        return {
            "source_path": self.source_path,
            "format": self.source_format,
            "cell_count": self.cell_count,
            "gene_count": self.gene_count,
            "vector_dim": self.vector_dim,
            "embedding_key": self.embedding_key,
            "visualization_source": self.visualization_source,
            "metadata_fields": self.metadata_fields,
        }


def load_cell_vectors(data_path: str | Path) -> CellVectorDataset:
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    if path.suffix.lower() == ".csv":
        return _load_csv(path)

    if path.suffix.lower() == ".h5ad":
        return _load_h5ad(path)

    raise ValueError("unsupported data format, expected .csv or .h5ad")


def inspect_cell_dataset(data_path: str | Path) -> dict:
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, nrows=5)
        vector_columns = [col for col in df.columns if col.startswith("v")]
        metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            row_count = max(sum(1 for _ in handle) - 1, 0)
        return {
            "source_path": str(path),
            "format": "csv",
            "cell_count": row_count,
            "gene_count": len(vector_columns),
            "vector_dim": len(vector_columns),
            "columns": list(df.columns),
            "metadata_columns": metadata_columns,
            "embedding_key": "csv_vector_columns",
            "visualization_source": "csv_columns_or_vector_projection",
        }

    if path.suffix.lower() == ".h5ad":
        import scanpy as sc

        adata = sc.read_h5ad(path, backed="r")
        try:
            embedding_key = "X_pca" if "X_pca" in adata.obsm else "X"
            vector_dim = int(adata.obsm["X_pca"].shape[1]) if embedding_key == "X_pca" else int(adata.n_vars)
            return {
                "source_path": str(path),
                "format": "h5ad",
                "cell_count": int(adata.n_obs),
                "gene_count": int(adata.n_vars),
                "vector_dim": vector_dim,
                "embedding_key": embedding_key,
                "metadata_columns": list(adata.obs.columns),
                "obsm_keys": list(adata.obsm.keys()),
            }
        finally:
            adata.file.close()

    raise ValueError("unsupported data format, expected .csv or .h5ad")


def load_dataset_visualization_preview(
    data_path: str | Path,
    limit: int = 10000,
    seed: int = 42,
) -> dict:
    if limit < 1 or limit > 100000:
        raise ValueError("limit must be between 1 and 100000")

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _csv_visualization_preview(path=path, limit=limit, seed=seed)
    if suffix == ".h5ad":
        return _h5ad_visualization_preview(path=path, limit=limit, seed=seed)
    raise ValueError("unsupported data format, expected .csv or .h5ad")


def _load_csv(path: Path) -> CellVectorDataset:
    df = pd.read_csv(path)
    if "cell_id" not in df.columns:
        raise ValueError("CSV must contain a cell_id column")

    vector_columns = [col for col in df.columns if col.startswith("v")]
    if not vector_columns:
        raise ValueError("CSV must contain vector columns named v1, v2, ...")

    vectors = df[vector_columns].to_numpy(dtype=np.float32)
    metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
    metadata = df[metadata_columns].to_dict(orient="records")
    visualization_points, visualization_source = _resolve_csv_visualization_points(df, vector_columns)

    return CellVectorDataset(
        cell_ids=df["cell_id"].astype(str).tolist(),
        vectors=vectors,
        metadata=metadata,
        visualization_points=visualization_points,
        visualization_source=visualization_source,
        metadata_fields=metadata_columns,
        source_path=str(path),
        source_format="csv",
        gene_count=len(vector_columns),
        embedding_key="csv_vector_columns",
    )


def _load_h5ad(path: Path) -> CellVectorDataset:
    import scanpy as sc

    adata = sc.read_h5ad(path, backed="r")
    try:
        embedding_key = "X_pca" if "X_pca" in adata.obsm else "X"
        if embedding_key == "X_pca":
            vectors = np.asarray(adata.obsm["X_pca"], dtype=np.float32)
        else:
            vectors = np.asarray(adata.X, dtype=np.float32)
        visualization_points, visualization_source = _resolve_h5ad_visualization_points(
            adata=adata,
            vectors=vectors,
        )

        metadata_columns = [
            column
            for column in ["cell_type", "disease", "AgeGroup", "sex", "tissue", "donor_id"]
            if column in adata.obs.columns
        ]
        metadata = (
            adata.obs[metadata_columns]
            .astype(str)
            .replace({"nan": None, "None": None})
            .reset_index(drop=True)
            .to_dict(orient="records")
        )
        return CellVectorDataset(
            cell_ids=[str(cell_id) for cell_id in adata.obs_names],
            vectors=vectors,
            metadata=metadata,
            visualization_points=visualization_points,
            visualization_source=visualization_source,
            metadata_fields=metadata_columns,
            source_path=str(path),
            source_format="h5ad",
            gene_count=int(adata.n_vars),
            embedding_key=embedding_key,
        )
    finally:
        adata.file.close()


def _sample_indices(total_count: int, limit: int, seed: int) -> np.ndarray:
    if total_count <= 0:
        return np.array([], dtype=np.int64)
    if total_count <= limit:
        return np.arange(total_count, dtype=np.int64)
    rng = np.random.default_rng(seed)
    sampled = rng.choice(total_count, size=limit, replace=False)
    return np.sort(sampled.astype(np.int64))


def _csv_visualization_preview(path: Path, limit: int, seed: int) -> dict:
    df = pd.read_csv(path)
    if "cell_id" not in df.columns:
        raise ValueError("CSV must contain a cell_id column")

    vector_columns = [col for col in df.columns if col.startswith("v")]
    if not vector_columns:
        raise ValueError("CSV must contain vector columns named v1, v2, ...")

    metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
    points, visualization_source = _resolve_csv_visualization_points(df, vector_columns)
    total_count = len(df)
    indices = _sample_indices(total_count=total_count, limit=limit, seed=seed)

    sampled_points = points[indices] if len(indices) else np.empty((0, 2), dtype=np.float32)
    sampled_ids = df["cell_id"].astype(str).to_numpy()[indices] if len(indices) else np.array([], dtype=str)
    sampled_metadata = (
        df[metadata_columns].astype(str).replace({"nan": None, "None": None}).to_dict(orient="records")
        if metadata_columns
        else [{} for _ in range(total_count)]
    )
    if len(indices):
        sampled_metadata = [sampled_metadata[int(idx)] for idx in indices]
    else:
        sampled_metadata = []

    result_points = [
        {
            "cell_id": str(cell_id),
            "x": float(coord[0]),
            "y": float(coord[1]),
            "metadata": metadata,
        }
        for cell_id, coord, metadata in zip(sampled_ids, sampled_points, sampled_metadata)
    ]

    return {
        "source_path": str(path),
        "format": "csv",
        "total_points": int(total_count),
        "returned_points": len(result_points),
        "sampled": bool(total_count > limit),
        "vector_dim": len(vector_columns),
        "embedding_key": "csv_vector_columns",
        "visualization_source": visualization_source,
        "metadata_columns": metadata_columns,
        "points": result_points,
    }


def _h5ad_visualization_preview(path: Path, limit: int, seed: int) -> dict:
    import scanpy as sc

    adata = sc.read_h5ad(path, backed="r")
    try:
        total_count = int(adata.n_obs)
        indices = _sample_indices(total_count=total_count, limit=limit, seed=seed)
        metadata_columns = [
            column
            for column in ["cell_type", "disease", "AgeGroup", "sex", "tissue", "donor_id"]
            if column in adata.obs.columns
        ]
        if not metadata_columns:
            metadata_columns = list(adata.obs.columns[:4])

        points, visualization_source = _resolve_h5ad_preview_points(adata=adata, indices=indices)
        sampled_ids = [str(cell_id) for cell_id in adata.obs_names[indices]]
        sampled_metadata = (
            adata.obs.iloc[indices][metadata_columns]
            .astype(str)
            .replace({"nan": None, "None": None})
            .to_dict(orient="records")
            if metadata_columns
            else [{} for _ in sampled_ids]
        )

        result_points = [
            {
                "cell_id": cell_id,
                "x": float(coord[0]),
                "y": float(coord[1]),
                "metadata": metadata,
            }
            for cell_id, coord, metadata in zip(sampled_ids, points, sampled_metadata)
        ]

        return {
            "source_path": str(path),
            "format": "h5ad",
            "total_points": total_count,
            "returned_points": len(result_points),
            "sampled": bool(total_count > limit),
            "cell_count": total_count,
            "gene_count": int(adata.n_vars),
            "vector_dim": int(points.shape[1]) if points.ndim == 2 and points.shape[1] > 0 else 0,
            "embedding_key": "X_pca" if "X_pca" in adata.obsm else "X",
            "visualization_source": visualization_source,
            "metadata_columns": metadata_columns,
            "points": result_points,
        }
    finally:
        adata.file.close()


def _resolve_h5ad_preview_points(adata, indices: np.ndarray) -> tuple[np.ndarray, str]:
    if "X_umap" in adata.obsm:
        try:
            coords = np.asarray(adata.obsm["X_umap"][indices, :2], dtype=np.float32)
        except Exception:
            coords = np.asarray(adata.obsm["X_umap"], dtype=np.float32)[indices, :2]
        if coords.ndim == 2 and coords.shape[1] >= 2:
            return coords[:, :2], "obsm.X_umap"

    if "X_pca" in adata.obsm:
        try:
            coords = np.asarray(adata.obsm["X_pca"][indices, :2], dtype=np.float32)
        except Exception:
            coords = np.asarray(adata.obsm["X_pca"], dtype=np.float32)[indices, :2]
        if coords.ndim == 2 and coords.shape[1] >= 2:
            return coords[:, :2], "obsm.X_pca"

    try:
        matrix = np.asarray(adata.X[indices, :2], dtype=np.float32)
    except Exception:
        matrix = np.asarray(adata.X, dtype=np.float32)[indices, :2]

    if matrix.ndim == 2 and matrix.shape[1] >= 2:
        return matrix[:, :2], "matrix_first_two_dims"
    if matrix.ndim == 2 and matrix.shape[1] == 1:
        axis = matrix[:, 0].astype(np.float32)
        return np.column_stack([axis, np.zeros_like(axis)]).astype(np.float32), "matrix_first_dim_plus_zeros"
    if matrix.ndim == 1:
        axis = matrix.astype(np.float32)
        return np.column_stack([axis, np.zeros_like(axis)]).astype(np.float32), "matrix_first_dim_plus_zeros"
    return np.zeros((len(indices), 2), dtype=np.float32), "zeros"


def _resolve_csv_visualization_points(df: pd.DataFrame, vector_columns: list[str]) -> tuple[np.ndarray, str]:
    candidate_pairs = [
        ("umap_1", "umap_2"),
        ("umap1", "umap2"),
        ("UMAP1", "UMAP2"),
        ("UMAP_1", "UMAP_2"),
        ("x", "y"),
        ("X", "Y"),
    ]
    for x_col, y_col in candidate_pairs:
        if x_col in df.columns and y_col in df.columns:
            points = df[[x_col, y_col]].to_numpy(dtype=np.float32)
            return points, f"csv:{x_col},{y_col}"

    if len(vector_columns) >= 2:
        points = df[[vector_columns[0], vector_columns[1]]].to_numpy(dtype=np.float32)
        return points, f"vector:{vector_columns[0]},{vector_columns[1]}"
    if len(vector_columns) == 1:
        x_axis = df[[vector_columns[0]]].to_numpy(dtype=np.float32).reshape(-1)
        points = np.column_stack([x_axis, np.zeros_like(x_axis)]).astype(np.float32)
        return points, f"vector:{vector_columns[0]}+zeros"

    row_count = len(df)
    return np.zeros((row_count, 2), dtype=np.float32), "zeros"


def _resolve_h5ad_visualization_points(adata, vectors: np.ndarray) -> tuple[np.ndarray, str]:
    if "X_umap" in adata.obsm:
        umap = np.asarray(adata.obsm["X_umap"], dtype=np.float32)
        if umap.ndim == 2 and umap.shape[1] >= 2:
            return umap[:, :2], "obsm.X_umap"

    if "X_pca" in adata.obsm:
        pca = np.asarray(adata.obsm["X_pca"], dtype=np.float32)
        if pca.ndim == 2 and pca.shape[1] >= 2:
            return pca[:, :2], "obsm.X_pca"

    if vectors.ndim == 2 and vectors.shape[1] >= 2:
        return vectors[:, :2], "matrix_first_two_dims"
    if vectors.ndim == 2 and vectors.shape[1] == 1:
        axis = vectors[:, 0].astype(np.float32)
        return np.column_stack([axis, np.zeros_like(axis)]).astype(np.float32), "matrix_first_dim_plus_zeros"

    row_count = vectors.shape[0] if vectors.ndim >= 1 else int(adata.n_obs)
    return np.zeros((row_count, 2), dtype=np.float32), "zeros"
