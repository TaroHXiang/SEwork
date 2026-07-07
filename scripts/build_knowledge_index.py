from __future__ import annotations

import argparse
import hashlib
import json
import logging
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
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"
DEFAULT_CHECKPOINT_DIRNAME = ".checkpoint"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _build_run_id() -> str:
    return _utc_now().strftime("%Y%m%d-%H%M%S")


def _setup_logger(log_dir: Path, run_id: str) -> tuple[logging.Logger, Path]:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"knowledge-index-{run_id}.log"
    logger = logging.getLogger(f"knowledge_index_build.{run_id}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)sZ | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger, log_path


def _atomic_write_text(path: Path, content: str) -> None:
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


def _checkpoint_paths(checkpoint_dir: Path) -> dict[str, Path]:
    return {
        "state": checkpoint_dir / "state.json",
        "vectors": checkpoint_dir / "vectors.npy",
    }


def _build_input_signature(
    *,
    documents,
    model_name: str,
    batch_size: int,
    source_paths: dict[str, list[Path]],
) -> str:
    hasher = hashlib.sha256()
    hasher.update(model_name.encode("utf-8"))
    hasher.update(str(int(batch_size)).encode("utf-8"))
    for key in sorted(source_paths):
        hasher.update(key.encode("utf-8"))
        for path in source_paths[key]:
            hasher.update(str(path).encode("utf-8"))
    for doc in documents:
        hasher.update(doc.doc_id.encode("utf-8"))
        hasher.update(doc.source.encode("utf-8"))
        hasher.update(doc.title.encode("utf-8"))
        hasher.update(doc.retrieval_text.encode("utf-8"))
    return hasher.hexdigest()


def _write_checkpoint_state(state_path: Path, payload: dict[str, object]) -> None:
    _atomic_write_text(state_path, json.dumps(payload, ensure_ascii=False, indent=2))


def _load_checkpoint_state(state_path: Path) -> dict[str, object] | None:
    if not state_path.exists():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


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
    logger: logging.Logger | None = None,
    checkpoint_dir: Path | None = None,
    resume: bool = False,
    run_id: str | None = None,
) -> dict[str, object]:
    logger = logger or logging.getLogger("knowledge_index_build")
    _ensure_output_dir(output_dir)
    checkpoint_dir = checkpoint_dir or (output_dir / DEFAULT_CHECKPOINT_DIRNAME)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_files = _checkpoint_paths(checkpoint_dir)
    current_stage = "startup"
    logger.info("build-start output_dir=%s model=%s batch_size=%s diagnose_only=%s", output_dir, model_name, batch_size, diagnose_only)
    try:
        documents = load_knowledge_documents()
        retrieval_texts = [doc.search_text for doc in documents]
        source_paths = knowledge_source_paths()
        input_signature = _build_input_signature(
            documents=documents,
            model_name=model_name,
            batch_size=batch_size,
            source_paths=source_paths,
        )
        current_stage = "documents_loaded"
        logger.info("documents-loaded count=%s", len(documents))
        from sentence_transformers import SentenceTransformer

        logger.info("embedder-load-start model=%s", model_name)
        embedder = SentenceTransformer(model_name)
        logger.info("embedder-load-finish device=%s", getattr(embedder, "device", "unknown"))
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
        checkpoint_state = {
            "run_id": run_id or "",
            "status": "running",
            "stage": current_stage,
            "output_dir": str(output_dir),
            "checkpoint_dir": str(checkpoint_dir),
            "model_name": model_name,
            "batch_size": int(batch_size),
            "input_signature": input_signature,
            "diagnostics": diagnostics,
            "source_paths": {
                key: [str(path) for path in paths]
                for key, paths in source_paths.items()
            },
            "updated_at": _utc_now().isoformat(),
        }
        _write_checkpoint_state(checkpoint_files["state"], checkpoint_state)
        logger.info("checkpoint-state-write stage=%s path=%s", current_stage, checkpoint_files["state"])
        logger.info("diagnostics=%s", json.dumps(diagnostics, ensure_ascii=False, sort_keys=True))
        print(json.dumps({"diagnostics": diagnostics}, ensure_ascii=False, indent=2), file=sys.stderr)
        if diagnose_only:
            checkpoint_state["status"] = "diagnose_only"
            checkpoint_state["updated_at"] = _utc_now().isoformat()
            _write_checkpoint_state(checkpoint_files["state"], checkpoint_state)
            logger.info("diagnose-only-finish")
            return diagnostics

        vectors = None
        checkpoint_loaded = False
        if resume:
            checkpoint_state_on_disk = _load_checkpoint_state(checkpoint_files["state"])
            if (
                checkpoint_state_on_disk
                and checkpoint_state_on_disk.get("input_signature") == input_signature
                and checkpoint_files["vectors"].exists()
            ):
                current_stage = "checkpoint_restore"
                logger.info("checkpoint-restore-start path=%s", checkpoint_files["vectors"])
                vectors = np.load(checkpoint_files["vectors"])
                checkpoint_loaded = True
                logger.info(
                    "checkpoint-restore-finish rows=%s cols=%s dtype=%s",
                    getattr(vectors, "shape", ["?"])[0],
                    getattr(vectors, "shape", ["?", "?"])[1],
                    getattr(vectors, "dtype", "unknown"),
                )
            else:
                logger.info("checkpoint-restore-skip reason=no-compatible-checkpoint")

        if vectors is None:
            current_stage = "embedding"
            logger.info("embedding-start count=%s batch_size=%s", len(retrieval_texts), max(1, int(batch_size)))
            vectors = embedder.encode(
                retrieval_texts,
                batch_size=max(1, int(batch_size)),
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=True,
            )
            logger.info(
                "embedding-finish rows=%s cols=%s dtype=%s",
                getattr(vectors, "shape", ["?"])[0],
                getattr(vectors, "shape", ["?", "?"])[1],
                getattr(vectors, "dtype", "unknown"),
            )
            vectors = _normalize_rows(vectors)
            np.save(checkpoint_files["vectors"], vectors)
            checkpoint_state.update(
                {
                    "status": "running",
                    "stage": "embeddings_ready",
                    "vectors_path": str(checkpoint_files["vectors"]),
                    "embedding_dim": int(vectors.shape[1]) if vectors.ndim == 2 else None,
                    "checkpoint_loaded": False,
                    "updated_at": _utc_now().isoformat(),
                }
            )
            _write_checkpoint_state(checkpoint_files["state"], checkpoint_state)
            logger.info("checkpoint-vectors-write path=%s", checkpoint_files["vectors"])
        else:
            vectors = _normalize_rows(vectors)
            checkpoint_state.update(
                {
                    "status": "running",
                    "stage": "embeddings_ready",
                    "vectors_path": str(checkpoint_files["vectors"]),
                    "embedding_dim": int(vectors.shape[1]) if vectors.ndim == 2 else None,
                    "checkpoint_loaded": checkpoint_loaded,
                    "updated_at": _utc_now().isoformat(),
                }
            )
            _write_checkpoint_state(checkpoint_files["state"], checkpoint_state)

        if vectors.ndim != 2 or vectors.shape[0] != len(documents):
            logger.error("embedding-shape-invalid shape=%s expected_rows=%s", getattr(vectors, "shape", None), len(documents))
            raise RuntimeError("Embedding result shape is invalid for knowledge documents.")

        current_stage = "faiss_build"
        logger.info("faiss-build-start dim=%s", int(vectors.shape[1]))
        index = faiss.IndexFlatIP(int(vectors.shape[1]))
        index.add(vectors)
        logger.info("faiss-build-finish ntotal=%s", index.ntotal)

        faiss_path = output_dir / "knowledge.faiss"
        metadata_path = output_dir / "metadata.json"
        current_stage = "faiss_write"
        logger.info("faiss-write-start path=%s", faiss_path)
        faiss.write_index(index, str(faiss_path))
        logger.info("faiss-write-finish path=%s", faiss_path)
        checkpoint_state.update(
            {
                "status": "running",
                "stage": "index_written",
                "faiss_path": str(faiss_path),
                "updated_at": _utc_now().isoformat(),
            }
        )
        _write_checkpoint_state(checkpoint_files["state"], checkpoint_state)

        metadata_payload = {
            "model_name": model_name,
            "embedding_dim": int(vectors.shape[1]),
            "document_count": len(documents),
            "built_at": _utc_now().isoformat(),
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
        current_stage = "metadata_write"
        logger.info("metadata-write-start path=%s", metadata_path)
        _atomic_write_text(metadata_path, json.dumps(metadata_payload, ensure_ascii=False, indent=2))
        logger.info("metadata-write-finish path=%s", metadata_path)

        checkpoint_state.update(
            {
                "status": "completed",
                "stage": "completed",
                "faiss_path": str(faiss_path),
                "metadata_path": str(metadata_path),
                "document_count": len(documents),
                "embedding_dim": int(vectors.shape[1]),
                "updated_at": _utc_now().isoformat(),
            }
        )
        _write_checkpoint_state(checkpoint_files["state"], checkpoint_state)
        logger.info("build-finish document_count=%s embedding_dim=%s", len(documents), int(vectors.shape[1]))
        return {
            "faiss_path": str(faiss_path),
            "metadata_path": str(metadata_path),
            "document_count": len(documents),
            "embedding_dim": int(vectors.shape[1]),
            "checkpoint_dir": str(checkpoint_dir),
            "checkpoint_vectors_path": str(checkpoint_files["vectors"]),
            "checkpoint_state_path": str(checkpoint_files["state"]),
        }
    except Exception as exc:
        failure_state = _load_checkpoint_state(checkpoint_files["state"]) or {}
        failure_state.update(
            {
                "run_id": run_id or failure_state.get("run_id", ""),
                "status": "failed",
                "stage": current_stage,
                "output_dir": str(output_dir),
                "checkpoint_dir": str(checkpoint_dir),
                "model_name": model_name,
                "batch_size": int(batch_size),
                "error": f"{exc.__class__.__name__}: {exc}",
                "updated_at": _utc_now().isoformat(),
            }
        )
        _write_checkpoint_state(checkpoint_files["state"], failure_state)
        raise


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
    parser.add_argument(
        "--log-dir",
        default=str(DEFAULT_LOG_DIR),
        help="Directory used to store timestamped build logs",
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="",
        help="Directory used to store resumable checkpoint artifacts; defaults to <output-dir>/.checkpoint",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse compatible checkpoint vectors if available to skip embedding",
    )
    args = parser.parse_args()
    run_id = _build_run_id()
    logger, log_path = _setup_logger(Path(args.log_dir), run_id)
    logger.info("cli-start run_id=%s argv=%s", run_id, json.dumps(sys.argv[1:], ensure_ascii=False))
    logger.info("python-executable=%s", sys.executable)
    logger.info("log-file=%s", log_path)

    try:
        result = build_knowledge_index(
            output_dir=Path(args.output_dir),
            model_name=str(args.model).strip() or RAG_EMBEDDING_MODEL,
            batch_size=max(1, int(args.batch_size)),
            diagnose_only=bool(args.diagnose_only),
            logger=logger,
            checkpoint_dir=Path(args.checkpoint_dir).expanduser() if str(args.checkpoint_dir).strip() else None,
            resume=bool(args.resume),
            run_id=run_id,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        logger.info("cli-finish success=true")
    except Exception:
        logger.exception("cli-finish success=false")
        raise


if __name__ == "__main__":
    main()
