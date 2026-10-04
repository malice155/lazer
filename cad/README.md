# CAD-пайплайн (CadQuery → STEP → КОМПАС или FreeCAD)

Конструктор работает в **CadQuery**. Покупать SolidWorks не нужно. КОМПАС и FreeCAD — чтобы открыть готовый `.step` у себя.

```bash
bash cad/install.sh
cad/.venv/bin/python cad/build.py
```

| Файл | Куда |
|---|---|
| `cad/out/*.step` | КОМПАС: Файл → Открыть |
| `cad/out/*.stl` | 3D-печать прототипа |
| `cad/out/*.png` | превью |

Сейчас в сборке: `demo-bracket`, `hydrofoil-demo`, **`tohatsu-m98-hydrofoil`** ([карточка](./tohatsu-m98.md)), **`granta-bmw-seat-rail`** — переходник сиденья BMW на Гранту ([карточка](./granta-bmw-seat.md)), **`tlc120-e39-bracket-outer` / `inner`** — гнутый кронштейн сиденья E39 на пол Prado 120 ([карточка](./tlc120-e39-seat.md)). Плоский `tlc120-bmw-seat-rail` на этот пол не класть.
