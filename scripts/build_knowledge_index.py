from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import faiss
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.rag_store import (
    RAG_EMBEDDING_MODEL,
    knowledge_index_artifact_paths,
    knowledge_source_paths,
    load_knowledge_documents,
)

DEFAULT_EMBED_BATCH_SIZE = 64


def _ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _normalize_rows(vectors: np.ndarray) -> np.ndarray:
    if vectors.size == 0:
        return vectors.astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vectors / norms).astype(np.float32)


def _text_length_stats(texts: list[str]) -> dict[str, int]:
    lengths = [len(text or "") for text in texts]
    if not lengths:
        return {"min": 0, "max": 0, "avg": 0}
    return {
        "min": int(min(lengths)),
        "max": int(max(lengths)),
        "avg": int(sum(lengths) / len(lengths)),
    }


def build_knowledge_index(
    *,
    output_dir: Path,
    model_name: str,
    batch_size: int,
    diagnose_only: bool = False,
) -> dict[str, object]:
    _ensure_output_dir(output_dir)

    documents = load_knowledge_documents()
    retrieval_texts = [doc.search_text for doc in documents]
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(model_name)
    diagnostics = {
        "document_count": len(documents),
        "model_name": model_name,
        "batch_size": int(batch_size),
        "device": str(getattr(embedder, "device", "unknown")),
        "first_text_length": len(retrieval_texts[0]) if retrieval_texts else 0,
        "text_length_stats": _text_length_stats(retrieval_texts),
        "first_doc_id": documents[0].doc_id if documents else "",
        "first_doc_source": documents[0].source if documents else "",
    }
    print(json.dumps({"diagnostics": diagnostics}, ensure_ascii=False, indent=2), file=sys.stderr)
    if diagnose_only:
        return diagnostics

    vectors = embedder.encode(
        retrieval_texts,
        batch_size=max(1, int(batch_size)),
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    vectors = _normalize_rows(vectors)
    if vectors.ndim != 2 or vectors.shape[0] != len(documents):
        raise RuntimeError("Embedding result shape is invalid for knowledge documents.")

    index = faiss.IndexFlatIP(int(vectors.shape[1]))
    index.add(vectors)

    faiss_path = output_dir / "knowledge.faiss"
    metadata_path = output_dir / "metadata.json"
    faiss.write_index(index, str(faiss_path))

    source_paths = knowledge_source_paths()
    metadata_payload = {
        "model_name": model_name,
        "embedding_dim": int(vectors.shape[1]),
        "document_count": len(documents),
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_paths": {
            key: [str(path) for path in paths]
            for key, paths in source_paths.items()
        },
        "documents": [
            {
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
            for doc in documents
        ],
    }
    metadata_path.write_text(json.dumps(metadata_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "faiss_path": str(faiss_path),
        "metadata_path": str(metadata_path),
        "document_count": len(documents),
        "embedding_dim": int(vectors.shape[1]),
    }


def main() -> None:
    default_paths = knowledge_index_artifact_paths()
    parser = argparse.ArgumentParser(description="Build offline FAISS index for RAG knowledge base.")
    parser.add_argument(
        "--output-dir",
        default=str(default_paths["index_dir"]),
        help="Output directory for knowledge.faiss and metadata.json",
    )
    parser.add_argument(
        "--model",
        default=RAG_EMBEDDING_MODEL,
        help="SentenceTransformer model name used for embeddings",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_EMBED_BATCH_SIZE,
        help="Batch size used by SentenceTransformer.encode()",
    )
    parser.add_argument(
        "--diagnose-only",
        action="store_true",
        help="Print dataset/model diagnostics and exit without building the FAISS index",
    )
    args = parser.parse_args()

    result = build_knowledge_index(
        output_dir=Path(args.output_dir),
        model_name=str(args.model).strip() or RAG_EMBEDDING_MODEL,
        batch_size=max(1, int(args.batch_size)),
        diagnose_only=bool(args.diagnose_only),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
