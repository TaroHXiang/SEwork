from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from services.rag_store import KnowledgeDocument, hybrid_search, load_knowledge_documents


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


@dataclass
class ResolvedConcept:
    title: str
    category: str
    concept_type: str
    aliases: list[str]
    children: list[str]
    related_terms: list[str]
    keywords: list[str]
    metadata: dict[str, Any]
    score: float
    retrieval_method: str
    matched_terms: list[str]


class ConceptResolver:
    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        self.documents = documents
        self.by_title = {_normalize_text(doc.title): doc for doc in documents if doc.title}
        self.alias_index: dict[str, list[KnowledgeDocument]] = {}
        for doc in documents:
            for alias in [doc.title] + list(doc.aliases):
                normalized = _normalize_text(alias)
                if not normalized:
                    continue
                self.alias_index.setdefault(normalized, []).append(doc)

    def _infer_concept_type(self, doc: KnowledgeDocument) -> str:
        return str((doc.metadata or {}).get("concept_type") or "generic").strip().lower() or "generic"

    def _doc_to_resolved(
        self,
        doc: KnowledgeDocument,
        *,
        score: float,
        retrieval_method: str,
        matched_terms: list[str] | None = None,
    ) -> ResolvedConcept:
        return ResolvedConcept(
            title=doc.title,
            category=doc.category,
            concept_type=self._infer_concept_type(doc),
            aliases=list(doc.aliases),
            children=list(doc.children),
            related_terms=list(doc.related_terms),
            keywords=list(doc.keywords),
            metadata=dict(doc.metadata),
            score=float(score),
            retrieval_method=retrieval_method,
            matched_terms=list(matched_terms or []),
        )

    def resolve(self, text: str, *, top_k: int = 5) -> list[ResolvedConcept]:
        normalized_text = _normalize_text(text)
        if not normalized_text:
            return []

        merged: dict[str, ResolvedConcept] = {}

        for alias, docs in self.alias_index.items():
            if not alias or alias not in normalized_text:
                continue
            for doc in docs:
                score = max(2.5, min(6.0, 1.0 + len(alias) / 8.0))
                merged[doc.doc_id] = self._doc_to_resolved(
                    doc,
                    score=score,
                    retrieval_method="concept_exact",
                    matched_terms=[alias],
                )

        semantic_hits = hybrid_search(text, top_k=max(top_k * 2, 8), categories=["concept"])
        for hit in semantic_hits:
            doc = next((item for item in self.documents if item.doc_id == hit.get("doc_id")), None)
            if not doc:
                continue
            existing = merged.get(doc.doc_id)
            resolved = self._doc_to_resolved(
                doc,
                score=float(hit.get("score") or 0.0),
                retrieval_method=str(hit.get("retrieval_method") or "concept_semantic"),
                matched_terms=list(hit.get("matched_terms") or []),
            )
            if not existing or resolved.score > existing.score:
                merged[doc.doc_id] = resolved

        ranked = list(merged.values())
        ranked.sort(key=lambda item: (-item.score, item.title))
        return ranked[: max(1, top_k)]


@lru_cache(maxsize=1)
def get_concept_resolver() -> ConceptResolver:
    documents = [doc for doc in load_knowledge_documents() if doc.category == "concept"]
    return ConceptResolver(documents)


def resolve_concepts(text: str, *, top_k: int = 5) -> list[ResolvedConcept]:
    return get_concept_resolver().resolve(text, top_k=top_k)
