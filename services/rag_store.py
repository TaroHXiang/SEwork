from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import faiss
import numpy as np

from config import BASE_DIR


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_+\-\.]+|[\u4e00-\u9fff]{1,}")
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
KNOWLEDGE_SOURCE_DIR = KNOWLEDGE_DIR / "source"
KNOWLEDGE_INDEX_DIR = KNOWLEDGE_DIR / "index"
LEGACY_KB_DIR = BASE_DIR / "data" / "kb"
DEFAULT_RUNTIME_DOCS = [
    BASE_DIR / "README.md",
    BASE_DIR / "数据说明.md",
]
# 优先级：knowledge/source/ 下优先读 filtered 版本（旧文件迁移后可删除此映射）
_DEFAULT_KB_FILENAMES = [
    "sc_knowledge.jsonl",
    "sc_concepts.jsonl",
    # filtered 版本由 filter_cell_marker_kb.py --aggressive 生成
    "cell_marker_kb_filtered.jsonl",
    # 兜底：旧版全量 marker 文件（待迁移完成后可移除）
    "cell_marker_kb.jsonl",
]
DEFAULT_KB_FILENAMES = _DEFAULT_KB_FILENAMES
DEFAULT_KB_PATHS = [
    (KNOWLEDGE_SOURCE_DIR / name) if (KNOWLEDGE_SOURCE_DIR / name).exists() else (LEGACY_KB_DIR / name)
    for name in DEFAULT_KB_FILENAMES
]
DEFAULT_USER_KB_DIRS = [
    KNOWLEDGE_SOURCE_DIR / "user",
    LEGACY_KB_DIR / "user",
]
USER_KB_ENV = "SEWORK_USER_KB_PATHS"
RAG_EMBEDDING_BACKEND = "sentence-transformers"
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5").strip() or "BAAI/bge-small-zh-v1.5"
RAG_INDEX_DIR = Path(os.getenv("SEWORK_KNOWLEDGE_INDEX_DIR") or KNOWLEDGE_INDEX_DIR)
RAG_FAISS_PATH = RAG_INDEX_DIR / "knowledge.faiss"
RAG_METADATA_PATH = RAG_INDEX_DIR / "metadata.json"


@dataclass
class KnowledgeDocument:
    doc_id: str
    source: str
    category: str
    title: str
    content: str
    keywords: list[str]
    metadata: dict[str, Any]
    aliases: list[str]
    question_examples: list[str]
    summary: str
    related_terms: list[str]
    marker_genes: list[str]
    disease_related: list[str]
    children: list[str]
    retrieval_text: str

    @property
    def search_text(self) -> str:
        return self.retrieval_text or " ".join(
            part
            for part in [
                self.title,
                self.summary,
                self.content,
                " ".join(self.aliases),
                " ".join(self.question_examples),
                " ".join(self.keywords),
                " ".join(self.related_terms),
                " ".join(self.marker_genes),
                " ".join(self.children),
                json.dumps(self.metadata, ensure_ascii=False),
            ]
            if part
        )


@dataclass
class KnowledgeIndex:
    documents: tuple[KnowledgeDocument, ...]
    faiss_index: faiss.Index
    backend: str
    model_name: str
    index_path: Path
    metadata_path: Path


def tokenize_text(text: str) -> list[str]:
    raw_tokens = TOKEN_PATTERN.findall(str(text or "").lower())
    return [token.strip() for token in raw_tokens if token.strip()]


def _unique_preserve_order(items: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = str(item or "").strip()
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _safe_doc_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:04d}"


def _normalize_existing_payload(payload: dict[str, Any]) -> dict[str, Any]:
    aliases = _unique_preserve_order(payload.get("aliases") or [])
    keywords = _unique_preserve_order(payload.get("keywords") or [])
    question_examples = _unique_preserve_order(payload.get("question_examples") or [])
    related_terms = _unique_preserve_order(payload.get("related_terms") or [])
    marker_genes = _unique_preserve_order(payload.get("marker_genes") or [])
    disease_related = _unique_preserve_order(payload.get("disease_related") or [])
    children = _unique_preserve_order(payload.get("children") or [])
    summary = str(payload.get("summary") or "").strip()
    content = str(payload.get("content") or payload.get("answer") or "").strip()
    title = str(payload.get("title") or "").strip()
    metadata = dict(payload.get("metadata") or {})
    retrieval_text = str(payload.get("retrieval_text") or "").strip()
    if not retrieval_text:
        retrieval_text = _build_retrieval_text(
            title=title,
            category=str(payload.get("category") or "general"),
            aliases=aliases,
            keywords=keywords,
            question_examples=question_examples,
            summary=summary,
            content=content,
            related_terms=related_terms,
            marker_genes=marker_genes,
            disease_related=disease_related,
            children=children,
            metadata=metadata,
        )
    return {
        "doc_id": str(payload.get("doc_id") or ""),
        "source": str(payload.get("source") or ""),
        "category": str(payload.get("category") or "general"),
        "title": title,
        "content": content,
        "keywords": keywords,
        "metadata": metadata,
        "aliases": aliases,
        "question_examples": question_examples,
        "summary": summary,
        "related_terms": related_terms,
        "marker_genes": marker_genes,
        "disease_related": disease_related,
        "children": children,
        "retrieval_text": retrieval_text,
    }


def _build_retrieval_text(
    *,
    title: str,
    category: str,
    aliases: list[str],
    keywords: list[str],
    question_examples: list[str],
    summary: str,
    content: str,
    related_terms: list[str],
    marker_genes: list[str],
    disease_related: list[str],
    children: list[str],
    metadata: dict[str, Any],
) -> str:
    parts = [
        f"Title: {title}" if title else "",
        f"Category: {category}" if category else "",
        f"Aliases: {', '.join(aliases)}" if aliases else "",
        f"Keywords: {', '.join(keywords)}" if keywords else "",
        f"Question Examples: {' | '.join(question_examples)}" if question_examples else "",
        f"Summary: {summary}" if summary else "",
        f"Content: {content}" if content else "",
        f"Related Terms: {', '.join(related_terms)}" if related_terms else "",
        f"Marker Genes: {', '.join(marker_genes)}" if marker_genes else "",
        f"Disease Related: {', '.join(disease_related)}" if disease_related else "",
        f"Children: {', '.join(children)}" if children else "",
        f"Metadata: {json.dumps(metadata, ensure_ascii=False)}" if metadata else "",
    ]
    return "\n".join(part for part in parts if part)


def _jsonl_documents(path: Path) -> list[KnowledgeDocument]:
    if not path.exists():
        return []
    docs: list[KnowledgeDocument] = []
    with path.open("r", encoding="utf-8") as fh:
        for index, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = _normalize_existing_payload(json.loads(stripped))
            docs.append(
                KnowledgeDocument(
                    doc_id=str(payload.get("doc_id") or _safe_doc_id(path.stem or "kb", index)),
                    source=str(payload.get("source") or path.name),
                    category=str(payload.get("category") or "general"),
                    title=str(payload.get("title") or f"知识片段 {index}"),
                    content=str(payload.get("content") or ""),
                    keywords=_unique_preserve_order(payload.get("keywords") or []),
                    metadata=dict(payload.get("metadata") or {}),
                    aliases=_unique_preserve_order(payload.get("aliases") or []),
                    question_examples=_unique_preserve_order(payload.get("question_examples") or []),
                    summary=str(payload.get("summary") or ""),
                    related_terms=_unique_preserve_order(payload.get("related_terms") or []),
                    marker_genes=_unique_preserve_order(payload.get("marker_genes") or []),
                    disease_related=_unique_preserve_order(payload.get("disease_related") or []),
                    children=_unique_preserve_order(payload.get("children") or []),
                    retrieval_text=str(payload.get("retrieval_text") or ""),
                )
            )
    return docs


def _markdown_documents(path: Path) -> list[KnowledgeDocument]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.replace("\r", "").split("\n")
    docs: list[KnowledgeDocument] = []
    heading = path.stem
    buffer: list[str] = []
    chunk_index = 0

    def flush_chunk() -> None:
        nonlocal buffer, chunk_index
        content = "\n".join(line for line in buffer if line.strip()).strip()
        if not content:
            buffer = []
            return
        chunk_index += 1
        excerpt = content[:420]
        summary = excerpt[:180]
        retrieval_text = _build_retrieval_text(
            title=heading,
            category="project_doc",
            aliases=[],
            keywords=tokenize_text(f"{heading} {excerpt}")[:24],
            question_examples=[],
            summary=summary,
            content=excerpt,
            related_terms=[],
            marker_genes=[],
            disease_related=[],
            children=[],
            metadata={"path": str(path.relative_to(BASE_DIR))},
        )
        docs.append(
            KnowledgeDocument(
                doc_id=_safe_doc_id(path.stem, chunk_index),
                source=path.name,
                category="project_doc",
                title=heading,
                content=excerpt,
                keywords=tokenize_text(f"{heading} {excerpt}")[:24],
                metadata={"path": str(path.relative_to(BASE_DIR))},
                aliases=[],
                question_examples=[],
                summary=summary,
                related_terms=[],
                marker_genes=[],
                disease_related=[],
                children=[],
                retrieval_text=retrieval_text,
            )
        )
        buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            flush_chunk()
            heading = stripped.lstrip("#").strip() or path.stem
            continue
        if not stripped and len(buffer) >= 6:
            flush_chunk()
            continue
        buffer.append(stripped)

    flush_chunk()
    return docs


def _resolve_user_kb_paths() -> list[Path]:
    resolved: list[Path] = []
    raw_paths = str(os.getenv(USER_KB_ENV) or "").strip()
    if raw_paths:
        for item in raw_paths.split(os.pathsep):
            candidate = Path(item).expanduser()
            if candidate.is_dir():
                resolved.extend(sorted(candidate.glob("*.jsonl")))
            elif candidate.suffix.lower() == ".jsonl":
                resolved.append(candidate)
    for user_dir in DEFAULT_USER_KB_DIRS:
        if user_dir.exists():
            resolved.extend(sorted(user_dir.glob("*.jsonl")))
    unique: list[Path] = []
    seen: set[str] = set()
    for path in resolved:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def knowledge_source_paths() -> dict[str, list[Path]]:
    default_jsonl = [path for path in DEFAULT_KB_PATHS if path.exists()]
    user_jsonl = [path for path in _resolve_user_kb_paths() if path.exists()]
    runtime_docs = [path for path in DEFAULT_RUNTIME_DOCS if path.exists()]
    return {
        "default_jsonl": default_jsonl,
        "user_jsonl": user_jsonl,
        "runtime_docs": runtime_docs,
    }


@lru_cache(maxsize=1)
def load_knowledge_documents() -> tuple[KnowledgeDocument, ...]:
    docs: list[KnowledgeDocument] = []
    sources = knowledge_source_paths()
    for jsonl_path in sources["default_jsonl"]:
        docs.extend(_jsonl_documents(jsonl_path))
    for jsonl_path in sources["user_jsonl"]:
        docs.extend(_jsonl_documents(jsonl_path))
    for doc_path in sources["runtime_docs"]:
        docs.extend(_markdown_documents(doc_path))
    return tuple(docs)


def knowledge_index_artifact_paths() -> dict[str, Path]:
    return {
        "index_dir": RAG_INDEX_DIR,
        "faiss_path": RAG_FAISS_PATH,
        "metadata_path": RAG_METADATA_PATH,
    }


def _document_to_payload(doc: KnowledgeDocument) -> dict[str, Any]:
    return {
        "doc_id": doc.doc_id,
        "source": doc.source,
        "category": doc.category,
        "title": doc.title,
        "content": doc.content,
        "keywords": doc.keywords,
        "metadata": doc.metadata,
        "aliases": doc.aliases,
        "question_examples": doc.question_examples,
        "summary": doc.summary,
        "related_terms": doc.related_terms,
        "marker_genes": doc.marker_genes,
        "disease_related": doc.disease_related,
        "children": doc.children,
        "retrieval_text": doc.retrieval_text,
    }


def _document_from_payload(payload: dict[str, Any], index: int = 0) -> KnowledgeDocument:
    normalized = _normalize_existing_payload(payload)
    return KnowledgeDocument(
        doc_id=str(normalized.get("doc_id") or _safe_doc_id("kb_meta", index)),
        source=str(normalized.get("source") or "metadata"),
        category=str(normalized.get("category") or "general"),
        title=str(normalized.get("title") or f"知识片段 {index}"),
        content=str(normalized.get("content") or ""),
        keywords=_unique_preserve_order(normalized.get("keywords") or []),
        metadata=dict(normalized.get("metadata") or {}),
        aliases=_unique_preserve_order(normalized.get("aliases") or []),
        question_examples=_unique_preserve_order(normalized.get("question_examples") or []),
        summary=str(normalized.get("summary") or ""),
        related_terms=_unique_preserve_order(normalized.get("related_terms") or []),
        marker_genes=_unique_preserve_order(normalized.get("marker_genes") or []),
        disease_related=_unique_preserve_order(normalized.get("disease_related") or []),
        children=_unique_preserve_order(normalized.get("children") or []),
        retrieval_text=str(normalized.get("retrieval_text") or ""),
    )


def _get_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is not installed. Please install dependencies and run the offline build script first."
        ) from exc
    return SentenceTransformer


@lru_cache(maxsize=4)
def get_query_embedder(model_name: str | None = None):
    SentenceTransformer = _get_sentence_transformer()
    return SentenceTransformer(model_name or RAG_EMBEDDING_MODEL)


def encode_query_texts(texts: list[str], *, model_name: str | None = None) -> np.ndarray:
    clean_texts = [str(text or "").strip() for text in texts]
    if not clean_texts:
        return np.zeros((0, 0), dtype=np.float32)
    embedder = get_query_embedder(model_name)
    vectors = embedder.encode(
        clean_texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return np.asarray(vectors, dtype=np.float32)


def _load_index_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Knowledge metadata not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_knowledge_index() -> KnowledgeIndex:
    if not RAG_FAISS_PATH.exists() or not RAG_METADATA_PATH.exists():
        raise FileNotFoundError(
            "Knowledge FAISS index artifacts are missing. Please run scripts/build_knowledge_index.py first."
        )
    metadata_payload = _load_index_metadata(RAG_METADATA_PATH)
    documents = tuple(
        _document_from_payload(payload, index=index)
        for index, payload in enumerate(metadata_payload.get("documents") or [], start=1)
    )
    faiss_index = faiss.read_index(str(RAG_FAISS_PATH))
    return KnowledgeIndex(
        documents=documents,
        faiss_index=faiss_index,
        backend=RAG_EMBEDDING_BACKEND,
        model_name=str(metadata_payload.get("model_name") or RAG_EMBEDDING_MODEL),
        index_path=RAG_FAISS_PATH,
        metadata_path=RAG_METADATA_PATH,
    )


def _document_to_match(
    doc: KnowledgeDocument,
    *,
    score: float,
    matched_terms: list[str] | None = None,
    retrieval_method: str,
    embedding_score: float | None = None,
    keyword_score: float | None = None,
) -> dict[str, Any]:
    return {
        "doc_id": doc.doc_id,
        "source": doc.source,
        "category": doc.category,
        "title": doc.title,
        "content": doc.content,
        "summary": doc.summary,
        "keywords": doc.keywords,
        "aliases": doc.aliases,
        "question_examples": doc.question_examples,
        "related_terms": doc.related_terms,
        "marker_genes": doc.marker_genes,
        "disease_related": doc.disease_related,
        "children": doc.children,
        "metadata": doc.metadata,
        "score": round(float(score), 4),
        "matched_terms": matched_terms or [],
        "retrieval_method": retrieval_method,
        "embedding_score": None if embedding_score is None else round(float(embedding_score), 4),
        "keyword_score": None if keyword_score is None else round(float(keyword_score), 4),
    }


def _keyword_score_for_doc(doc: KnowledgeDocument, query_terms: list[str], query_text: str) -> tuple[float, list[str]]:
    haystack = doc.search_text.lower()
    keyword_set = {keyword.lower() for keyword in doc.keywords}
    alias_set = {alias.lower() for alias in doc.aliases}
    overlap_terms: list[str] = []
    score = 0.0
    for term in query_terms:
        term_norm = term.lower()
        if not term_norm or term_norm not in haystack:
            continue
        overlap_terms.append(term)
        if term_norm in keyword_set:
            score += 3.0
        elif term_norm in alias_set:
            score += 2.7
        elif term_norm in doc.title.lower():
            score += 2.4
        elif term_norm in doc.summary.lower():
            score += 1.6
        else:
            score += 1.1
    if not overlap_terms and query_text.lower() in haystack:
        score = 1.0
    return score, overlap_terms[:8]


def search_knowledge_by_keyword(
    query: str,
    *,
    top_k: int = 5,
    categories: list[str] | None = None,
    extra_terms: list[str] | None = None,
) -> list[dict[str, Any]]:
    normalized_query = str(query or "").strip()
    if not normalized_query:
        return []
    query_terms = _unique_preserve_order(tokenize_text(normalized_query) + list(extra_terms or []))
    category_set = {str(item).strip() for item in (categories or []) if str(item).strip()}
    matches: list[dict[str, Any]] = []
    for doc in load_knowledge_documents():
        if category_set and doc.category not in category_set:
            continue
        score, overlap_terms = _keyword_score_for_doc(doc, query_terms, normalized_query)
        if score <= 0:
            continue
        matches.append(
            _document_to_match(
                doc,
                score=score,
                matched_terms=overlap_terms,
                retrieval_method="keyword",
                keyword_score=score,
            )
        )
    matches.sort(key=lambda item: (-float(item.get("score") or 0.0), item.get("title") or ""))
    return matches[: max(1, top_k)]


def search_knowledge_by_embedding(
    query: str,
    *,
    top_k: int = 5,
    categories: list[str] | None = None,
    extra_terms: list[str] | None = None,
) -> list[dict[str, Any]]:
    normalized_query = str(query or "").strip()
    if not normalized_query:
        return []
    try:
        index = get_knowledge_index()
    except (FileNotFoundError, RuntimeError):
        return []

    query_text = " ".join(_unique_preserve_order([normalized_query] + list(extra_terms or [])))
    query_vectors = encode_query_texts([query_text], model_name=index.model_name)
    if query_vectors.size == 0:
        return []

    category_set = {str(item).strip() for item in (categories or []) if str(item).strip()}
    search_limit = max(top_k * 4, 20)
    scores, indices = index.faiss_index.search(query_vectors, search_limit)
    results: list[dict[str, Any]] = []
    for raw_score, raw_index in zip(scores[0], indices[0]):
        if raw_index < 0:
            continue
        doc = index.documents[int(raw_index)]
        if category_set and doc.category not in category_set:
            continue
        score = float(raw_score)
        results.append(
            _document_to_match(
                doc,
                score=score,
                retrieval_method="embedding",
                embedding_score=score,
            )
        )
        if len(results) >= max(1, top_k):
            break
    return results


def hybrid_search(
    query: str,
    *,
    top_k: int = 5,
    categories: list[str] | None = None,
    extra_terms: list[str] | None = None,
) -> list[dict[str, Any]]:
    keyword_hits = search_knowledge_by_keyword(
        query,
        top_k=max(top_k * 2, 8),
        categories=categories,
        extra_terms=extra_terms,
    )
    embedding_hits = search_knowledge_by_embedding(
        query,
        top_k=max(top_k * 2, 8),
        categories=categories,
        extra_terms=extra_terms,
    )

    merged: dict[str, dict[str, Any]] = {}
    for hit in embedding_hits:
        merged[hit["doc_id"]] = {
            **hit,
            "retrieval_method": "embedding",
            "hybrid_score": float(hit.get("embedding_score") or hit.get("score") or 0.0),
        }
    for hit in keyword_hits:
        existing = merged.get(hit["doc_id"])
        keyword_score = float(hit.get("keyword_score") or hit.get("score") or 0.0)
        if not existing:
            merged[hit["doc_id"]] = {**hit, "retrieval_method": "keyword", "hybrid_score": keyword_score}
            continue
        existing["matched_terms"] = _unique_preserve_order((existing.get("matched_terms") or []) + (hit.get("matched_terms") or []))
        existing["keyword_score"] = keyword_score
        existing["score"] = max(float(existing.get("score") or 0.0), keyword_score)
        existing["retrieval_method"] = "hybrid"
        existing["hybrid_score"] = float(existing.get("embedding_score") or 0.0) * 0.65 + keyword_score * 0.45 + 0.25

    results = list(merged.values())
    results.sort(
        key=lambda item: (
            -float(item.get("hybrid_score") or item.get("score") or 0.0),
            -float(item.get("keyword_score") or 0.0),
            item.get("title") or "",
        )
    )
    trimmed = results[: max(1, top_k)]
    for item in trimmed:
        item["score"] = round(float(item.get("hybrid_score") or item.get("score") or 0.0), 4)
    return trimmed


def search_knowledge(
    query: str,
    *,
    top_k: int = 5,
    categories: list[str] | None = None,
    extra_terms: list[str] | None = None,
) -> list[dict[str, Any]]:
    try:
        return hybrid_search(query, top_k=top_k, categories=categories, extra_terms=extra_terms)
    except Exception:
        return search_knowledge_by_keyword(query, top_k=top_k, categories=categories, extra_terms=extra_terms)
