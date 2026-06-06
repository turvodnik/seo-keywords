# Multi-pass SEO/GEO prompt-chain

Универсальная цепочка для Phase 2-4 `seo-cycle`: сбор ключей, интентов, сущностей, связей, E-E-A-T и QA-аудита через LLM CLI / Perplexity / Codex-native.

## Параметры

- `{TOPIC}` — базовый запрос / категория.
- `{DOMAIN}` — домен проекта.
- `{PROJECT_NAME}` — бренд/проект.
- `{PROJECT_TYPE}` — ecommerce / local / blog / SaaS.
- `{COUNTRY}` — страна.
- `{REGION}` — регион продвижения.
- `{LANG}` — язык вывода.
- `{SEGMENT}` — B2C / B2B / B2C+B2B.
- `{CATEGORIES}` — соседние категории/ассортимент.
- `{CITIES}` — важные города региона.
- `{RUN_ID}` — стабильный id запуска.

## Общие правила для всех фаз

Вставлять в начало каждого промпта.

```text
Режим: используй лучшую доступную модель, deep research / deep reasoning / максимальную точность. Если интерфейс позволяет выбирать модель, выбери самую сильную reasoning/web модель. Google NLP API не использовать.

Роль: ты Senior SEO/GEO Architect, E-commerce Data Architect и Technical SEO QA.

Проект:
- Тема: {TOPIC}
- Домен: {DOMAIN}
- Проект: {PROJECT_NAME}
- Тип проекта: {PROJECT_TYPE}
- Страна/регион: {COUNTRY}, {REGION}
- Язык: {LANG}
- Сегмент: {SEGMENT}
- Ассортимент/соседние категории: {CATEGORIES}
- Гео: {CITIES}
- Run ID: {RUN_ID}

Правила качества:
1. Не выдумывай бренды, стандарты, свойства и цифры. Если источник не найден или факт сомнителен, ставь `[needs_fact_check]`.
2. Разделяй: `confirmed`, `inferred`, `needs_fact_check`.
3. Не раскрывай внутреннюю цепочку рассуждений. Дай только проверяемый итог, таблицы, списки, источники и объяснение решений.
4. Масштаб обязателен, но не ценой мусора: лучше меньше, но пригодно для фильтров, URL, FAQ, schema и карточек товара.
5. Каждый результат должен быть пригоден для повторного использования: добавляй stable slug, тип сущности, relation triples, source/evidence.
6. Отмечай интенты: `[К]` commercial, `[И]` informational, `[B2B]`, `[B2C]`, `[GEO]`, `[FAQ]`, `[FILTER]`, `[URL]`.
7. Для РФ/проектов без зарубежных tracking tags не предлагай установку analytics pixels. Off-site research и search-console источники допустимы.

Формат каждого ответа:
- Markdown для человека.
- В конце блок `## Vector-ready records` в JSONL: 10-30 строк, по одной записи на сущность/кластер/связь.
```

## Phase 1 — Entity foundation, taxonomy, filters

```text
{COMMON_RULES}

Задача Phase 1: создать фундамент для ecommerce-категории и будущей векторной памяти.

Сгенерируй:

1. Таксономия:
   - 20+ узлов: главный hub, подкатегории, посадочные URL, микро-ниши.
   - Для каждого узла: `slug`, `intent`, `page_type`, `priority`, `parent`.

2. Коммерческие атрибуты:
   - 30+ фасетов/свойств для фильтров и карточек товара.
   - Раздели на `must_have_filter`, `optional_filter`, `card_attribute`, `faq_only`, `schema_property`.
   - Для каждого атрибута: тип данных, единицы измерения, допустимые значения, конфликтные значения.

3. Бренды, линейки, производители:
   - Только реальные бренды/производители рынка.
   - Для каждого: `brand`, `product_line`, `market_role`, `evidence_url` или `[needs_fact_check]`.

4. Экосистема:
   - 20+ кросс-селл/апсейл сущностей: расходники, крепеж, инструмент, логистика, защитные материалы, услуги.

5. `## Vector-ready records`:
   - JSONL поля: `run_id`, `project`, `topic`, `record_type`, `slug`, `label`, `parent_slug`, `intent`, `page_type`, `attributes`, `relations`, `evidence`, `confidence`.
```

## Phase 2 — Keywords, intents, routing, relation triples

```text
{COMMON_RULES}

Вход: используй и проверь результат Phase 1 ниже.

{PHASE_1_OUTPUT}

Задача Phase 2: построить семантическое ядро, интенты, routing и связи.

Сгенерируй:

1. 80+ long-tail запросов:
   - 30 commercial `[К]`.
   - 30 informational `[И]`.
   - 10 B2B/опт.
   - 10 GEO/локальные.
   - Для каждого: `intent`, `stage` TOFU/MOFU/BOFU/Retention, `page_target`, `entity_slug`, `url_or_filter`.

2. Routing:
   - Что должно стать статичным URL.
   - Что должно быть SEO-тегом/индексируемой посадкой.
   - Что оставить динамическим фильтром noindex/canonical к категории.
   - Что должно быть FAQ.

3. Relation triples:
   - 40+ связей вида `subject -> predicate -> object`.
   - Типы связей: `is_type_of`, `has_attribute`, `used_for`, `competes_with`, `requires`, `risk_if`, `covered_by_standard`, `cross_sell`.

4. UX zero-results guard:
   - 10+ конфликтов фасетов/сценариев, которые не должны вести к пустой выдаче или неверному подбору.

5. `## Vector-ready records`:
   - JSONL поля: `run_id`, `record_type`, `query`, `intent`, `stage`, `target_slug`, `relations`, `routing`, `confidence`, `source_phase`.
```

## Phase 3 — Evidence, E-E-A-T, GEO/AEO answers

```text
{COMMON_RULES}

Вход: используй Phase 1 и Phase 2 ниже.

{PHASE_1_OUTPUT}

{PHASE_2_OUTPUT}

Задача Phase 3: усилить кластер проверяемой фактологией, E-E-A-T и ответами для AI-поиска.

Сгенерируй:

1. Evidence map:
   - 20+ проверяемых фактов: стандарты, классы, размеры, форматы, область применения, ограничения, риски.
   - Для каждого: `claim`, `source_type`, `source_url`, `confidence`, `needs_fact_check`.
   - Если нет источника, не утверждай как факт.

2. Direct Answer snippets:
   - 10 ответов до 50 слов.
   - Каждый ответ должен закрывать конкретный вопрос и включать сущность/атрибут/ограничение.

3. E-E-A-T matrix:
   - Experience: 5 практических нюансов монтажа/логистики/выбора.
   - Expertise: 5 технических объяснений.
   - Authority: 5 стандартов/сертификатов/официальных источников.
   - Trust: 5 рисков и как их раскрыть на странице.

4. AI/GEO visibility:
   - 20 запросов, по которым AI-ответ может цитировать страницу.
   - Какие блоки страницы должны быть citation-ready.

5. `## Vector-ready records`:
   - JSONL поля: `run_id`, `record_type`, `claim`, `entity_slug`, `evidence_url`, `answer_snippet`, `eeat_type`, `confidence`, `needs_fact_check`.
```

## Phase 4 — Auditor, dedupe, final SEO brief

```text
{COMMON_RULES}

Вход: проверь все предыдущие фазы ниже.

{PHASE_1_OUTPUT}

{PHASE_2_OUTPUT}

{PHASE_3_OUTPUT}

Роль: злой Senior Technical SEO Auditor. Твоя задача — не соглашаться, а улучшать.

Сгенерируй:

1. Fact-check audit:
   - Исправь галлюцинации, устаревшие стандарты, слабые бренды, неподтвержденные цифры.
   - Каждому исправлению дай `before`, `after`, `reason`, `confidence`.

2. Missing entities:
   - 10+ сущностей/атрибутов/страниц, которые были упущены.

3. Final keyword clusters:
   - 12-20 кластеров с primary/secondary queries, intent, page target, URL decision.

4. Final entity graph:
   - 40+ связей с приоритетом для Title/H1/H2/filter/FAQ/schema/internal links.

5. Production-ready page brief:
   - Title, H1, meta description.
   - H2/H3 структура.
   - Фильтры.
   - FAQ.
   - Schema.
   - Internal links.
   - Факты, которые нельзя публиковать без ручной проверки.

6. Экспертный вывод:
   - Что делать первым.
   - Что отложить.
   - Что опасно публиковать без проверки.
   - Какой источник/модель дала лучший результат.

7. `## Vector-ready records`:
   - JSONL поля: `run_id`, `record_type`, `final_cluster`, `entity_slug`, `page_target`, `relation`, `priority`, `evidence_status`, `reuse_scope`.
```

## Phase 5 — Iterative unpacking queue

Запускать не всегда. Использовать только после Phase 4, когда уже есть `vector/records.jsonl`, `vector/relations.jsonl`, `vector/evidence.jsonl` и cosine-neighbor report.

```text
{COMMON_RULES}

Вход:
- Final brief.
- Keyword clusters.
- Entity graph / relation triples.
- Cosine-neighbor report.
- Fact-check queue.

Задача Phase 5: выбрать, какие сущности и под-интенты нужно распаковать глубже, а какие нельзя трогать.

Правила:
1. Не распаковывай всё подряд. Максимум 5 seed nodes за итерацию.
2. Распаковывай только узлы, где есть:
   - высокий commercial/GEO/B2B potential;
   - высокий evidence confidence или понятная fact-check задача;
   - связь с category/filter/FAQ/schema/internal links;
   - нехватка покрывающего контента или слабая cosine-близость к существующим узлам.
3. Не распаковывай:
   - неподтвержденные бренды;
   - точные технические цифры без источника;
   - города без отдельной логистики/условий;
   - комбинации фильтров без спроса и ассортимента.

Сгенерируй:

1. `Unpacking candidates`:
   - 5-10 кандидатов.
   - Поля: `seed_slug`, `why_unpack`, `sub_intents`, `expected_page_type`, `risk`, `evidence_needed`, `priority`.

2. `Sub-intent map`:
   - Для каждого seed node: 8-15 под-интентов.
   - Раздели на commercial, informational, comparison, troubleshooting, logistics, B2B.

3. `Expansion prompts`:
   - 1 короткий промпт на каждый P1 seed node.
   - Промпт должен быть пригоден для Antigravity/Perplexity/Codex.

4. `Stop conditions`:
   - Когда прекращать итерации.
   - Какие признаки говорят, что мы уже переупаковываем тему.

5. `## Vector-ready records`:
   - JSONL поля: `run_id`, `record_type`, `seed_slug`, `sub_intent`, `target_slug`, `priority`, `unpack_reason`, `stop_condition`, `reuse_scope`.
```
