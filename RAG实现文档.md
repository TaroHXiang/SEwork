# RAG 实现文档

## 1. 文档目的

本文档面向项目开发者，说明本项目中 RAG 能力的实现边界、核心模块、调用链路、知识库组织方式、运行依赖与可扩展点。

这里的 RAG 不是单纯的知识问答，而是一个面向单细胞分析场景的混合检索系统，整体链路由以下部分组成：

- 自然语言查询解析
- 概念知识解析与扩展
- 本地知识库混合检索
- 数据集候选细胞召回与重排
- 证据融合
- LLM 或规则化回答生成

## 2. 设计目标

当前 RAG 设计主要解决以下问题：

- 用户不一定知道精确的 `cell_type`、`marker`、`disease` 或 `tissue` 字段值，系统需要先理解自然语言问题
- 单靠知识库命中无法直接代表当前数据集中的证据，因此需要再回到当前数据集或活动索引中检索候选细胞
- 单靠候选细胞结果又不足以解释“为什么命中”，因此需要知识库提供生物学解释、概念扩展和分析提示
- AI 输出不能只给结论，还要尽量区分“数据集中的直接证据”和“知识库中的辅助知识”

因此，本项目采用了“知识检索 + 数据召回 + 证据融合 + 回答生成”的组合式 RAG，而不是只让大模型直接读知识库。

## 3. 系统定位

RAG 相关能力主要服务于接口 `POST /api/ai/cell-query`。

该接口与 `POST /api/ai/chat`、`POST /api/ai/index-advice` 的定位不同：

- `/api/ai/chat` 和 `/api/ai/index-advice` 更偏向索引类型、参数配置、构建策略建议
- `/api/ai/cell-query` 才是完整的细胞分析 RAG 主链路，会结合知识库、当前数据集和候选细胞结果返回解释性答案

## 4. 整体架构

RAG 主链路可以概括为：

1. 前端提交自然语言问题与当前数据集上下文
2. 后端解析问题意图、筛选条件和概念信息
3. 知识库执行关键词检索和向量检索的混合召回
4. 系统把知识命中转成 `cell_type`、`disease`、`tissue`、`marker` 等 hint
5. 系统在当前数据集或活动索引中召回候选细胞并重排
6. 系统将知识证据、数据证据和元数据证据融合成结构化上下文
7. 若配置了 LLM，则调用大模型生成回答；否则返回规则化回答

对应的主干调用关系如下：

```text
app.py
  -> analyze_cell_query()
     -> parse_nl_query()
     -> resolve_concepts()
     -> hybrid_search()
     -> search_cells()
     -> fuse_evidence()
     -> request_cell_analysis_chat() / build_rule_based_answer()
```

## 5. 核心模块

### 5.1 接口编排层

文件：

- `app.py`

职责：

- 暴露 `POST /api/ai/cell-query`
- 读取 `data_path`、`user_question`、`dataset_info`、`index_id`、`current_results`、`selected_cell_id`、`query_context`
- 在必要时先检查数据集并构造 `dataset_context`
- 调用 `analyze_cell_query()` 完成完整分析链路
- 将结果整理为前端可消费的结构化响应

### 5.2 RAG 总控层

文件：

- `services/cell_analysis_agent.py`

职责：

- 作为 RAG 主控制器串联所有子模块
- 先调用 `parse_nl_query()` 解析用户问题
- 再调用 `hybrid_search()` 做知识召回
- 基于知识结果提取 hint
- 调用 `search_cells()` 在当前数据集或活动索引中召回候选细胞
- 调用证据融合模块生成统一上下文
- 根据是否存在 `ZHIPU_API_KEY` 决定走 LLM 或规则回答

这个模块的价值在于把“自然语言理解、知识检索、数据检索、回答生成”从接口层剥离出来，使接口逻辑保持薄而稳定。

### 5.3 查询解析层

文件：

- `services/query_parser.py`

职责：

- 从自然语言问题中抽取 `top_k`
- 识别是否是索引参数相关问题
- 识别 `cell_type`、`disease`、`tissue`、`pathway`
- 结合 metadata options 进行字段值匹配
- 决定本次请求是否需要搜知识库、是否需要搜细胞
- 调用概念解析模块，对上位概念进行扩展

这一层的目标不是构建通用 NLU，而是围绕当前业务做轻量、可控、可解释的意图识别。

### 5.4 概念解析层

文件：

- `services/concept_search.py`

职责：

- 从知识库中筛出 `category == "concept"` 的文档
- 先做别名、标题的精确匹配
- 再调用 `hybrid_search()` 对概念类文档做语义召回
- 将命中的概念扩展为 `children`、`related_terms` 等结构

这一层用于把用户的上位概念问题转成更适合下游检索的具体线索，例如把“免疫细胞”展开成若干更具体的候选子类。

### 5.5 知识检索层

文件：

- `services/rag_store.py`
- `scripts/build_knowledge_index.py`

职责：

- 装载默认知识库、用户补充知识库和运行时文档
- 维护知识文档的数据结构
- 提供关键词检索、向量检索、混合检索
- 负责离线构建本地 FAISS 知识索引

RAG 知识库的默认来源包括（按加载优先级）：

- `knowledge/source/sc_knowledge.jsonl`
- `knowledge/source/sc_concepts.jsonl`
- `knowledge/source/cell_marker_kb_filtered.jsonl`（精简版，36,401 条，丢弃冗余 marker 条目）
- `knowledge/source/cell_marker_kb.jsonl`（全量版兜底，123,170 条，CPU 推理约 24 小时）

其中 `cell_marker_kb_filtered.jsonl` 由 `python scripts/filter_cell_marker_kb.py --aggressive` 生成，原始数据源为 `all_cell_marker.txt`（CellMarker 3.0）。运行 `build_knowledge_index.py` 时系统会自动优先读取 filtered 版本。

同时，以下运行时文档也会被纳入知识源：

- `README.md`
- `数据说明.md`

这意味着项目说明文档本身也会参与知识检索，能帮助 AI 回答运行方式、数据要求和项目使用相关问题。

### 5.6 细胞召回层

文件：

- `services/cell_search_engine.py`

职责：

- 接收查询解析结果和知识命中结果
- 从知识命中中抽取 `cell_type`、`disease`、`tissue`、`marker_genes` 等 hint
- 优先基于当前活动索引的可视化点做候选召回
- 若当前没有可用索引，则退化为基于数据预览点的候选检索
- 结合 metadata 和关键词进行重排

因此，知识库并不直接产生最终答案，而是作为“提示器”和“解释器”，最终仍要回到当前数据集寻找可落地的候选细胞证据。

### 5.7 证据融合层

文件：

- `services/evidence_fusion.py`

职责：

- 从知识命中中提取领域术语和元数据线索
- 组织 `knowledge_evidence`
- 组织 `dataset_evidence`
- 组织 `metadata_evidence`
- 生成 `llm_context`
- 在未配置大模型时生成规则化回答

这一层是整个实现中非常关键的一层，它保证了后续回答不是直接把原始命中列表拼给模型，而是先整理成更稳定、更可控的结构化证据。

### 5.8 LLM 回答层

文件：

- `services/ai_advisor.py`

职责：

- 构造数据集摘要 `dataset_context`
- 构造细胞分析专用 prompt
- 在有 `ZHIPU_API_KEY` 时调用智谱接口
- 在系统提示中要求模型使用中文，并区分数据证据与知识证据

若未配置 `ZHIPU_API_KEY`，系统不会中断整个 RAG 链路，而是回退到规则化回答。

## 6. 知识库组织方式

### 6.1 知识文档来源

知识源通过 `knowledge_source_paths()` 汇总，主要分为三类：

- 默认 JSONL 知识文件
- 用户补充 JSONL 知识文件
- 运行时 Markdown 文档

用户补充知识支持两种方式：

- 将 JSONL 文件放到 `knowledge/source/user`
- 通过环境变量 `SEWORK_USER_KB_PATHS` 指向额外文件或目录

为了更适合开源发布，当前项目推荐使用如下目录结构：

```text
knowledge/
├── index/
│   ├── knowledge.faiss           # FAISS 离线索引产物
│   └── metadata.json             # 索引元数据与文档内容
├── source/
│   ├── README.md                # 知识来源、可复现性说明
│   ├── sc_knowledge.jsonl        # 基础知识条目（手动维护）
│   ├── sc_concepts.jsonl         # 概念层级、别名与上下位关系
│   ├── cell_marker_kb_filtered.jsonl  # 精简版 CellMarker 知识（推荐）
│   ├── cell_marker_kb.jsonl     # 全量版 CellMarker 知识（CPU 推理约 24 小时）
│   └── user/                   # 用户自定义扩展知识
└── examples/
    └── demo.jsonl              # JSONL 格式示例，供二次扩展参考
```

设计原因有两点：

- 可复现性：不仅公开索引产物，还公开知识源文件和来源说明，便于别人理解 `knowledge.faiss` 的来源
- 可扩展性：通过示例 JSONL 和目录约定，降低二次扩充知识库的成本

**精简版 vs 全量版**：全量 `cell_marker_kb.jsonl` 包含 123,170 条记录（cell_type + marker_gene 各一条），CPU 推理构建索引约需 24 小时。精简版 `cell_marker_kb_filtered.jsonl` 只保留 36,401 条 cell_type 条目，CPU 推理约 1.5~2 小时。推荐在 CPU 环境下使用精简版，或通过 `scripts/filter_cell_marker_kb.py` 按需生成。

兼容说明：

- 如果 `knowledge/source/` 中不存在对应默认文件，系统会回退读取旧的 `data/kb/`

### 6.2 知识文档结构

知识文档在运行时会被统一整理为内部 `KnowledgeDocument` 结构，主要包含以下信息：

- `doc_id`
- `source`
- `category`
- `title`
- `content`
- `keywords`
- `metadata`
- `aliases`
- `question_examples`
- `summary`
- `related_terms`
- `marker_genes`
- `disease_related`
- `children`
- `retrieval_text`

其中 `retrieval_text` 是向量化与检索时最关键的文本字段。

### 6.3 离线知识索引

离线知识索引通过脚本 `scripts/build_knowledge_index.py` 生成。

脚本流程如下：

1. 调用 `load_knowledge_documents()` 加载所有知识文档
2. 取出每条文档的 `search_text`
3. 使用 `SentenceTransformer` 生成 embedding
4. 对向量做归一化
5. 使用 `faiss.IndexFlatIP` 构建索引
6. 输出 `knowledge.faiss`
7. 输出 `metadata.json`

默认 embedding 模型为：

- `BAAI/bge-small-zh-v1.5`

默认知识索引目录为：

- `knowledge/index`

可通过环境变量 `SEWORK_KNOWLEDGE_INDEX_DIR` 修改输出目录。

**命令行参数说明：**

```powershell
# 推荐用法（CPU 环境，batch_size=256）
python scripts/build_knowledge_index.py --batch-size 256

# 仅诊断（查看文档数、设备、文本长度，不实际构建）
python scripts/build_knowledge_index.py --diagnose-only

# 完整参数
python scripts/build_knowledge_index.py --batch-size 256 --output-dir knowledge/index --model BAAI/bge-small-zh-v1.5
```

**性能说明：**

- 12.3 万条全量数据 × CPU × batch_size 未显式设置：约 11 小时只跑完约 2231 条
- `bge-small-zh-v1.5` 必须显式传 `--batch-size`，否则 SentenceTransformer 默认极小批次
- CPU 环境下推荐 `batch_size=256`，36,401 条精简数据约 1.5~2 小时可完成
- GPU 环境可增大到 `batch_size=512` 或更高，大幅缩短时间

## 7. 运行时检索策略

### 7.1 为什么采用混合检索

单细胞分析问题中，用户的问题经常同时包含：

- 中文自然语言描述
- 专有名词
- marker gene
- 疾病名
- 组织来源
- 泛化概念

只做关键词检索容易漏掉语义近义表达，只做向量检索又可能缺少高精度术语命中。因此这里采用混合检索。

### 7.2 混合检索流程

`hybrid_search()` 的基本流程如下：

1. 先执行关键词检索
2. 再执行向量检索
3. 按 `doc_id` 合并去重
4. 使用融合分数排序
5. 返回统一格式的知识命中列表

另外，`search_knowledge()` 做了降级保护：

- 优先调用 `hybrid_search()`
- 若向量检索失败，则回退到 `search_knowledge_by_keyword()`

这保证了即使离线索引缺失或 embedding 运行异常，系统仍保留基础知识问答能力。

## 8. 数据集侧的二次召回

当前实现的关键特点是：知识检索不是终点，候选细胞检索才是把答案落到当前数据集上的关键一步。

系统在拿到 `knowledge_hits` 后，会先抽取：

- 候选 `cell_type`
- 候选 `disease`
- 候选 `tissue`
- 候选 `marker_genes`
- 概念子项

随后，`search_cells()` 根据这些 hint 做二次召回。

召回优先级大致为：

1. 若存在活动索引，优先使用索引关联的可视化点或检索上下文
2. 若没有活动索引，则使用数据集预览数据
3. 在候选结果上再叠加 metadata 条件与关键词信号做排序

这样做的好处是：

- 避免知识库答案脱离当前数据集
- 能把“知识上的可能相关”转换为“当前数据中真实出现的候选细胞”
- 使最终回答更适合课程展示和结果解释

## 9. 证据融合与回答生成

### 9.1 融合目的

如果直接把 `knowledge_hits` 和 `cell_hits` 原样交给模型，容易产生以下问题：

- 上下文冗余
- 证据来源不清晰
- 模型更容易编造
- 前端也难以直接展示结构化依据

因此系统先做证据融合，再交给模型或规则回答层。

### 9.2 融合结果

证据融合阶段会形成以下内容：

- `knowledge_evidence`
- `dataset_evidence`
- `metadata_evidence`
- `llm_context`
- `retrieval_source`

其中 `llm_context` 是给大模型的核心结构化上下文，而 `retrieval_source` 则用于前端说明当前候选结果来自哪里。

### 9.3 回答策略

系统支持两种回答策略：

- LLM 模式
- 规则模式

当配置了：

- `ZHIPU_API_KEY`

时，系统会调用智谱模型生成回答。

未配置时：

- 仍会完成前面的知识检索、候选召回和证据融合
- 最后使用 `build_rule_based_answer()` 输出规则化结果

因此，LLM 只是“回答生成器”，不是 RAG 主链路的唯一依赖。

## 10. 请求与返回

### 10.1 主接口

RAG 主接口为：

```http
POST /api/ai/cell-query
```

常见请求字段包括：

- `data_path`
- `user_question`
- `dataset_info`
- `current_build_options`
- `index_id`
- `conversation_history`
- `current_results`
- `selected_cell_id`
- `query_context`

常见返回字段包括：

- `answer`
- `intent`
- `applied_filters`
- `knowledge_hits`
- `cell_hits`
- `cell_summary`
- `next_steps`
- `retrieval_source`
- `query_context`

### 10.2 与索引顾问接口的区别

以下接口不属于完整细胞 RAG 主链路：

- `POST /api/ai/chat`
- `POST /api/ai/index-advice`

它们更偏向索引类型、距离度量和参数设置建议。

## 11. 关键配置项

RAG 相关配置重点如下：

- `RAG_EMBEDDING_MODEL`：知识库 embedding 模型
- `SEWORK_KNOWLEDGE_INDEX_DIR`：知识索引目录
- `SEWORK_USER_KB_PATHS`：用户扩展知识文件路径
- `ZHIPU_API_KEY`：是否启用大模型回答
- `ZHIPU_MODEL`：大模型名称
- `ZHIPU_API_URL`：大模型接口地址

此外，RAG 依赖以下系统能力：

- `FAISS_SERVICE_URL`：数据集检索与可视化相关能力
- `DATABASE_URL`：用户体系、索引记录、任务记录等

## 12. 运行前提

若要让 RAG 主链路完整可用，至少要满足：

1. 已安装 Python 依赖
2. MySQL 服务可用
3. 独立 FAISS 服务可用
4. 已生成知识索引 `knowledge.faiss` 和 `metadata.json`

若要启用 LLM 生成回答，还需配置：

- `ZHIPU_API_KEY`

## 13. 扩展方式

当前实现比较适合以下扩展方向：

### 13.1 扩展知识库

**快速生成精简知识库：**

```powershell
# 激进精简（丢弃 marker_gene 条目，仅保留 cell_type，36,401 条）
python scripts/filter_cell_marker_kb.py --aggressive --output knowledge/source/cell_marker_kb_filtered.jsonl

# 保守精简（保留 cell_type + 最多 10,000 条 marker_gene）
python scripts/filter_cell_marker_kb.py --marker-cap 10000

# 仅预览精简效果
python scripts/filter_cell_marker_kb.py --dry-run --aggressive
```

**扩展知识库步骤：**

1. 往 `knowledge/source/user` 中新增 JSONL（参考 `knowledge/examples/demo.jsonl` 格式）
2. 或通过 `SEWORK_USER_KB_PATHS` 注入额外知识文件
3. 重新构建索引：`python scripts/build_knowledge_index.py --batch-size 256`

### 13.2 扩展概念解析

- 在 `sc_concepts.jsonl` 中补充更多上位概念、别名和子类关系
- 强化 `children`、`related_terms`、`aliases` 字段

### 13.3 扩展回答风格

- 调整 `services/ai_advisor.py` 中的系统提示词
- 增强 `services/evidence_fusion.py` 中的结构化证据字段
- 提升规则模式下的回答模板

### 13.4 扩展细胞召回策略

- 在 `services/cell_search_engine.py` 中增加更强的 metadata 打分逻辑
- 增加 marker gene 匹配权重
- 引入更多与当前查询上下文相关的重排特征

## 14. 当前实现的特点与边界

### 14.1 优点

- 不是只做知识库问答，而是显式联动当前数据集
- 有知识检索失败时的降级策略
- 有无大模型都能输出结果
- 证据链相对清晰，便于前端展示
- 知识库支持默认知识、用户知识和运行时文档三类来源

### 14.2 边界

- 查询理解仍以规则与轻量匹配为主，不是通用语义解析器
- 候选细胞召回质量仍然依赖当前 metadata 完整度和活动索引可用性
- 知识库质量直接影响概念扩展与解释质量
- 若 README 或数据说明文本质量较弱，其作为运行时文档纳入知识库时也会影响问答表现

## 15. 建议的阅读顺序

如果要继续深入理解实现，建议按以下顺序阅读代码：

1. `app.py`
2. `services/cell_analysis_agent.py`
3. `services/query_parser.py`
4. `services/concept_search.py`
5. `services/rag_store.py`
6. `services/cell_search_engine.py`
7. `services/evidence_fusion.py`
8. `services/ai_advisor.py`
9. `scripts/build_knowledge_index.py`

## 16. 总结

本项目的 RAG 设计本质上是一个“面向单细胞分析任务的混合式检索增强系统”：

- 前半段负责理解问题、召回知识和定位候选细胞
- 中间层负责把多源证据整理成可解释上下文
- 后半段负责用 LLM 或规则将结构化证据转成自然语言回答

这种设计比单纯的大模型问答更可控，也比只做向量检索更适合解释“为什么这些细胞会被召回，以及下一步应该怎么分析”。
