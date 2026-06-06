#!/usr/bin/env python3
"""Tests for vNext vector record inputs."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "vectorize-records.py"


class VectorizeRecordsTest(unittest.TestCase):
    def make_run_dir(self) -> pathlib.Path:
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="seo-keywords-vector-"))
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        vector = tmp / "vector"
        vector.mkdir(parents=True)
        return tmp

    def write_jsonl(self, vector_dir: pathlib.Path, filename: str, rows: list[dict]) -> None:
        vector_dir.joinpath(filename).write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
            encoding="utf-8",
        )

    def test_vectorizer_reads_vnext_answer_prompt_and_coverage_records(self) -> None:
        run_dir = self.make_run_dir()
        vector = run_dir / "vector"
        self.write_jsonl(
            vector,
            "answer_units.jsonl",
            [
                {
                    "record_type": "answer_unit",
                    "answer_unit_id": "osb-answer-1",
                    "answer_unit": "ОСП-3 подходит для чернового пола при правильном подборе толщины.",
                    "answer_unit_type": "commercial_direct_answer",
                    "intent_stage": "MOFU",
                    "synthetic_prompt_group": "comparison",
                    "thesis": "ОСП-3 подходит для пола.",
                    "proof": "Нужна проверка по стандарту и нагрузке.",
                }
            ],
        )
        self.write_jsonl(
            vector,
            "synthetic_prompts.jsonl",
            [
                {
                    "record_type": "synthetic_prompt",
                    "prompt_id": "osb-prompt-1",
                    "prompt": "Какую ОСП выбрать для пола в частном доме?",
                    "prompt_group": "selection",
                    "page_format_preference": "category_faq",
                }
            ],
        )
        self.write_jsonl(
            vector,
            "entity_coverage.jsonl",
            [
                {
                    "record_type": "entity_coverage",
                    "entity_slug": "osp-3",
                    "label": "ОСП-3",
                    "entity_coverage_status": "underdeveloped",
                    "competitor_median_coverage": 4,
                    "similarity_score": 0.51,
                }
            ],
        )

        subprocess.run([sys.executable, str(SCRIPT), str(run_dir), "--top-k", "2", "--min-score", "0.01"], check=True)

        report = vector.joinpath("neighbor-report.md").read_text(encoding="utf-8")
        similarity = vector.joinpath("similarity.jsonl").read_text(encoding="utf-8")
        self.assertIn("osb-answer-1", report)
        self.assertIn("osb-prompt-1", report)
        self.assertIn("osp-3", report)
        self.assertTrue(similarity.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
