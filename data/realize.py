import scanpy as sc
import pandas as pd
import numpy as np

# 1. 读取数据
file_path = "./data/liver.h5ad" 
adata = sc.read_h5ad(file_path)

def get_cell_full_report(adata, cell_idx_or_name):
    """
    获取单个细胞的所有信息
    :param cell_idx_or_name: 可以是数字索引（如 0），也可以是细胞名（如 'cell_1'）
    """
    # 统一获取索引
    if isinstance(cell_idx_or_name, int):
        idx = cell_idx_or_name
        cell_name = adata.obs_names[idx]
    else:
        cell_name = cell_idx_or_name
        idx = adata.obs.index.get_loc(cell_name)

    print(f"{'='*20} 细胞全信息报告: {cell_name} {'='*20}")

    # --- 1. 细胞元信息 (Metadata / obs) ---
    print("\n[1. 基础元数据 (obs)]")
    print(adata.obs.iloc[idx].to_dict())

    # --- 2. 降维特征向量 (Embeddings / obsm) ---
    print("\n[2. 降维特征空间 (obsm)]")
    for key in adata.obsm.keys():
        vector = adata.obsm[key][idx]
        # 如果维度太长（如PCA有50维），这里只打印前5个数值演示
        print(f" - {key}: {vector[:5]} ... (总长度: {len(vector)})")

    # --- 3. 基因表达数据 (Expression Matrix / X) ---
    print("\n[3. 基因表达详情 (X)]")
    # 获取该细胞的表达行
    if hasattr(adata.X, "toarray"):
        row = adata.X[idx, :].toarray().flatten()
    else:
        row = adata.X[idx, :].flatten()
    
    # 过滤掉表达量为 0 的基因（为了让打印结果更清晰）
    # 在单细胞中，绝大部分基因都是 0，打印出来没意义
    non_zero_indices = np.where(row > 0)[0]
    expressed_genes = {
        adata.var_names[i]: row[i] 
        for i in non_zero_indices
    }
    
    print(f"该细胞共有 {len(non_zero_indices)} 个基因有表达 (非0值)。")
    # 打印前 10 个有表达的基因作为示例
    sample_genes = dict(list(expressed_genes.items())[:10])
    print(f"部分表达基因示例: {sample_genes}")
    
    print(f"\n{'='*60}")

# 2. 调用：打印第一个细胞（索引为 0）的所有信息
get_cell_full_report(adata, 0)