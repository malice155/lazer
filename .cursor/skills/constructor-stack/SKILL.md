---
name: constructor-stack
description: Use when choosing CAD software for this workshop — CadQuery, FreeCAD, КОМПАС, SolidWorks — or when asked what the constructor needs installed.
---

# Стек конструктора

Я конструирую **кодом**. Окна SolidWorks и КОМПАС у меня нет. Мост в цех — **STEP**.

| Программа | Кто | Зачем | Ставить |
|---|---|---|---|
| **Python 3.12 + CadQuery 2.8** | я | модель, STEP/STL/DXF | да, `bash cad/install.sh` |
| **FreeCAD** | ты (и скрипт, если стоит `freecadcmd`) | покрутить STEP, поправить дерево, чертёж | бесплатно, по желанию |
| **КОМПАС-3D** | ты | чертёж под цех, ГОСТ | только если уже есть лицензия |
| **SolidWorks** | не нужен | тот же STEP откроется и там | не покупать ради меня |

OpenSCAD не используем, если цель — КОМПАС: на выходе сетка, не солид.

## Порядок работы

1. Параметры в мм в `cad/parts/<name>.py`
2. `cad/.venv/bin/python cad/build.py <name>`
3. `cad/out/<name>.step` → КОМПАС или FreeCAD
4. DXF слоя CUT — на лазер, STL — только прототип

Перед геометрией читай `cadquery-brep`. Перед «как резать» — `dfm-review`. Если пользователь правит модель мышкой — `freecad-bridge`.
