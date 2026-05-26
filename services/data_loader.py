from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class CellVectorDataset:
    cell_ids: list[str]
    vectors: np.ndarray
    metadata: list[dict]
    source_path: str
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
            "cell_count": self.cell_count,
            "gene_count": self.gene_count,
            "vector_dim": self.vector_dim,
            "embedding_key": self.embedding_key,
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
        return {
            "source_path": str(path),
            "format": "csv",
            "vector_dim": len(vector_columns),
            "columns": list(df.columns),
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

    return CellVectorDataset(
        cell_ids=df["cell_id"].astype(str).tolist(),
        vectors=vectors,
        metadata=metadata,
        source_path=str(path),
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
            source_path=str(path),
            gene_count=int(adata.n_vars),
            embedding_key=embedding_key,
        )
    finally:
        adata.file.close()
