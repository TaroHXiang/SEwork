# 单细胞相似性检索系统

软件工程小组大作业项目。系统读取单细胞数据集，提取细胞向量，使用 Qdrant/HNSW 构建近似最近邻索引，支持按细胞 ID 或向量进行 Top-K 相似细胞检索，并通过 Web 页面展示数据集、UMAP、检索结果和用户管理功能。

## 技术栈

- 后端：Python + Flask
- 前端：HTML + CSS + JavaScript
- 用户与历史索引元数据：MySQL
- 向量数据库：Qdrant，底层使用 HNSW 索引
- 数据读取：scanpy / anndata / pandas
- 向量处理：numpy
- 部署辅助：Docker Desktop + Docker Compose

## 项目结构

```text
.
├── app.py
├── config.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── data/
│   └── sample_cells.csv
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

## 环境准备

### 1. 安装 Docker Desktop

Windows 上建议安装 Docker Desktop：

```text
https://www.docker.com/products/docker-desktop/
```

下载并安装 **Docker Desktop for Windows**。安装完成后启动 Docker Desktop，等待界面显示 Docker Engine 正在运行。

在 PowerShell 中检查：

```powershell
docker --version
docker compose version
```

能看到版本号说明 Docker 命令可用。

### 2. 启动 MySQL 和 Qdrant

进入项目目录：

```powershell
cd D:\softwareEgeneering\SEwork
```

启动服务：

```powershell
docker compose up -d
```

查看容器状态：

```powershell
docker ps
```

正常情况下应该看到：

```text
ann-mysql
ann-qdrant
```

### 3. 配置 .env

创建 `.env` 文件：

```env
DATABASE_URL=mysql+pymysql://sework:sework123@127.0.0.1:3306/sework
QDRANT_URL=http://127.0.0.1:6333
SECRET_KEY=change-this-secret
```

说明：

- `DATABASE_URL`：Flask 连接 MySQL 的地址，用于保存用户、管理员和历史索引记录。
- `QDRANT_URL`：Flask 连接 Qdrant 的地址，用于保存和查询向量索引。
- `SECRET_KEY`：Token 签名密钥，正式部署时应改成更复杂的随机字符串。

### 4. 安装 Python 依赖

```powershell
pip install -r requirements.txt
```

### 5. 启动 Flask

```powershell
python app.py
```

浏览器打开：

```text
http://127.0.0.1:5000
```

首次启动时，后端会自动在 MySQL 中创建：

```text
users
user_indexes
```

## 数据库查看

### 查看 MySQL 表

进入 MySQL：

```powershell
docker exec -it ann-mysql mysql -usework -psework123 sework
```

查看表：

```sql
SHOW TABLES;
```

查看用户：

```sql
SELECT id, username, role, is_active, created_at FROM users;
```

查看历史索引：

```sql
SELECT id, user_id, index_name, collection_name, data_path, is_active, status FROM user_indexes;
```

退出：

```sql
exit;
```

也可以直接执行：

```powershell
docker exec -it ann-mysql mysql -usework -psework123 sework -e "SHOW TABLES;"
```

### 查看 Qdrant

浏览器打开：

```text
http://127.0.0.1:6333/dashboard
```

或使用接口：

```powershell
curl http://127.0.0.1:6333/collections
```

构建索引成功后，Qdrant 中会出现对应 collection。

## 使用流程

1. 打开 `http://127.0.0.1:5000`。
2. 注册用户，可选择普通用户或管理员。
3. 登录系统。
4. 在数据集入口输入：

```text
data/sample_cells.csv
```

5. 进入核心页面后点击“检查数据”。
6. 点击“构建索引”。
7. 索引构建完成后，可以按细胞 ID 或向量进行 Top-K 检索。
8. 管理员账号可以进行用户管理。
9. 已构建的索引会记录到 MySQL 的 `user_indexes` 表中，下次登录可从历史索引进入，不必重复构建。

## 数据说明

当前项目自带样例数据：

```text
data/sample_cells.csv
```

如果使用真实 `.h5ad` 数据，可以放到：

```text
data/liver.h5ad
```

页面中填写：

```text
data/liver.h5ad
```

`.h5ad` 数据要求：

- 优先使用 `adata.obsm["X_pca"]` 作为检索向量。
- 可使用 `adata.obsm["X_umap"]` 作为 UMAP 可视化坐标。
- 常用元数据字段包括 `cell_type`、`disease`、`AgeGroup`、`sex` 等。

## 主要接口

### 认证接口

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

登录成功后，前端使用 Bearer Token 调用需要认证的接口。

### 管理员接口

```http
GET    /api/admin/users
POST   /api/admin/users
PATCH  /api/admin/users/<user_id>
DELETE /api/admin/users/<user_id>
```

用于查看、新增、修改和删除用户。

### 数据集接口

```http
POST /api/dataset/inspect
GET  /api/dataset/umap-preview
GET  /api/dataset/metadata-options
```

用于检查数据集、读取 UMAP 预览和获取元数据筛选项。

### 索引接口

```http
POST /api/index/build
GET  /api/index/build/jobs/<job_id>
GET  /api/indexes
GET  /api/indexes/active
POST /api/indexes/<index_id>/activate
```

用于构建索引、查看构建进度、查看历史索引和激活历史索引。

### 检索接口

```http
POST /api/search/by-id
POST /api/search/by-vector
POST /api/search/evaluate/by-id
POST /api/search/evaluate/by-vector
```

用于执行 Top-K 相似细胞检索和性能评估。

### data file not found

如果页面提示：

```text
data file not found
```

说明页面填写的数据路径不存在。可以先使用：

```text
data/sample_cells.csv
```

如果使用真实数据，需要把文件放到项目的 `data/` 目录下。

## 存储说明

当前系统使用：

```text
MySQL：保存用户、管理员、历史索引元数据
Qdrant：保存向量索引和 HNSW 检索数据
data/：保存 CSV 或 h5ad 数据集文件
```

相比早期本地 SQLite 和本地 Qdrant 目录，MySQL + Qdrant 服务更接近真实部署环境，支持更好的数据管理、服务解耦和后续扩展。
