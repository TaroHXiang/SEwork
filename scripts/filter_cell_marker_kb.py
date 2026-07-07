"""
过滤并精简 cell_marker_kb.jsonl。

策略：
  1. 保留所有 cell_type 条目（已按细胞类型聚合，包含 5~12 个 marker gene，质量高）。
  2. marker_gene 条目（每条一个基因）对于 RAG 检索链路贡献有限，
     因为查询解析层是基于 cell_type/disease/tissue/marker 关键词搜索，而不是搜单个基因名。
  3. 提供两种模式：
     - --aggressive（推荐）：丢弃所有 marker_gene，只保留 cell_type（36,401 条）
     - --marker-cap N      ：保留最多 N 条 marker_gene 条目（按关联细胞类型丰富度排序）

用法：
    # 仅预览效果
    python scripts/filter_cell_marker_kb.py --dry-run --aggressive

    # 执行激进精简（只保留 cell_type）
    python scripts/filter_cell_marker_kb.py --aggressive --output knowledge/source/cell_marker_kb_filtered.jsonl

    # 精简 + 截断长文本
    python scripts/filter_cell_marker_kb.py --aggressive --truncate

    # 保守精简：保留 cell_type + 最多 10,000 条 marker_gene（按关联丰富度排序）
    python scripts/filter_cell_marker_kb.py --marker-cap 10000
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "kb" / "cell_marker_kb.jsonl"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parents[1] / "knowledge" / "source" / "cell_marker_kb_filtered.jsonl"
)

# 截断配置（字符数）
DEFAULT_MAX_CONTENT_LEN = 800
DEFAULT_MAX_RETRIEVAL_LEN = 1200
DEFAULT_MAX_KEYWORDS = 15
DEFAULT_MAX_RELATED_TERMS = 15
DEFAULT_MAX_ALIASES = 8
DEFAULT_MAX_METADATA_VALUES = 5


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """逐行解析 JSONL，返回纯字典列表。"""
    records = []
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError:
                pass
    return records


def _truncate_field(value: str | list | None, max_len: int) -> str | list:
    """对字符串做字符截断，对列表做长度截断。"""
    if value is None:
        return [] if isinstance(value, list) else ""
    if isinstance(value, list):
        return value[:max_len]
    if isinstance(value, str):
        return value[:max_len]
    return value


def _compact_list(items: list, limit: int) -> list:
    """去重保序并截断。"""
    seen: set[str] = set()
    result = []
    for item in items:
        key = str(item).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(str(item).strip())
        if len(result) >= limit:
            break
    return result


def _richer_record(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """
    比较两条记录，返回信息更丰富的那条。
    比较优先级：marker_genes 数量 > content 长度 > keywords 数量 > related_terms 数量。
    """
    def score(r: dict[str, Any]) -> tuple[int, int, int, int]:
        marker_len = len(r.get("marker_genes") or [])
        content_len = len(r.get("content") or "")
        keyword_len = len(r.get("keywords") or [])
        related_len = len(r.get("related_terms") or [])
        return (marker_len, content_len, keyword_len, related_len)

    return a if score(a) >= score(b) else b


def _truncate_record(record: dict[str, Any], max_content_len: int, max_retrieval_len: int) -> dict[str, Any]:
    """对单条记录的关键字段做截断。"""
    out = dict(record)

    # 列表字段截断
    for list_field in ("keywords", "related_terms", "aliases", "question_examples",
                       "marker_genes", "disease_related", "children"):
        if list_field in out and isinstance(out[list_field], list):
            limit = {
                "keywords": DEFAULT_MAX_KEYWORDS,
                "related_terms": DEFAULT_MAX_RELATED_TERMS,
                "aliases": DEFAULT_MAX_ALIASES,
                "question_examples": 4,
                "marker_genes": 6,
                "disease_related": 4,
                "children": 8,
            }.get(list_field, 20)
            out[list_field] = _compact_list(out[list_field], limit)

    # 文本字段截断
    if "content" in out and isinstance(out["content"], str):
        out["content"] = out["content"][:max_content_len]

    if "retrieval_text" in out and isinstance(out["retrieval_text"], str):
        out["retrieval_text"] = out["retrieval_text"][:max_retrieval_len]

    # metadata 简化（只保留关键字段）
    metadata = out.get("metadata") or {}
    if isinstance(metadata, dict):
        key_fields = [
            "species", "tissue_type", "disease", "cellontology_id",
            "marker_source", "pmid", "journal", "year",
        ]
        simplified = {k: v for k, v in metadata.items() if k in key_fields}
        # 对列表字段做截断
        for k, v in list(simplified.items()):
            if isinstance(v, list):
                simplified[k] = _compact_list(v, DEFAULT_MAX_METADATA_VALUES)
        out["metadata"] = simplified

    return out


def _extract_gene_symbol(record: dict[str, Any]) -> str:
    """从 marker_gene 记录中提取基因符号。"""
    # 优先从 title 提取
    symbol = str(record.get("title") or "").strip().upper()
    if symbol:
        return symbol
    # 从 doc_id 提取（格式为 marker_xxx）
    doc_id = str(record.get("doc_id") or "").strip()
    if doc_id.startswith("marker_"):
        return doc_id[len("marker_"):].upper()
    # 从 metadata.gene_name 提取
    meta = record.get("metadata") or {}
    if isinstance(meta, dict):
        gene_name = str(meta.get("gene_name") or "").strip().upper()
        if gene_name:
            return gene_name
        symbol_field = str(meta.get("symbol") or "").strip().upper()
        if symbol_field:
            return symbol_field
    return ""


def filter_knowledge_base(
    *,
    input_path: Path,
    output_path: Path | None = None,
    dry_run: bool = False,
    aggressive: bool = False,
    marker_cap: int | None = None,
    truncate: bool = False,
    max_content_len: int = DEFAULT_MAX_CONTENT_LEN,
    max_retrieval_len: int = DEFAULT_MAX_RETRIEVAL_LEN,
) -> dict[str, Any]:
    """
    读取 JSONL，执行精简/去重/截断，写入新文件。

    Args:
        aggressive: True 时丢弃所有 marker_gene 条目，只保留 cell_type。
        marker_cap: 最多保留 N 条 marker_gene（按关联细胞类型丰富度排序）。
                    aggressive 和 marker_cap 互斥。
    """
    print(f"[*] 读取: {input_path}")
    records = _load_jsonl(input_path)
    total_in = len(records)
    print(f"[*] 共 {total_in} 条记录")

    # 按 category 分组
    cell_type_records: list[dict[str, Any]] = []
    marker_records: list[dict[str, Any]] = []
    other_records: list[dict[str, Any]] = []

    for rec in records:
        cat = str(rec.get("category") or "").strip().lower()
        if cat == "cell_type":
            cell_type_records.append(rec)
        elif cat == "marker_gene":
            marker_records.append(rec)
        else:
            other_records.append(rec)

    print(f"    cell_type : {len(cell_type_records)} 条")
    print(f"    marker_gene: {len(marker_records)} 条")
    print(f"    other     : {len(other_records)} 条")

    # ---- marker_gene 处理策略 ----
    kept_markers: list[dict[str, Any]] = []

    if aggressive:
        print("[*] 模式: --aggressive（丢弃所有 marker_gene，仅保留 cell_type）")
        kept_markers = []

    elif marker_cap is not None and marker_cap > 0:
        print(f"[*] 模式: --marker-cap {marker_cap}（按关联丰富度排序，保留 top {marker_cap} 条 marker_gene）")
        # 关联丰富度 = related_cell_types 数量 + disease 数量 + tissue 数量
        def marker_richness(rec: dict[str, Any]) -> int:
            meta = rec.get("metadata") or {}
            score = 0
            related = meta.get("related_cell_types") or []
            if isinstance(related, list):
                score += len(related)
            diseases = [d for d in (meta.get("disease") or "").split(",") if d.strip()]
            score += len(diseases)
            tissues = [t for t in (meta.get("tissue_type") or "").split(",") if t.strip()]
            score += len(tissues)
            return score

        sorted_markers = sorted(marker_records, key=marker_richness, reverse=True)
        kept_markers = sorted_markers[:marker_cap]
        print(f"    保留 {len(kept_markers)} 条 marker_gene（丢弃 {len(marker_records) - len(kept_markers)} 条）")

    else:
        # 默认：按基因符号去重
        print("[*] 模式: 默认去重（marker_gene 按基因符号去重）")
        symbol_to_best: dict[str, dict[str, Any]] = {}
        for rec in marker_records:
            symbol = _extract_gene_symbol(rec)
            if not symbol:
                symbol = f"_unknown_{len(symbol_to_best)}"
            if symbol in symbol_to_best:
                symbol_to_best[symbol] = _richer_record(symbol_to_best[symbol], rec)
            else:
                symbol_to_best[symbol] = rec
        kept_markers = list(symbol_to_best.values())
        print(f"    去重后: {len(kept_markers)} 条（减少了 {len(marker_records) - len(kept_markers)} 条）")

    # ---- 合并输出 ----
    output_records: list[dict[str, Any]] = []
    output_records.extend(cell_type_records)
    output_records.extend(kept_markers)
    output_records.extend(other_records)

    # ---- 截断 ----
    if truncate:
        print(f"[*] 截断长文本 (content<={max_content_len}, retrieval_text<={max_retrieval_len}) ...")
        before_sizes = [len(r.get("content", "") or "") for r in output_records]
        output_records = [
            _truncate_record(r, max_content_len, max_retrieval_len) for r in output_records
        ]
        after_sizes = [len(r.get("content", "") or "") for r in output_records]
        print(f"    content 平均长度: {sum(before_sizes)/max(1, len(before_sizes)):.0f} → {sum(after_sizes)/max(1, len(after_sizes)):.0f} 字符")

    total_out = len(output_records)
    compression = (1 - total_out / total_in) * 100
    print(f"[*] 输出记录总数: {total_out} 条")
    print(f"    压缩: {total_in} → {total_out} （减少 {compression:.1f}%）")
    print(f"[*] 预估 embedding batches（batch_size=256）: ~{max(1, (total_out + 255) // 256)} 批次")

    if dry_run:
        print("[*] --dry-run: 不写入文件，仅预览")
        return {
            "input_total": total_in,
            "output_total": total_out,
            "cell_type_count": len(cell_type_records),
            "marker_gene_kept": len(kept_markers),
            "marker_gene_dropped": len(marker_records) - len(kept_markers),
            "compression_ratio": round(1 - total_out / total_in, 4),
            "estimated_batches_256": (total_out + 255) // 256,
        }

    if output_path is None:
        output_path = DEFAULT_OUTPUT

    print(f"[*] 写入: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        for rec in output_records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("[+] 完成")

    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "input_total": total_in,
        "output_total": total_out,
        "cell_type_count": len(cell_type_records),
        "marker_gene_kept": len(kept_markers),
        "marker_gene_dropped": len(marker_records) - len(kept_markers),
        "compression_ratio": round(1 - total_out / total_in, 4),
        "estimated_batches_256": (total_out + 255) // 256,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="精简 cell_marker_kb.jsonl：去重/过滤 marker_gene，保留 cell_type，可选截断长文本。",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="输入 JSONL 路径（默认: data/kb/cell_marker_kb.jsonl）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出 JSONL 路径（默认: knowledge/source/cell_marker_kb_filtered.jsonl）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅统计并打印结果，不写入文件",
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="激进精简：丢弃所有 marker_gene 条目，仅保留 cell_type（推荐，36,401 条）",
    )
    parser.add_argument(
        "--marker-cap",
        type=int,
        default=None,
        help="保守精简：保留最多 N 条 marker_gene（按关联细胞类型丰富度排序）",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="对 content / retrieval_text / 列表字段做截断，减少 embedding token 量",
    )
    parser.add_argument(
        "--max-content-len",
        type=int,
        default=DEFAULT_MAX_CONTENT_LEN,
        help=f"content 字段最大字符数（默认: {DEFAULT_MAX_CONTENT_LEN}）",
    )
    parser.add_argument(
        "--max-retrieval-len",
        type=int,
        default=DEFAULT_MAX_RETRIEVAL_LEN,
        help=f"retrieval_text 字段最大字符数（默认: {DEFAULT_MAX_RETRIEVAL_LEN}）",
    )
    args = parser.parse_args()

    result = filter_knowledge_base(
        input_path=args.input,
        output_path=args.output,
        dry_run=args.dry_run,
        aggressive=args.aggressive,
        marker_cap=args.marker_cap,
        truncate=args.truncate,
        max_content_len=args.max_content_len,
        max_retrieval_len=args.max_retrieval_len,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
