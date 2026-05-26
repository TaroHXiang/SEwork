# 单细胞相似性检索系统

软件工程小组大作业项目：读取单细胞数据，提取细胞向量，构建 HNSW ANN 索引，按细胞 ID 或向量查询 Top-K 相似细胞，并在 Web 页面展示结果。

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
├── config.py
├── requirements.txt
├── docker-compose.yml
├── 数据说明.md
├── 前端依赖接口清单.md
├── data/
│   ├── sample_cells.csv
│   └── users.db
├── services/
│   ├── auth_service.py
│   ├── data_loader.py
│   └── vector_index.py
├── static/
│   ├── app.js
│   └── styles.css
└── templates/
    └── index.html
```

## 启动方式

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 启动 Qdrant

```bash
docker compose up -d
```

如果本机暂时没有 Docker，系统会自动使用内存模式的 Qdrant 客户端，便于中期答辩演示。内存模式在服务重启后需要重新构建索引。

若要显式连接 Docker 中运行的 Qdrant 服务，可设置环境变量：

```bash
set QDRANT_URL=http://127.0.0.1:6333
```

### 3. 启动 Flask 服务

```bash
python app.py
```

### 4. 打开页面

```text
http://127.0.0.1:5000
```

## 页面说明

系统前端采用单页应用 (SPA) 模式，分为**登录注册页**和**主控台**。

### 1. 登录注册页

- 刚进入系统时，若未携带有效凭证，将展示居中的登录注册卡片。
- 支持注册普通用户或管理员。
- 登录成功后，系统会自动保存 Token 并跳转至主控台。

### 2. 主控台 - 顶部状态区

- 左侧：展示系统名称与当前索引状态徽标。
- 右侧：包含“帮助文档”链接、当前登录用户名、以及“退出登录”按钮。

### 3. 主控台 - 左侧：数据集与索引区

- 输入数据文件路径。
- 点击“检查数据”后展示数据集摘要信息（细胞数、基因数、维度等）。
- 点击“构建索引”后触发向量加载与 HNSW 索引构建。
- 面板底部实时显示状态提示与耗时。

### 4. 主控台 - 右侧：相似细胞查询区

- 支持两种查询方式：
  - 按细胞 ID 查询
  - 按向量查询
- 支持 `cell_type`、`disease`、`AgeGroup` 三类过滤条件。
- 支持自定义 `Top-K` 查询数量。
- 点击“开始查询”后向后端发起检索请求。

### 5. 主控台 - 下方：结果展示区

- 以表格形式展示 Top-K 相似细胞列表。
- 当前展示字段包括：排名、细胞编号、距离、相似度、细胞类型、疾病、年龄组、性别。
- 查询无结果时展示空状态，失败时展示红色错误提示。

## 接口说明

前端联调详细约定见 `前端依赖接口清单.md`。下面列出当前页面直接依赖的主要接口。

### 1. 健康检查

```http
GET /api/health
```

用途：

- 获取服务运行状态
- 判断索引是否已经构建
- 获取当前数据集摘要

返回示例：

```json
{
  "status": "ok",
  "indexed": false,
  "dataset": null
}
```

### 2. 数据集检查

```http
POST /api/dataset/inspect
Content-Type: application/json

{
  "data_path": "liver.h5ad"
}
```

用途：

- 检查数据文件能否正常读取
- 获取细胞数、基因数、向量维度、向量来源等信息

### 3. 构建索引

```http
POST /api/index/build
Content-Type: application/json

{
  "data_path": "liver.h5ad"
}
```

说明：

- `data_path` 可填写 CSV 或 h5ad 文件路径。
- 不传时默认加载示例数据。

返回示例：

```json
{
  "message": "index built",
  "collection": "cell_vectors",
  "cell_count": 1000,
  "gene_count": 2000,
  "vector_dim": 30,
  "embedding_key": "X_pca",
  "build_time_ms": 1234.56
}
```

### 4. 按细胞 ID 查询

```http
POST /api/search/by-id
Content-Type: application/json

{
  "cell_id": "AAACCTGAGCAGGTCA-1_2",
  "top_k": 10,
  "filters": {
    "cell_type": "T cell",
    "disease": "healthy",
    "AgeGroup": "adult"
  }
}
```

返回字段：

- `query`
- `query_time_ms`
- `results`

### 5. 按向量查询

```http
POST /api/search/by-vector
Content-Type: application/json

{
  "vector": [0.12, 0.34, 0.56],
  "top_k": 10,
  "filters": {}
}
```

返回字段：

- `query`
- `query_time_ms`
- `results`

### 6. 用户认证相关

```http
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

用途：

- 注册普通用户或管理员
- 登录并获取 Bearer Token
- 获取当前登录用户信息

### 7. 管理员用户管理

```http
GET /api/admin/users
POST /api/admin/users
PATCH /api/admin/users/<user_id>
DELETE /api/admin/users/<user_id>
```

用途：

- 查看用户列表
- 新增用户
- 修改用户角色或状态
- 删除指定用户

## 前端协作说明

- 前端负责文件：
  - `templates/index.html`
  - `static/app.js`
  - `static/styles.css`
  - `README.md`
- 前端通过 API 与后端协作，不直接依赖 `services/` 内部实现。
- 联调时若接口字段发生变更，应优先同步 `前端依赖接口清单.md`。

## 后续扩展

- 接入真实单细胞数据集，统一细胞 ID、向量列和元数据字段。
- 增加 PCA、归一化、标准化等向量预处理流程。
- 在页面增加数据上传、索引状态、可视化图表和 UMAP 展示。
- 补充单元测试和接口测试。
- 将项目推送到 GitHub，使用分支和 Pull Request 管理协作。
