"""Tohatsu 9.8 hydrofoil (M9.8B 2-stroke and clones). Sheet for laser + КОМПАС.

PROMPT
------
Спроектировать гидрокрыло на антикавитационную плиту Tohatsu 9.8 (самый
частый у нас — 2-такт M9.8B / Nissan NS9.8 / клоны Sea-Pro, Parsun, HDX).
Не сверлить редуктор: U-вырез + зажимные планки. Параметры в мм наверху
файла. Выход: STEP уже с гибами 15° вниз, DXF — плоская развёртка на лазер.
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

import math

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

# Two brakes, tips down. Inner radius = sheet thickness. Flange at the
# narrow (leading) end stays longer than a V24 die.
BEND_ANGLE = 15.0
BEND_R = 3.0
BEND_K = 0.4
FLANGE_AT_LE = 32.0

SHOW = {"roll": -12.0, "elevation": -22.0, "azimuth": 48.0, "zoom": 1.05}
SHOW_CLAMP = {"roll": 0.0, "elevation": -80.0, "azimuth": 20.0, "zoom": 1.2}


def _notch_half() -> float:
    return LEG_NOTCH_W / 2.0


def _bolt_y() -> float:
    return AV_PLATE_W / 2.0 + BOLT_OUTBOARD


def _y_bend() -> float:
    """Bend tangent, measured from the centerline. Same on both tips."""
    return SPAN_LE / 2.0 - FLANGE_AT_LE


def _bend_allowance() -> float:
    return math.radians(BEND_ANGLE) * (BEND_R + BEND_K * THICKNESS)


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


def _inside(shape: cq.Shape, x: float, y: float) -> bool:
    return shape.isInside(cq.Vector(x, y, THICKNESS / 2.0))


def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
    """DFM: slots are open, metal remains around them, bend line clears the slots."""
    if not shape.isValid():
        raise RuntimeError("solid is not valid")
    if len(shape.Solids()) != 1:
        raise RuntimeError("expected one solid")
    # The U-notch is empty; the plate beside it is not.
    if not clamp and _inside(shape, LEG_NOTCH_DEPTH / 2.0, 0.0):
        raise RuntimeError("leg notch is filled")
    if not clamp and not _inside(shape, LEG_NOTCH_DEPTH / 2.0, LEG_NOTCH_W / 2.0 + 8.0):
        raise RuntimeError("plate beside the notch is missing")
    half = SLOT_LEN / 2.0
    radius = BOLT_D / 2.0
    min_wall = 2.0 * THICKNESS
    points = (
        [(CHORD - HOLE_FROM_TE, _bolt_y()), (CHORD - HOLE_FROM_TE - HOLE_SPACING_X, _bolt_y())]
        if clamp
        else bolt_points()
    )
    for x, y in points:
        if _inside(shape, x, y):
            raise RuntimeError(f"slot still filled at {x},{y}")
        sign = 1.0 if y > 0 else -1.0
        for px, py in (
            (x, y + sign * (half + 2.0)),
            (x, y - sign * (half + 2.0)),
            (x - (radius + 2.0), y),
            (x + (radius + 2.0), y),
        ):
            if not _inside(shape, px, py):
                raise RuntimeError(f"slot breaks the edge at {px:.1f},{py:.1f}")
        if HOLE_FROM_TE - radius < min_wall:
            raise RuntimeError("slot too close to the trailing edge")
    if not clamp:
        bend_gap = _y_bend() - (_bolt_y() + half)
        if bend_gap < min_wall:
            raise RuntimeError(f"bend line too close to slot: {bend_gap:.1f} mm")
        # Mid-thickness of the +Y flange, 18 mm past the tangent, must sit below the sheet.
        if not shape.isInside(cq.Vector(CHORD * 0.75, _y_bend() + 20.0, -3.0)):
            raise RuntimeError("tip did not bend down")


def _tip_profile(straight: float) -> cq.Workplane:
    """Cross-section in YZ: inner radius, then a straight flange downward."""
    angle = math.radians(BEND_ANGLE)
    ca, sa = math.cos(angle), math.sin(angle)
    radius = BEND_R
    thick = THICKNESS
    inner_arc = (radius * sa, -radius + radius * ca)
    outer_arc = ((radius + thick) * sa, -radius + (radius + thick) * ca)
    inner_end = (inner_arc[0] + straight * ca, inner_arc[1] - straight * sa)
    outer_end = (outer_arc[0] + straight * ca, outer_arc[1] - straight * sa)
    return (
        cq.Workplane("YZ")
        .moveTo(0, 0)
        .lineTo(*inner_arc)
        .lineTo(*inner_end)
        .lineTo(*outer_end)
        .lineTo(*outer_arc)
        .radiusArc((0, thick), -(radius + thick))
        .close()
    )


def _planform_prism() -> cq.Workplane:
    sheet = outline().extrude(THICKNESS).edges("|Z").fillet(CORNER_FILLET)
    return sheet.faces(">Z").wires().toPending().extrude(-60)


def build_flat() -> cq.Workplane:
    """Laser blank. Bend lines are drawn on this, not cut."""
    plate = outline().extrude(THICKNESS)
    plate = plate.edges("|Z").fillet(CORNER_FILLET)
    holes = (
        cq.Workplane("XY")
        .pushPoints(bolt_points())
        .slot2D(SLOT_LEN, BOLT_D, 90.0)
        .extrude(THICKNESS + 2.0)
    )
    return plate.cut(holes)


def build() -> cq.Workplane:
    """Formed part: flat centre, both tips bent down."""
    flat = build_flat()
    y_bend = _y_bend()
    guard = (
        cq.Workplane("XY")
        .box(CHORD + 80.0, 2.0 * y_bend + 0.1, THICKNESS + 8.0)
        .translate((CHORD / 2.0, 0.0, THICKNESS / 2.0))
    )
    center = flat.intersect(guard)
    # Longest flat flange is at the trailing edge; the planform prism trims the rest.
    straight = (SPAN_TE / 2.0 - y_bend) - _bend_allowance()
    bar = _tip_profile(straight).extrude(CHORD + 40.0).translate((-20.0, y_bend, 0.0))
    prism = _planform_prism()
    positive = bar.intersect(prism)
    formed = center.union(positive).union(positive.mirror("XZ"))
    audit(formed.val())
    return formed


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
    part = strap.cut(holes)
    audit(part.val(), clamp=True)
    return part


def post_dxf(path) -> None:
    """Flat laser blank. CUT is the contour, BEND is the brake line — do not cut it."""
    import ezdxf
    from ezdxf import colors
    from cadquery import exporters

    exporters.exportDXF(build_flat().section(), str(path), approx="arc")
    doc = ezdxf.readfile(str(path))
    if "CUT" not in doc.layers:
        doc.layers.add("CUT", color=colors.RED)
    if "BEND" not in doc.layers:
        doc.layers.add("BEND", color=colors.YELLOW)
    msp = doc.modelspace()
    for ent in msp:
        ent.dxf.layer = "CUT"
    y_bend = _y_bend()
    note = f"BEND {BEND_ANGLE:.0f}deg DOWN  Rin {BEND_R:.0f}  x2  do not cut"
    msp.add_text(note, dxfattribs={"layer": "BEND", "height": 5}).set_placement((16.0, 8.0))
    for y in (y_bend, -y_bend):
        msp.add_line((2.0, y), (CHORD - 2.0, y), dxfattribs={"layer": "BEND"})
    doc.saveas(str(path))


class ClampPart:
    NAME = CLAMP_NAME
    SHOW = SHOW_CLAMP

    @staticmethod
    def build() -> cq.Workplane:
        return build_clamp()
