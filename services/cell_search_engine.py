from __future__ import annotations

from collections import Counter
from typing import Any

from services.data_loader import load_dataset_visualization_preview


def _normalize_token(value: str) -> str:
    return str(value or "").strip().lower()


def _token_overlap_score(text: str, keywords: list[str]) -> float:
    haystack = _normalize_token(text)
    score = 0.0
    for keyword in keywords:
        token = _normalize_token(keyword)
        if token and token in haystack:
            score += 1.0
    return score


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _best_option_match(value: str, options: list[str]) -> str:
    target = _normalize_token(value)
    if not target:
        return ""
    for option in options:
        normalized_option = _normalize_token(option)
        if normalized_option == target:
            return str(option)
    for option in options:
        normalized_option = _normalize_token(option)
        if target in normalized_option or normalized_option in target:
            return str(option)
    return ""


def merge_filters_with_hints(
    intent: dict[str, Any],
    metadata_options: dict[str, Any] | None,
    knowledge_hints: dict[str, Any] | None,
) -> dict[str, str]:
    filters = dict(intent.get("filters") or {})
    available_options = (metadata_options or {}).get("options") or {}
    hints = dict(knowledge_hints or {})

    if not filters.get("disease"):
        for candidate in hints.get("diseases") or []:
            matched = _best_option_match(candidate, list(available_options.get("disease") or []))
            if matched:
                filters["disease"] = matched
                break

    if not filters.get("tissue"):
        for candidate in hints.get("tissues") or []:
            matched = _best_option_match(candidate, list(available_options.get("tissue") or []))
            if matched:
                filters["tissue"] = matched
                break

    if not filters.get("cell_type"):
        for candidate in hints.get("cell_types") or []:
            matched = _best_option_match(candidate, list(available_options.get("cell_type") or []))
            if matched:
                filters["cell_type"] = matched
                break

    return filters


def _build_reason_signals(
    metadata: dict[str, Any],
    *,
    intent: dict[str, Any],
    knowledge_hints: dict[str, Any],
    from_existing_results: bool = False,
) -> list[str]:
    reasons: list[str] = []
    cell_type = str(metadata.get("cell_type") or "").strip()
    disease = str(metadata.get("disease") or "").strip()
    tissue = str(metadata.get("tissue") or "").strip()

    if from_existing_results:
        reasons.append("来自当前检索结果，可直接用于解释已召回细胞。")

    filters = dict(intent.get("filters") or {})
    if filters:
        matched_pairs = []
        for field_name, field_value in filters.items():
            candidate = str(metadata.get(field_name) or "").strip()
            if candidate and candidate == str(field_value):
                matched_pairs.append(f"{field_name}={field_value}")
        if matched_pairs:
            reasons.append(f"匹配了筛选条件：{'，'.join(matched_pairs)}。")

    matched_cell_types = [_normalize_token(item) for item in intent.get("matched_cell_types") or []]
    if matched_cell_types and any(term in _normalize_token(cell_type) for term in matched_cell_types):
        reasons.append(f"cell_type 与问题中的目标细胞类型接近：{cell_type or '未标注'}。")

    knowledge_cell_types = [_normalize_token(item) for item in knowledge_hints.get("cell_types") or []]
    if knowledge_cell_types and any(term in _normalize_token(cell_type) for term in knowledge_cell_types):
        reasons.append("与知识检索阶段识别出的候选细胞类型一致。")

    matched_diseases = [_normalize_token(item) for item in intent.get("matched_diseases") or []]
    if disease and any(term in _normalize_token(disease) for term in matched_diseases):
        reasons.append(f"disease 字段与问题中的疾病关键词一致：{disease}。")

    matched_tissues = [_normalize_token(item) for item in intent.get("matched_tissues") or []]
    if tissue and any(term in _normalize_token(tissue) for term in matched_tissues):
        reasons.append(f"tissue 字段与问题中的组织关键词一致：{tissue}。")

    if knowledge_hints.get("marker_genes"):
        reasons.append("可结合知识库中召回的 marker gene 与当前 metadata 一起解释。")

    return reasons[:4]


def _rank_points(
    points: list[dict[str, Any]],
    *,
    intent: dict[str, Any],
    knowledge_hints: dict[str, Any],
    knowledge_terms: list[str],
) -> list[dict[str, Any]]:
    query_keywords = list(intent.get("keywords") or [])
    target_cell_types = [_normalize_token(item) for item in intent.get("matched_cell_types") or []]
    knowledge_cell_types = [_normalize_token(item) for item in knowledge_hints.get("cell_types") or []]
    matched_diseases = [_normalize_token(item) for item in intent.get("matched_diseases") or []]
    matched_tissues = [_normalize_token(item) for item in intent.get("matched_tissues") or []]

    ranked: list[dict[str, Any]] = []
    for point in points:
        metadata = dict(point.get("metadata") or {})
        cell_type = _normalize_token(metadata.get("cell_type"))
        disease = _normalize_token(metadata.get("disease"))
        tissue = _normalize_token(metadata.get("tissue"))
        metadata_text = " ".join(str(value) for value in metadata.values())
        score = 0.0

        if target_cell_types and any(term in cell_type for term in target_cell_types):
            score += 5.0
        if knowledge_cell_types and any(term in cell_type for term in knowledge_cell_types):
            score += 3.5

        filters = dict(intent.get("filters") or {})
        if filters:
            for field_name, field_value in filters.items():
                candidate = _normalize_token(metadata.get(field_name))
                if candidate and candidate == _normalize_token(field_value):
                    score += 2.5

        score += _token_overlap_score(metadata_text, query_keywords) * 0.9
        score += _token_overlap_score(metadata_text, knowledge_terms) * 0.45
        score += _token_overlap_score(point.get("cell_id") or "", query_keywords) * 0.5

        if disease and any(term in disease for term in matched_diseases):
            score += 1.8
        if tissue and any(term in tissue for term in matched_tissues):
            score += 1.5

        ranked.append(
            {
                "cell_id": point.get("cell_id") or "",
                "metadata": metadata,
                "umap": {"x": point.get("x"), "y": point.get("y")},
                "score": round(score, 4),
                "distance": round(max(0.0, 1.0 - min(score / 10.0, 0.99)), 4),
                "reason_signals": _build_reason_signals(
                    metadata,
                    intent=intent,
                    knowledge_hints=knowledge_hints,
                ),
            }
        )

    ranked.sort(
        key=lambda item: (
            -float(item.get("score") or 0.0),
            str((item.get("metadata") or {}).get("cell_type") or ""),
            str(item.get("cell_id") or ""),
        )
    )
    return ranked


def _normalize_existing_results(
    current_results: list[dict[str, Any]],
    *,
    intent: dict[str, Any],
    knowledge_hints: dict[str, Any],
    selected_cell_id: str = "",
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    selected_id = str(selected_cell_id or "").strip()

    for rank_index, item in enumerate(current_results, start=1):
        cell_id = str(item.get("cell_id") or "").strip()
        if not cell_id:
            continue
        metadata = dict(item.get("metadata") or {})
        viz = dict(item.get("viz") or {})
        score = item.get("score")
        if score is None:
            raw_similarity = item.get("similarity")
            if raw_similarity is not None:
                score = _safe_float(raw_similarity, default=0.0)
            else:
                raw_distance = item.get("distance")
                score = max(0.0, 1.0 - _safe_float(raw_distance, default=1.0))
        distance = item.get("distance")
        if distance is None:
            distance = round(max(0.0, 1.0 - _safe_float(score, default=0.0)), 4)

        normalized.append(
            {
                "cell_id": cell_id,
                "metadata": metadata,
                "umap": {"x": viz.get("x"), "y": viz.get("y")},
                "score": round(_safe_float(score, default=0.0), 4),
                "distance": round(_safe_float(distance, default=0.0), 4),
                "reason_signals": _build_reason_signals(
                    metadata,
                    intent=intent,
                    knowledge_hints=knowledge_hints,
                    from_existing_results=True,
                ),
                "rank_from_existing_query": rank_index,
                "selected": bool(selected_id and cell_id == selected_id),
            }
        )

    normalized.sort(
        key=lambda item: (
            0 if item.get("selected") else 1,
            int(item.get("rank_from_existing_query") or 9999),
            -float(item.get("score") or 0.0),
        )
    )
    return normalized


def summarize_cell_hits(cell_hits: list[dict[str, Any]]) -> dict[str, Any]:
    counter = Counter()
    for item in cell_hits:
        cell_type = str((item.get("metadata") or {}).get("cell_type") or "未知类型").strip()
        counter[cell_type] += 1
    return {
        "hit_count": len(cell_hits),
        "top_cell_types": [{"name": name, "count": count} for name, count in counter.most_common(5)],
    }


def search_cells(
    *,
    intent: dict[str, Any],
    data_path: str,
    metadata_options: dict[str, Any] | None,
    active_index_record: dict[str, Any] | None,
    vector_index,
    knowledge_hints: dict[str, Any] | None,
    knowledge_terms: list[str] | None,
    current_results: list[dict[str, Any]] | None = None,
    selected_cell_id: str | None = None,
) -> dict[str, Any]:
    hints = dict(knowledge_hints or {})
    filters = merge_filters_with_hints(intent, metadata_options, hints)
    retrieval_source = "none"
    supplied_results = list(current_results or [])
    point_limit = max(120, min(int(intent.get("top_k") or 8) * 20, 500))

    if supplied_results:
        cell_hits = _normalize_existing_results(
            supplied_results,
            intent=intent,
            knowledge_hints=hints,
            selected_cell_id=str(selected_cell_id or ""),
        )
        return {
            "retrieval_source": "existing_query_results",
            "applied_filters": filters,
            "candidate_points": [],
            "cell_hits": cell_hits,
            "cell_summary": summarize_cell_hits(cell_hits),
        }

    candidate_points: list[dict[str, Any]] = []
    if active_index_record:
        retrieval_source = "active_index"
        visualization = vector_index.get_visualization_points(
            collection_name=active_index_record["collection_name"],
            limit=point_limit,
            filters=filters or None,
        )
        candidate_points = list(visualization.get("points") or [])
    else:
        retrieval_source = "dataset_preview"
        preview = load_dataset_visualization_preview(
            data_path=data_path,
            limit=point_limit,
            level="cluster",
        )
        candidate_points = list(preview.get("points") or [])
        if filters:
            filtered_points = []
            for point in candidate_points:
                metadata = dict(point.get("metadata") or {})
                if all(str(metadata.get(field_name) or "") == str(field_value) for field_name, field_value in filters.items()):
                    filtered_points.append(point)
            candidate_points = filtered_points

    if hints.get("cell_types"):
        filtered_by_hints = []
        target_cell_types = [_normalize_token(item) for item in hints.get("cell_types") or []]
        for point in candidate_points:
            metadata = dict(point.get("metadata") or {})
            cell_type_value = _normalize_token(metadata.get("cell_type"))
            if any(term and (term in cell_type_value or cell_type_value in term) for term in target_cell_types):
                filtered_by_hints.append(point)
        if filtered_by_hints:
            candidate_points = filtered_by_hints
            retrieval_source = f"{retrieval_source}+knowledge_celltype_filter"

    ranked_hits = _rank_points(
        candidate_points,
        intent=intent,
        knowledge_hints=hints,
        knowledge_terms=list(knowledge_terms or []),
    )
    cell_hits = ranked_hits[: max(3, min(int(intent.get("top_k") or 8), 20))]
    return {
        "retrieval_source": retrieval_source,
        "applied_filters": filters,
        "candidate_points": candidate_points,
        "cell_hits": cell_hits,
        "cell_summary": summarize_cell_hits(cell_hits),
    }
