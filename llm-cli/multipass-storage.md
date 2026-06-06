# Multi-pass LLM SEO storage, cache, and vector reuse

Цель: один и тот же метод должен работать в любом проекте `seo-cycle`, сохранять сырьё, дистилляты, связи и vector-ready записи так, чтобы результаты можно было переиспользовать между категориями и проектами без повторного расхода LLM.

## Каталог запуска

Для каждого multi-pass запуска:

```text
seo/research/llm-cli/results/<topic>-multipass-<YYYY-MM-DD>/
├── manifest.yaml
├── prompts/
│   ├── 01-entities.prompt.md
│   ├── 02-keywords-routing.prompt.md
│   ├── 03-eeat-evidence.prompt.md
│   └── 04-audit-brief.prompt.md
├── raw/
│   ├── antigravity/
│   ├── perplexity/
│   └── codex-native/
├── distillates/
│   ├── antigravity-summary.md
│   ├── perplexity-summary.md
│   ├── codex-native-summary.md
│   └── cross-source-merged.md
├── vector/
│   ├── records.jsonl
│   ├── relations.jsonl
│   ├── evidence.jsonl
│   ├── subintents.jsonl
│   ├── similarity.jsonl
│   ├── neighbor-report.md
│   └── README.md
└── final/
    ├── seo-brief.md
    ├── keyword-clusters.csv
    ├── entity-graph.md
    └── fact-check-queue.csv
```

## Manifest

`manifest.yaml` должен быть главным индексом запуска:

```yaml
run_id: plita-osp-2026-06-06-multipass
topic: "Плита ОСП"
domain: "emwoody.ru"
project: "Эмвуди"
project_type: ecommerce
country: RU
region: "Москва и Московская область"
language: ru
segment: B2C+B2B
google_nlp_api: not_used
models:
  antigravity: best_available_deep_reasoning_requested
  perplexity: best_available_deep_research_requested
  codex_native: native_reasoning
cache:
  key: sha256(topic+region+segment+categories+prompt_version)
  ttl_days: 30
  reuse_allowed: true
outputs:
  canonical_brief: final/seo-brief.md
  vector_records: vector/records.jsonl
  relation_graph: vector/relations.jsonl
```

## Cache policy

Кэшировать нужно не только финальный текст, а четыре слоя:

1. `prompt_hash` — версия промпта и входных параметров.
2. `raw_output_hash` — сырой ответ модели.
3. `distillate_hash` — нормализованный краткий вывод.
4. `entity_graph_hash` — граф сущностей/связей.

Повторный запуск нужен, если:

- изменился prompt-chain;
- изменился регион/язык/сегмент;
- изменилась категория/ассортимент проекта;
- прошло больше TTL;
- требуется fact-check по новым источникам;
- появились данные из GSC/Я.Вебмастера/Wordstat/NeuronWriter.

Повторный запуск не нужен, если:

- нужна только страница для похожей толщины/формата внутри той же категории;
- меняется только URL slug или meta;
- есть свежий `final/seo-brief.md` и `vector/records.jsonl`.

## Vector-ready JSONL

Минимальная запись:

```json
{"run_id":"plita-osp-2026-06-06-multipass","project":"emwoody.ru","topic":"Плита ОСП","record_type":"entity","slug":"osb-3","label":"OSB-3","intent":["commercial","informational"],"page_targets":["category","filter","faq"],"relations":[{"predicate":"is_type_of","object":"osp"}],"evidence":[{"url":"https://example.com","status":"needs_fact_check"}],"confidence":"medium","reuse_scope":"category_cluster"}
```

Типы записей:

- `entity`
- `keyword_cluster`
- `query`
- `relation`
- `evidence`
- `faq`
- `page_target`
- `filter`
- `risk`
- `schema_property`

## Relation graph

Связи хранить отдельно, чтобы потом строить внутренние ссылки и entity gaps:

```json
{"run_id":"plita-osp-2026-06-06-multipass","subject":"osb-3","predicate":"used_for","object":"chernovoy-pol","priority":"high","surface":["H2","FAQ","filter"],"evidence_status":"needs_fact_check"}
{"run_id":"plita-osp-2026-06-06-multipass","subject":"osp","predicate":"competes_with","object":"fanera-fsf","priority":"high","surface":["comparison-block","internal-link"]}
```

## Triplets

Triplets — основной способ превратить LLM-ответ из текста в управляемый граф:

```text
subject -> predicate -> object
```

Нормальные predicate-типы:

- `is_type_of`
- `has_attribute`
- `used_for`
- `competes_with`
- `requires`
- `risk_if`
- `covered_by_standard`
- `cross_sell`
- `has_sub_intent`
- `targets_geo`
- `supports_schema`
- `needs_evidence`

Каждый triplet должен иметь:

- `priority`: P1/P2/P3.
- `surface`: где использовать связь — Title/H1/H2/filter/FAQ/schema/internal_link/product_card.
- `evidence_status`: confirmed / confirmed_general / inferred / needs_fact_check.
- `reuse_scope`: global_material / country_regulation / regional_commercial / project_specific.

Triplets используются для:

- выбора внутренних ссылок;
- поиска entity gaps;
- генерации FAQ;
- определения indexable/static URL;
- защиты от пустых фильтров;
- проверки, не противоречит ли текст карточке товара.

## Sub-intents

Под-интент — это не просто ключевик. Это причина, зачем пользователь спрашивает про сущность.

Пример:

```json
{"seed_slug":"osb-dlya-pola","sub_intent":"подобрать толщину под шаг лаг","intent_type":"informational_commercial","surface":["FAQ","filter_hint"],"target_slug":"osb-thickness-floor","priority":"P1"}
```

Типы sub-intents:

- `commercial`
- `informational`
- `comparison`
- `troubleshooting`
- `logistics`
- `B2B`
- `compliance`
- `safety`

Sub-intents нужны, чтобы не создавать страницы только по словам. Мы создаем страницу, FAQ или фильтр только когда под-интент связан с сущностью, спросом, товаром и evidence.

## Vectorization and cosine similarity

Векторизация нужна не для ранжирования Google напрямую. Она нужна нам как рабочий механизм:

1. Найти похожие сущности и кластеры.
2. Увидеть дубли и каннибализацию.
3. Понять, какие узлы плохо связаны с текущим графом.
4. Выбрать seed nodes для iterative unpacking.
5. Переиспользовать знания между проектами.

Минимальный локальный вариант:

- `records.jsonl` + `relations.jsonl` + `evidence.jsonl` превращаются в текстовые документы.
- Скрипт строит TF-IDF / n-gram векторы без внешних API.
- Затем считает cosine similarity.
- Результат пишется в `vector/similarity.jsonl` и `vector/neighbor-report.md`.

Production-вариант:

- тот же contract JSONL;
- embeddings через OpenAI/Gemini/локальную модель только если разрешены budget/API;
- хранение в vector DB или локальном индексе;
- cosine threshold и top-K такие же, чтобы поведение было переносимым.

Рекомендуемые пороги:

- `>=0.82` — вероятный дубль или каннибализация.
- `0.62-0.82` — близкая сущность, кандидат на внутреннюю ссылку или общий блок FAQ.
- `0.42-0.62` — слабая связь, кандидат на bridge content.
- `<0.42` — отдельный кластер или плохо связанный узел, смотреть вручную.

## Iterative unpacking

Итеративная распаковка нужна, но только контролируемая. Не запускай ее по всей теме.

Запускать, если:

- есть P1/P2 узел с большим commercial/GEO/B2B потенциалом;
- cosine report показывает слабое покрытие или мало соседей;
- fact-check queue понятна и выполнима;
- есть реальный page surface: URL, FAQ, filter, schema, internal link.

Не запускать, если:

- узел уже имеет сильных соседей `>=0.82`;
- нет SKU/товара/ассортимента;
- нужны точные цифры без источника;
- это город без отдельной логистики;
- это бренд без наличия/официального подтверждения.

Ограничения:

- максимум 5 seed nodes за итерацию;
- максимум 2 итерации без новых confirmed P1/P2 records;
- stop, если новая итерация дает менее 20% новых полезных records;
- stop, если растет только long-tail без новых сущностей/связей/evidence.

## Повторное использование между проектами

У записи должно быть поле `reuse_scope`:

- `global_material` — можно переносить между проектами почти без изменений: определения, базовые виды, альтернативы.
- `country_regulation` — переносить только внутри страны/правовой зоны.
- `regional_commercial` — зависит от региона, доставки, гео и складов.
- `project_specific` — только для конкретного сайта: URL, наличие, бренды в каталоге, цены.

## Эффективный workflow

1. Запустить Phase 1-4 один раз для широкой категории.
2. Сохранить raw, distillates и vector JSONL.
3. Перед созданием новой посадки сначала искать по локальным records:
   - topic slug;
   - entity slug;
   - relation object;
   - page target.
4. Если найден свежий кэш — не запускать LLM, а собрать brief из records.
5. LLM запускать только для gaps:
   - новые бренды;
   - новые стандарты;
   - новый регион;
   - новый тип страницы;
   - конфликт источников.

## Что важно для качества

- Perplexity лучше использовать для web/GEO sanity-check и источников.
- Antigravity полезен для быстрых широких taxonomy/long-tail гипотез.
- Codex-native нужен для финального merge, критики и production brief.
- Нельзя публиковать нормативные цифры, если они не прошли отдельный `fact-check-queue.csv`.
- Google NLP подключать только как отдельный guarded entity audit, когда разрешён бюджет; в этом методе он не обязателен.
