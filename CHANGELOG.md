# Changelog — seo-keywords

## [1.3.0] — 2026-06-06

### SEO/AEO/GEO vector records

- Extended `scripts/vectorize-records.py` to ingest vNext JSONL files: `triplets`, `answer_units`, `synthetic_prompts`, `entity_coverage`, `eeat_evidence`, `local_seo_signals`, `commercial_factors`, `ai_visibility_checks`, `traffic_diagnostics`, and `source_pack`.
- Added vector text fields for `intent_stage`, `page_format_preference`, `answer_unit_type`, `entity_coverage_status`, `competitor_median_coverage`, `similarity_score`, and `synthetic_prompt_group`.
- Updated multipass documentation and prompts for Answer Units, synthetic AI prompts, entity coverage, source-pack reuse, and controlled iterative unpacking.
- Added tests for vNext vector ingestion and neighbor report generation.
