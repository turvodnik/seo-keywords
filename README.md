# seo-keywords

Version: `1.3.0`

**Фазовый скилл сбора семантики и кластеризации** (Phase 2-3 модульной архитектуры `seo-cycle`).
Собирает ключи из всех активных источников региона, сводит в ядро, кластеризует, размечает интенты.

Часть экосистемы [seo-cycle](https://github.com/turvodnik/seo-cycle). Может работать **самостоятельно** или как **звено цикла** (координация через `_state.json`).

## Что делает
- Multi-source сбор: Яндекс (Wordstat/Suggest), Google (GSC/Trends/Suggest), Serpstat (вкл. РФ `g_ru`), SpyFu (US/UK/EU), NeuronWriter, LLM-CLI (Antigravity+Codex, deep), AnswerThePublic, Perplexity.
- Региональная адаптация: РФ → Яндекс+Serpstat; запад → Google+SpyFu+Ahrefs (через `region_profile`).
- Экономия: кэш с TTL, дистилляты в контекст, guard'ы кредитов Serpstat/SpyFu.
- Кластеризация (SERP-overlap) + разметка интентов + hub-and-spoke.
- Multi-pass для сложных ecommerce-категорий: Antigravity Phase 1-2, Perplexity deep research Phase 1-4, Codex-native final audit/brief.
- Structured reuse: `records.jsonl`, triplets `relations.jsonl`, `evidence.jsonl`, `sub_intents.jsonl` (`subintents.jsonl` legacy alias), cosine-neighbor report и controlled iterative unpacking.
- SEO/AEO/GEO vNext records: `answer_units.jsonl`, `synthetic_prompts.jsonl`, `entity_coverage.jsonl`, `eeat_evidence.jsonl`, `local_seo_signals.jsonl`, `commercial_factors.jsonl`, `ai_visibility_checks.jsonl`, `traffic_diagnostics.jsonl`, `source_pack.jsonl`.
- Optional support toolchain из `seo-cycle`: MarkItDown для trusted document ingestion, Graphify для mixed research/docs/code graph, CodeGraph для code-symbol navigation, Spec Kit для крупных изменений skill/repo, NotebookLM MCP для curated expert knowledge base.

## Multi-pass правило

После сбора через LLM сохраняй не только markdown, но и vector-ready слой:

```text
seo/research/llm-cli/results/<topic>-multipass-<date>/
├── distillates/cross-source-merged.md
├── vector/records.jsonl
├── vector/relations.jsonl
├── vector/triplets.jsonl
├── vector/evidence.jsonl
├── vector/sub_intents.jsonl
├── vector/answer_units.jsonl
├── vector/synthetic_prompts.jsonl
├── vector/entity_coverage.jsonl
├── vector/eeat_evidence.jsonl
├── vector/local_seo_signals.jsonl
├── vector/commercial_factors.jsonl
├── vector/ai_visibility_checks.jsonl
├── vector/traffic_diagnostics.jsonl
├── vector/source_pack.jsonl
├── vector/similarity.jsonl
├── vector/neighbor-report.md
└── final/seo-brief.md
```

Итеративную распаковку делай только после final audit, Answer Units, synthetic prompts и cosine-neighbor отчета: максимум 5 P1/P2 seed nodes, где есть commercial/GEO/B2B ценность, понятный page surface и проверяемый evidence path.

Готовые файлы в репозитории:

- `llm-cli/prompts/multipass-seo-chain.md`
- `llm-cli/prompts/iterative-unpacking.md`
- `llm-cli/multipass-storage.md`
- `scripts/vectorize-records.py`

Локальная векторизация без внешних API:

```bash
python3 scripts/vectorize-records.py seo/research/llm-cli/results/<run-dir> --top-k 6 --min-score 0.12
```

Support toolchain ставится из core `seo-cycle`:

```bash
bash ~/.codex/skills/seo-cycle/scripts/install-ai-toolchain.sh --codex
bash ~/.codex/skills/seo-cycle/scripts/install-ai-toolchain.sh --codex --notebooklm
```

Правила: `markitdown` только для trusted local files/явно разрешённых URL; `graphify-out/` и `.codegraph/` не коммитить; CodeGraph и NotebookLM не использовать как источник SEO-частот; NotebookLM ответы переносить в evidence/fact-check queue только с citations/source excerpts; stealth/anti-bot инструменты не входят в стандартный workflow.

## Установка
```bash
# 1. Нужен core seo-cycle (shared-скрипты + конфиг-схема)
git clone https://github.com/turvodnik/seo-cycle ~/.codex/skills/seo-cycle
# 2. Этот скилл
git clone https://github.com/turvodnik/seo-keywords ~/.codex/skills/seo-keywords   # если раздаётся отдельно
pip3 install pyyaml requests
# 3. Конфиг проекта (region_profile, источники) — см. seo-cycle/INSTALL.md
```

## Использование
В Claude Code / Codex: «собери семантическое ядро для категории X».
Полная логика — в [SKILL.md](SKILL.md). Контракт состояния — `cycle-state.py` в core.

## Вход → Выход
| Вход | Выход |
|---|---|
| тема + `seo-cycle.yaml` (регион/источники) | `02-keywords.md` (ядро), `03-clusters.md` (кластеры), raw на диске |

## Место в цепочке
`audit → **keywords → clusters** → entity_map → ...` — после завершения обновляет `_state.json`, разблокируя `entity_map`.

Лицензия: личное использование (укажи свою при публикации).
