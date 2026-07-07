# Knowledge Sources

本目录用于公开说明本项目 RAG 知识库的来源、组织方式和扩展方法，保证知识索引具有可复现性与可扩展性。

## 1. 目录约定

推荐的知识库目录结构如下：

```text
knowledge/
├── index/
│   ├── knowledge.faiss
│   └── metadata.json
├── source/
│   ├── README.md
│   ├── sc_knowledge.jsonl
│   ├── sc_concepts.jsonl
│   ├── cell_marker_kb.jsonl
│   └── user/
└── examples/
    └── demo.jsonl
```

其中：

- `knowledge/index/` 保存离线构建出来的检索产物
- `knowledge/source/` 保存可公开追溯的知识源文件
- `knowledge/source/user/` 用于放置用户自行补充的 JSONL
- `knowledge/examples/` 提供最小示例，方便二次扩展

## 2. 当前知识来源

当前仓库中的 RAG 知识主要来自以下几部分：

### 2.1 自定义基础知识

文件：

- `knowledge/source/sc_knowledge.jsonl`

用途：

- 提供常见 `cell_type`、marker、疾病和组织相关的基础说明
- 用于在自然语言问答中补充生物学解释

### 2.2 自定义概念知识

文件：

- `knowledge/source/sc_concepts.jsonl`

用途：

- 提供 `Immune Cell`、`Myeloid Cell`、`Lymphocyte` 等上位概念
- 用于把自然语言里的泛化概念扩展成更具体的候选细胞类型

### 2.3 CellMarker 派生知识

文件：

- `knowledge/source/cell_marker_kb.jsonl`

生成来源：

- 原始输入文件为 `data/kb/all_cell_marker/all_cell_marker.txt`
- 由脚本 `scripts/build_cell_marker_kb.py` 聚合生成

用途：

- 提供大量 cell type 与 marker gene 的关联信息
- 为细胞解释、marker 问答和候选细胞召回提供结构化知识

说明：

- 当前仓库中可明确确认其 `source` 字段为 `all_cell_marker`
- 如果你后续将其替换为 CellMarker 3.0 或其他数据库导出的标准化结果，建议在生成时把真实数据源写入 `source` 和 `metadata`

### 2.4 运行时项目文档

运行时还会把以下 Markdown 文档切分后纳入知识库：

- 项目根目录 `README.md`
- 项目根目录 `数据说明.md`

用途：

- 用于回答项目使用方式、数据要求与部分运行说明相关问题

## 3. 为什么要公开知识来源

这样设计主要出于两个原因：

### 3.1 可复现性

如果仓库里只有：

- `knowledge.faiss`
- `metadata.json`

别人只能知道“有一个索引”，但无法知道：

- 知识来自哪些原始文件
- 是否使用了 CellMarker、概念词表、疾病词表或自定义知识
- 如何重新生成同样的结果

因此需要把知识源文件和来源说明一起开放出来。

### 3.2 可扩展性

如果希望其他人继续扩充知识库，就必须告诉他们：

- JSONL 应该怎么写
- 至少哪些字段是推荐字段
- 修改完知识后应该重新执行什么脚本

## 4. JSONL 最小格式

用户至少可以按下面的最小格式准备一条知识：

```json
{
  "title": "T cell 基础特征",
  "category": "cell_type",
  "retrieval_text": "T cell, CD3D, CD3E, TRBC1, IL7R",
  "content": "T cell 是适应性免疫细胞，常见 marker gene 包括 CD3D、CD3E、TRBC1、IL7R。"
}
```

建议字段包括：

- `doc_id`：文档唯一标识，缺失时系统会自动生成
- `source`：知识来源名称，例如 `manual_kb`、`CellMarker3.0`、`custom_concept`
- `category`：知识类型，例如 `cell_type`、`concept`、`marker_gene`、`disease`
- `title`：标题
- `content`：正文
- `retrieval_text`：用于检索的拼接文本，若缺失系统会自动生成
- `keywords`：关键词列表
- `aliases`：别名列表
- `summary`：摘要
- `related_terms`：相关术语
- `marker_genes`：marker gene 列表
- `disease_related`：疾病关联列表
- `children`：概念的下位项
- `metadata`：其余结构化元信息

## 5. 推荐的概念类格式

如果是概念扩展类知识，推荐使用如下结构：

```json
{
  "doc_id": "concept_immune_cell",
  "source": "custom_concept",
  "category": "concept",
  "title": "Immune Cell",
  "aliases": ["immune cell", "immune cells", "免疫细胞"],
  "keywords": ["immune", "lymphocyte", "myeloid"],
  "summary": "Immune Cell 是一个上位概念。",
  "content": "该概念可展开到 T cell、B cell、NK cell、Macrophage、Monocyte 等候选细胞类型。",
  "children": ["T cell", "B cell", "NK cell", "Macrophage", "Monocyte"],
  "related_terms": ["Myeloid Cell", "Lymphocyte"],
  "metadata": {
    "concept_type": "cell_group"
  }
}
```

## 6. 更新流程

如果你添加或修改了 `knowledge/source/` 或 `knowledge/source/user/` 下的知识文件，推荐按以下顺序更新：

1. 准备或修改 JSONL
2. 执行 `python scripts/build_knowledge_index.py`
3. 确认生成了 `knowledge/index/knowledge.faiss` 和 `knowledge/index/metadata.json`
4. 重启应用，使新的知识索引生效

## 7. 兼容说明

当前代码已兼容旧目录：

- `data/kb/`

如果 `knowledge/source/` 中没有对应文件，系统会继续回退读取旧的 `data/kb/`。

这保证了旧项目结构仍可运行，同时逐步过渡到更适合开源发布的目录布局。
