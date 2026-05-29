# seo-keywords

**Фазовый скилл сбора семантики и кластеризации** (Phase 2-3 модульной архитектуры `seo-cycle`).
Собирает ключи из всех активных источников региона, сводит в ядро, кластеризует, размечает интенты.

Часть экосистемы [seo-cycle](https://github.com/turvodnik/seo-cycle). Может работать **самостоятельно** или как **звено цикла** (координация через `_state.json`).

## Что делает
- Multi-source сбор: Яндекс (Wordstat/Suggest), Google (GSC/Trends/Suggest), Serpstat (вкл. РФ `g_ru`), SpyFu (US/UK/EU), NeuronWriter, LLM-CLI (Antigravity+Codex, deep), AnswerThePublic, Perplexity.
- Региональная адаптация: РФ → Яндекс+Serpstat; запад → Google+SpyFu+Ahrefs (через `region_profile`).
- Экономия: кэш с TTL, дистилляты в контекст, guard'ы кредитов Serpstat/SpyFu.
- Кластеризация (SERP-overlap) + разметка интентов + hub-and-spoke.

## Установка
```bash
# 1. Нужен core seo-cycle (shared-скрипты + конфиг-схема)
git clone https://github.com/turvodnik/seo-cycle ~/.claude/skills/seo-cycle
# 2. Этот скилл
git clone https://github.com/turvodnik/seo-keywords ~/.claude/skills/seo-keywords   # если раздаётся отдельно
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
