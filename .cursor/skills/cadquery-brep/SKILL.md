---
name: cadquery-brep
description: Use when writing CadQuery geometry. BRep habits, selectors, fillets, holes. Distilled from jmwright/cadquery-llm-skill.
---

# CadQuery (BRep)

Источник правил: [jmwright/cadquery-llm-skill](https://github.com/jmwright/cadquery-llm-skill). В этом репо — короткая выжимка, не копия репозитория. API: fluent `cq.Workplane`. Free Function (`cadquery.func`) не мешать в том же скрипте.

## Как строить

- Отверстие: `.faces(">Z").workplane().hole(d)`, не вырезать цилиндром, если плоскость ровная.
- Карман: `.workplane(invert=True).rect(...).cutBlind(depth)` — без `invert` рез уходит наружу.
- Фаска/скругление: `.edges("|Z").fillet(r)` в конце. Радиус меньше самой короткой соседней кромки, иначе `BREP_API command not done`.
- Профиль из `.lineTo()` закрывать `.close()` до `.extrude()`.
- Селекторы `">Z"`, `"<X"`, `"|Z"`. Индексы `">>Z[1]"` ломаются после фаски — ставь `.tag()`.
- `.workplane()` по умолчанию `ProjectedOrigin`. Если отверстие уехало — `centerOption="CenterOfBoundBox"` или режь в мировой XY, как в `hydrofoil_demo`.
- После `.faces()` стек — грани, не тело. Вернуться: `.end()` или снова выбрать грань и `.workplane()`.
- `.val()` берёт только первый объект. Несколько — `.vals()`.
- Много отверстий: один `compound` и один `.cut()`, не цикл boolean.

## Проверка

Собрать через `cad/build.py`. `verify_step` должен видеть солид. Габарит сверить с константами наверху файла.
