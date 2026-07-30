#!/usr/bin/env python3
"""Generate laser DXF for stacked R47 press-brake punch from 5 mm sheet."""

from __future__ import annotations

import math
from pathlib import Path

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

# --- Punch geometry (mm) ---
R = 47.0  # tip radius = required inner bend radius
INCLUDED_ANGLE_DEG = 90.0  # punch included angle
BODY_WIDTH = 80.0  # parallel shank width
OVERALL_HEIGHT = 120.0  # tip -> top
PLATE_THICKNESS = 5.0
WORKING_LENGTH = 160.0  # >= part width 130
QTY = int(round(WORKING_LENGTH / PLATE_THICKNESS))  # 32

# Assembly holes (clamp stack while welding)
HOLE_D = 10.0
HOLE_Y = (55.0, 95.0)  # from tip
HOLE_X = (-18.0, 18.0)

OUT_DIR = Path(__file__).resolve().parents[1] / "dxf"


def punch_outline_points() -> list[tuple[float, float]]:
    """Closed outline: tip at (0,0), body along +Y."""
    half = math.radians(INCLUDED_ANGLE_DEG / 2.0)
    # Tip at (0, 0), radius center at (0, R)
    tp_x = R * math.sin(half)
    tp_y = R * (1.0 - math.cos(half))

    half_w = BODY_WIDTH / 2.0
    dx_needed = half_w - tp_x
    if dx_needed < 0:
        raise ValueError("BODY_WIDTH too narrow for this radius/angle")
    ds = dx_needed / math.sin(half)
    shoulder_y = tp_y + ds * math.cos(half)
    if shoulder_y >= OVERALL_HEIGHT:
        raise ValueError("OVERALL_HEIGHT too small")

    pts: list[tuple[float, float]] = [
        (-half_w, OVERALL_HEIGHT),
        (half_w, OVERALL_HEIGHT),
        (half_w, shoulder_y),
        (tp_x, tp_y),
    ]

    n_arc = 48
    a_right = -math.pi / 2 + half
    a_left = -math.pi / 2 - half
    for i in range(1, n_arc):
        a = a_right + (a_left - a_right) * (i / n_arc)
        pts.append((R * math.cos(a), R + R * math.sin(a)))

    pts += [
        (-tp_x, tp_y),
        (-half_w, shoulder_y),
        (-half_w, OVERALL_HEIGHT),
    ]
    return pts


def add_cut_polyline(msp, points: list[tuple[float, float]], dx: float = 0.0, dy: float = 0.0):
    shifted = [(x + dx, y + dy) for x, y in points]
    # remove duplicate closing point if present
    if math.hypot(shifted[0][0] - shifted[-1][0], shifted[0][1] - shifted[-1][1]) < 1e-9:
        shifted = shifted[:-1]
    msp.add_lwpolyline(
        shifted,
        close=True,
        dxfattribs={"layer": "CUT", "color": 1},  # red = cut
    )


def add_holes(msp, dx: float = 0.0, dy: float = 0.0):
    for y in HOLE_Y:
        for x in HOLE_X:
            msp.add_circle(
                (x + dx, y + dy),
                radius=HOLE_D / 2.0,
                dxfattribs={"layer": "CUT", "color": 1},
            )


def make_single(path: Path):
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    for name, color in (("CUT", 1), ("ENGRAVE", 3), ("INFO", 7)):
        doc.layers.add(name, color=color)

    msp = doc.modelspace()
    outline = punch_outline_points()
    add_cut_polyline(msp, outline)
    add_holes(msp)

    # Engrave mark (optional, machine may ignore or etch)
    msp.add_text(
        "R47 PUNCH 5mm",
        height=4.0,
        dxfattribs={"layer": "ENGRAVE", "color": 3},
    ).set_placement((0, OVERALL_HEIGHT - 12), align=TextEntityAlignment.MIDDLE_CENTER)

    msp.add_text(
        f"x{QTY}  L={WORKING_LENGTH:.0f}",
        height=3.5,
        dxfattribs={"layer": "ENGRAVE", "color": 3},
    ).set_placement((0, OVERALL_HEIGHT - 20), align=TextEntityAlignment.MIDDLE_CENTER)

    # Reference dims on INFO layer (not for cutting)
    msp.add_text(
        f"R{R:g} | {INCLUDED_ANGLE_DEG:g}deg | B{BODY_WIDTH:g} | H{OVERALL_HEIGHT:g} | t{PLATE_THICKNESS:g}",
        height=3.0,
        dxfattribs={"layer": "INFO", "color": 7},
    ).set_placement((0, -12), align=TextEntityAlignment.MIDDLE_CENTER)

    doc.saveas(path)


def make_nest(path: Path, cols: int = 8, rows: int = 4, gap: float = 3.0):
    assert cols * rows >= QTY
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    doc.layers.add("CUT", color=1)
    doc.layers.add("ENGRAVE", color=3)
    doc.layers.add("INFO", color=7)
    msp = doc.modelspace()

    outline = punch_outline_points()
    pitch_x = BODY_WIDTH + gap
    pitch_y = OVERALL_HEIGHT + gap

    n = 0
    for r in range(rows):
        for c in range(cols):
            if n >= QTY:
                break
            dx = c * pitch_x + BODY_WIDTH / 2.0
            dy = r * pitch_y
            add_cut_polyline(msp, outline, dx=dx, dy=dy)
            add_holes(msp, dx=dx, dy=dy)
            n += 1
        if n >= QTY:
            break

    sheet_w = cols * pitch_x
    sheet_h = rows * pitch_y
    msp.add_lwpolyline(
        [(0, -10), (sheet_w, -10), (sheet_w, sheet_h), (0, sheet_h)],
        close=True,
        dxfattribs={"layer": "INFO", "color": 8},
    )
    msp.add_text(
        f"NEST R47 punch | {QTY} pcs x {PLATE_THICKNESS:g}mm | stack L={WORKING_LENGTH:g}mm | sheet ~{sheet_w:.0f}x{sheet_h:.0f}",
        height=5.0,
        dxfattribs={"layer": "INFO", "color": 7},
    ).set_placement((sheet_w / 2, -25), align=TextEntityAlignment.MIDDLE_CENTER)

    doc.saveas(path)
    return sheet_w, sheet_h


def make_preview_png(path: Path):
    from PIL import Image, ImageDraw

    scale = 4  # px/mm
    margin = 40
    w = int(BODY_WIDTH * scale + 2 * margin)
    h = int(OVERALL_HEIGHT * scale + 2 * margin + 40)
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)

    def sx(x):
        return margin + (x + BODY_WIDTH / 2) * scale

    def sy(y):
        return margin + (OVERALL_HEIGHT - y) * scale

    outline = punch_outline_points()
    if math.hypot(outline[0][0] - outline[-1][0], outline[0][1] - outline[-1][1]) < 1e-9:
        poly = outline[:-1]
    else:
        poly = outline
    draw.polygon([(sx(x), sy(y)) for x, y in poly], outline="red", fill=(255, 230, 230))

    for y in HOLE_Y:
        for x in HOLE_X:
            r = HOLE_D / 2 * scale
            cx, cy = sx(x), sy(y)
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline="red", width=2)

    draw.text((margin, h - 30), f"R{R:g} punch plate t={PLATE_THICKNESS:g}  qty={QTY}  L={WORKING_LENGTH:g}", fill="black")
    img.save(path)


def _arc_points(cx: float, cy: float, radius: float, a0: float, a1: float, n: int = 48):
    """Arc points from angle a0 to a1 (radians, CCW from +X)."""
    pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


def make_radius_gauge(path: Path):
    """Female + male R47 gauges for post-weld check (1+1 from 5 mm)."""
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    doc.layers.add("CUT", color=1)
    doc.layers.add("ENGRAVE", color=3)
    doc.layers.add("INFO", color=7)
    msp = doc.modelspace()

    # Female: plate with semicircle R47 seat on top (width 100 >= 2R)
    fw, fh = 100.0, 60.0
    fcx = fw / 2.0
    # endpoints of semicircle on top edge: (fcx±R, fh)
    female = [
        (0.0, 0.0),
        (fw, 0.0),
        (fw, fh),
        (fcx + R, fh),
    ]
    # from right endpoint angle 0° CW to left 180° via bottom (-90°)
    female += _arc_points(fcx, fh, R, 0.0, -math.pi)
    female += [(fcx - R, fh), (0.0, fh)]
    msp.add_lwpolyline(female, close=True, dxfattribs={"layer": "CUT", "color": 1})
    msp.add_text(
        "GAUGE R47 INT",
        height=4,
        dxfattribs={"layer": "ENGRAVE", "color": 3},
    ).set_placement((fcx, 16), align=TextEntityAlignment.MIDDLE_CENTER)

    # Male: convex R47 tip pointing up above rectangular base
    ox = 120.0
    bw, bh = 100.0, 20.0
    mcx = ox + bw / 2.0
    # center on top of base; tip at y = bh+R
    span = math.radians(75)
    a_l = math.pi / 2 + span
    a_r = math.pi / 2 - span
    p_l = (mcx + R * math.cos(a_l), bh + R * math.sin(a_l))
    p_r = (mcx + R * math.cos(a_r), bh + R * math.sin(a_r))
    male = [
        (ox, 0.0),
        (ox + bw, 0.0),
        (ox + bw, bh),
        p_r,
    ]
    male += _arc_points(mcx, bh, R, a_r, a_l)  # right -> tip(+90) -> left
    male += [p_l, (ox, bh)]
    msp.add_lwpolyline(male, close=True, dxfattribs={"layer": "CUT", "color": 1})
    msp.add_text(
        "GAUGE R47 EXT",
        height=4,
        dxfattribs={"layer": "ENGRAVE", "color": 3},
    ).set_placement((mcx, 8), align=TextEntityAlignment.MIDDLE_CENTER)

    msp.add_text(
        "1+1 pcs t=5mm | check punch nose after weld",
        height=3.5,
        dxfattribs={"layer": "INFO", "color": 7},
    ).set_placement((110, -12), align=TextEntityAlignment.MIDDLE_CENTER)

    doc.saveas(path)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    single = OUT_DIR / "punch-R47-plate-5mm.dxf"
    nest = OUT_DIR / "punch-R47-nest-32pcs-5mm.dxf"
    gauge = OUT_DIR / "punch-R47-gauge-5mm.dxf"
    preview = OUT_DIR / "punch-R47-preview.png"

    make_single(single)
    sw, sh = make_nest(nest)
    make_radius_gauge(gauge)
    make_preview_png(preview)

    card = OUT_DIR / "punch-R47-cutting-card.md"
    half = INCLUDED_ANGLE_DEG / 2
    tp_x = R * math.sin(math.radians(half))
    tp_y = R * (1 - math.cos(math.radians(half)))
    card.write_text(
        f"""# Лазер: пластины пуансона R47

## Файлы
- `{single.name}` — 1 контур (для ЧПУ / ручного размножения)
- `{nest.name}` — готовый нестинг **{QTY} шт** (~{sw:.0f}×{sh:.0f} мм)
- `{gauge.name}` — шаблоны контроля радиуса R47 (внутр. + наруж.), 2 шт
- `{preview.name}` — эскиз профиля

## Параметры пластины пуансона
| | |
|---|---|
| Материал | лист **{PLATE_THICKNESS:g} мм** (Ст3 / S235 и аналог) |
| Количество | **{QTY} шт** |
| Длина пакета после сборки | **{WORKING_LENGTH:g} мм** (деталь 130 мм) |
| Радиус носика | **R{R:g}** |
| Угол пуансона | **{INCLUDED_ANGLE_DEG:g}°** |
| Ширина хвостовика | **{BODY_WIDTH:g} мм** |
| Высота пластины | **{OVERALL_HEIGHT:g} мм** |
| Отверстия сборки | **4×Ø{HOLE_D:g}** (шпильки M10) |

## Слои DXF
- `CUT` (красный) — рез
- `ENGRAVE` (зелёный) — маркировка (по желанию)
- `INFO` — не резать

## Сборка
1. Вырезать {QTY} пластин (+ 2 калибра из `{gauge.name}`).
2. Собрать пакет на 4 шпильки M10, выровнять по контуру.
3. Обварить по периметру короткими швами вразброс (чтобы не повело).
4. Зачистить носик; проверить калибром R47.
5. Сверху хвостовика 80 мм приварить/прикрутить переходник под зажим вашего листогиба.

## Лазер
- Ед. измерения DXF: **мм**
- Контур в номинале. Компенсацию керифа задайте в ПО станка так, чтобы **R47 ≥ чертежа** (лучше чуть больше, чем меньше).
- Рекомендуемый зазор нестинга: уже заложен **3 мм**.
""",
        encoding="utf-8",
    )

    print(f"QTY={QTY}")
    print(f"wrote {single}")
    print(f"wrote {nest} nest~{sw:.0f}x{sh:.0f}")
    print(f"wrote {gauge}")
    print(f"wrote {preview}")
    print(f"wrote {card}")
    print(f"TP=({tp_x:.3f},{tp_y:.3f})")


if __name__ == "__main__":
    main()
