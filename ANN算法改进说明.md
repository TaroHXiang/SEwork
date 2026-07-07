# ANN 算法改进说明

## 1. 改进目标

本项目的单细胞相似性检索使用 FAISS 作为 ANN（Approximate Nearest Neighbor，近似最近邻）检索后端，支持 HNSW、IVF、PQ 等索引类型。原始 ANN 查询在无过滤条件时直接返回 ANN 的 Top-K 结果，在带 metadata 过滤条件时会退化为全量精确搜索。

本次改进目标是在尽量保持查询速度的前提下，提高 ANN 检索结果的准确性，并降低部分过滤查询的全量扫描开销。

重点优化方向包括：

- 提升 ANN Top-K 结果的精度。
- 在 metadata 过滤查询中减少不必要的全量 exact search。
- 保持原有接口兼容，已有查询逻辑不需要改调用方式。
- 不增加持久化索引文件大小，仅增加查询时少量临时候选计算。

## 2. 原有检索流程

原有逻辑位于 `services/faiss_engine.py`。

无过滤条件时：

```text
query vector
  -> FAISS ANN search(top_k)
  -> 返回 ANN Top-K
```

有过滤条件时：

```text
query vector + metadata filters
  -> 找出所有满足过滤条件的候选 offset
  -> 对候选集合执行 exact search
  -> 返回 Top-K
```

这种方式简单稳定，但有两个问题：

- ANN 直接返回 Top-K 时，近似检索可能存在排序误差。
- 只要带过滤条件，就会跳过 ANN，过滤候选较多时查询时间可能偏高。

## 3. 改进方案

本次实现了“ANN 粗召回 + 原始向量精排”的两阶段检索策略。

### 3.1 无过滤查询：ANN 扩大召回后精排

改进后，无过滤查询不再只让 FAISS 返回 `top_k` 个结果，而是先返回更多候选，再用原始向量重新计算精确距离或相似度。

流程如下：

```text
query vector
  -> FAISS ANN search(max(top_k, rerank_k))
  -> 取 ANN 候选 offset
  -> 使用原始向量 exact rerank
  -> 返回最终 Top-K
```

这样可以减少 ANN 近似排序带来的误差，提高 Top-K 排名质量。

### 3.2 过滤查询：ANN 候选过滤 + 不足时回退 exact

改进后，带 metadata 过滤条件时，系统会先尝试用 ANN 扩大候选范围，再在候选中应用过滤条件。

流程如下：

```text
query vector + metadata filters
  -> FAISS ANN search(top_k * filter_candidate_multiplier)
  -> 对 ANN 候选应用 metadata 过滤
  -> 若过滤后候选数量足够，执行候选精排
  -> 若候选不足，回退到原有 exact search
```

这种策略在过滤条件不太稀疏时，可以避免直接全量 exact search，从而降低查询时间；当 ANN 候选不足时仍然回退 exact，保证结果完整性。

## 4. 新增参数

本次新增两个查询参数，位于 `DEFAULT_SEARCH_PARAMS`：

```python
DEFAULT_SEARCH_PARAMS = {
    "hnsw_ef": 128,
    "nprobe": 8,
    "exact": False,
    "rerank_k": 50,
    "filter_candidate_multiplier": 20,
}
```

### 4.1 rerank_k

`rerank_k` 控制无过滤 ANN 查询时的粗召回候选数量。

含义：

```text
先用 ANN 召回 max(top_k, rerank_k) 个候选，再用原始向量精排。
```

默认值：

```text
50
```

影响：

- 值越大，精排候选越多，召回质量通常越好。
- 值越大，查询时间会略微增加。
- 不影响索引构建时间和索引文件大小。

### 4.2 filter_candidate_multiplier

`filter_candidate_multiplier` 控制带过滤查询时 ANN 粗召回规模。

含义：

```text
ANN 候选数量至少为 top_k * filter_candidate_multiplier。
```

默认值：

```text
20
```

影响：

- 值越大，过滤后保留足够候选的概率越高。
- 值越大，ANN 查询和后续过滤开销会增加。
- 如果候选不足，系统会自动回退 exact search。

## 5. 涉及代码

主要修改文件：

```text
services/faiss_engine.py
```

核心函数：

- `search_by_vector_with_timing()`
- `_resolve_search_params()`
- `_ann_filtered_rerank_search()`
- `_rerank_ann_hits()`
- `_unique_offsets()`

新增逻辑：

- 无过滤查询使用 ANN 扩召回 + exact rerank。
- 带过滤查询优先尝试 ANN 候选过滤。
- 新增 `rerank_k` 和 `filter_candidate_multiplier` 参数校验。

## 6. 改进效果预期

### 6.1 检索精度

无过滤 ANN 查询的 Top-K 结果会经过原始向量重排，因此排序更接近 exact search。

预期效果：

```text
precision_at_k 提升
recall_at_k 提升或保持不变
```

### 6.2 查询时间

无过滤查询会增加一次候选精排，因此查询时间可能略有上升。

带过滤查询在过滤条件不太稀疏时，可能避免全量 exact search，因此查询时间可能下降。

预期效果：

```text
无过滤查询：查询时间略增，精度提升
过滤查询：部分场景查询时间下降
```

### 6.3 内存占用

本次改进没有改变 FAISS 索引结构，也没有新增持久化向量副本。

内存影响主要来自查询时临时候选数组，规模由 `rerank_k` 和 `filter_candidate_multiplier` 控制。

预期效果：

```text
持久化索引大小不变
运行时临时内存轻微增加
```

## 7. 验证方法

项目已有 ANN 与 exact 对照评估能力，可通过接口或前端评估功能查看：

- `ann_query_time_ms`
- `exact_query_time_ms`
- `precision_at_k`
- `recall_at_k`
- `overlap_count`

建议对比以下场景：

### 7.1 无过滤查询

对同一个 cell_id 执行 ANN 评估，比较改进前后的：

```text
precision_at_k
recall_at_k
ann_query_time_ms
```

预期是精度提升，查询时间略增。

### 7.2 带 metadata 过滤查询

使用常见过滤条件，例如：

```text
cell_type = T cell
disease = normal
tissue = caudate lobe of liver
```

比较：

```text
ann_query_time_ms
precision_at_k
recall_at_k
```

预期是在候选充足时减少全量 exact search 带来的耗时。

### 7.3 极稀疏过滤条件

如果过滤条件非常稀疏，ANN 候选中可能找不到足够匹配项。此时系统会自动回退 exact search。

预期：

```text
结果完整性保持不变
查询时间接近原 exact search
```

## 8. 参数调优建议

如果更关注检索精度：

```json
{
  "rerank_k": 100,
  "filter_candidate_multiplier": 50
}
```

如果更关注查询速度：

```json
{
  "rerank_k": 20,
  "filter_candidate_multiplier": 10
}
```

如果数据规模较大且交互查询频繁，建议从默认值开始：

```json
{
  "rerank_k": 50,
  "filter_candidate_multiplier": 20
}
```

再根据 `precision_at_k`、`recall_at_k` 和 `ann_query_time_ms` 做调整。

## 9. 总结

本次 ANN 改进采用了保守、兼容的两阶段检索策略：

```text
ANN 快速召回候选 + 原始向量精确重排
```

该策略不改变索引构建流程，不增加索引文件大小，主要通过查询阶段的候选重排提升检索精度，并在部分过滤查询场景下减少全量扫描开销。

