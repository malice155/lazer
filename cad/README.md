# CAD-пайплайн (CadQuery → STEP → КОМПАС)

Ничего покупать не нужно. КОМПАС — только чтобы открыть готовый `.step` у себя.

```bash
bash cad/install.sh
cad/.venv/bin/python cad/build.py
```

| Файл | Куда |
|---|---|
| `cad/out/*.step` | КОМПАС: Файл → Открыть |
| `cad/out/*.stl` | 3D-печать прототипа |
| `cad/out/*.png` | превью |

Сейчас в сборке: `demo-bracket` (дырочная пластина) и `hydrofoil-demo` (шаблон крыла, не посадка на конкретный мотор).
