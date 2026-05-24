from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class CellVectorDataset:
    cell_ids: list[str]
    vectors: np.ndarray
    metadata: list[dict]

    @property
    def vector_dim(self) -> int:
        return int(self.vectors.shape[1])


def load_cell_vectors(data_path: str | Path) -> CellVectorDataset:
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    if path.suffix.lower() == ".csv":
        return _load_csv(path)

    if path.suffix.lower() == ".h5ad":
        return _load_h5ad(path)

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
    )


def _load_h5ad(path: Path) -> CellVectorDataset:
    import scanpy as sc

    adata = sc.read_h5ad(path)
    if "X_pca" in adata.obsm:
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
    )
