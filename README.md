# 单细胞相似性检索系统

软件工程小组大作业中期框架：读取单细胞数据，提取细胞向量，构建 HNSW ANN 索引，按细胞 ID 或向量查询 Top-K 相似细胞，并在 Web 页面展示结果。

## 技术栈

- 后端：Python + Flask
- 前端：HTML + CSS + JavaScript + Bootstrap
- 数据读取：scanpy / anndata
- 向量处理：numpy / pandas
- ANN 检索：Qdrant，底层使用 HNSW 图索引
- 版本管理：Git + GitHub

## 项目结构

```text
.
├── app.py
├── requirements.txt
├── docker-compose.yml
├── config.py
├── data/
│   └── sample_cells.csv
├── services/
│   ├── data_loader.py
│   └── vector_index.py
├── static/
│   ├── app.js
│   └── styles.css
└── templates/
    └── index.html
```

## 快速启动

1. 创建虚拟环境并安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. 启动 Qdrant：

```bash
docker compose up -d
```

如果暂时没有 Docker，系统会自动使用内存模式的 Qdrant 客户端，便于中期答辩演示。内存模式重启服务后需要重新构建索引。若要连接 Docker 中的 Qdrant 服务，可设置环境变量：

```bash
set QDRANT_URL=http://127.0.0.1:6333
```

3. 启动 Flask：

```bash
python app.py
```

4. 打开页面：

```text
http://127.0.0.1:5000
```

## API

### 构建索引

```http
POST /api/index/build
Content-Type: application/json

{
  "data_path": "data/sample_cells.csv"
}
```

`data_path` 可填写 CSV 或 h5ad 文件路径。不传时默认加载示例数据。

### 按细胞 ID 查询

```http
POST /api/search/by-id
Content-Type: application/json

{
  "cell_id": "cell_001",
  "top_k": 5
}
```

### 按向量查询

```http
POST /api/search/by-vector
Content-Type: application/json

{
  "vector": [0.12, 0.34, 0.56],
  "top_k": 5
}
```

## 后续扩展

- 接入真实单细胞数据集，统一细胞 ID、向量列和元数据字段。
- 增加 PCA、归一化、标准化等向量预处理流程。
- 在页面增加数据上传、索引状态、可视化图表。
- 补充单元测试和接口测试。
- 将项目推送到 GitHub，使用分支和 Pull Request 管理协作。
