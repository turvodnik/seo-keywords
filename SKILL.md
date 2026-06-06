---
name: seo-keywords
description: Фазовый скилл сбора семантики и кластеризации (Phase 2-3 SEO-цикла). Используй когда нужно «собрать семантическое ядро», «найти ключевые слова», «multi-source keyword research», «расширить семантику», «кластеризовать ключи», «сгруппировать запросы по интентам», «hub-and-spoke под тему». Собирает из активных источников региона (Яндекс Wordstat/Suggest + Google GSC/Trends/Suggest + Serpstat + SpyFu + NeuronWriter + LLM-CLI + AnswerThePublic + Perplexity), сводит, кластеризует, размечает интенты. Часть модульной архитектуры seo-cycle — читает/обновляет _state.json. Можно запускать самостоятельно или как звено цикла. НЕ пишет тексты (это seo-writing) и не делает аудит.
---

# seo-keywords — сбор семантики и кластеризация (Phase 2-3)

Самостоятельный фазовый скилл модульной архитектуры `seo-cycle`. Делает **только** сбор семантики и кластеризацию — и делает это хорошо. Координируется с другими фазами через `_state.json` (контракт `cycle-state.py`).

## Когда запускать
«собери семантическое ядро для X» · «keyword research под тему Y» · «расширь семантику кластера Z» · «кластеризуй ключи» · «сгруппируй запросы по интентам».

## Вход
- Тема/кластер (от пользователя или из `_state.json` текущего цикла).
- `seo-cycle.yaml` проекта: `region_profile`, `sources.*`, `locale`, `research_cache_ttl_days`.
- (если в цикле) `01-audit.md` — гэпы, на которые ориентироваться.

## Процесс

1. **Развернуть активные источники региона:**
   ```bash
   python3 ~/.claude/skills/seo-cycle/scripts/resolve-sources.py
   ```
   Запускать только то, что в активном списке (РФ → Яндекс+Serpstat; запад → Google+SpyFu+Ahrefs).

2. **Собрать из активных источников** (каждый — свой скрипт core seo-cycle; кэш предотвращает повторные траты):
   - Яндекс Suggest: `yandex-suggest.py "<seed>" --region <code> --depth 2`
   - Google Suggest/Trends: `google-suggest.py` / `google-trends.py`
   - Serpstat (volume/KD, вкл. РФ): `serpstat-fetch.py keywords-info "<kw>" --se g_ru` (беречь кредиты — `stats`)
   - SpyFu (US/UK/EU competitor): `spyfu-fetch.py domain-stats <domain>`
   - NeuronWriter: `nw-cli.sh get <query_id>`
   - LLM-CLI (deep): `llm-cli-collect.sh "<тема>"` → `llm-cli-merge.py` (RUNTIME-aware)
   - AnswerThePublic: `atp-fetch.py "<en keyword>"`
   - Яндекс Wordstat / Вебмастер / Perplexity — делегат/браузер по рантайму.
   - **В контекст тяни только дистилляты** (`*-merged-*.md`), не сырьё.

3. **Для сложных ecommerce-категорий включить LLM multi-pass**:
   - Antigravity Phase 1-2 — ширина, long-tail, локальные гипотезы.
   - Perplexity Pro/deep research Phase 1-4 — источники, evidence, self-audit.
   - Codex-native final audit/brief — production decisions, fact-check queue, vector records.
   - Google NLP API не использовать без явного разрешения проекта.

   Храни не только текст, но и структуру:
   - `vector/records.jsonl` — сущности, кластеры, FAQ, фильтры.
   - `vector/relations.jsonl` — triplets `subject -> predicate -> object`.
   - `vector/evidence.jsonl` — проверяемые claims и источники.
   - `vector/subintents.jsonl` — под-интенты и page targets.
   - `vector/similarity.jsonl` + `vector/neighbor-report.md` — cosine-neighbors, каннибализация, internal-link candidates.

   Итеративную распаковку запускать только после Phase 4 и neighbor report: максимум 5 seed nodes, только P1/P2 commercial/GEO/B2B узлы с понятным page surface и evidence. Не распаковывать все бренды, города и фильтры подряд.

4. **Свести в ядро** `02-keywords.md`: таблица `Ключ | volume | KD | intent | cluster | source`. Веди `seo/source-attribution.csv` (источник каждого ключа).

5. **Кластеризовать** → `03-clusters.md`: группы по SERP-overlap/интенту, модель hub-and-spoke (hub=категория, spokes=статьи). Делегат: `claude-seo:seo-cluster` (если доступен) + `seo-keyword-researcher`.

## Выход
- `<cycle>/02-keywords.md` — сводное ядро.
- `<cycle>/03-clusters.md` — кластеры + интенты + тип страницы.
- raw-экспорты в `seo/research/.../results/` (на диске, не в контекст).

## Обновление состояния (handoff)
После завершения — отметить фазы в state, чтобы разблокировать следующую (`entity_map`):
```bash
python3 ~/.claude/skills/seo-cycle/scripts/cycle-state.py set keywords --status done --output 02-keywords.md --gate-passed
python3 ~/.claude/skills/seo-cycle/scripts/cycle-state.py set clusters --status done --output 03-clusters.md --gate-passed
python3 ~/.claude/skills/seo-cycle/scripts/cycle-state.py next   # покажет следующую фазу
```
Quality-gate здесь: ядро непустое, у ключей размечен intent, кластеры сопоставлены страницам.

## Самостоятельный запуск (вне цикла)
Можно без `_state.json` — просто отдай тему, скилл соберёт ядро в указанный каталог. Тогда шаги 1-4 без шага handoff.

## Зависимости
- Core-скрипты из `~/.claude/skills/seo-cycle/scripts/` (shared). Установка: см. `README.md`.
- `seo-cycle.yaml` в проекте (источники/регион). Без него — спросить регион/язык у пользователя.

## Чего НЕ делает
Не пишет тексты (→ `seo-writing`), не строит Entity Map (→ `seo-entity-map`/`emwoody-semantic-brief`), не публикует, не делает аудит.
