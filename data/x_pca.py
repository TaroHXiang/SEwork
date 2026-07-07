import scanpy as sc
import numpy as np
import pandas as pd
import os


# ==================== 1. 参数设置 ====================

# h5ad 数据路径
data_path = "data/liver.h5ad"

# 这里填写你要查询的真实细胞 ID
cell_id = "GGGACCTTCTGTCTCG-1_16"

# 输出文件
out_csv = "cell_30d_vector.csv"


# ==================== 2. 检查文件是否存在 ====================

if not os.path.exists(data_path):
    raise FileNotFoundError(f"找不到数据文件: {data_path}")


# ==================== 3. 读取 h5ad 数据 ====================

print("正在读取数据...")
adata = sc.read_h5ad(data_path)
print("读取完成")

print("细胞数:", adata.n_obs)
print("基因数:", adata.n_vars)


# ==================== 4. 检查是否存在 X_pca ====================

print("obsm keys:", list(adata.obsm.keys()))

if "X_pca" not in adata.obsm:
    raise KeyError("该数据集中没有 adata.obsm['X_pca']，无法输出 30 维 PCA 向量")


X_pca = adata.obsm["X_pca"]

print("X_pca shape:", X_pca.shape)


# ==================== 5. 检查维度是否为 30 ====================

if X_pca.shape[1] != 30:
    print(f"警告：当前 X_pca 不是 30 维，而是 {X_pca.shape[1]} 维")


# ==================== 6. 查找指定细胞 ID ====================

if cell_id not in adata.obs_names:
    raise KeyError(f"没有找到该细胞 ID: {cell_id}")

cell_idx = adata.obs_names.get_loc(cell_id)


# ==================== 7. 提取该细胞的 30 维向量 ====================

vector = X_pca[cell_idx, :]

vector = np.asarray(vector).ravel()


# ==================== 8. 打印结果 ====================

print("\n==================== 指定细胞 30 维向量 ====================")
print("细胞 ID:", cell_id)
print("向量维度:", len(vector))

for i, value in enumerate(vector, start=1):
    print(f"dim_{i}: {float(value):.10f}")


# ==================== 9. 保存为 CSV ====================

columns = [f"dim_{i}" for i in range(1, len(vector) + 1)]

df = pd.DataFrame([vector], columns=columns)
df.insert(0, "cell_id", cell_id)

df.to_csv(out_csv, index=False, encoding="utf-8-sig")

print(f"\n已保存到: {out_csv}")