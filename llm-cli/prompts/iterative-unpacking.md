# Iterative unpacking prompt

Используется после multi-pass Phase 4 и локальной векторизации. Цель — не расширять тему бесконечно, а найти только те под-интенты и сущности, которые реально улучшают SEO/GEO, фильтры, FAQ, schema и внутренние ссылки.

```text
Режим: deep reasoning / deep research. Google NLP API не использовать.

Роль: Senior SEO/GEO Architect, Entity Graph QA и E-commerce Information Architect.

Проект:
- Topic: {TOPIC}
- Domain: {DOMAIN}
- Region: {REGION}
- Segment: {SEGMENT}
- Run ID: {RUN_ID}

Вход:
1. Final SEO brief:
{FINAL_BRIEF}

2. Keyword clusters:
{KEYWORD_CLUSTERS}

3. Relation triples:
{RELATIONS}

4. Cosine-neighbor report:
{COSINE_REPORT}

5. Fact-check queue:
{FACT_CHECK_QUEUE}

Задача: сделать controlled iterative unpacking.

Правила:
1. Выбери максимум 5 seed nodes.
2. Не выбирай узлы с `evidence_status=needs_fact_check`, если нет понятного источника проверки.
3. Не выбирай комбинации фильтров без коммерческой логики.
4. Для каждого seed node покажи, какой именно пробел закрываем: keyword gap, entity gap, evidence gap, FAQ gap, internal-link gap, schema gap.
5. Если seed node уже хорошо покрыт соседними узлами по cosine similarity, не распаковывай его.

Формат:

## Unpacking candidates

Таблица: `seed_slug`, `priority`, `gap_type`, `why_unpack`, `expected_surface`, `risk`, `evidence_needed`.

## Sub-intent map

Для каждого P1/P2 seed node:
- commercial
- informational
- comparison
- troubleshooting
- logistics
- B2B

## Expansion prompts

Короткие промпты для следующего LLM-запуска, по одному на каждый P1 seed node.

## Stop conditions

Когда прекращаем распаковку.

## Vector-ready records

JSONL:
{"run_id":"...","record_type":"unpacking_candidate","seed_slug":"...","sub_intent":"...","target_slug":"...","priority":"P1","unpack_reason":"...","stop_condition":"...","reuse_scope":"..."}
```
