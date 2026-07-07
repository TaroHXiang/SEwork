import scanpy as sc

adata = sc.read_h5ad("data/liver.h5ad")

adata.obsm.pop("X_pca", None)
adata.obsm.pop("X_umap", None)

adata.write_h5ad("data/liver_no_pca_umap.h5ad")