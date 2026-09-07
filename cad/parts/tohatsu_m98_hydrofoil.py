"""Tohatsu 9.8 hydrofoil (M9.8B 2-stroke and clones). Sheet for laser + КОМПАС.

PROMPT
------
Спроектировать гидрокрыло на антикавитационную плиту Tohatsu 9.8 (самый
частый у нас — 2-такт M9.8B / Nissan NS9.8 / клоны Sea-Pro, Parsun, HDX).
Не сверлить редуктор: U-вырез + зажимные планки. Параметры в мм наверху
файла. Выход: STEP в КОМПАС, DXF на лазер (лист АМГ 3 мм), STL прототип.
Вырез и ширину плиты пометить MEASURE — официального размера АКП нет.
Задняя кромка крыла — впереди плоскости винта. Это прикидка, не ГОСТ.

Источники (публичные, не чертёж завода):
- Tohatsu M9.8B: 7.2 кВт, 26 кг, винт 8.5×9, АКП ниже днища 30–50 мм
  https://www.tohatsu.com/marine/int/outboards/M9.8B.html
- Серийное съёмное крыло 5–9.8 л.с.: 290×320 мм, нерж 2 мм, без сверления
  (d-techno / магазины РФ)
- SE Sport 200 (8–40 hp): 13.5×14.3 in = 343×363 мм — часто ставят на 9.8/9.9
- DIY РФ 4–10 л.с.: АМГ-5м 3 мм, U-вырез под ногу мерить на моторе
- GitHub: готового CadQuery/STEP под Tohatsu 9.8 нет (fingerfoil и т.п. — другой тип крыльев)
"""

from __future__ import annotations

import cadquery as cq

NAME = "tohatsu-m98-hydrofoil"
CLAMP_NAME = "tohatsu-m98-clamp"

# --- envelope from commercial 5–9.8 hp clamp-on foils (mm) ---
SPAN_LE = 280.0  # leading span, slightly narrower
SPAN_TE = 320.0  # trailing span = d-techno width
CHORD = 290.0  # d-techno length
THICKNESS = 3.0  # AMG-5M / Д16; нерж — 2.0
CORNER_FILLET = 14.0

# --- MEASURE on the motor (defaults = photo/prop scale + DIY, not factory CAD) ---
# Housing width at AV plate + 6…8 mm clearance. M9.8B ~75–82 mm housing.
LEG_NOTCH_W = 88.0
LEG_NOTCH_DEPTH = 118.0
# AV plate width at trailing third. Scaled vs 8.5" (216 mm) prop in photos.
AV_PLATE_W = 158.0
AV_PLATE_THICK = 6.0  # cast plate; clamp gap uses this

# --- clamp-on M6, bolts outboard of the plate (no drill into gearcase) ---
BOLT_D = 6.6  # clearance for M6
SLOT_LEN = 14.0  # ±7 mm for plate-width scatter
BOLT_OUTBOARD = 11.0  # plate edge → bolt center
CLAMP_OVERLAP = 28.0  # how far the strap goes under the plate
HOLE_FROM_TE = 32.0
HOLE_SPACING_X = 48.0

SHOW = {"roll": 0.0, "elevation": -70.0, "azimuth": 18.0, "zoom": 1.0}
SHOW_CLAMP = {"roll": 0.0, "elevation": -80.0, "azimuth": 20.0, "zoom": 1.2}


def _notch_half() -> float:
    return LEG_NOTCH_W / 2.0


def _bolt_y() -> float:
    return AV_PLATE_W / 2.0 + BOLT_OUTBOARD


def bolt_points() -> list[tuple[float, float]]:
    y = _bolt_y()
    x1 = CHORD - HOLE_FROM_TE
    x0 = x1 - HOLE_SPACING_X
    return [(x0, y), (x1, y), (x0, -y), (x1, -y)]


def outline() -> cq.Workplane:
    """Closed planform: U opens forward (bow), trailing toward propeller."""
    nw = _notch_half()
    nd = LEG_NOTCH_DEPTH
    sle = SPAN_LE / 2.0
    ste = SPAN_TE / 2.0
    return (
        cq.Workplane("XY")
        .moveTo(0.0, nw)
        .lineTo(0.0, sle)
        .lineTo(CHORD, ste)
        .lineTo(CHORD, -ste)
        .lineTo(0.0, -sle)
        .lineTo(0.0, -nw)
        .lineTo(nd, -nw)
        .lineTo(nd, nw)
        .close()
    )


def build() -> cq.Workplane:
    plate = outline().extrude(THICKNESS)
    plate = plate.edges("|Z").fillet(CORNER_FILLET)
    holes = (
        cq.Workplane("XY")
        .pushPoints(bolt_points())
        .slot2D(SLOT_LEN, BOLT_D, 90.0)
        .extrude(THICKNESS + 2.0)
    )
    return plate.cut(holes)


def build_clamp() -> cq.Workplane:
    """One strap (cut 2 pcs; second is mirrored in Y). Slots match the wing."""
    y_in = AV_PLATE_W / 2.0 - CLAMP_OVERLAP
    y_out = AV_PLATE_W / 2.0 + BOLT_OUTBOARD + 12.0
    x1 = CHORD - HOLE_FROM_TE
    x0 = x1 - HOLE_SPACING_X
    pad = 16.0
    strap = (
        cq.Workplane("XY")
        .moveTo(x0 - pad, y_in)
        .lineTo(x1 + pad, y_in)
        .lineTo(x1 + pad, y_out)
        .lineTo(x0 - pad, y_out)
        .close()
        .extrude(THICKNESS)
        .edges("|Z")
        .fillet(4.0)
    )
    holes = (
        cq.Workplane("XY")
        .pushPoints([(x0, _bolt_y()), (x1, _bolt_y())])
        .slot2D(SLOT_LEN, BOLT_D, 90.0)
        .extrude(THICKNESS + 2.0)
    )
    return strap.cut(holes)


def post_dxf(path) -> None:
    """Shop layers: CUT (laser) + BEND (optional 15° tip downturn on the brake)."""
    import ezdxf
    from ezdxf import colors

    doc = ezdxf.readfile(str(path))
    if "CUT" not in doc.layers:
        doc.layers.add("CUT", color=colors.RED)
    if "BEND" not in doc.layers:
        doc.layers.add("BEND", color=colors.YELLOW)
    msp = doc.modelspace()
    for ent in msp:
        if ent.dxf.layer != "BEND":
            ent.dxf.layer = "CUT"
    y_bend = SPAN_TE / 2.0 - 40.0
    for y in (y_bend, -y_bend):
        msp.add_line(
            (18.0, y),
            (CHORD - 12.0, y),
            dxfattribs={"layer": "BEND"},
        )
    doc.saveas(str(path))


class ClampPart:
    NAME = CLAMP_NAME
    SHOW = SHOW_CLAMP

    @staticmethod
    def build() -> cq.Workplane:
        return build_clamp()
