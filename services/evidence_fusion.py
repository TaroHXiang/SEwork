from __future__ import annotations

from typing import Any


def extract_knowledge_terms(knowledge_hits: list[dict[str, Any]]) -> list[str]:
    terms: list[str] = []
    for hit in knowledge_hits:
        for field_name in ["matched_terms", "keywords", "aliases", "related_terms", "marker_genes", "disease_related"]:
            values = hit.get(field_name) or []
            if isinstance(values, list):
                terms.extend(str(item).strip() for item in values if str(item).strip())
        title = str(hit.get("title") or "").strip()
        if title:
            terms.append(title)
    return list(dict.fromkeys(item for item in terms if item))


def extract_knowledge_hints(knowledge_hits: list[dict[str, Any]]) -> dict[str, Any]:
    cell_types: list[str] = []
    diseases: list[str] = []
    tissues: list[str] = []
    marker_genes: list[str] = []
    categories: list[str] = []
    concept_children: list[str] = []

    for hit in knowledge_hits:
        category = str(hit.get("category") or "").strip()
        categories.append(category)
        title = str(hit.get("title") or "").strip()
        metadata = dict(hit.get("metadata") or {})

        if category == "cell_type" and title:
            cell_types.append(title)

        related_cell_types = metadata.get("related_cell_types") or []
        if isinstance(related_cell_types, list):
            cell_types.extend(str(item).strip() for item in related_cell_types if str(item).strip())

        children = hit.get("children") or metadata.get("children") or []
        if isinstance(children, list):
            concept_children.extend(str(item).strip() for item in children if str(item).strip())
            cell_types.extend(str(item).strip() for item in children if str(item).strip())

        if metadata.get("disease"):
            diseases.append(str(metadata.get("disease") or "").strip())
        disease_related = hit.get("disease_related") or []
        if isinstance(disease_related, list):
            diseases.extend(str(item).strip() for item in disease_related if str(item).strip())

        for tissue_key in ["tissue", "tissue_type", "tissue_class"]:
            if metadata.get(tissue_key):
                tissues.append(str(metadata.get(tissue_key) or "").strip())

        marker_values = hit.get("marker_genes") or []
        if isinstance(marker_values, list):
            marker_genes.extend(str(item).strip() for item in marker_values if str(item).strip())

    return {
        "cell_types": list(dict.fromkeys(item for item in cell_types if item)),
        "diseases": list(dict.fromkeys(item for item in diseases if item and item.lower() != "normal")),
        "tissues": list(dict.fromkeys(item for item in tissues if item)),
        "marker_genes": list(dict.fromkeys(item for item in marker_genes if item)),
        "categories": list(dict.fromkeys(item for item in categories if item)),
        "concept_children": list(dict.fromkeys(item for item in concept_children if item)),
    }


def build_next_steps(
    *,
    intent: dict[str, Any],
    cell_hits: list[dict[str, Any]],
) -> list[str]:
    suggestions = []
    if intent.get("asks_marker"):
        suggestions.append("结合命中的 cell_type，进一步核对 marker gene 是否与知识库描述一致。")
    if intent.get("filters"):
        suggestions.append("将当前自然语言解析得到的筛选条件同步到左侧过滤器，再观察 UMAP 空间分布。")
    if cell_hits:
        suggestions.append("优先点击结果表中的高分细胞，查看 UMAP 位置与详细 metadata。")
        suggestions.append("若结果集中在单一 cell_type，可继续做该群体的差异表达或子群聚类分析。")
    else:
        suggestions.append("尝试补充更明确的 cell_type、disease 或 tissue 关键词，以缩小搜索范围。")
    if intent.get("asks_index"):
        suggestions.append("对当前数据集可继续比较 HNSW 与 IVF 的召回率和查询时延，形成参数对照表。")
    return suggestions[:5]


def build_evidence_bundle(
    *,
    question: str,
    intent: dict[str, Any],
    dataset_context: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    cell_search_result: dict[str, Any],
    query_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cell_hits = list(cell_search_result.get("cell_hits") or [])
    cell_summary = dict(cell_search_result.get("cell_summary") or {})
    knowledge_hints = extract_knowledge_hints(knowledge_hits)
    knowledge_terms = extract_knowledge_terms(knowledge_hits)
    next_steps = build_next_steps(intent=intent, cell_hits=cell_hits)

    knowledge_evidence = {
        "top_hits": knowledge_hits[:5],
        "hints": knowledge_hints,
        "term_count": len(knowledge_terms),
    }
    dataset_evidence = {
        "retrieval_source": cell_search_result.get("retrieval_source"),
        "applied_filters": dict(cell_search_result.get("applied_filters") or {}),
        "cell_hits": cell_hits[:8],
        "cell_summary": cell_summary,
    }
    metadata_evidence = {
        "dataset_context": dataset_context,
        "query_context": dict(query_context or {}),
    }

    llm_context = {
        "question": question,
        "intent": intent,
        "knowledge_evidence": knowledge_evidence,
        "dataset_evidence": dataset_evidence,
        "metadata_evidence": metadata_evidence,
        "next_steps": next_steps,
    }

    return {
        "question": question,
        "intent": intent,
        "knowledge_hits": knowledge_hits,
        "knowledge_hints": knowledge_hints,
        "knowledge_terms": knowledge_terms,
        "cell_hits": cell_hits,
        "cell_summary": cell_summary,
        "next_steps": next_steps,
        "applied_filters": dict(cell_search_result.get("applied_filters") or {}),
        "retrieval_source": cell_search_result.get("retrieval_source"),
        "knowledge_evidence": knowledge_evidence,
        "dataset_evidence": dataset_evidence,
        "metadata_evidence": metadata_evidence,
        "llm_context": llm_context,
    }


def build_rule_based_answer(
    *,
    question: str,
    dataset_context: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> str:
    intent = dict(evidence_bundle.get("intent") or {})
    knowledge_hits = list(evidence_bundle.get("knowledge_hits") or [])
    cell_hits = list(evidence_bundle.get("cell_hits") or [])
    next_steps = list(evidence_bundle.get("next_steps") or [])
    applied_filters = dict(evidence_bundle.get("applied_filters") or {})
    cell_summary = dict(evidence_bundle.get("cell_summary") or {})

    lines = ["## 结论"]
    if cell_hits:
        cell_type_names = "、".join(item["name"] for item in cell_summary.get("top_cell_types") or [] if item.get("name")) or "当前筛选命中的细胞"
        lines.append(
            f"- 针对问题“{question}”，系统在当前数据集中优先命中了 {cell_summary.get('hit_count', len(cell_hits))} 个相关细胞，主要集中在 {cell_type_names}。"
        )
    else:
        lines.append("- 当前没有直接命中的细胞结果，回答主要依据知识库和数据集摘要生成。")

    lines.append("## 结构化依据")
    if applied_filters:
        filter_text = "，".join(f"{key}={value}" for key, value in applied_filters.items())
        lines.append(f"- 解析并应用的筛选条件：{filter_text}")
    else:
        lines.append("- 当前问题没有落到明确的 metadata 精确筛选，因此主要依据知识片段和候选结果重排进行解释。")
    lines.append(
        f"- 数据集概览：{dataset_context.get('format', '-')}"
        f"；细胞数 {dataset_context.get('cell_count', '-')}"
        f"；向量维度 {dataset_context.get('vector_dim', '-')}"
    )

    if knowledge_hits:
        lines.append("## 命中知识")
        for hit in knowledge_hits[:3]:
            lines.append(f"- {hit['title']}：{str(hit.get('summary') or hit.get('content') or '')[:120]}")

    if cell_hits:
        lines.append("## 数据集证据")
        for item in cell_hits[:3]:
            metadata = item.get("metadata") or {}
            lines.append(
                f"- {item['cell_id']}：cell_type={metadata.get('cell_type', '-')}"
                f"，disease={metadata.get('disease', '-')}"
                f"，tissue={metadata.get('tissue', '-')}"
                f"，综合匹配分数={item.get('score', '-')}"
            )
            for reason in item.get("reason_signals") or []:
                lines.append(f"  - {reason}")

    lines.append("## 下一步建议")
    for suggestion in next_steps[:4]:
        lines.append(f"- {suggestion}")
    return "\n".join(lines)
