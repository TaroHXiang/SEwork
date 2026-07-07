from __future__ import annotations

import re
from typing import Any

from services.concept_search import resolve_concepts
from services.rag_store import tokenize_text


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _extract_top_k(question: str, default: int = 8) -> int:
    text = str(question or "")
    patterns = [
        r"top[\s\-]*k[:：]?\s*(\d+)",
        r"前\s*(\d+)\s*(个|条|种)?",
        r"(\d+)\s*(个|条|种)\s*(结果|细胞)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = int(match.group(1))
            return max(3, min(value, 30))
    return default


def _unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = _normalize_text(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(str(item).strip())
    return result


def _resolve_concept_matches(question: str) -> dict[str, Any]:
    resolved = resolve_concepts(question, top_k=6)
    matched_cell_types: list[str] = []
    matched_diseases: list[str] = []
    matched_tissues: list[str] = []
    matched_pathways: list[str] = []
    mentions_immune = False
    concept_payloads: list[dict[str, Any]] = []

    for concept in resolved:
        concept_payloads.append(
            {
                "title": concept.title,
                "concept_type": concept.concept_type,
                "aliases": concept.aliases,
                "children": concept.children,
                "related_terms": concept.related_terms,
                "score": round(concept.score, 4),
                "retrieval_method": concept.retrieval_method,
                "matched_terms": concept.matched_terms,
            }
        )
        concept_type = concept.concept_type
        if concept_type in {"cell_group", "cell_type"}:
            matched_cell_types.extend(concept.children or [])
            if concept_type == "cell_type":
                matched_cell_types.append(concept.title)
        elif concept_type == "disease":
            matched_diseases.append(concept.title)
        elif concept_type == "tissue":
            matched_tissues.append(concept.title)
        elif concept_type == "pathway":
            matched_pathways.append(concept.title)

        if _normalize_text(concept.title) == "immune cell":
            mentions_immune = True

    return {
        "resolved_concepts": concept_payloads,
        "matched_cell_types": _unique_preserve_order(matched_cell_types),
        "matched_diseases": _unique_preserve_order(matched_diseases),
        "matched_tissues": _unique_preserve_order(matched_tissues),
        "matched_pathways": _unique_preserve_order(matched_pathways),
        "mentions_immune": mentions_immune,
    }


def _best_metadata_match(question: str, candidates: list[str]) -> str | None:
    text = _normalize_text(question)
    best_value = None
    best_score = 0
    for candidate in candidates:
        normalized_candidate = _normalize_text(candidate)
        if not normalized_candidate:
            continue
        score = 0
        if normalized_candidate in text:
            score += len(normalized_candidate)
        candidate_tokens = tokenize_text(normalized_candidate)
        if candidate_tokens:
            overlap = [token for token in candidate_tokens if token in text]
            score += len(overlap)
        if score > best_score:
            best_value = candidate
            best_score = score
    return best_value


def parse_nl_query(
    question: str,
    *,
    metadata_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = str(question or "").strip()
    normalized = _normalize_text(text)
    metadata_options = dict(metadata_options or {})
    available_options = metadata_options.get("options") or {}
    filters: dict[str, str] = {}
    concept_result = _resolve_concept_matches(text)

    matched_cell_types = list(concept_result["matched_cell_types"])
    matched_diseases = list(concept_result["matched_diseases"])
    matched_tissues = list(concept_result["matched_tissues"])
    matched_pathways = list(concept_result["matched_pathways"])
    asks_marker = any(term in normalized for term in ["marker", "markers", "marker gene", "标记基因", "marker基因"])
    asks_explanation = any(term in normalized for term in ["为什么", "解释", "意义", "说明", "分析"])
    asks_index = any(term in normalized for term in ["hnsw", "ivf", "pq", "索引", "参数", "召回", "nprobe", "nlist"])
    asks_next_steps = any(term in normalized for term in ["下一步", "建议", "怎么做", "分析建议", "后续"])
    asks_similarity = any(term in normalized for term in ["最像", "相似", "相关", "closest", "similar"])
    asks_cell_query = any(term in normalized for term in ["查找", "查询", "哪些", "哪类", "哪些细胞", "细胞"]) or asks_similarity
    mentions_immune = bool(concept_result["mentions_immune"])

    for field_name, values in available_options.items():
        selected = _best_metadata_match(text, list(values or []))
        if selected:
            filters[field_name] = selected

    if matched_cell_types and "cell_type" not in filters:
        matched_value = _best_metadata_match(" ".join([text] + matched_cell_types), list(available_options.get("cell_type") or []))
        if matched_value:
            filters["cell_type"] = matched_value

    if matched_diseases and "disease" not in filters:
        matched_value = _best_metadata_match(" ".join([text] + matched_diseases), list(available_options.get("disease") or []))
        if matched_value:
            filters["disease"] = matched_value

    if matched_tissues and "tissue" not in filters:
        matched_value = _best_metadata_match(" ".join([text] + matched_tissues), list(available_options.get("tissue") or []))
        if matched_value:
            filters["tissue"] = matched_value

    analysis_type = "cell_query"
    if asks_index and not asks_cell_query:
        analysis_type = "index_advice"
    elif asks_marker and not asks_cell_query:
        analysis_type = "knowledge_qa"
    elif asks_explanation and asks_similarity:
        analysis_type = "result_explanation"
    elif asks_marker or asks_explanation or asks_next_steps:
        analysis_type = "hybrid"

    should_search_cells = analysis_type in {"cell_query", "result_explanation", "hybrid"} or bool(filters)
    should_search_knowledge = analysis_type in {"knowledge_qa", "result_explanation", "hybrid", "index_advice"} or asks_marker

    return {
        "question": text,
        "analysis_type": analysis_type,
        "keywords": tokenize_text(text)[:24],
        "top_k": _extract_top_k(text),
        "filters": filters,
        "matched_cell_types": matched_cell_types,
        "matched_diseases": matched_diseases,
        "matched_tissues": matched_tissues,
        "matched_pathways": matched_pathways,
        "resolved_concepts": concept_result["resolved_concepts"],
        "mentions_immune": mentions_immune,
        "asks_marker": asks_marker,
        "asks_explanation": asks_explanation,
        "asks_next_steps": asks_next_steps,
        "asks_index": asks_index,
        "asks_similarity": asks_similarity,
        "should_search_cells": should_search_cells,
        "should_search_knowledge": should_search_knowledge,
    }
