from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_INPUT = REPO_ROOT / "data" / "kb" / "all_cell_marker" / "all_cell_marker.txt"
DEFAULT_INPUT = (
    REPO_ROOT / "knowledge" / "source" / "raw" / "all_cell_marker.txt"
    if (REPO_ROOT / "knowledge" / "source" / "raw" / "all_cell_marker.txt").exists()
    else LEGACY_INPUT
)
DEFAULT_OUTPUT = REPO_ROOT / "knowledge" / "source" / "cell_marker_kb.jsonl"

TOKEN_SPLIT_RE = re.compile(r"[\s,;/|]+")


def normalize_text(value: object) -> str:
    return str(value or "").strip()


def slugify(value: str) -> str:
    normalized = normalize_text(value).lower()
    normalized = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "item"


def dedupe_keep_order(items: Iterable[object]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = normalize_text(item)
        key = value.casefold()
        if not value or key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def compact_list(items: Iterable[object], *, limit: int | None = None) -> list[str]:
    values = dedupe_keep_order(items)
    return values[:limit] if limit is not None else values


def maybe_int_string(value: str) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    if text.endswith(".0"):
        return text[:-2]
    return text


def build_retrieval_text(payload: dict) -> str:
    lines: list[str] = []

    def add_line(label: str, values: Iterable[object] | object) -> None:
        if isinstance(values, (list, tuple, set)):
            rendered = ", ".join(compact_list(values))
        else:
            rendered = normalize_text(values)
        if rendered:
            lines.append(f"{label}: {rendered}")

    add_line("Title", payload.get("title"))
    add_line("Category", payload.get("category"))
    add_line("Aliases", payload.get("aliases") or [])
    add_line("Keywords", payload.get("keywords") or [])
    add_line("Question Examples", payload.get("question_examples") or [])
    add_line("Summary", payload.get("summary"))
    add_line("Content", payload.get("content"))
    add_line("Related Terms", payload.get("related_terms") or [])
    add_line("Marker Genes", payload.get("marker_genes") or [])
    add_line("Disease Related", payload.get("disease_related") or [])

    metadata = payload.get("metadata") or {}
    if isinstance(metadata, dict):
        ordered_meta_parts = []
        for key in [
            "species",
            "tissue_class",
            "tissue_type",
            "uberon_id",
            "disease",
            "cellontology_id",
            "technology_seq",
            "marker_source",
            "journal",
            "year",
            "method_details",
        ]:
            value = normalize_text(metadata.get(key))
            if value:
                ordered_meta_parts.append(f"{key}={value}")
        if ordered_meta_parts:
            lines.append("Metadata: " + "; ".join(ordered_meta_parts))

    return "\n".join(lines)


def detect_dialect(path: Path) -> csv.Dialect:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters="\t,")
    except csv.Error:
        return csv.excel_tab


@dataclass
class CellTypeAggregate:
    species: str
    tissue_class: str
    tissue_type: str
    uberon_id: str
    disease: str
    cell_name_class: str
    cell_name: str
    cellontology_id: str
    aliases: set[str] = field(default_factory=set)
    keywords: set[str] = field(default_factory=set)
    related_terms: set[str] = field(default_factory=set)
    marker_genes: list[str] = field(default_factory=list)
    gene_names: set[str] = field(default_factory=set)
    technologies: set[str] = field(default_factory=set)
    marker_sources: set[str] = field(default_factory=set)
    pmids: set[str] = field(default_factory=set)
    titles: set[str] = field(default_factory=set)
    journals: set[str] = field(default_factory=set)
    years: set[str] = field(default_factory=set)
    series_ids: set[str] = field(default_factory=set)
    methods: set[str] = field(default_factory=set)


@dataclass
class MarkerAggregate:
    symbol: str
    marker: str
    gene_id: str
    gene_type: str
    gene_name: str
    uniprot_id: str
    aliases: set[str] = field(default_factory=set)
    related_cell_types: set[str] = field(default_factory=set)
    related_terms: set[str] = field(default_factory=set)
    species: set[str] = field(default_factory=set)
    tissues: set[str] = field(default_factory=set)
    diseases: set[str] = field(default_factory=set)
    technologies: set[str] = field(default_factory=set)
    marker_sources: set[str] = field(default_factory=set)
    pmids: set[str] = field(default_factory=set)
    titles: set[str] = field(default_factory=set)
    journals: set[str] = field(default_factory=set)
    years: set[str] = field(default_factory=set)
    methods: set[str] = field(default_factory=set)


def build_celltype_questions(cell_name: str, tissue_type: str, disease: str, marker_genes: list[str]) -> list[str]:
    disease_text = disease if disease and disease.lower() != "normal" else "该组织场景"
    top_markers = marker_genes[:3]
    marker_phrase = "、".join(top_markers) if top_markers else "常见 marker"
    return compact_list(
        [
            f"{cell_name}是什么？",
            f"{cell_name}有哪些marker？",
            f"{cell_name}在{tissue_type}中的作用是什么？" if tissue_type else "",
            f"{cell_name}在{disease_text}中有什么作用？",
            f"{cell_name} marker",
            f"{cell_name}和{marker_phrase}有什么关系？" if marker_phrase else "",
        ],
        limit=6,
    )


def build_marker_questions(symbol: str, gene_name: str, cell_types: list[str]) -> list[str]:
    example_cell_type = cell_types[0] if cell_types else "哪些细胞"
    return compact_list(
        [
            f"{symbol}是什么？",
            f"{symbol}代表什么细胞？",
            f"哪些细胞表达{symbol}？",
            f"{symbol}和{example_cell_type}有什么关系？" if example_cell_type else "",
            f"{symbol} marker gene",
            f"{gene_name}对应什么功能？" if gene_name else "",
        ],
        limit=6,
    )


def celltype_payload(agg: CellTypeAggregate) -> dict:
    marker_genes = compact_list(agg.marker_genes, limit=12)
    disease_related = compact_list([agg.disease] if agg.disease and agg.disease.lower() != "normal" else [])
    aliases = compact_list(
        [
            agg.cell_name,
            agg.cell_name_class,
            f"{agg.tissue_type} {agg.cell_name}" if agg.tissue_type else "",
            f"{agg.species} {agg.cell_name}" if agg.species else "",
        ]
        + list(agg.aliases),
        limit=8,
    )
    keywords = compact_list(
        [
            agg.cell_name,
            agg.cell_name_class,
            agg.tissue_type,
            agg.tissue_class,
            agg.species,
            agg.disease,
            *marker_genes[:6],
        ]
        + list(agg.keywords),
        limit=20,
    )
    related_terms = compact_list(
        [agg.tissue_type, agg.tissue_class, agg.disease, *marker_genes[:8]] + list(agg.related_terms),
        limit=20,
    )
    summary = (
        f"{agg.cell_name} 是 {agg.species} {agg.tissue_type} 中的细胞类型，"
        f"常见 marker gene 包括 {', '.join(marker_genes[:5]) or '待补充'}。"
    )
    content_parts = [
        f"{agg.cell_name}（{agg.cell_name_class or agg.cell_name}）在 {agg.species} 的 {agg.tissue_type or agg.tissue_class or '组织'} 中被记录为 marker 相关细胞类型。",
        f"该细胞在当前数据源中关联的 marker gene 包括 {', '.join(marker_genes) or '待补充'}。",
    ]
    if agg.disease:
        content_parts.append(f"该条目对应的疾病/状态场景为 {agg.disease}。")
    if agg.technologies:
        content_parts.append(f"相关数据来自 {', '.join(compact_list(agg.technologies, limit=4))} 等技术。")
    if agg.methods:
        content_parts.append(f"文献或数据库记录的方法细节包括 {', '.join(compact_list(agg.methods, limit=4))}。")
    payload = {
        "doc_id": f"celltype_{slugify(agg.species)}_{slugify(agg.tissue_type)}_{slugify(agg.cell_name)}",
        "source": "all_cell_marker",
        "category": "cell_type",
        "title": agg.cell_name,
        "aliases": aliases,
        "keywords": keywords,
        "question_examples": build_celltype_questions(agg.cell_name, agg.tissue_type, agg.disease, marker_genes),
        "content": " ".join(part for part in content_parts if part),
        "summary": summary,
        "related_terms": related_terms,
        "marker_genes": marker_genes,
        "disease_related": disease_related,
        "metadata": {
            "species": agg.species,
            "tissue_class": agg.tissue_class,
            "tissue_type": agg.tissue_type,
            "uberon_id": agg.uberon_id,
            "disease": agg.disease,
            "cellontology_id": agg.cellontology_id,
            "technology_seq": compact_list(agg.technologies, limit=6),
            "marker_source": compact_list(agg.marker_sources, limit=6),
            "pmid": compact_list(agg.pmids, limit=6),
            "journal": compact_list(agg.journals, limit=4),
            "year": compact_list(agg.years, limit=4),
            "series_id": compact_list(agg.series_ids, limit=6),
            "method_details": compact_list(agg.methods, limit=6),
            "titles": compact_list(agg.titles, limit=3),
        },
    }
    payload["retrieval_text"] = build_retrieval_text(payload)
    return payload


def marker_payload(agg: MarkerAggregate) -> dict:
    related_cell_types = compact_list(agg.related_cell_types, limit=12)
    aliases = compact_list([agg.symbol, agg.marker, agg.gene_name] + list(agg.aliases), limit=8)
    keywords = compact_list(
        [
            agg.symbol,
            agg.marker,
            agg.gene_name,
            agg.gene_type,
            *related_cell_types[:6],
            *compact_list(agg.tissues, limit=4),
        ],
        limit=20,
    )
    diseases = compact_list(item for item in agg.diseases if item and item.lower() != "normal")
    summary = (
        f"{agg.symbol} 是一个与 {', '.join(related_cell_types[:3]) or '相关细胞类型'} 有关的 marker gene，"
        f"在当前知识源中关联基因名称为 {agg.gene_name or agg.symbol}。"
    )
    content_parts = [
        f"{agg.symbol}（{agg.gene_name or agg.marker or agg.symbol}）在 all_cell_marker 数据源中被记录为 marker gene。",
        f"它关联的细胞类型包括 {', '.join(related_cell_types) or '待补充'}。",
    ]
    if diseases:
        content_parts.append(f"相关疾病/状态包括 {', '.join(diseases[:6])}。")
    if agg.tissues:
        content_parts.append(f"相关组织包括 {', '.join(compact_list(agg.tissues, limit=6))}。")
    payload = {
        "doc_id": f"marker_{slugify(agg.symbol)}",
        "source": "all_cell_marker",
        "category": "marker_gene",
        "title": agg.symbol,
        "aliases": aliases,
        "keywords": keywords,
        "question_examples": build_marker_questions(agg.symbol, agg.gene_name, related_cell_types),
        "content": " ".join(part for part in content_parts if part),
        "summary": summary,
        "related_terms": compact_list(list(agg.related_terms) + related_cell_types + diseases, limit=20),
        "marker_genes": [agg.symbol],
        "disease_related": diseases[:8],
        "metadata": {
            "gene_id": agg.gene_id,
            "gene_type": agg.gene_type,
            "gene_name": agg.gene_name,
            "uniprot_id": agg.uniprot_id,
            "species": compact_list(agg.species, limit=6),
            "tissue_type": compact_list(agg.tissues, limit=8),
            "related_cell_types": related_cell_types,
            "technology_seq": compact_list(agg.technologies, limit=6),
            "marker_source": compact_list(agg.marker_sources, limit=6),
            "pmid": compact_list(agg.pmids, limit=6),
            "journal": compact_list(agg.journals, limit=4),
            "year": compact_list(agg.years, limit=4),
            "method_details": compact_list(agg.methods, limit=6),
            "titles": compact_list(agg.titles, limit=3),
        },
    }
    payload["retrieval_text"] = build_retrieval_text(payload)
    return payload


def build_documents(input_path: Path) -> list[dict]:
    dialect = detect_dialect(input_path)
    celltype_map: dict[tuple[str, ...], CellTypeAggregate] = {}
    marker_map: dict[str, MarkerAggregate] = {}

    with input_path.open("r", encoding="utf-8", errors="ignore", newline="") as fh:
        reader = csv.DictReader(fh, dialect=dialect)
        for raw_row in reader:
            if not raw_row:
                continue
            row = {normalize_text(key): normalize_text(value) for key, value in raw_row.items()}
            species = row.get("species", "")
            tissue_class = row.get("tissue_class", "")
            tissue_type = row.get("tissue_type", "")
            uberon_id = row.get("uberon_id", "")
            disease = row.get("disease", "")
            cell_name_class = row.get("cell_name_class", "")
            cell_name = row.get("cell_name", "")
            cellontology_id = row.get("cellontology_id", "")
            marker = row.get("marker", "")
            symbol = row.get("symbol", "") or marker
            gene_id = maybe_int_string(row.get("gene_id", ""))
            gene_type = row.get("gene_type", "")
            gene_name = row.get("gene_name", "")
            uniprot_id = row.get("uniprot_id", "")
            technology_seq = row.get("technology_seq", "")
            marker_source = row.get("marker_source", "")
            pmid = maybe_int_string(row.get("pmid", ""))
            title = row.get("title", "")
            journal = row.get("journal", "")
            year = maybe_int_string(row.get("year", ""))
            series_id = row.get("series_id", "")
            method_details = row.get("method_details", "")

            if not cell_name and not symbol:
                continue

            cell_key = (
                species,
                tissue_class,
                tissue_type,
                uberon_id,
                disease,
                cell_name_class,
                cell_name,
                cellontology_id,
            )
            if cell_key not in celltype_map:
                celltype_map[cell_key] = CellTypeAggregate(
                    species=species,
                    tissue_class=tissue_class,
                    tissue_type=tissue_type,
                    uberon_id=uberon_id,
                    disease=disease,
                    cell_name_class=cell_name_class,
                    cell_name=cell_name,
                    cellontology_id=cellontology_id,
                )
            cell_agg = celltype_map[cell_key]
            cell_agg.aliases.update(item for item in [cell_name_class] if item and item != cell_name)
            cell_agg.keywords.update(
                item
                for item in [
                    species,
                    tissue_class,
                    tissue_type,
                    disease,
                    marker,
                    symbol,
                    technology_seq,
                    marker_source,
                    method_details,
                ]
                if item
            )
            cell_agg.related_terms.update(item for item in [gene_name, journal, marker_source] if item)
            if symbol:
                cell_agg.marker_genes.append(symbol)
            if gene_name:
                cell_agg.gene_names.add(gene_name)
            for target_set, value in [
                (cell_agg.technologies, technology_seq),
                (cell_agg.marker_sources, marker_source),
                (cell_agg.pmids, pmid),
                (cell_agg.titles, title),
                (cell_agg.journals, journal),
                (cell_agg.years, year),
                (cell_agg.series_ids, series_id),
                (cell_agg.methods, method_details),
            ]:
                if value:
                    target_set.add(value)

            marker_key = symbol or marker
            if marker_key:
                if marker_key not in marker_map:
                    marker_map[marker_key] = MarkerAggregate(
                        symbol=symbol or marker,
                        marker=marker,
                        gene_id=gene_id,
                        gene_type=gene_type,
                        gene_name=gene_name,
                        uniprot_id=uniprot_id,
                    )
                marker_agg = marker_map[marker_key]
                marker_agg.aliases.update(item for item in [marker, gene_name, uniprot_id] if item and item != symbol)
                marker_agg.related_cell_types.add(cell_name)
                marker_agg.related_terms.update(
                    item for item in [cell_name, cell_name_class, tissue_type, tissue_class, disease] if item
                )
                for target_set, value in [
                    (marker_agg.species, species),
                    (marker_agg.tissues, tissue_type or tissue_class),
                    (marker_agg.diseases, disease),
                    (marker_agg.technologies, technology_seq),
                    (marker_agg.marker_sources, marker_source),
                    (marker_agg.pmids, pmid),
                    (marker_agg.titles, title),
                    (marker_agg.journals, journal),
                    (marker_agg.years, year),
                    (marker_agg.methods, method_details),
                ]:
                    if value:
                        target_set.add(value)

    documents: list[dict] = []
    for agg in celltype_map.values():
        documents.append(celltype_payload(agg))
    for agg in marker_map.values():
        documents.append(marker_payload(agg))

    documents.sort(key=lambda item: (item.get("category") or "", item.get("title") or ""))
    return documents


def write_jsonl(documents: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        for payload in documents:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 all_cell_marker.txt 聚合转换为适合 RAG 检索的 JSONL，并自动生成 retrieval_text。"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="输入的 all_cell_marker 文本路径")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出 JSONL 路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"输入文件不存在: {args.input}")

    documents = build_documents(args.input)
    write_jsonl(documents, args.output)
    category_counts: dict[str, int] = defaultdict(int)
    for item in documents:
        category_counts[str(item.get("category") or "unknown")] += 1

    print(f"Generated {len(documents)} documents -> {args.output}")
    for category, count in sorted(category_counts.items()):
        print(f"  - {category}: {count}")


if __name__ == "__main__":
    main()
