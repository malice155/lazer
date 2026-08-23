#!/usr/bin/env python3
"""Раскладки пуансона R47 Amada на листах 3015 и 4020."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dxf"
GAP = 4.0
MARGIN = 20.0
SHEETS = {"3015": (3000.0, 1500.0), "4020": (4000.0, 2000.0)}


def _load_amada():
    path = Path(__file__).resolve().parent / "generate_punch_r47_amada_dxf.py"
    spec = importlib.util.spec_from_file_location("punch_r47_amada", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load_amada()


def rot90(x: float, y: float) -> tuple[float, float]:
    return (-y, x)


def origin_shift(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    minx = min(p[0] for p in pts)
    miny = min(p[1] for p in pts)
    return [(p[0] - minx, p[1] - miny) for p in pts]


def part_outline(rotate: bool) -> list[tuple[float, float]]:
    pts = M.punch_outline_points()
    if rotate:
        pts = [rot90(x, y) for x, y in pts]
    return origin_shift(pts)


def part_holes(rotate: bool) -> list[tuple[float, float]]:
    raw = [(x, y) for y in M.HOLE_Y for x in M.HOLE_X]
    base = M.punch_outline_points()
    if rotate:
        base = [rot90(x, y) for x, y in base]
        raw = [rot90(x, y) for x, y in raw]
    minx = min(p[0] for p in base)
    miny = min(p[1] for p in base)
    return [(x - minx, y - miny) for x, y in raw]


def part_wh(rotate: bool) -> tuple[float, float]:
    pts = part_outline(rotate)
    return max(p[0] for p in pts), max(p[1] for p in pts)


def capacity(sheet: str, rotate: bool) -> tuple[int, int, int, float, float]:
    sw, sh = SHEETS[sheet]
    pw, ph = part_wh(rotate)
    px, py = pw + GAP, ph + GAP
    cols = int((sw - 2 * MARGIN) // px)
    rows = int((sh - 2 * MARGIN) // py)
    return cols, rows, cols * rows, px, py


def write_dxf(name: str, sheet: str, cols: int, rows: int, rotate: bool, limit: int | None = None) -> tuple[Path, int]:
    sw, sh = SHEETS[sheet]
    _c, _r, _n, px, py = capacity(sheet, rotate)
    pts = part_outline(rotate)
    hs = part_holes(rotate)
    doc = M._new_doc()
    msp = doc.modelspace()
    n = 0
    for r in range(rows):
        for c in range(cols):
            if limit is not None and n >= limit:
                break
            dx = MARGIN + c * px
            dy = MARGIN + r * py
            M.add_cut_polyline(msp, pts, dx=dx, dy=dy)
            for hx, hy in hs:
                msp.add_circle(
                    (hx + dx, hy + dy),
                    radius=M.HOLE_D / 2.0,
                    dxfattribs={"layer": "CUT", "color": 1},
                )
            n += 1
        if limit is not None and n >= limit:
            break
    msp.add_lwpolyline(
        [(0, 0), (sw, 0), (sw, sh), (0, sh)],
        close=True,
        dxfattribs={"layer": "INFO", "color": 8},
    )
    pose = "rot90" if rotate else "upright"
    msp.add_text(
        f"R47 Amada nest {n}pcs t{M.PLATE_THICKNESS:g} {int(sw)}x{int(sh)} gap{GAP:g} {pose}",
        height=14,
        dxfattribs={"layer": "INFO", "color": 7},
    ).set_placement((12, sh + 18))
    path = OUT / name
    doc.saveas(path)
    return path, n


def write_png(
    name: str,
    sheet: str,
    cols: int,
    rows: int,
    rotate: bool,
    title: str,
    limit: int | None = None,
    crop: bool = False,
) -> Path:
    sw, sh = SHEETS[sheet]
    _c, _r, _n, px, py = capacity(sheet, rotate)
    if crop:
        sw = 2 * MARGIN + cols * px
        sh = 2 * MARGIN + rows * py
    pts = part_outline(rotate)
    scale = 900.0 / sw
    pad_x, pad_top, pad_bot = 26, 34, 26
    W = int(sw * scale) + pad_x * 2
    H = int(sh * scale) + pad_top + pad_bot
    img = Image.new("RGB", (W, H), "#f3efe6")
    d = ImageDraw.Draw(img)

    def xy(x: float, y: float) -> tuple[float, float]:
        return pad_x + x * scale, pad_top + (sh - y) * scale

    d.rectangle([xy(0, sh), xy(sw, 0)], outline="#2a2a2a", width=2)
    n = 0
    for r in range(rows):
        for c in range(cols):
            if limit is not None and n >= limit:
                break
            dx = MARGIN + c * px
            dy = MARGIN + r * py
            d.polygon([xy(x + dx, y + dy) for x, y in pts], outline="#8b1e1e", fill="#e2b7aa")
            n += 1
        if limit is not None and n >= limit:
            break
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
        small = font
    d.text((pad_x, 8), title, fill="#1b1b1b", font=font)
    pw, ph = part_wh(rotate)
    kim = 100.0 * n * pw * ph / (sw * sh)
    d.text((pad_x, H - 20), f"{n} шт · контурный КИМ {kim:.1f}%", fill="#333", font=small)
    path = OUT / name
    img.save(path, optimize=True)
    return path


def write_card(n_strip: int, n_3015: int, n_4020: int, c15: int, r15: int, c20: int, r20: int) -> Path:
    pw, ph = part_wh(False)
    pwr, phr = part_wh(True)
    compact_w = 8 * (pw + GAP) + 2 * MARGIN
    compact_h = 4 * (ph + GAP) + 2 * MARGIN
    qty = M.QTY
    rows = [
        (
            "A компакт 32",
            f"обрезь ~{compact_w:.0f}×{compact_h:.0f}",
            "стоя",
            "8×4",
            32,
            32 / qty,
            100 * 32 * pw * ph / (compact_w * compact_h),
            "текущий заказ, минимум металла",
        ),
        (
            "B полоса 3015",
            "3000×1500",
            "лёжа 90°, 2 ряда",
            f"{c15}×2",
            n_strip,
            n_strip / qty,
            100 * n_strip * pwr * phr / (3000 * 1500),
            "комплект + запас, остаток листа под другие детали",
        ),
        (
            "C полный 3015",
            "3000×1500",
            "лёжа 90°",
            f"{c15}×{r15}",
            n_3015,
            n_3015 / qty,
            100 * n_3015 * pwr * phr / (3000 * 1500),
            "серия комплектов / задел пластин",
        ),
        (
            "D полный 4020",
            "4000×2000",
            "лёжа 90°",
            f"{c20}×{r20}",
            n_4020,
            n_4020 / qty,
            100 * n_4020 * pwr * phr / (4000 * 2000),
            "только если будет стол 4×2 и кран",
        ),
    ]
    lines = [
        "# Раскладки пуансона R47 на лист 3015 / 4020",
        "",
        f"Деталь: Amada/Promecam, **5 мм**, зазор **{GAP:g} мм**, поле зажимов **{MARGIN:g} мм**.",
        f"Один комплект = **{qty} шт** (пакет {M.WORKING_LENGTH:g} мм). Габарит пластины ≈ **{pw:.0f}×{ph:.0f} мм**.",
        "",
        "Ориентир скорости реза 5 мм стали (не паспорт): CO₂ 3 кВт ≈ 2,6 м/мин; fiber 6 кВт ≈ 4,5; fiber 12 кВт ≈ 8.",
        "",
        "| Раскладка | Лист | Поза | Сетка | Шт | Комплектов | КИМ контура | Зачем |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for name, sheet, pose, grid, n, kits, kim, why in rows:
        lines.append(f"| **{name}** | {sheet} | {pose} | {grid} | {n} | {kits:.1f} | {kim:.1f}% | {why} |")
    lines += [
        "",
        "## Файлы",
        "- `punch-R47-amada-nest-32pcs-5mm.dxf` — A (резать сейчас)",
        "- `punch-R47-amada-nest-3015-strip.dxf` — B",
        "- `punch-R47-amada-nest-3015-full.dxf` — C",
        "- `punch-R47-amada-nest-4020-full.dxf` — D",
        "",
        "## Рекомендация",
        "Разовый комплект 32 шт — **A** или **B**. Полный 3015 — когда режете сразу много комплектов.",
        "Стол 4020 этой детали почти не нужен: штук больше, но лист 4×2 без кран-балки не завести.",
        "",
        "```bash",
        "python3 tools/generate_punch_r47_sheet_nests.py",
        "```",
        "",
    ]
    path = OUT / "punch-R47-sheet-nests.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("standing", part_wh(False), "rotated", part_wh(True))
    c15, r15, n15, _, _ = capacity("3015", True)
    c20, r20, n20, _, _ = capacity("4020", True)
    print("3015", c15, "x", r15, "=", n15)
    print("4020", c20, "x", r20, "=", n20)

    write_dxf("punch-R47-amada-nest-3015-strip.dxf", "3015", c15, 2, True)
    write_png("punch-R47-amada-nest-3015-strip.png", "3015", c15, 2, True, "B · полоса 3015 · 2 ряда")

    write_dxf("punch-R47-amada-nest-3015-full.dxf", "3015", c15, r15, True)
    write_png("punch-R47-amada-nest-3015-full.png", "3015", c15, r15, True, "C · полный лист 3015")

    write_dxf("punch-R47-amada-nest-4020-full.dxf", "4020", c20, r20, True)
    write_png("punch-R47-amada-nest-4020-full.png", "4020", c20, r20, True, "D · полный лист 4020")

    write_png(
        "punch-R47-amada-nest-32pcs-preview.png",
        "3015",
        8,
        4,
        False,
        "A · компакт 8×4 · 32 шт",
        limit=32,
        crop=True,
    )

    card = write_card(c15 * 2, n15, n20, c15, r15, c20, r20)
    print(card)


if __name__ == "__main__":
    main()
