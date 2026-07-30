#!/usr/bin/env python3
"""Laser DXF: laminated R47 punch with Amada/Promecam 13 mm tang."""

from __future__ import annotations

import math
from pathlib import Path

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

# Working nose
R = 47.0
INCLUDED_ANGLE_DEG = 90.0

# Amada / Promecam tang (European 13 mm)
TANG_W = 13.0
TANG_H = 45.0  # shoulder -> top
GROOVE_FROM_TOP = 6.5
GROOVE_H = 7.0
GROOVE_DEPTH = 5.5  # from FRONT (+X) face only

# Must be >= 2*R*sin(half_angle) so flanks don't undercut the nose
BODY_W = 70.0  # width at / below shoulder (>= 66.5 for R47/90°)
OVERALL_H = 150.0  # tip -> top of tang

PLATE_THICKNESS = 5.0
WORKING_LENGTH = 160.0
QTY = int(round(WORKING_LENGTH / PLATE_THICKNESS))  # 32

# stack alignment holes in body (not in tang)
HOLE_D = 10.0
HOLE_Y = (55.0, 90.0)
HOLE_X = (-15.0, 15.0)

OUT_DIR = Path(__file__).resolve().parents[1] / "dxf"


def punch_outline_points() -> list[tuple[float, float]]:
    """Tip at (0,0), +Y up. Tang centered, safety groove on +X (front)."""
    half = math.radians(INCLUDED_ANGLE_DEG / 2.0)
    tp_x = R * math.sin(half)
    tp_y = R * (1.0 - math.cos(half))

    half_body = BODY_W / 2.0
    half_tang = TANG_W / 2.0
    shoulder_y = OVERALL_H - TANG_H
    if shoulder_y <= tp_y + 15:
        raise ValueError("overall height too small for R47 + tang")

    # Flank from TP out to body width (45° for 90° punch)
    dx_needed = half_body - tp_x
    ds = dx_needed / math.sin(half)
    flare_y = tp_y + ds * math.cos(half)

    # Groove geometry (front = +X)
    g_top = OVERALL_H - GROOVE_FROM_TOP
    g_bot = g_top - GROOVE_H
    g_x = half_tang - GROOVE_DEPTH  # inward from front face

    pts: list[tuple[float, float]] = []

    # --- top of tang, left -> right ---
    pts.append((-half_tang, OVERALL_H))
    pts.append((half_tang, OVERALL_H))

    # front face down to groove
    pts.append((half_tang, g_top))
    # groove pocket
    pts.append((g_x, g_top))
    pts.append((g_x, g_bot))
    pts.append((half_tang, g_bot))

    # front face down to shoulder
    pts.append((half_tang, shoulder_y))
    # right shoulder seat
    pts.append((half_body, shoulder_y))

    # right body down to flare, then flank to TP
    if flare_y < shoulder_y - 0.5:
        pts.append((half_body, flare_y))
    pts.append((tp_x, tp_y))

    # arc tip
    n_arc = 56
    a_right = -math.pi / 2 + half
    a_left = -math.pi / 2 - half
    for i in range(1, n_arc):
        a = a_right + (a_left - a_right) * (i / n_arc)
        pts.append((R * math.cos(a), R + R * math.sin(a)))

    pts.append((-tp_x, tp_y))
    if flare_y < shoulder_y - 0.5:
        pts.append((-half_body, flare_y))

    # left shoulder + tang back face up
    pts.append((-half_body, shoulder_y))
    pts.append((-half_tang, shoulder_y))
    pts.append((-half_tang, OVERALL_H))
    return pts


def add_cut_polyline(msp, points, dx=0.0, dy=0.0):
    shifted = [(x + dx, y + dy) for x, y in points]
    if math.hypot(shifted[0][0] - shifted[-1][0], shifted[0][1] - shifted[-1][1]) < 1e-9:
        shifted = shifted[:-1]
    msp.add_lwpolyline(shifted, close=True, dxfattribs={"layer": "CUT", "color": 1})


def add_holes(msp, dx=0.0, dy=0.0):
    for y in HOLE_Y:
        for x in HOLE_X:
            msp.add_circle((x + dx, y + dy), radius=HOLE_D / 2.0, dxfattribs={"layer": "CUT", "color": 1})


def _new_doc():
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.header["$INSUNITS"] = units.MM
    for name, color in (("CUT", 1), ("ENGRAVE", 3), ("INFO", 7)):
        doc.layers.add(name, color=color)
    return doc


def make_single(path: Path):
    doc = _new_doc()
    msp = doc.modelspace()
    add_cut_polyline(msp, punch_outline_points())
    add_holes(msp)
    msp.add_text(
        "R47 AMADA/PROMECAM",
        height=3.5,
        dxfattribs={"layer": "ENGRAVE", "color": 3},
    ).set_placement((0, OVERALL_H - TANG_H - 10), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(
        f"tang {TANG_W:g}  x{QTY} L={WORKING_LENGTH:g}",
        height=3.0,
        dxfattribs={"layer": "ENGRAVE", "color": 3},
    ).set_placement((0, OVERALL_H - TANG_H - 18), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(
        f"R{R:g} | tang{TANG_W:g} groove{GROOVE_DEPTH:g} | H{OVERALL_H:g} | t{PLATE_THICKNESS:g}",
        height=2.8,
        dxfattribs={"layer": "INFO", "color": 7},
    ).set_placement((0, -14), align=TextEntityAlignment.MIDDLE_CENTER)
    doc.saveas(path)


def make_nest(path: Path, cols=8, rows=4, gap=3.0):
    doc = _new_doc()
    msp = doc.modelspace()
    outline = punch_outline_points()
    # nesting pitch uses bbox width ~ BODY_W
    pitch_x = BODY_W + gap + 4  # small extra for tang asymmetry visual
    pitch_y = OVERALL_H + gap
    n = 0
    for r in range(rows):
        for c in range(cols):
            if n >= QTY:
                break
            dx = c * pitch_x + BODY_W / 2.0
            dy = r * pitch_y
            add_cut_polyline(msp, outline, dx=dx, dy=dy)
            add_holes(msp, dx=dx, dy=dy)
            n += 1
        if n >= QTY:
            break
    sheet_w = cols * pitch_x
    sheet_h = rows * pitch_y
    msp.add_lwpolyline(
        [(0, -12), (sheet_w, -12), (sheet_w, sheet_h), (0, sheet_h)],
        close=True,
        dxfattribs={"layer": "INFO", "color": 8},
    )
    msp.add_text(
        f"NEST R47 Amada/Promecam | {QTY}x{PLATE_THICKNESS:g}mm | L={WORKING_LENGTH:g} | ~{sheet_w:.0f}x{sheet_h:.0f}",
        height=4.5,
        dxfattribs={"layer": "INFO", "color": 7},
    ).set_placement((sheet_w / 2, -28), align=TextEntityAlignment.MIDDLE_CENTER)
    doc.saveas(path)
    return sheet_w, sheet_h


def make_preview(path: Path):
    from PIL import Image, ImageDraw

    outline = punch_outline_points()
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    scale = 5
    ml, mr, mt, mb = 90, 120, 50, 70
    W = int((max(xs) - min(xs)) * scale + ml + mr)
    Himg = int((max(ys) - min(ys)) * scale + mt + mb)
    img = Image.new("RGB", (W, Himg), "white")
    d = ImageDraw.Draw(img)
    minx, maxy = min(xs), max(ys)

    def sx(x):
        return ml + (x - minx) * scale

    def sy(y):
        return mt + (maxy - y) * scale

    poly = [(sx(x), sy(y)) for x, y in outline[:-1]]
    d.polygon(poly, outline="#b00000", fill="#ffe0e0")
    for y in HOLE_Y:
        for x in HOLE_X:
            rr = HOLE_D / 2 * scale
            cx, cy = sx(x), sy(y)
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline="#b00000", width=2)

    # dims
    half_tang = TANG_W / 2
    half_body = BODY_W / 2
    shoulder_y = OVERALL_H - TANG_H
    d.line([(sx(-half_tang), sy(OVERALL_H) - 22), (sx(half_tang), sy(OVERALL_H) - 22)], fill="#003399", width=2)
    d.text((sx(0) - 12, sy(OVERALL_H) - 40), "13", fill="#003399")
    d.line([(sx(half_body) + 28, sy(0)), (sx(half_body) + 28, sy(OVERALL_H))], fill="#003399", width=2)
    d.text((sx(half_body) + 34, sy(OVERALL_H / 2)), "150", fill="#003399")
    d.text((sx(0) - 18, sy(0) + 8), "R47", fill="#003399")
    d.text((sx(half_tang) + 8, sy(OVERALL_H - 10)), "канавка", fill="#003399")
    d.text((sx(0) - 40, sy(shoulder_y) - 14), "плечо Amada", fill="#003399")
    d.text((20, Himg - 45), "Amada/Promecam tang 13mm + safety groove | sheet 5mm | 32pcs => L=160", fill="#111")
    d.text((20, Himg - 22), "FOR Amada Operateur / Promecam clamps (not flat 80mm shank)", fill="#111")
    img.save(path)


def make_card(path: Path, nest_w: float, nest_h: float):
    path.write_text(
        f"""# Пуансон R47 под Amada / Promecam

Станок: **Amada + Operateur**, зажим Promecam (пружинный/сегментный).
Старый DXF с прямоугольным хвостовиком 80 мм — **не подходит**.

## Новый профиль
| | |
|---|---|
| Носик | **R47**, угол 90° |
| Хвостовик | **13 мм** (Amada/Promecam) |
| Канавка безопасности | глубина **{GROOVE_DEPTH:g}**, высота **{GROOVE_H:g}**, от верха **{GROOVE_FROM_TOP:g}** |
| Высота плеча→верх | **{TANG_H:g} мм** |
| Ширина плеча/тела | **{BODY_W:g} мм** |
| Полная высота | **{OVERALL_H:g} мм** |
| Лист | **{PLATE_THICKNESS:g} мм**, **{QTY} шт**, пакет **{WORKING_LENGTH:g} мм** |

## Файлы
- `punch-R47-amada-nest-32pcs-5mm.dxf` — резать (~{nest_w:.0f}×{nest_h:.0f})
- `punch-R47-amada-plate-5mm.dxf` — 1 шт
- `punch-R47-amada-preview.png` — эскиз

## Сборка
1. Вырезать {QTY} пластин.
2. Собрать на шпильки M10, выровнять **по хвостовику 13 мм**.
3. Обварить короткими швами вразброс.
4. **Обязательно прошлифовать плоскости хвостовика 13 мм** (чтобы зашёл в зажим без ступенек).
5. Проверить посадку в зажим Amada на одном сегменте до полной обварки, если возможно.

## В контроллере Operateur
Заведите новый инструмент (например вместо `R PUNCH 8802`): радиус **47**, высота инструмента по факту после изготовления, материал STEEL, толщина детали **1.5**.
""",
        encoding="utf-8",
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    single = OUT_DIR / "punch-R47-amada-plate-5mm.dxf"
    nest = OUT_DIR / "punch-R47-amada-nest-32pcs-5mm.dxf"
    preview = OUT_DIR / "punch-R47-amada-preview.png"
    card = OUT_DIR / "punch-R47-amada-cutting-card.md"

    make_single(single)
    sw, sh = make_nest(nest)
    make_preview(preview)
    make_card(card, sw, sh)
    print("QTY", QTY)
    print(single)
    print(nest, f"{sw:.0f}x{sh:.0f}")
    print(preview)
    print(card)


if __name__ == "__main__":
    main()
