from __future__ import annotations

from services.ai_advisor import request_cell_analysis_chat
from services.cell_search_engine import search_cells
from services.evidence_fusion import (
    build_evidence_bundle,
    build_rule_based_answer,
    extract_knowledge_hints,
    extract_knowledge_terms,
)
from services.query_parser import parse_nl_query
from services.rag_store import hybrid_search


def analyze_cell_query(
    *,
    question: str,
    data_path: str,
    dataset_context: dict[str, Any],
    metadata_options: dict[str, Any] | None,
    active_index_record: dict[str, Any] | None,
    vector_index,
    api_key: str | None,
    api_url: str,
    model: str,
    conversation_history: list[dict[str, str]] | None = None,
    current_results: list[dict[str, Any]] | None = None,
    selected_cell_id: str | None = None,
    query_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    intent = parse_nl_query(question, metadata_options=metadata_options)
    knowledge_hits = (
        hybrid_search(
            question,
            top_k=5,
            extra_terms=(intent.get("matched_cell_types") or [])
            + (intent.get("matched_diseases") or [])
            + (intent.get("matched_tissues") or []),
        )
        if intent.get("should_search_knowledge")
        else []
    )
    knowledge_hints = extract_knowledge_hints(knowledge_hits)
    knowledge_terms = extract_knowledge_terms(knowledge_hits)

    cell_search_result = search_cells(
        intent=intent,
        data_path=data_path,
        metadata_options=metadata_options,
        active_index_record=active_index_record,
        vector_index=vector_index,
        knowledge_hints=knowledge_hints,
        knowledge_terms=knowledge_terms,
        current_results=current_results,
        selected_cell_id=selected_cell_id,
    )
    evidence_bundle = build_evidence_bundle(
        question=question,
        intent=intent,
        dataset_context=dataset_context,
        knowledge_hits=knowledge_hits,
        cell_search_result=cell_search_result,
        query_context=query_context,
    )
    fallback_answer = build_rule_based_answer(
        question=question,
        dataset_context=dataset_context,
        evidence_bundle=evidence_bundle,
    )

    if api_key:
        ai_result = request_cell_analysis_chat(
            api_key=api_key,
            model=model,
            api_url=api_url,
            dataset_context=dataset_context,
            user_question=question,
            intent=intent,
            knowledge_hits=evidence_bundle["knowledge_hits"],
            cell_hits=evidence_bundle["cell_hits"],
            next_steps=evidence_bundle["next_steps"],
            evidence_bundle=evidence_bundle,
            conversation_history=conversation_history or [],
        )
        answer = ai_result["answer"]
        model_name = ai_result["model"]
    else:
        answer = fallback_answer
        model_name = "rule-based-fallback"

    return {
        "analysis_type": intent.get("analysis_type"),
        "model": model_name,
        "answer": answer,
        "intent": intent,
        "applied_filters": evidence_bundle["applied_filters"],
        "knowledge_hits": evidence_bundle["knowledge_hits"],
        "knowledge_hints": evidence_bundle["knowledge_hints"],
        "cell_hits": evidence_bundle["cell_hits"],
        "cell_summary": evidence_bundle["cell_summary"],
        "next_steps": evidence_bundle["next_steps"],
        "retrieval_source": evidence_bundle["retrieval_source"],
        "evidence_bundle": evidence_bundle,
        "query_context": dict(query_context or {}),
    }
