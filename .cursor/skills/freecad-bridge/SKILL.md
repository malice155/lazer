---
name: freecad-bridge
description: Use when the user opens FreeCAD, asks for an FCStd script, or wants to edit a STEP with a feature tree. Headless Part API only.
---

# Мост в FreeCAD

Источник API: [awesome-copilot freecad-scripts](https://github.com/github/awesome-copilot/blob/main/skills/freecad-scripts/SKILL.md). Здесь только headless Part, без GUI, Sketcher и PySide.

Основная модель этого репо — CadQuery → STEP. FreeCAD нужен, когда человек хочет дерево в своём окне или когда `freecadcmd` уже стоит.

## Когда писать скрипт FreeCAD

- Пользователь явно открывает FreeCAD.
- Нужен `.FCStd`, а не только STEP.

Иначе не переписывай деталь на FreeCAD.

## Headless (если есть freecadcmd)

```python
import FreeCAD as App
import Part

doc = App.newDocument("part")
box = doc.addObject("Part::Feature", "Body")
box.Shape = Part.makeBox(100, 60, 8)
doc.recompute()
box.Shape.exportStep("/tmp/part.step")
```

Запуск: `freecadcmd script.py` (без GUI). В облаке FreeCAD может не быть — тогда оставайся на CadQuery.

Импорт нашего STEP в FreeCAD у пользователя: Файл → Открыть. Тело будет без эскизов CadQuery; правки посадки — обратно в параметры `cad/parts/`.
