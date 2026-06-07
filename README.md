# 单细胞相似性检索系统

面向单细胞数据分析场景的 Web 系统。用户可以上传或指定本地单细胞数据文件，检查数据集内容，构建 FAISS 向量索引，并按细胞 ID 或向量执行 Top-K 相似检索；系统同时提供 UMAP 可视化、历史索引管理、管理员后台和 AI 索引建议能力。

本 README 面向实际使用本项目的用户，重点说明如何部署、登录、构建索引、执行检索以及处理常见问题。

## 1. 项目概览

### 1.1 核心能力

- 支持读取 `.csv` 和 `.h5ad` 两类单细胞数据文件
- 支持在构建前检查数据集规模、向量维度、元数据字段
- 支持生成数据集 UMAP 预览、统计信息和元数据筛选项
- 支持构建 `HNSW`、`IVF`、`PQ` 三类 FAISS 索引
- 支持使用 `cosine`、`ip`、`l2`、`pearson` 距离度量
- 支持按细胞 ID 检索相似细胞
- 支持按自定义向量检索相似细胞
- 支持对 ANN 检索与精确检索结果进行评估
- 支持用户管理自己的历史索引、激活索引、删除索引
- 支持管理员查看用户、数据集、索引、构建任务和审计日志
- 支持 AI 助手结合当前数据集给出索引类型与参数建议

### 1.2 系统架构

项目由 3 个部分组成：

- Flask 主应用：负责页面渲染、用户认证、业务接口编排
- MySQL：负责保存用户、数据集、历史索引、构建任务和审计日志
- 独立 FAISS 服务：负责向量索引构建、相似检索和可视化数据读取

默认情况下：

- Web 应用地址：`http://127.0.0.1:5000`
- FAISS 服务地址：`http://127.0.0.1:8000`
- MySQL 映射端口：`3307`

## 2. 适用对象

本项目适合以下用户：

- 需要对单细胞数据做相似细胞检索的普通使用者
- 需要比较不同近似索引方案效果的课程项目或实验人员
- 需要统一管理用户、数据集和索引历史的管理员

系统内置 3 种角色：

- `user`：普通用户，可注册、登录、检查数据、构建索引、执行检索
- `admin`：管理员，可查看和管理普通用户相关资源
- `super_admin`：超级管理员，可进一步管理管理员账号

说明：

- 普通用户支持自助注册
- 管理员账号不开放网页自助注册，需要通过脚本预置

## 3. 功能清单

### 3.1 普通用户功能

- 注册、登录、退出登录
- 查看“我的历史索引”
- 输入数据路径并检查数据集
- 查看数据集摘要、元数据字段、统计信息、UMAP 预览
- 选择索引类型、距离度量和构建参数
- 同步或异步构建索引
- 查看构建进度
- 激活历史索引
- 按细胞 ID 检索
- 按向量检索
- 使用元数据条件过滤结果
- 查看检索结果和 UMAP 可视化
- 执行 ANN vs Exact 评估
- 使用 AI 助手咨询索引和参数选择

### 3.2 管理员功能

- 查看系统总览
- 查看用户列表与用户详情
- 创建用户
- 修改用户角色、状态、显示名、邮箱
- 重置用户密码
- 删除用户
- 查看数据集列表并删除数据集
- 查看索引列表、强制激活索引、删除索引
- 查看构建任务历史
- 查看审计日志

## 4. 环境准备

### 4.1 必备软件

在启动项目之前，请确保本机已安装：

- Python
- `pip`
- Docker
- Docker Compose

### 4.2 Python 依赖

项目当前依赖包括：

- `Flask`
- `faiss-cpu`
- `numpy`
- `pandas`
- `scanpy`
- `anndata`
- `python-dotenv`
- `PyMySQL`
- `cryptography`

安装命令：

```powershell
pip install -r requirements.txt
```

## 5. 快速开始

### 5.1 克隆或进入项目目录

```powershell
cd d:\HuaweiMoveData\Users\20105\Documents\xinan\dasanxia\软件工程\大作业\homework_final\SEwork
```

### 5.2 启动 Docker 依赖服务

```powershell
docker compose up -d --build
```

该命令会启动：

- `ann-mysql`
- `ann-faiss`

### 5.3 创建 `.env` 文件

在项目根目录创建 `.env`，可参考下面的配置：

```env
DATABASE_URL=mysql+pymysql://sework:qwerxjl159357@127.0.0.1:3307/sework
FAISS_SERVICE_URL=http://127.0.0.1:8000
SECRET_KEY=change-this-secret
ZHIPU_API_KEY=
ZHIPU_MODEL=glm-4-flash-250414
ZHIPU_API_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
```

关键变量说明：

- `DATABASE_URL`：Flask 主应用连接 MySQL 的地址
- `FAISS_SERVICE_URL`：Flask 主应用连接 FAISS 服务的地址
- `SECRET_KEY`：登录令牌签名密钥，生产或答辩环境中请务必修改
- `ZHIPU_API_KEY`：AI 助手能力所需，可为空；为空时 AI 接口不可用
- `ZHIPU_MODEL`：AI 模型名称
- `ZHIPU_API_URL`：AI 服务接口地址

### 5.4 安装主应用依赖

```powershell
pip install -r requirements.txt
```

### 5.5 启动主应用

```powershell
python app.py
```

启动成功后，在浏览器访问：

```text
http://127.0.0.1:5000
```

## 6. 数据准备说明

### 6.1 支持的数据格式

系统当前支持：

- `.csv`
- `.h5ad`

### 6.2 CSV 数据要求

CSV 数据需满足以下约束：

- 必须包含 `cell_id` 列
- 所有向量列必须以 `v` 开头，例如 `v1`、`v2`、`v3`
- 所有向量列维度必须一致，且内容应为数值
- 其余列会被视为元数据字段

示例字段结构：

```text
cell_id,v1,v2,v3,cell_type,disease,AgeGroup,sex,tissue,donor_id
```

### 6.3 H5AD 数据要求

`.h5ad` 数据应满足以下约束：

- 细胞 ID 来自 `obs_names`
- 向量优先读取 `obsm["X_pca"]`
- 若不存在 `X_pca`，则退回使用 `X`
- 可选元数据通常来自 `obs`

常见可用元数据字段包括：

- `cell_type`
- `disease`
- `AgeGroup`
- `sex`
- `tissue`
- `donor_id`

### 6.4 数据文件放置建议

推荐将待处理数据文件放在项目目录内，例如：

```text
data/sample_cells.csv
data/liver.h5ad
```

原因：

- Docker 中的 FAISS 服务默认以只读方式挂载整个项目目录到容器内 `/workspace`
- 项目目录内的数据文件可被主应用和 FAISS 服务同时访问

如果数据文件位于项目目录之外，需要额外为 `faiss` 服务配置对应的挂载路径，否则索引构建可能失败。

## 7. 首次使用流程

### 7.1 注册与登录

1. 打开首页
2. 使用用户名和密码注册普通用户
3. 使用注册成功的账号登录系统

说明：

- 网页端只允许注册普通用户
- 管理员账号必须由项目维护者预置

### 7.2 进入历史索引页

登录后，你会看到：

- 我的历史索引
- 录入新数据集入口
- 退出登录按钮
- 管理员用户额外可见 Admin Dashboard

### 7.3 录入新数据集

进入主工作页面后，通常先执行以下操作：

1. 输入 `data_path`
2. 点击检查数据集
3. 查看数据集摘要、元数据字段、统计信息和 UMAP 预览
4. 选择索引类型与参数
5. 构建索引

如果未填写数据路径，系统默认会尝试使用：

```text
data/sample_cells.csv
```

## 8. 索引构建指南

### 8.1 可选索引类型

系统支持以下索引类型：

- `hnsw`
- `ivf`
- `pq`

### 8.2 可选距离度量

系统支持以下距离度量：

- `cosine`
- `ip`
- `l2`
- `pearson`

### 8.3 构建参数

前端页面支持的参数包括：

- `Index Type`
- `Distance Metric`
- `IVF NList`
- `IVF NProbe`
- `PQ Compression`

此外，后端还支持传入：

- `hnsw_params`
- `search_params`
- `quantization_config`

### 8.4 同步与异步构建

系统支持两种构建方式：

- 同步构建：请求返回时即完成构建
- 异步构建：后台执行构建，前端可轮询任务进度

异步构建适用于：

- 数据规模较大
- 构建耗时较长
- 希望前端持续展示进度和阶段信息

### 8.5 可复用索引

如果你对同一数据集使用相同构建参数重复发起构建，系统会尝试复用已有索引，避免重复计算。

## 9. 检索与评估指南

### 9.1 按细胞 ID 检索

适用场景：

- 已知一个细胞 ID，希望找到最相似的细胞

能力特点：

- 可设置 `top_k`
- 可使用元数据过滤条件
- 可选择当前激活索引或指定索引

### 9.2 按向量检索

适用场景：

- 你已拥有一个向量表示，希望找到最相似的细胞

能力特点：

- 支持自定义向量输入
- 支持 `top_k`
- 支持元数据过滤

### 9.3 ANN vs Exact 评估

系统支持对近似检索结果进行评估，用于比较：

- `precision_at_k`
- `recall_at_k`
- `overlap_count`
- `ann_query_time_ms`
- `exact_query_time_ms`

这对课程展示、实验分析或参数调优非常有帮助。

### 9.4 UMAP 可视化

系统支持展示：

- 数据集 UMAP 散点图
- 细胞详情
- 结果表格
- 可视化相关统计信息

UMAP 查询支持部分元数据过滤条件，例如：

- `cell_type`
- `disease`
- `AgeGroup`
- `sex`
- `tissue`
- `donor_id`

## 10. AI 助手说明

系统提供 AI 助手，用于回答：

- HNSW、IVF、PQ 的区别
- 距离度量如何选择
- 参数如何设置
- 当前数据集适合什么构建方案

使用前提：

- 在 `.env` 中配置 `ZHIPU_API_KEY`

未配置时的表现：

- AI 接口会返回错误
- 不影响普通检索、索引构建和管理功能

说明：

- AI 助手回答内容会基于当前数据集摘要
- 默认以中文输出

## 11. 管理员初始化

### 11.1 什么时候需要执行

如果你需要使用管理员后台，请先初始化管理员账号。

### 11.2 执行方式

在项目根目录执行：

```powershell
python scripts/bootstrap_admins.py
```

脚本默认会处理以下管理员用户名：

- `admin01`
- `admin02`
- `admin03`
- `admin04`

默认行为：

- 第一个管理员默认为 `super_admin`
- 其余账号默认为 `admin`
- 若账号不存在则创建
- 若账号已存在则更新角色并启用

### 11.3 可选环境变量

脚本支持以下可选配置：

- `BOOTSTRAP_ADMIN_USERS`：用逗号分隔的管理员用户名列表
- `BOOTSTRAP_SUPER_ADMIN`：指定哪个用户名为超级管理员
- `BOOTSTRAP_ADMIN_PASSWORDS_JSON`：为部分账号显式指定密码

如果没有显式提供密码，脚本会自动生成随机密码并输出到终端，请妥善保存。

## 12. 主要页面说明

### 12.1 登录注册页

用于：

- 普通用户注册
- 已有用户登录

### 12.2 历史索引页

用于：

- 查看当前用户已有索引
- 激活已有索引
- 删除历史索引
- 进入新数据集处理流程

### 12.3 主工作页

用于：

- 填写数据路径
- 检查数据集
- 查看预览与统计
- 选择索引参数
- 构建索引
- 执行检索
- 查看可视化结果
- 使用 AI 助手

### 12.4 管理员工作台

管理员可在该区域执行：

- 用户管理
- 数据集管理
- 索引管理
- 构建任务查看
- 审计日志查看

## 13. 用户常用接口

本项目主要面向网页使用，但如果你需要联调接口，可参考以下入口。

### 13.1 认证接口

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### 13.2 数据集接口

- `POST /api/dataset/inspect`
- `GET /api/dataset/umap-preview`
- `GET /api/dataset/umap-stats`
- `GET /api/dataset/metadata-options`

### 13.3 索引接口

- `POST /api/index/build`
- `GET /api/index/build/jobs/<job_id>`
- `GET /api/index/build/jobs/latest-running`
- `GET /api/indexes`
- `GET /api/indexes/active`
- `POST /api/indexes/<index_id>/activate`
- `DELETE /api/indexes/<index_id>`
- `POST /api/index/import`

### 13.4 检索接口

- `POST /api/search/by-id`
- `POST /api/search/by-vector`
- `POST /api/search/evaluate/by-id`
- `POST /api/search/evaluate/by-vector`
- `GET /api/visualization/umap`

### 13.5 AI 接口

- `POST /api/ai/chat`
- `POST /api/ai/index-advice`

### 13.6 管理员接口

- `GET /api/admin/overview`
- `GET /api/admin/users`
- `POST /api/admin/users`
- `PATCH /api/admin/users/<user_id>`
- `POST /api/admin/users/<user_id>/reset-password`
- `DELETE /api/admin/users/<user_id>`
- `GET /api/admin/datasets`
- `DELETE /api/admin/datasets/<dataset_id>`
- `GET /api/admin/indexes`
- `POST /api/admin/indexes/<index_id>/activate`
- `DELETE /api/admin/indexes/<index_id>`
- `GET /api/admin/build-jobs`
- `GET /api/admin/audit-logs`

## 14. 目录结构

```text
SEwork/
├── app.py                       # Flask 主应用入口
├── faiss_service.py             # 独立 FAISS HTTP 服务
├── config.py                    # 环境变量与项目配置
├── docker-compose.yml           # MySQL 与 FAISS 容器编排
├── Dockerfile.faiss             # FAISS 服务镜像构建文件
├── requirements.txt             # Python 依赖
├── data/                        # 示例数据与数据说明
├── scripts/
│   └── bootstrap_admins.py      # 管理员初始化脚本
├── services/
│   ├── auth_service.py          # 用户认证与 MySQL 存储
│   ├── admin_service.py         # 管理后台数据访问
│   ├── ai_advisor.py            # AI 助手调用逻辑
│   ├── data_loader.py           # 数据读取、预览、统计
│   ├── faiss_engine.py          # FAISS 引擎封装
│   └── vector_index.py          # 主应用到 FAISS 服务的调用封装
├── static/                      # 前端脚本与样式
└── templates/
    └── index.html               # 主页面模板
```

## 15. 常见问题

### 15.1 页面可以打开，但构建索引时报错

优先检查：

- `ann-faiss` 容器是否正常运行
- `.env` 中的 `FAISS_SERVICE_URL` 是否正确
- 数据文件是否位于 FAISS 服务可访问的目录中

### 15.2 登录时报数据库连接错误

优先检查：

- `ann-mysql` 是否正常启动
- `.env` 中的 `DATABASE_URL` 是否正确
- MySQL 映射端口是否与 `docker-compose.yml` 一致

### 15.3 AI 助手不可用

优先检查：

- 是否配置了 `ZHIPU_API_KEY`
- 当前网络是否能访问智谱 AI 接口

### 15.4 提示找不到数据文件

优先检查：

- `data_path` 是否填写为正确的本机路径
- 文件是否真实存在
- 文件后缀是否为 `.csv` 或 `.h5ad`
- 若文件在项目目录外，FAISS 容器是否增加了对应挂载

### 15.5 无法注册管理员账号

这是预期行为。

原因：

- 网页自助注册仅开放给普通用户
- 管理员账号需要通过 `python scripts/bootstrap_admins.py` 初始化

## 16. 使用建议

- 首次体验建议先使用 `data/sample_cells.csv`
- 构建大数据集时建议使用异步模式
- 对同一数据集比较不同索引类型时，记录 `index_type`、距离度量和检索评估指标
- 演示管理员功能前，先执行管理员初始化脚本
- 对外展示前，先修改 `.env` 中的 `SECRET_KEY`

## 17. 已知运行前提

- 主应用依赖 MySQL，没有 `DATABASE_URL` 时无法启动用户体系
- 索引相关功能依赖独立 FAISS 服务，未启动时检索与索引接口会报连接错误
- AI 问答依赖智谱接口配置，未配置时仅 AI 相关功能不可用

## 18. 许可证与说明

仓库中当前未看到明确的许可证文件。

如果你准备将本项目用于课程提交之外的分发、复用或公开发布，建议项目维护者补充明确的许可证声明。
