#!/usr/bin/env python3
"""
Local vectorization for multi-pass SEO records.

No external API. Builds lightweight TF-IDF vectors from JSONL records and writes:
- vector/similarity.jsonl
- vector/neighbor-report.md

This is a deterministic local baseline. For production semantic embeddings, keep
the same input/output contract and replace the vectorizer only.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
from dataclasses import dataclass
from typing import Any


TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9][A-Za-zА-Яа-яЁё0-9._-]{1,}")


@dataclass(frozen=True)
class Doc:
    doc_id: str
    record_type: str
    label: str
    slug: str
    text: str
    source_file: str


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in {path}:{lineno}: {exc}") from exc
    return out


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)
    if isinstance(value, dict):
        parts = []
        for key, val in value.items():
            parts.append(str(key))
            parts.append(flatten(val))
        return " ".join(parts)
    return str(value)


def record_to_doc(record: dict[str, Any], source_file: str, index: int) -> Doc:
    record_type = str(record.get("record_type") or source_file.replace(".jsonl", ""))
    slug = str(
        record.get("slug")
        or record.get("entity_slug")
        or record.get("seed_slug")
        or record.get("target_slug")
        or record.get("answer_unit_id")
        or record.get("prompt_id")
        or record.get("sub_intent_id")
        or record.get("subject")
        or record.get("final_cluster")
        or record.get("query")
        or f"{record_type}-{index}"
    )
    label = str(
        record.get("label")
        or record.get("title")
        or record.get("claim")
        or record.get("answer_unit")
        or record.get("prompt")
        or record.get("query")
        or record.get("sub_intent")
        or record.get("final_cluster")
        or slug
    )
    doc_id = f"{source_file}:{index}:{slug}"
    important_fields = [
        "topic",
        "record_type",
        "slug",
        "label",
        "intent",
        "intent_stage",
        "page_targets",
        "page_target",
        "page_format_preference",
        "relations",
        "evidence",
        "confidence",
        "reuse_scope",
        "subject",
        "predicate",
        "object",
        "priority",
        "surface",
        "evidence_status",
        "claim",
        "answer_snippet",
        "answer_unit",
        "answer_unit_type",
        "thesis",
        "context",
        "proof",
        "conclusion",
        "sub_intent",
        "sub_intents",
        "sub_intent_id",
        "target_slug",
        "entity_coverage_status",
        "competitor_median_coverage",
        "similarity_score",
        "synthetic_prompt_group",
        "prompt",
        "prompt_group",
        "source_label",
        "source_url",
        "source_topic",
    ]
    text = " ".join(flatten(record.get(field)) for field in important_fields)
    if not text.strip():
        text = flatten(record)
    return Doc(doc_id=doc_id, record_type=record_type, label=label, slug=slug, text=text, source_file=source_file)


def tokenize(text: str) -> list[str]:
    base = [t.lower().replace("ё", "е") for t in TOKEN_RE.findall(text)]
    # Add simple character trigrams for Russian/English morphology robustness.
    grams: list[str] = []
    for token in base:
        if len(token) >= 5:
            grams.extend(f"ch:{token[i:i+3]}" for i in range(len(token) - 2))
    return base + grams


def build_vectors(docs: list[Doc]) -> list[dict[str, float]]:
    term_counts = [collections.Counter(tokenize(doc.text)) for doc in docs]
    df: collections.Counter[str] = collections.Counter()
    for counts in term_counts:
        df.update(counts.keys())
    total = len(docs)
    vectors: list[dict[str, float]] = []
    for counts in term_counts:
        vec: dict[str, float] = {}
        for term, count in counts.items():
            tf = 1.0 + math.log(count)
            idf = math.log((1 + total) / (1 + df[term])) + 1.0
            vec[term] = tf * idf
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vectors.append({term: val / norm for term, val in vec.items()})
    return vectors


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(val * b.get(term, 0.0) for term, val in a.items())


def load_docs(vector_dir: pathlib.Path) -> list[Doc]:
    docs: list[Doc] = []
    for filename in [
        "records.jsonl",
        "relations.jsonl",
        "triplets.jsonl",
        "evidence.jsonl",
        "subintents.jsonl",
        "sub_intents.jsonl",
        "answer_units.jsonl",
        "synthetic_prompts.jsonl",
        "entity_coverage.jsonl",
        "eeat_evidence.jsonl",
        "local_seo_signals.jsonl",
        "commercial_factors.jsonl",
        "ai_visibility_checks.jsonl",
        "traffic_diagnostics.jsonl",
        "source_pack.jsonl",
    ]:
        path = vector_dir / filename
        for idx, record in enumerate(read_jsonl(path), 1):
            docs.append(record_to_doc(record, filename, idx))
    return docs


def similarity_band(score: float) -> str:
    if score >= 0.82:
        return "duplicate_or_cannibalization"
    if score >= 0.62:
        return "close_neighbor"
    if score >= 0.42:
        return "bridge_candidate"
    return "weak"


def write_outputs(vector_dir: pathlib.Path, docs: list[Doc], vectors: list[dict[str, float]], top_k: int, min_score: float) -> None:
    pairs: list[dict[str, Any]] = []
    for i, doc in enumerate(docs):
        scored = []
        for j, other in enumerate(docs):
            if i == j:
                continue
            score = cosine(vectors[i], vectors[j])
            if score >= min_score:
                scored.append((score, other))
        scored.sort(key=lambda item: item[0], reverse=True)
        for score, other in scored[:top_k]:
            pairs.append(
                {
                    "source_id": doc.doc_id,
                    "source_slug": doc.slug,
                    "source_type": doc.record_type,
                    "target_id": other.doc_id,
                    "target_slug": other.slug,
                    "target_type": other.record_type,
                    "score": round(score, 4),
                    "band": similarity_band(score),
                }
            )

    (vector_dir / "similarity.jsonl").write_text(
        "\n".join(json.dumps(pair, ensure_ascii=False) for pair in pairs) + ("\n" if pairs else ""),
        encoding="utf-8",
    )

    by_source: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for pair in pairs:
        by_source[pair["source_id"]].append(pair)

    lines = ["# Vector neighbor report", ""]
    lines.append(f"- Documents: {len(docs)}")
    lines.append(f"- Pairs written: {len(pairs)}")
    lines.append(f"- min_score: {min_score}")
    lines.append(f"- top_k: {top_k}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- `>=0.82`: likely duplicate/cannibalization.")
    lines.append("- `0.62-0.82`: close neighbor, good internal-link or shared FAQ candidate.")
    lines.append("- `0.42-0.62`: bridge candidate, may need a connecting FAQ/paragraph.")
    lines.append("")
    lines.append("## Neighbors")
    lines.append("")
    doc_by_id = {doc.doc_id: doc for doc in docs}
    for doc in docs:
        neighbors = by_source.get(doc.doc_id, [])
        lines.append(f"### {doc.slug} ({doc.record_type})")
        if not neighbors:
            lines.append("")
            lines.append("- No neighbors above threshold. Candidate for manual review or iterative unpacking if priority is high.")
            lines.append("")
            continue
        for pair in neighbors:
            target = doc_by_id[pair["target_id"]]
            lines.append(f"- {pair['score']:.4f} `{pair['band']}` -> `{target.slug}` ({target.record_type})")
        lines.append("")
    (vector_dir / "neighbor-report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=pathlib.Path, help="Multi-pass run directory")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=0.18)
    args = parser.parse_args()

    vector_dir = args.run_dir / "vector"
    if not vector_dir.exists():
        raise SystemExit(f"Vector dir not found: {vector_dir}")
    docs = load_docs(vector_dir)
    if not docs:
        raise SystemExit(f"No JSONL records found in {vector_dir}")
    vectors = build_vectors(docs)
    write_outputs(vector_dir, docs, vectors, args.top_k, args.min_score)
    print(f"Vectorized {len(docs)} docs")
    print(f"Wrote {vector_dir / 'similarity.jsonl'}")
    print(f"Wrote {vector_dir / 'neighbor-report.md'}")


if __name__ == "__main__":
    main()
