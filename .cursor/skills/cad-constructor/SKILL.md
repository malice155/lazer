---
name: cad-constructor
description: Use when building or editing 3D geometry with CadQuery, holes, fillets, parametric models, or STEP/STL/SVG export for КОМПАС.
---

# Конструктор 3D (CadQuery)

Геометрия = Python (CadQuery). Перед кодом читай `cadquery-brep`. Если деталь садится на машину, сиденье или мотор — сначала `designer`: незамеренное число в модель не идёт. КОМПАС и SolidWorks не открываем: отдаём STEP. FreeCAD — только если просят окно или `.FCStd` (`freecad-bridge`).

## Правила модели

- Единицы **мм**. Константы — наверху модуля, не магические числа в цепочке.
- Один солид на деталь, если нет сборки. Скругления и фаски — в конце.
- Отверстия под болт: зазор (M8 → Ø8.4…8.5), не номинал резьбы.
- Не использовать OpenSCAD, если цель — КОМПАС (уйдёт сетка STL).
- Импортированное в КОМПАС тело **без дерева эскизов**. Правка посадки — снова в параметрах скрипта.

## Шаблон детали

```python
import cadquery as cq

NAME = "part-name"
LENGTH = 100.0
HOLE_D = 8.5

def build() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(LENGTH, 60, 8)
        .edges("|Z").fillet(6)
        .faces(">Z").workplane()
        .rect(76, 36, forConstruction=True)
        .vertices()
        .hole(HOLE_D)
    )
```

Подключить в `cad/build.py` → `PARTS`.

## Экспорт

```bash
cad/.venv/bin/python cad/build.py              # все
cad/.venv/bin/python cad/build.py demo-bracket
```

Файлы: `cad/out/<name>.step` (КОМПАС), `.stl` (печать), `.svg` (вид), `.png` (превью).

В КОМПАС: Файл → Открыть → `*.step`. Если тело «поверхности» — перестроить экспорт, не отдавать STL как рабочую модель.
