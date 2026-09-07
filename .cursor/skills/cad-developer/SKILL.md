---
name: cad-developer
description: Use when changing the cad/ Python pipeline, venv, requirements, build.py, CadQuery install, or STEP export tooling.
---

# Разработчик пайплайна

Стек: **Python 3.12 + CadQuery 2.8** в `cad/.venv`. Покупать КОМПАС/SolidWorks для генерации не нужно.

## Установка

```bash
bash cad/install.sh
# или:
python3 -m venv cad/.venv
cad/.venv/bin/pip install -r cad/requirements.txt
```

Системные libGL обычно уже есть. На голой Ubuntu ещё: `python3.12-venv`, `libglu1-mesa`.

## Команды

```bash
cad/.venv/bin/python cad/build.py                 # все детали
cad/.venv/bin/python cad/build.py demo-bracket
cad/.venv/bin/python cad/build.py hydrofoil-demo
```

Не гонять CadQuery системным `python3` — только venv.

## Куда класть код

- `cad/parts/<name>.py` — `NAME` + `build() -> Workplane`
- регистрация в `PARTS` внутри `cad/build.py`
- экспорт — только через `cad/lib.py` (`export_solid`)
- `.venv` не коммитить; `cad/out/*.step` можно, это выдача под КОМПАС

## Проверка

После экспорта `verify_step()` должен видеть солиды. Если импорт пустой — не отдавать файл пользователю.

Новую деталь не описывай «открой КОМПАС и кликни»: сначала скрипт, потом STEP.
