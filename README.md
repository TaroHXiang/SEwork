# 单细胞相似性检索系统

系统读取单细胞数据集，提取细胞向量，使用 `FAISS` 构建近似最近邻索引，支持按细胞 ID 或向量进行 Top-K 相似细胞检索，并通过 Web 页面展示数据集、UMAP、检索结果和用户管理功能。

当前架构：

- 主应用：本地运行 `Flask`
- 元数据数据库：`MySQL`，通过 Docker 运行
- 向量索引服务：`FAISS service`，通过 Docker 运行

这意味着主应用不再直接读写本地 `.faiss/` 目录，而是像之前访问 Qdrant 一样，通过 HTTP 调用容器内的 FAISS 服务。

## 技术栈

- 后端：Python + Flask
- 前端：HTML + CSS + JavaScript
- 用户与历史索引元数据：MySQL
- 向量索引：FAISS（独立 Docker 服务）
- 数据读取：scanpy / anndata / pandas
- 向量处理：numpy

## 项目结构

```text
.
├── app.py
├── faiss_service.py
├── Dockerfile.faiss
├── config.py
├── requirements.txt
├── docker-compose.yml
├── data/
├── services/
│   ├── auth_service.py
│   ├── data_loader.py
│   ├── faiss_engine.py
│   └── vector_index.py
├── static/
└── templates/
```

## 启动方式

### 1. 启动 Docker 服务

```powershell
docker compose up -d --build
```

会启动：

- `ann-mysql`
- `ann-faiss`

### 2. 配置 `.env`

示例：

```env
DATABASE_URL=mysql+pymysql://sework:sework123@127.0.0.1:3307/sework
FAISS_SERVICE_URL=http://127.0.0.1:8000
SECRET_KEY=change-this-secret
```

说明：

- `DATABASE_URL`：主应用连接 MySQL
- `FAISS_SERVICE_URL`：主应用连接 Docker 中的 FAISS 服务
- `SECRET_KEY`：登录 token 签名密钥

### 3. 安装主应用依赖

```powershell
pip install -r requirements.txt
```

### 4. 启动主应用

```powershell
python app.py
```

浏览器访问：

```text
http://127.0.0.1:5000
```

## Docker 中的 FAISS 服务

`docker-compose.yml` 中新增了 `faiss` 服务：

- 监听端口：`8000`
- 持久化目录：Docker volume `faiss_storage`
- 数据集根目录：容器内 `/workspace`

因此推荐把待建索引的数据文件放在项目目录内，例如：

```text
data/sample_cells.csv
data/liver.h5ad
```

如果使用项目目录之外的数据文件，需要额外给 `faiss` 服务添加 bind mount。

## 支持的索引类型

- `hnsw`
- `ivf`
- `pq`

支持的距离度量：

- `cosine`
- `ip`
- `l2`
- `pearson`

## 前端构建索引

页面已支持在构建时选择：

- `Index Type`
- `Distance Metric`
- `IVF NList`
- `IVF NProbe`
- `PQ Compression`

## 典型构建请求

```json
{
  "data_path": "data/liver.h5ad",
  "index_name": "liver_ivf_v1",
  "index_type": "ivf",
  "distance_metric": "cosine",
  "quantization_config": {
    "nlist": 128
  },
  "search_params": {
    "nprobe": 8
  },
  "async": true,
  "activate": true
}
```

## 说明

- 历史索引元数据仍保存在 MySQL
- `collection_name` 字段继续保留，便于兼容既有业务逻辑
- 向量索引文件现在保存在 Docker volume 中，而不是主应用本地目录
- 如果 `ann-faiss` 未启动，主应用会在索引相关接口上报连接错误
