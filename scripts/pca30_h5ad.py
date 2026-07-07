from __future__ import annotations

import argparse
from pathlib import Path

import scanpy as sc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recompute obsm['X_pca'] with a fixed number of components for h5ad files."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Input .h5ad files. If omitted, all data/*.h5ad files are processed.",
    )
    parser.add_argument("--n-comps", type=int, default=30, help="Number of PCA components.")
    parser.add_argument(
        "--output-dir",
        default="data/processed/pca30",
        help="Directory for processed .h5ad files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output files if they already exist.",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Run normalize_total and log1p before PCA. Leave off to PCA the current X matrix.",
    )
    return parser.parse_args()


def default_inputs() -> list[Path]:
    return sorted(
        path
        for path in Path("data").glob("*.h5ad")
        if "_pca30" not in path.stem.lower()
    )


def output_path_for(input_path: Path, output_dir: Path) -> Path:
    return output_dir / f"{input_path.stem}_pca30.h5ad"


def process_file(input_path: Path, output_path: Path, n_comps: int, normalize: bool) -> None:
    print(f"Reading {input_path}")
    adata = sc.read_h5ad(input_path)
    if min(adata.n_obs, adata.n_vars) <= n_comps:
        raise ValueError(
            f"{input_path} cannot produce {n_comps} PCA components: "
            f"shape={adata.n_obs} cells x {adata.n_vars} genes"
        )

    if normalize:
        print("  normalize_total + log1p")
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

    print(f"  PCA n_comps={n_comps}")
    sc.pp.pca(adata, n_comps=n_comps)
    print(f"  X_pca shape={adata.obsm['X_pca'].shape}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(output_path)
    print(f"  Wrote {output_path}")


def main() -> None:
    args = parse_args()
    inputs = [Path(item) for item in args.inputs] if args.inputs else default_inputs()
    output_dir = Path(args.output_dir)

    if not inputs:
        raise SystemExit("No .h5ad files found.")

    for input_path in inputs:
        if not input_path.exists():
            raise FileNotFoundError(f"input file not found: {input_path}")
        output_path = output_path_for(input_path, output_dir)
        if output_path.exists() and not args.overwrite:
            print(f"Skipping existing output {output_path}")
            continue
        process_file(
            input_path=input_path,
            output_path=output_path,
            n_comps=args.n_comps,
            normalize=args.normalize,
        )


if __name__ == "__main__":
    main()
