from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
import pandas as pd

TARGET_INDEX_VECTOR_DIM = 30
PCA_RANDOM_STATE = 42
PCA_BATCH_SIZE = 512

DEFAULT_METADATA_FILTER_FIELDS = [
    "cell_type",
    "disease",
    "AgeGroup",
    "dataset_name",
    "sex",
    "tissue",
    "donor_id",
]

DEFAULT_UMAP_LEVEL_LIMITS = {
    "preview": 10000,
    "cluster": 15000,
    "detail": 60000,
}

METADATA_FIELD_ALIASES = {
    "cell_type": [
        "cell_type",
        "celltype",
        "cell type",
        "CellType",
        "major_cell_type",
        "annotation",
        "cell_ontology_class",
    ],
    "disease": [
        "disease",
        "condition",
        "status",
        "diagnosis",
        "phenotype",
    ],
    "AgeGroup": [
        "AgeGroup",
        "age_group",
        "agegroup",
        "age group",
        "age",
    ],
    "sex": [
        "sex",
        "gender",
    ],
    "tissue": [
        "tissue",
        "organ",
        "sample_tissue",
        "tissue_type",
    ],
    "donor_id": [
        "donor_id",
        "donor",
        "donorid",
        "patient_id",
        "sample_id",
        "individual",
    ],
}

QUALITY_FIELD_ALIASES = {
    "gene_count": [
        "n_genes_by_counts",
        "n_genes",
        "nfeature_rna",
        "gene_count",
        "genes_detected",
    ],
    "umi_count": [
        "total_counts",
        "ncount_rna",
        "umi_count",
        "umi",
        "counts",
    ],
    "mito_pct": [
        "pct_counts_mt",
        "percent_mt",
        "percent_mito",
        "mito_pct",
        "mt_ratio",
        "mitochondrial_pct",
    ],
    "sample_id": [
        "sample_id",
        "sample",
        "donor_id",
        "batch",
        "donor",
    ],
}

PREVIEW_METADATA_FIELDS = [
    "cell_type",
    "disease",
    "AgeGroup",
    "sex",
    "tissue",
    "donor_id",
    "sample_id",
    "gene_count",
    "umi_count",
    "mito_pct",
]


def _parse_data_paths(data_path: str | Path | list[str | Path] | tuple[str | Path, ...]) -> list[Path]:
    if isinstance(data_path, (list, tuple)):
        raw_items = [str(item).strip() for item in data_path]
    else:
        raw_text = str(data_path or "").strip()
        raw_items = [item.strip() for item in re.split(r"[;\n,]+", raw_text)]
    paths = [Path(item) for item in raw_items if item]
    if not paths:
        raise ValueError("data_path is required")
    return paths


def _dataset_source_prefix(dataset_name: str, dataset_index: int) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_]+", "_", str(dataset_name or "")).strip("_").lower()
    return normalized or f"dataset_{dataset_index + 1}"


def _visualization_x_offset(points: np.ndarray) -> float:
    if points.size == 0:
        return 0.0
    x_values = points[:, 0]
    span = float(np.nanmax(x_values) - np.nanmin(x_values))
    return max(span * 1.35, 10.0)


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
    vector_transform: dict | None

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
    paths = _parse_data_paths(data_path)
    if len(paths) > 1:
        return load_joint_cell_vectors(paths)

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    if path.suffix.lower() == ".csv":
        return _load_csv(path)

    if path.suffix.lower() == ".h5ad":
        return _load_h5ad(path)

    raise ValueError("unsupported data format, expected .csv or .h5ad")


def load_joint_cell_vectors(data_paths: list[str | Path]) -> CellVectorDataset:
    paths = _parse_data_paths(data_paths)
    if len(paths) < 2:
        return load_cell_vectors(paths[0])

    datasets = [load_cell_vectors(path) for path in paths]
    vector_dims = {dataset.vector_dim for dataset in datasets}
    if len(vector_dims) != 1:
        detail = ", ".join(f"{Path(dataset.source_path).name}: {dataset.vector_dim}" for dataset in datasets)
        raise ValueError(f"joint index requires matching vector dimensions, got {detail}")

    cell_ids: list[str] = []
    metadata: list[dict] = []
    visualization_parts: list[np.ndarray] = []
    metadata_fields = set()
    total_gene_count = 0
    embedding_keys = []
    source_formats = []

    for dataset_index, dataset in enumerate(datasets):
        source_path = str(dataset.source_path)
        dataset_name = Path(source_path).stem or f"dataset_{dataset_index + 1}"
        source_prefix = _dataset_source_prefix(dataset_name, dataset_index)
        total_gene_count += int(dataset.gene_count or 0)
        embedding_keys.append(str(dataset.embedding_key))
        source_formats.append(str(dataset.source_format))

        for raw_cell_id, raw_metadata in zip(dataset.cell_ids, dataset.metadata):
            cell_ids.append(f"{source_prefix}::{raw_cell_id}")
            enriched = dict(raw_metadata or {})
            enriched.update(
                {
                    "dataset_id": source_prefix,
                    "dataset_name": dataset_name,
                    "source_path": source_path,
                    "original_cell_id": str(raw_cell_id),
                }
            )
            metadata.append(enriched)
            metadata_fields.update(enriched.keys())

        points = np.asarray(dataset.visualization_points, dtype=np.float32)
        if points.ndim != 2 or points.shape[1] < 2:
            points = np.zeros((dataset.cell_count, 2), dtype=np.float32)
        points = points[:, :2].copy()
        if len(datasets) > 1 and len(points):
            points[:, 0] += float(dataset_index) * _visualization_x_offset(points)
        visualization_parts.append(points)

    vectors = np.vstack([dataset.vectors.astype(np.float32, copy=False) for dataset in datasets])
    visualization_points = (
        np.vstack(visualization_parts).astype(np.float32, copy=False)
        if visualization_parts
        else np.empty((0, 2), dtype=np.float32)
    )
    source_paths = [str(path) for path in paths]
    return CellVectorDataset(
        cell_ids=cell_ids,
        vectors=vectors,
        metadata=metadata,
        visualization_points=visualization_points,
        visualization_source="joint_dataset_offsets",
        metadata_fields=sorted(metadata_fields),
        source_path="; ".join(source_paths),
        source_format="joint:" + "+".join(sorted(set(source_formats))),
        gene_count=total_gene_count,
        embedding_key="joint:" + "+".join(sorted(set(embedding_keys))),
        vector_transform={
            "type": "joint_dataset",
            "sources": [
                {
                    "source_path": dataset.source_path,
                    "cell_count": dataset.cell_count,
                    "vector_dim": dataset.vector_dim,
                    "embedding_key": dataset.embedding_key,
                    "source_format": dataset.source_format,
                }
                for dataset in datasets
            ],
        },
    )


def inspect_cell_dataset(data_path: str | Path) -> dict:
    paths = _parse_data_paths(data_path)
    if len(paths) > 1:
        inspected = [inspect_cell_dataset(path) for path in paths]
        vector_dims = sorted({int(item.get("vector_dim") or 0) for item in inspected})
        source_paths = [str(path) for path in paths]
        return {
            "source_path": "; ".join(source_paths),
            "source_paths": source_paths,
            "format": "joint",
            "source_format": "joint",
            "is_joint": True,
            "dataset_count": len(inspected),
            "datasets": inspected,
            "cell_count": sum(int(item.get("cell_count") or 0) for item in inspected),
            "gene_count": sum(int(item.get("gene_count") or 0) for item in inspected),
            "vector_dim": vector_dims[0] if len(vector_dims) == 1 else None,
            "vector_dims": vector_dims,
            "embedding_key": "joint",
            "visualization_source": "joint_dataset_offsets",
            "metadata_columns": sorted(
                {
                    column
                    for item in inspected
                    for column in (item.get("metadata_columns") or [])
                }
                | {"dataset_id", "dataset_name", "source_path", "original_cell_id"}
            ),
        }

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, nrows=5)
        vector_columns = [col for col in df.columns if col.startswith("v")]
        metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            row_count = max(sum(1 for _ in handle) - 1, 0)
        raw_vector_dim = len(vector_columns)
        vector_dim = _target_dim_for_shape(row_count, raw_vector_dim)
        return {
            "source_path": str(path),
            "format": "csv",
            "cell_count": row_count,
            "gene_count": len(vector_columns),
            "vector_dim": vector_dim,
            "original_vector_dim": raw_vector_dim,
            "columns": list(df.columns),
            "metadata_columns": metadata_columns,
            "embedding_key": _embedding_key_with_pca_suffix("csv_vector_columns", raw_vector_dim, vector_dim),
            "visualization_source": "csv_columns_or_vector_projection",
        }

    if path.suffix.lower() == ".h5ad":
        adata = _read_h5ad_backed(path)
        try:
            embedding_key = "X_pca" if "X_pca" in adata.obsm else "X"
            raw_vector_dim = int(adata.obsm["X_pca"].shape[1]) if embedding_key == "X_pca" else int(adata.n_vars)
            vector_dim = min(raw_vector_dim, TARGET_INDEX_VECTOR_DIM) if embedding_key == "X_pca" else _target_dim_for_shape(int(adata.n_obs), raw_vector_dim)
            effective_embedding_key = (
                f"X_pca[:{vector_dim}]"
                if embedding_key == "X_pca" and raw_vector_dim > vector_dim
                else _embedding_key_with_pca_suffix(embedding_key, raw_vector_dim, vector_dim)
            )
            return {
                "source_path": str(path),
                "format": "h5ad",
                "cell_count": int(adata.n_obs),
                "gene_count": int(adata.n_vars),
                "vector_dim": vector_dim,
                "original_vector_dim": raw_vector_dim,
                "embedding_key": effective_embedding_key,
                "metadata_columns": list(adata.obs.columns),
                "obsm_keys": list(adata.obsm.keys()),
            }
        finally:
            adata.file.close()

    raise ValueError("unsupported data format, expected .csv or .h5ad")


def load_dataset_visualization_preview(
    data_path: str | Path,
    limit: int | None = 10000,
    seed: int = 42,
    level: str = "preview",
) -> dict:
    sampling_level = (level or "preview").strip().lower()
    if sampling_level not in DEFAULT_UMAP_LEVEL_LIMITS:
        raise ValueError("level must be one of: preview, cluster, detail")

    if limit is None:
        limit = DEFAULT_UMAP_LEVEL_LIMITS[sampling_level]

    if limit < 1 or limit > 100000:
        raise ValueError("limit must be between 1 and 100000")

    paths = _parse_data_paths(data_path)
    if len(paths) > 1:
        per_dataset_limit = max(1, int(np.ceil(limit / len(paths))))
        previews = [
            load_dataset_visualization_preview(path, limit=per_dataset_limit, seed=seed + idx, level=sampling_level)
            for idx, path in enumerate(paths)
        ]
        points = []
        total_points = 0
        metadata_columns = set()
        for idx, preview in enumerate(previews):
            dataset_name = Path(preview.get("source_path") or paths[idx]).stem
            source_prefix = _dataset_source_prefix(dataset_name, idx)
            preview_points = list(preview.get("points") or [])
            x_values = [float(point.get("x") or 0.0) for point in preview_points]
            x_offset = (max(x_values) - min(x_values) if x_values else 10.0)
            x_offset = max(float(x_offset) * 1.35, 10.0) * idx
            for point in preview_points:
                original_cell_id = str(point.get("cell_id") or "")
                metadata = dict(point.get("metadata") or {})
                metadata.update(
                    {
                        "dataset_id": source_prefix,
                        "dataset_name": dataset_name,
                        "source_path": str(paths[idx]),
                        "original_cell_id": original_cell_id,
                    }
                )
                metadata_columns.update(metadata.keys())
                points.append(
                    {
                        "cell_id": f"{source_prefix}::{original_cell_id}",
                        "x": float(point.get("x") or 0.0) + x_offset,
                        "y": float(point.get("y") or 0.0),
                        "metadata": metadata,
                    }
                )
            total_points += int(preview.get("total_points") or 0)
        return {
            "source_path": "; ".join(str(path) for path in paths),
            "source_paths": [str(path) for path in paths],
            "format": "joint",
            "total_points": total_points,
            "returned_points": len(points),
            "sampled": total_points > len(points),
            "sampling_level": sampling_level,
            "visualization_source": "joint_dataset_offsets",
            "metadata_columns": sorted(metadata_columns),
            "points": points[:limit],
        }

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _csv_visualization_preview(path=path, limit=limit, seed=seed, level=sampling_level)
    if suffix == ".h5ad":
        return _h5ad_visualization_preview(path=path, limit=limit, seed=seed, level=sampling_level)
    raise ValueError("unsupported data format, expected .csv or .h5ad")


def load_dataset_analytics(data_path: str | Path) -> dict:
    paths = _parse_data_paths(data_path)
    if len(paths) > 1:
        inspected = [inspect_cell_dataset(path) for path in paths]
        analytics_parts = [load_dataset_analytics(path) for path in paths]
        return _merge_joint_dataset_analytics(paths=paths, inspected=inspected, analytics_parts=analytics_parts)

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _csv_dataset_analytics(path)
    if suffix == ".h5ad":
        return _h5ad_dataset_analytics(path)
    raise ValueError("unsupported data format, expected .csv or .h5ad")


def _weighted_average(values: list[tuple[float | None, int]]) -> float | None:
    weighted_sum = 0.0
    total_weight = 0
    for value, weight in values:
        if value is None or weight <= 0:
            continue
        weighted_sum += float(value) * int(weight)
        total_weight += int(weight)
    if total_weight <= 0:
        return None
    return round(weighted_sum / total_weight, 4)


def _merge_histograms(histograms: list[dict]) -> dict:
    bucket_counts: dict[float, int] = {}
    for histogram in histograms:
        bins = histogram.get("bins") or []
        counts = histogram.get("counts") or []
        for bin_value, count in zip(bins, counts):
            try:
                key = round(float(bin_value), 4)
            except Exception:
                continue
            bucket_counts[key] = bucket_counts.get(key, 0) + int(count or 0)
    if not bucket_counts:
        return {"bins": [], "counts": []}
    ordered = sorted(bucket_counts.items(), key=lambda item: item[0])
    return {
        "bins": [value for value, _ in ordered[:30]],
        "counts": [count for _, count in ordered[:30]],
    }


def _merge_joint_dataset_analytics(
    *,
    paths: list[Path],
    inspected: list[dict],
    analytics_parts: list[dict],
) -> dict:
    source_paths = [str(path) for path in paths]
    total_cells = sum(int((part.get("summary") or {}).get("total_cells") or 0) for part in analytics_parts)
    gene_count_total = sum(int(item.get("gene_count") or 0) for item in inspected)

    cell_type_accumulator: dict[str, dict] = {}
    for part in analytics_parts:
        for row in part.get("cell_type_distribution") or []:
            name = str(row.get("name") or "Unknown")
            count = int(row.get("count") or row.get("value") or 0)
            current = cell_type_accumulator.setdefault(
                name,
                {
                    "name": name,
                    "count": 0,
                    "gene_values": [],
                    "mito_values": [],
                },
            )
            current["count"] += count
            current["gene_values"].append((row.get("avg_gene_count"), count))
            current["mito_values"].append((row.get("avg_mito_pct"), count))

    cell_type_rows = []
    for item in sorted(cell_type_accumulator.values(), key=lambda row: row["count"], reverse=True)[:12]:
        cell_type_rows.append(
            {
                "name": item["name"],
                "count": int(item["count"]),
                "avg_gene_count": _weighted_average(item["gene_values"]),
                "avg_mito_pct": _weighted_average(item["mito_values"]),
            }
        )

    sample_labels: list[str] = []
    sample_type_counts: dict[str, dict[str, int]] = {}
    all_cell_types: list[str] = []
    for path, part in zip(paths, analytics_parts):
        dataset_name = Path(path).stem or "dataset"
        sample_distribution = part.get("sample_distribution") or {}
        samples = [str(value) for value in (sample_distribution.get("samples") or [])]
        for sample in samples:
            label = f"{dataset_name}:{sample}"
            sample_labels.append(label)
            sample_type_counts.setdefault(label, {})
        for series in sample_distribution.get("series") or []:
            cell_type = str(series.get("name") or "Unknown")
            if cell_type not in all_cell_types:
                all_cell_types.append(cell_type)
            for sample, value in zip(samples, series.get("data") or []):
                label = f"{dataset_name}:{sample}"
                sample_type_counts.setdefault(label, {})[cell_type] = int(value or 0)

    sample_labels = sample_labels[:12]
    all_cell_types = all_cell_types[:10]
    sample_table = pd.DataFrame(
        [
            {cell_type: sample_type_counts.get(sample, {}).get(cell_type, 0) for cell_type in all_cell_types}
            for sample in sample_labels
        ],
        index=sample_labels,
    )
    sample_distribution = {
        "samples": sample_labels,
        "cell_types": all_cell_types,
        "series": [
            {
                "name": cell_type,
                "data": [int(sample_type_counts.get(sample, {}).get(cell_type, 0)) for sample in sample_labels],
            }
            for cell_type in all_cell_types
        ],
        "similarity": _build_similarity_matrix(sample_table) if not sample_table.empty else {"labels": [], "matrix": []},
    }

    boxplot_labels: list[str] = []
    boxplot_series: list[list[float]] = []
    for part in analytics_parts:
        quality = part.get("quality") or {}
        boxplot = quality.get("boxplot_gene_count") or {}
        for label, series in zip(boxplot.get("labels") or [], boxplot.get("series") or []):
            if label in boxplot_labels:
                continue
            boxplot_labels.append(str(label))
            boxplot_series.append(series)
            if len(boxplot_labels) >= 8:
                break
        if len(boxplot_labels) >= 8:
            break

    summary_values = [(part.get("summary") or {}, int((part.get("summary") or {}).get("total_cells") or 0)) for part in analytics_parts]
    return {
        "dataset_name": "Joint Dataset",
        "source_path": "; ".join(source_paths),
        "source_paths": source_paths,
        "format": "joint",
        "summary": {
            "dataset_name": "Joint Dataset",
            "total_cells": total_cells,
            "cell_type_count": len(cell_type_accumulator),
            "sample_count": len(sample_labels),
            "avg_gene_count": _weighted_average([(summary.get("avg_gene_count"), weight) for summary, weight in summary_values]),
            "avg_umi_count": _weighted_average([(summary.get("avg_umi_count"), weight) for summary, weight in summary_values]),
            "avg_mito_pct": _weighted_average([(summary.get("avg_mito_pct"), weight) for summary, weight in summary_values]),
            "gene_count_total": gene_count_total,
            "vector_dim": inspected[0].get("vector_dim") if inspected else None,
            "embedding_key": "joint",
            "visualization_source": "joint_dataset_offsets",
            "dataset_count": len(paths),
        },
        "cell_type_distribution": cell_type_rows,
        "sample_distribution": sample_distribution,
        "quality": {
            "gene_count_histogram": _merge_histograms([(part.get("quality") or {}).get("gene_count_histogram") or {} for part in analytics_parts]),
            "umi_count_histogram": _merge_histograms([(part.get("quality") or {}).get("umi_count_histogram") or {} for part in analytics_parts]),
            "mito_pct_histogram": _merge_histograms([(part.get("quality") or {}).get("mito_pct_histogram") or {} for part in analytics_parts]),
            "boxplot_gene_count": {
                "labels": boxplot_labels,
                "series": boxplot_series,
            },
        },
        "datasets": inspected,
    }


def load_dataset_metadata_options(
    data_path: str | Path,
    fields: list[str] | None = None,
    max_values_per_field: int = 200,
) -> dict:
    if max_values_per_field < 1:
        raise ValueError("max_values_per_field must be greater than 0")

    target_fields = list(fields or DEFAULT_METADATA_FILTER_FIELDS)
    target_fields = [field for field in target_fields if field]
    if not target_fields:
        target_fields = list(DEFAULT_METADATA_FILTER_FIELDS)

    paths = _parse_data_paths(data_path)
    if len(paths) > 1:
        merged_options: dict[str, set[str]] = {field: set() for field in target_fields}
        merged_options.setdefault("dataset_name", set())
        unique_counts: dict[str, int] = {}
        resolved_fields: dict[str, str] = {}
        missing_fields = set()
        truncated_fields = set()
        available_fields = set()
        for path in paths:
            info = load_dataset_metadata_options(path, fields=target_fields, max_values_per_field=max_values_per_field)
            dataset_name = Path(path).stem
            merged_options["dataset_name"].add(dataset_name)
            available_fields.update(info.get("available_fields") or [])
            resolved_fields.update(info.get("resolved_fields") or {})
            missing_fields.update(info.get("missing_fields") or [])
            truncated_fields.update(info.get("truncated_fields") or [])
            for field, values in (info.get("options") or {}).items():
                merged_options.setdefault(field, set()).update(str(value) for value in values if value is not None)
        options = {
            field: sorted(values)[:max_values_per_field]
            for field, values in merged_options.items()
            if values
        }
        for field, values in merged_options.items():
            unique_counts[field] = len(values)
            if len(values) > max_values_per_field:
                truncated_fields.add(field)
        return {
            "source_path": "; ".join(str(path) for path in paths),
            "source_paths": [str(path) for path in paths],
            "format": "joint",
            "available_fields": sorted(available_fields | {"dataset_name", "dataset_id", "source_path", "original_cell_id"}),
            "options": options,
            "unique_counts": unique_counts,
            "truncated_fields": sorted(truncated_fields),
            "resolved_fields": resolved_fields,
            "missing_fields": sorted(missing_fields),
        }

    path = paths[0]
    if not path.exists():
        raise FileNotFoundError(f"data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _csv_metadata_options(
            path=path,
            target_fields=target_fields,
            max_values_per_field=max_values_per_field,
        )
    if suffix == ".h5ad":
        return _h5ad_metadata_options(
            path=path,
            target_fields=target_fields,
            max_values_per_field=max_values_per_field,
        )
    raise ValueError("unsupported data format, expected .csv or .h5ad")


def _normalize_field_token(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (field_name or "").strip().lower())


def _resolve_target_field_mapping(
    *,
    available_columns: list[str],
    target_fields: list[str],
) -> tuple[dict[str, str], list[str]]:
    normalized_to_original: dict[str, str] = {}
    for column in available_columns:
        normalized = _normalize_field_token(column)
        if normalized and normalized not in normalized_to_original:
            normalized_to_original[normalized] = column

    resolved: dict[str, str] = {}
    missing: list[str] = []

    for target in target_fields:
        if not target:
            continue
        candidates = METADATA_FIELD_ALIASES.get(target, []) + [target]
        matched_column = None
        for candidate in candidates:
            normalized_candidate = _normalize_field_token(candidate)
            if normalized_candidate in normalized_to_original:
                matched_column = normalized_to_original[normalized_candidate]
                break
        if matched_column:
            resolved[target] = matched_column
        else:
            missing.append(target)

    return resolved, missing


def _read_h5ad_backed(path: Path):
    try:
        import scanpy as sc

        return sc.read_h5ad(path, backed="r")
    except Exception:
        try:
            import anndata as ad

            return ad.read_h5ad(path, backed="r")
        except Exception as exc:
            raise ImportError(
                "reading .h5ad requires either scanpy or anndata to be installed"
            ) from exc


def _target_dim_for_shape(row_count: int, vector_dim: int, target_dim: int = TARGET_INDEX_VECTOR_DIM) -> int:
    if vector_dim <= 0 or row_count <= 0:
        return max(vector_dim, 0)
    return min(int(target_dim), int(vector_dim), int(row_count))


def _embedding_key_with_pca_suffix(base_key: str, raw_dim: int, vector_dim: int) -> str:
    if raw_dim > vector_dim and vector_dim == TARGET_INDEX_VECTOR_DIM:
        return f"{base_key}->pca{TARGET_INDEX_VECTOR_DIM}"
    if raw_dim > vector_dim:
        return f"{base_key}->pca{vector_dim}"
    return base_key


def _as_float32_matrix(matrix) -> np.ndarray:
    if hasattr(matrix, "to_memory"):
        matrix = matrix.to_memory()

    try:
        from scipy import sparse

        if sparse.issparse(matrix):
            return matrix.toarray().astype(np.float32, copy=False)
    except Exception:
        pass

    array = np.asarray(matrix)
    if array.ndim == 0 and hasattr(matrix, "toarray"):
        array = matrix.toarray()
    array = np.asarray(array, dtype=np.float32)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    return array


def _iter_h5ad_x_batches(adata, batch_size: int = PCA_BATCH_SIZE):
    row_count = int(adata.n_obs)
    for start in range(0, row_count, batch_size):
        stop = min(start + batch_size, row_count)
        batch = _as_float32_matrix(adata.X[start:stop])
        yield start, stop, np.nan_to_num(batch, nan=0.0, posinf=0.0, neginf=0.0)


def _reduce_h5ad_x_for_index(adata) -> tuple[np.ndarray, str, dict | None]:
    row_count = int(adata.n_obs)
    raw_dim = int(adata.n_vars)
    target_dim = _target_dim_for_shape(row_count, raw_dim)
    if raw_dim <= target_dim:
        return np.ascontiguousarray(_as_float32_matrix(adata.X), dtype=np.float32), "X", None

    try:
        from scipy import sparse
        from sklearn.decomposition import TruncatedSVD

        sparse_matrix = adata.X.to_memory() if hasattr(adata.X, "to_memory") else adata.X
        if sparse.issparse(sparse_matrix):
            sparse_matrix = sparse_matrix.astype(np.float32, copy=False)
            svd = TruncatedSVD(n_components=target_dim, random_state=PCA_RANDOM_STATE)
            reduced = svd.fit_transform(sparse_matrix)
            return (
                np.ascontiguousarray(reduced, dtype=np.float32),
                f"X->truncated_svd{target_dim}",
                {
                    "type": "truncated_svd",
                    "input_dim": raw_dim,
                    "output_dim": target_dim,
                    "components": np.asarray(svd.components_, dtype=np.float32),
                },
            )
    except Exception as exc:
        raise RuntimeError(
            "h5ad does not contain obsm['X_pca']; failed to compute 30-dimensional SVD from sparse X. "
            f"Original error: {exc}"
        ) from exc

    try:
        from sklearn.decomposition import IncrementalPCA

        batch_size = max(PCA_BATCH_SIZE, target_dim * 4)
        pca = IncrementalPCA(n_components=target_dim, batch_size=batch_size)
        for _, _, batch in _iter_h5ad_x_batches(adata, batch_size=batch_size):
            if batch.shape[0] >= target_dim:
                pca.partial_fit(batch)

        reduced = np.empty((row_count, target_dim), dtype=np.float32)
        for start, stop, batch in _iter_h5ad_x_batches(adata, batch_size=batch_size):
            reduced[start:stop] = pca.transform(batch).astype(np.float32, copy=False)
        return (
            np.ascontiguousarray(reduced, dtype=np.float32),
            f"X->incremental_pca{target_dim}",
            {
                "type": "pca",
                "input_dim": raw_dim,
                "output_dim": target_dim,
                "mean": np.asarray(pca.mean_, dtype=np.float32),
                "components": np.asarray(pca.components_, dtype=np.float32),
            },
        )
    except Exception as exc:
        raise RuntimeError(
            "h5ad does not contain obsm['X_pca']; failed to compute 30-dimensional PCA from X in batches. "
            f"Original error: {exc}"
        ) from exc


def _reduce_vectors_for_index(vectors: np.ndarray, base_embedding_key: str) -> tuple[np.ndarray, str, dict | None]:
    vectors = _as_float32_matrix(vectors)
    if vectors.ndim != 2:
        raise ValueError("vectors must be a 2D matrix")
    vectors = np.nan_to_num(vectors, nan=0.0, posinf=0.0, neginf=0.0)

    raw_dim = int(vectors.shape[1])
    target_dim = _target_dim_for_shape(int(vectors.shape[0]), raw_dim)
    if raw_dim <= target_dim:
        return np.ascontiguousarray(vectors, dtype=np.float32), base_embedding_key, None

    if base_embedding_key == "X_pca":
        reduced = vectors[:, :target_dim]
        embedding_key = f"X_pca[:{target_dim}]"
        vector_transform = {
            "type": "slice",
            "input_dim": raw_dim,
            "output_dim": target_dim,
        }
    else:
        try:
            from sklearn.decomposition import PCA

            pca = PCA(n_components=target_dim, random_state=PCA_RANDOM_STATE)
            reduced = pca.fit_transform(vectors)
            vector_transform = {
                "type": "pca",
                "input_dim": raw_dim,
                "output_dim": target_dim,
                "mean": np.asarray(pca.mean_, dtype=np.float32),
                "components": np.asarray(pca.components_, dtype=np.float32),
            }
        except Exception:
            centered = vectors - np.mean(vectors, axis=0, keepdims=True)
            _, _, vt = np.linalg.svd(centered, full_matrices=False)
            reduced = centered @ vt[:target_dim].T
            vector_transform = {
                "type": "pca",
                "input_dim": raw_dim,
                "output_dim": target_dim,
                "mean": np.asarray(np.mean(vectors, axis=0), dtype=np.float32),
                "components": np.asarray(vt[:target_dim], dtype=np.float32),
            }
        embedding_key = _embedding_key_with_pca_suffix(base_embedding_key, raw_dim, target_dim)

    return np.ascontiguousarray(reduced, dtype=np.float32), embedding_key, vector_transform


def _load_csv(path: Path) -> CellVectorDataset:
    df = pd.read_csv(path)
    if "cell_id" not in df.columns:
        raise ValueError("CSV must contain a cell_id column")

    vector_columns = [col for col in df.columns if col.startswith("v")]
    if not vector_columns:
        raise ValueError("CSV must contain vector columns named v1, v2, ...")

    raw_vectors = df[vector_columns].to_numpy(dtype=np.float32)
    vectors, embedding_key, vector_transform = _reduce_vectors_for_index(raw_vectors, "csv_vector_columns")
    all_metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
    resolved_fields, _ = _resolve_target_field_mapping(
        available_columns=all_metadata_columns,
        target_fields=DEFAULT_METADATA_FILTER_FIELDS,
    )
    metadata_columns = list(resolved_fields.keys())
    if metadata_columns:
        canonical_df = pd.DataFrame(
            {target_key: df[source_col] for target_key, source_col in resolved_fields.items()}
        )
        metadata = (
            canonical_df.astype(str)
            .replace({"nan": None, "None": None})
            .to_dict(orient="records")
        )
    else:
        metadata = [{} for _ in range(len(df))]
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
        embedding_key=embedding_key,
        vector_transform=vector_transform,
    )


def _csv_metadata_options(path: Path, target_fields: list[str], max_values_per_field: int) -> dict:
    header_df = pd.read_csv(path, nrows=0)
    available_columns = list(header_df.columns)
    resolved_fields, missing_fields = _resolve_target_field_mapping(
        available_columns=available_columns,
        target_fields=target_fields,
    )
    selected_columns = sorted(set(resolved_fields.values()))
    if not selected_columns:
        return {
            "source_path": str(path),
            "format": "csv",
            "available_fields": [],
            "options": {},
            "unique_counts": {},
            "truncated_fields": [],
            "resolved_fields": {},
            "missing_fields": missing_fields,
        }

    metadata_df = pd.read_csv(path, usecols=selected_columns)
    options, unique_counts, truncated_fields = _extract_metadata_options(
        metadata_df=metadata_df,
        field_mapping=resolved_fields,
        max_values_per_field=max_values_per_field,
    )
    return {
        "source_path": str(path),
        "format": "csv",
        "available_fields": selected_columns,
        "options": options,
        "unique_counts": unique_counts,
        "truncated_fields": truncated_fields,
        "resolved_fields": resolved_fields,
        "missing_fields": missing_fields,
    }


def _load_h5ad(path: Path) -> CellVectorDataset:
    adata = _read_h5ad_backed(path)
    try:
        embedding_key = "X_pca" if "X_pca" in adata.obsm else "X"
        if embedding_key == "X_pca":
            raw_vectors = adata.obsm["X_pca"]
            vectors, embedding_key, vector_transform = _reduce_vectors_for_index(raw_vectors, embedding_key)
        else:
            vectors, embedding_key, vector_transform = _reduce_h5ad_x_for_index(adata)
        visualization_points, visualization_source = _resolve_h5ad_visualization_points(
            adata=adata,
            vectors=vectors,
        )

        available_columns = [str(column) for column in list(adata.obs.columns)]
        resolved_fields, _ = _resolve_target_field_mapping(
            available_columns=available_columns,
            target_fields=DEFAULT_METADATA_FILTER_FIELDS,
        )
        metadata_columns = list(resolved_fields.keys())
        if metadata_columns:
            canonical_df = pd.DataFrame(
                {target_key: adata.obs[source_col] for target_key, source_col in resolved_fields.items()}
            )
            metadata = (
                canonical_df.astype(str)
                .replace({"nan": None, "None": None})
                .reset_index(drop=True)
                .to_dict(orient="records")
            )
        else:
            metadata = [{} for _ in range(int(adata.n_obs))]
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
            vector_transform=vector_transform,
        )
    finally:
        adata.file.close()


def _h5ad_metadata_options(path: Path, target_fields: list[str], max_values_per_field: int) -> dict:
    adata = _read_h5ad_backed(path)
    try:
        available_columns = [str(column) for column in list(adata.obs.columns)]
        resolved_fields, missing_fields = _resolve_target_field_mapping(
            available_columns=available_columns,
            target_fields=target_fields,
        )
        selected_columns = sorted(set(resolved_fields.values()))
        if not selected_columns:
            return {
                "source_path": str(path),
                "format": "h5ad",
                "available_fields": [],
                "options": {},
                "unique_counts": {},
                "truncated_fields": [],
                "resolved_fields": {},
                "missing_fields": missing_fields,
            }

        metadata_df = adata.obs[selected_columns].copy()
        options, unique_counts, truncated_fields = _extract_metadata_options(
            metadata_df=metadata_df,
            field_mapping=resolved_fields,
            max_values_per_field=max_values_per_field,
        )
        return {
            "source_path": str(path),
            "format": "h5ad",
            "available_fields": selected_columns,
            "options": options,
            "unique_counts": unique_counts,
            "truncated_fields": truncated_fields,
            "resolved_fields": resolved_fields,
            "missing_fields": missing_fields,
        }
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


def _sample_indices_stratified(labels: list[str], limit: int, seed: int) -> np.ndarray:
    total_count = len(labels)
    if total_count <= 0:
        return np.array([], dtype=np.int64)
    if total_count <= limit:
        return np.arange(total_count, dtype=np.int64)

    label_series = pd.Series(labels).fillna("Unknown").astype(str)
    groups = label_series.groupby(label_series).groups
    rng = np.random.default_rng(seed)
    selected: list[int] = []
    allocations: dict[str, int] = {}

    for label, index_values in groups.items():
        count = len(index_values)
        allocated = max(1, int(round(count / total_count * limit)))
        allocations[label] = min(allocated, count)

    allocated_total = sum(allocations.values())
    labels_sorted = sorted(groups.keys())
    while allocated_total > limit:
        for label in labels_sorted:
            if allocations[label] > 1 and allocated_total > limit:
                allocations[label] -= 1
                allocated_total -= 1
    while allocated_total < limit:
        for label in labels_sorted:
            if allocations[label] < len(groups[label]) and allocated_total < limit:
                allocations[label] += 1
                allocated_total += 1

    for label, index_values in groups.items():
        choices = np.asarray(index_values, dtype=np.int64)
        choose_n = allocations[label]
        if choose_n >= len(choices):
            selected.extend(choices.tolist())
        else:
            sampled = rng.choice(choices, size=choose_n, replace=False)
            selected.extend(sampled.astype(np.int64).tolist())
    return np.sort(np.asarray(selected[:limit], dtype=np.int64))


def _sample_indices_density_weighted(points: np.ndarray, limit: int, seed: int) -> np.ndarray:
    total_count = int(points.shape[0]) if isinstance(points, np.ndarray) and points.ndim == 2 else 0
    if total_count <= 0:
        return np.array([], dtype=np.int64)
    if total_count <= limit:
        return np.arange(total_count, dtype=np.int64)

    coords = np.asarray(points[:, :2], dtype=np.float32)
    if coords.size == 0:
        return _sample_indices(total_count=total_count, limit=limit, seed=seed)

    rng = np.random.default_rng(seed)
    bins = max(12, min(42, int(np.sqrt(limit))))
    x_values = coords[:, 0]
    y_values = coords[:, 1]
    x_edges = np.linspace(float(np.min(x_values)), float(np.max(x_values)), bins + 1)
    y_edges = np.linspace(float(np.min(y_values)), float(np.max(y_values)), bins + 1)
    x_ids = np.clip(np.digitize(x_values, x_edges[1:-1], right=False), 0, bins - 1)
    y_ids = np.clip(np.digitize(y_values, y_edges[1:-1], right=False), 0, bins - 1)

    groups: dict[tuple[int, int], list[int]] = {}
    for idx, key in enumerate(zip(x_ids.tolist(), y_ids.tolist())):
        groups.setdefault(key, []).append(idx)

    sampled: list[int] = []
    for _, indices in sorted(groups.items(), key=lambda item: len(item[1])):
        count = len(indices)
        keep = count if count <= 3 else max(2, int(np.sqrt(count)))
        keep = min(keep, count)
        if keep == count:
            sampled.extend(indices)
        else:
            chosen = rng.choice(np.asarray(indices, dtype=np.int64), size=keep, replace=False)
            sampled.extend(chosen.astype(np.int64).tolist())

    sampled = sorted(set(sampled))
    if len(sampled) > limit:
        chosen = rng.choice(np.asarray(sampled, dtype=np.int64), size=limit, replace=False)
        return np.sort(chosen.astype(np.int64))
    if len(sampled) < limit:
        remaining = np.setdiff1d(np.arange(total_count, dtype=np.int64), np.asarray(sampled, dtype=np.int64))
        extra = rng.choice(remaining, size=min(limit - len(sampled), len(remaining)), replace=False)
        sampled.extend(extra.astype(np.int64).tolist())
    return np.sort(np.asarray(sampled[:limit], dtype=np.int64))


def _resolve_preview_indices(
    *,
    total_count: int,
    limit: int,
    seed: int,
    level: str,
    stratify_labels: list[str] | None = None,
    points: np.ndarray | None = None,
) -> np.ndarray:
    if level == "detail":
        return _sample_indices(total_count=total_count, limit=limit, seed=seed)
    if level == "cluster" and points is not None:
        return _sample_indices_density_weighted(points=points, limit=limit, seed=seed)
    if stratify_labels:
        return _sample_indices_stratified(labels=stratify_labels, limit=limit, seed=seed)
    return _sample_indices(total_count=total_count, limit=limit, seed=seed)


def _resolve_alias_field(available_columns: list[str], aliases: list[str]) -> str | None:
    normalized_map = {
        _normalize_field_token(column): column
        for column in available_columns
        if _normalize_field_token(column)
    }
    for alias in aliases:
        normalized = _normalize_field_token(alias)
        if normalized in normalized_map:
            return normalized_map[normalized]
    return None


def _resolve_preview_metadata_mapping(available_columns: list[str]) -> dict[str, str]:
    preview_mapping: dict[str, str] = {}
    resolved_metadata, _ = _resolve_target_field_mapping(
        available_columns=available_columns,
        target_fields=DEFAULT_METADATA_FILTER_FIELDS,
    )
    preview_mapping.update(resolved_metadata)

    quality_mapping = {
        "sample_id": QUALITY_FIELD_ALIASES["sample_id"],
        "gene_count": QUALITY_FIELD_ALIASES["gene_count"],
        "umi_count": QUALITY_FIELD_ALIASES["umi_count"],
        "mito_pct": QUALITY_FIELD_ALIASES["mito_pct"],
    }
    for output_key, aliases in quality_mapping.items():
        source_column = _resolve_alias_field(available_columns, aliases)
        if source_column:
            preview_mapping[output_key] = source_column

    return {key: preview_mapping[key] for key in PREVIEW_METADATA_FIELDS if key in preview_mapping}


def _string_series(values) -> pd.Series:
    # Categorical columns cannot accept a new fill value unless it is already a
    # category. Convert to object first so missing values can be normalized
    # consistently for h5ad obs metadata.
    series = pd.Series(values).astype("object")
    series = series.where(series.notna(), "Unknown").astype(str)
    return series.replace({"nan": "Unknown", "None": "Unknown", "": "Unknown"})


def _numeric_series(values) -> pd.Series:
    series = pd.to_numeric(pd.Series(values), errors="coerce")
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    return series.astype(float)


def _series_mean_or_none(values) -> float | None:
    if values.empty:
        return None
    return float(np.round(values.mean(), 4))


def _build_histogram(values: pd.Series, bins: int = 16) -> dict:
    if values.empty:
        return {"bins": [], "counts": []}
    min_value = float(values.min())
    max_value = float(values.max())
    if min_value == max_value:
        return {"bins": [round(min_value, 4)], "counts": [int(values.shape[0])]}
    counts, edges = np.histogram(values.to_numpy(dtype=np.float32), bins=bins)
    centers = ((edges[:-1] + edges[1:]) / 2.0).astype(float).tolist()
    return {
        "bins": [round(value, 4) for value in centers],
        "counts": [int(value) for value in counts.tolist()],
    }


def _five_number_summary(values: pd.Series) -> list[float] | None:
    if values.empty:
        return None
    array = values.to_numpy(dtype=np.float32)
    minimum = float(np.min(array))
    q1, median, q3 = np.quantile(array, [0.25, 0.5, 0.75]).astype(float).tolist()
    maximum = float(np.max(array))
    return [round(minimum, 4), round(q1, 4), round(median, 4), round(q3, 4), round(maximum, 4)]


def _build_similarity_matrix(table: pd.DataFrame) -> dict:
    if table.empty:
        return {"labels": [], "matrix": []}
    labels = [str(label) for label in table.index.tolist()]
    values = table.to_numpy(dtype=np.float32)
    row_sums = values.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    normalized = values / row_sums
    norms = np.linalg.norm(normalized, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    cosine = (normalized @ normalized.T) / (norms @ norms.T)
    matrix = []
    for row_idx, _ in enumerate(labels):
        for col_idx, _ in enumerate(labels):
            matrix.append([row_idx, col_idx, round(float(cosine[row_idx, col_idx]), 4)])
    return {"labels": labels, "matrix": matrix}


def _build_dataset_analytics_frame(
    *,
    metadata_df: pd.DataFrame,
    dataset_name: str,
    source_path: str,
    source_format: str,
    gene_count_total: int | None,
    vector_dim: int | None,
    embedding_key: str,
    visualization_source: str,
) -> dict:
    available_columns = list(metadata_df.columns)
    resolved_metadata, _ = _resolve_target_field_mapping(
        available_columns=available_columns,
        target_fields=DEFAULT_METADATA_FILTER_FIELDS,
    )
    cell_type_col = resolved_metadata.get("cell_type")
    sample_col = _resolve_alias_field(available_columns, QUALITY_FIELD_ALIASES["sample_id"]) or resolved_metadata.get("donor_id")
    gene_metric_col = _resolve_alias_field(available_columns, QUALITY_FIELD_ALIASES["gene_count"])
    umi_metric_col = _resolve_alias_field(available_columns, QUALITY_FIELD_ALIASES["umi_count"])
    mito_metric_col = _resolve_alias_field(available_columns, QUALITY_FIELD_ALIASES["mito_pct"])

    total_cells = int(metadata_df.shape[0])
    cell_type_series = _string_series(metadata_df[cell_type_col]) if cell_type_col else _string_series(["Unknown"] * total_cells)
    sample_series = _string_series(metadata_df[sample_col]) if sample_col else _string_series(["Sample-1"] * total_cells)
    gene_metric = _numeric_series(metadata_df[gene_metric_col]) if gene_metric_col else pd.Series(dtype=float)
    umi_metric = _numeric_series(metadata_df[umi_metric_col]) if umi_metric_col else pd.Series(dtype=float)
    mito_metric = _numeric_series(metadata_df[mito_metric_col]) if mito_metric_col else pd.Series(dtype=float)

    cell_type_counts = cell_type_series.value_counts().sort_values(ascending=False)
    top_cell_types = cell_type_counts.index.tolist()[:12]
    cell_type_rows: list[dict] = []
    for cell_type in top_cell_types:
        mask = cell_type_series == cell_type
        cell_type_rows.append(
            {
                "name": str(cell_type),
                "count": int(mask.sum()),
                "avg_gene_count": _series_mean_or_none(_numeric_series(metadata_df.loc[mask, gene_metric_col])) if gene_metric_col else None,
                "avg_mito_pct": _series_mean_or_none(_numeric_series(metadata_df.loc[mask, mito_metric_col])) if mito_metric_col else None,
            }
        )

    sample_cell_table = pd.crosstab(sample_series, cell_type_series)
    if sample_cell_table.shape[1] > 10:
        sample_cell_table = sample_cell_table.iloc[:, :10]
    sample_distribution = {
        "samples": [str(value) for value in sample_cell_table.index.tolist()],
        "cell_types": [str(value) for value in sample_cell_table.columns.tolist()],
        "series": [
            {"name": str(column), "data": [int(value) for value in sample_cell_table[column].tolist()]}
            for column in sample_cell_table.columns
        ],
        "similarity": _build_similarity_matrix(sample_cell_table),
    }

    boxplot_labels: list[str] = []
    boxplot_values: list[list[float]] = []
    if gene_metric_col:
        for cell_type in top_cell_types[:8]:
            mask = cell_type_series == cell_type
            summary = _five_number_summary(_numeric_series(metadata_df.loc[mask, gene_metric_col]))
            if summary:
                boxplot_labels.append(str(cell_type))
                boxplot_values.append(summary)

    return {
        "dataset_name": dataset_name,
        "source_path": source_path,
        "format": source_format,
        "summary": {
            "dataset_name": dataset_name,
            "total_cells": total_cells,
            "cell_type_count": int(cell_type_series.nunique()),
            "sample_count": int(sample_series.nunique()),
            "avg_gene_count": _series_mean_or_none(gene_metric),
            "avg_umi_count": _series_mean_or_none(umi_metric),
            "avg_mito_pct": _series_mean_or_none(mito_metric),
            "gene_count_total": gene_count_total,
            "vector_dim": vector_dim,
            "embedding_key": embedding_key,
            "visualization_source": visualization_source,
        },
        "cell_type_distribution": cell_type_rows,
        "sample_distribution": sample_distribution,
        "quality": {
            "gene_count_histogram": _build_histogram(gene_metric),
            "umi_count_histogram": _build_histogram(umi_metric),
            "mito_pct_histogram": _build_histogram(mito_metric),
            "boxplot_gene_count": {
                "labels": boxplot_labels,
                "series": boxplot_values,
            },
        },
    }


def _extract_metadata_options(
    metadata_df: pd.DataFrame,
    field_mapping: dict[str, str],
    max_values_per_field: int,
) -> tuple[dict[str, list[str]], dict[str, int], list[str]]:
    options: dict[str, list[str]] = {}
    unique_counts: dict[str, int] = {}
    truncated_fields: list[str] = []

    for output_field, source_column in field_mapping.items():
        if source_column not in metadata_df.columns:
            continue
        raw_values = (
            metadata_df[source_column]
            .astype(str)
            .map(lambda item: item.strip())
            .replace({"nan": "", "NaN": "", "None": "", "null": "", "NULL": ""})
        )
        values = sorted({value for value in raw_values.tolist() if value})
        unique_counts[output_field] = len(values)
        if len(values) > max_values_per_field:
            options[output_field] = values[:max_values_per_field]
            truncated_fields.append(output_field)
        else:
            options[output_field] = values

    return options, unique_counts, truncated_fields


def _csv_visualization_preview(path: Path, limit: int, seed: int, level: str) -> dict:
    df = pd.read_csv(path)
    if "cell_id" not in df.columns:
        raise ValueError("CSV must contain a cell_id column")

    vector_columns = [col for col in df.columns if col.startswith("v")]
    if not vector_columns:
        raise ValueError("CSV must contain vector columns named v1, v2, ...")

    available_metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
    preview_mapping = _resolve_preview_metadata_mapping(available_metadata_columns)
    points, visualization_source = _resolve_csv_visualization_points(df, vector_columns)
    total_count = len(df)
    stratify_labels = None
    if preview_mapping.get("cell_type"):
        stratify_labels = df[preview_mapping["cell_type"]].fillna("Unknown").astype(str).tolist()
    indices = _resolve_preview_indices(
        total_count=total_count,
        limit=limit,
        seed=seed,
        level=level,
        stratify_labels=stratify_labels,
        points=points,
    )

    sampled_points = points[indices] if len(indices) else np.empty((0, 2), dtype=np.float32)
    sampled_ids = df["cell_id"].astype(str).to_numpy()[indices] if len(indices) else np.array([], dtype=str)
    sampled_metadata = []
    if preview_mapping and len(indices):
        preview_df = (
            pd.DataFrame(
                {
                    output_key: df.iloc[indices][source_column]
                    for output_key, source_column in preview_mapping.items()
                }
            )
            .replace({np.nan: None})
        )
        sampled_metadata = preview_df.to_dict(orient="records")
    elif len(indices):
        sampled_metadata = [{} for _ in range(len(indices))]

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
        "sampling_level": level,
        "vector_dim": len(vector_columns),
        "embedding_key": "csv_vector_columns",
        "visualization_source": visualization_source,
        "metadata_columns": list(preview_mapping.keys()),
        "points": result_points,
    }


def _h5ad_visualization_preview(path: Path, limit: int, seed: int, level: str) -> dict:
    adata = _read_h5ad_backed(path)
    try:
        total_count = int(adata.n_obs)
        available_columns = [str(column) for column in list(adata.obs.columns)]
        preview_mapping = _resolve_preview_metadata_mapping(available_columns)

        all_points, visualization_source = _resolve_h5ad_preview_points(
            adata=adata,
            indices=np.arange(total_count, dtype=np.int64),
        )
        stratify_labels = None
        source_cell_type_column = preview_mapping.get("cell_type")
        if source_cell_type_column:
            stratify_labels = adata.obs[source_cell_type_column].astype(str).fillna("Unknown").tolist()
        indices = _resolve_preview_indices(
            total_count=total_count,
            limit=limit,
            seed=seed,
            level=level,
            stratify_labels=stratify_labels,
            points=all_points,
        )
        points = all_points[indices] if len(indices) else np.empty((0, 2), dtype=np.float32)
        sampled_ids = [str(cell_id) for cell_id in adata.obs_names[indices]]
        sampled_metadata = (
            pd.DataFrame(
                {
                    output_key: adata.obs.iloc[indices][source_column]
                    for output_key, source_column in preview_mapping.items()
                }
            )
            .replace({np.nan: None})
            .to_dict(orient="records")
            if preview_mapping
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
            "sampling_level": level,
            "cell_count": total_count,
            "gene_count": int(adata.n_vars),
            "vector_dim": int(points.shape[1]) if points.ndim == 2 and points.shape[1] > 0 else 0,
            "embedding_key": "X_pca" if "X_pca" in adata.obsm else "X",
            "visualization_source": visualization_source,
            "metadata_columns": list(preview_mapping.keys()),
            "points": result_points,
        }
    finally:
        adata.file.close()


def _csv_dataset_analytics(path: Path) -> dict:
    df = pd.read_csv(path)
    if "cell_id" not in df.columns:
        raise ValueError("CSV must contain a cell_id column")
    vector_columns = [col for col in df.columns if col.startswith("v")]
    metadata_columns = [col for col in df.columns if col not in {"cell_id", *vector_columns}]
    metadata_df = df[metadata_columns].copy() if metadata_columns else pd.DataFrame(index=df.index)
    return _build_dataset_analytics_frame(
        metadata_df=metadata_df,
        dataset_name=path.stem,
        source_path=str(path),
        source_format="csv",
        gene_count_total=len(vector_columns),
        vector_dim=len(vector_columns),
        embedding_key="csv_vector_columns",
        visualization_source=_resolve_csv_visualization_points(df, vector_columns)[1],
    )


def _h5ad_dataset_analytics(path: Path) -> dict:
    adata = _read_h5ad_backed(path)
    try:
        metadata_df = adata.obs.copy()
        embedding_key = "X_pca" if "X_pca" in adata.obsm else "X"
        vector_dim = int(adata.obsm["X_pca"].shape[1]) if embedding_key == "X_pca" else int(adata.n_vars)
        visualization_source = "obsm.X_umap" if "X_umap" in adata.obsm else ("obsm.X_pca" if "X_pca" in adata.obsm else "matrix_first_two_dims")
        return _build_dataset_analytics_frame(
            metadata_df=metadata_df,
            dataset_name=path.stem,
            source_path=str(path),
            source_format="h5ad",
            gene_count_total=int(adata.n_vars),
            vector_dim=vector_dim,
            embedding_key=embedding_key,
            visualization_source=visualization_source,
        )
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
