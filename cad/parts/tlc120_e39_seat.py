"""Rigid frame: BMW E39 seat on a Toyota Prado 120 (TLC 120) floor.

The J120 floor under a front seat is not one plane. The tunnel-side bolts
sit higher than the door-side bolts. Two separate slotted channels can
twist and slide, so this seat sits on a frame:

- one bent rail on the door side
- one bent rail on the tunnel side, shorter web by FLOOR_STEP
- one flat tie plate bolted across both top flanges

Four holes, not slots. The holes sit on the measured floor pattern:
520 mm along each rail, 420 mm between the rails. The plate uses the
same four centers. No second pitch is drawn in for the E39 rail.
FLOOR_STEP is still not measured.

Brake: 4 mm steel, two bends 90°, inside radius 4 mm, die V32.
Promecam tang 13 mm. The R47 punch in dxf/ is a different tool.
A gooseneck punch clears the first flange on the second bend.
The tie plate is laser only, no bend.
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

NAME_OUTER = "tlc120-e39-bracket-outer"
NAME_INNER = "tlc120-e39-bracket-inner"
NAME_PLATE = "tlc120-e39-tie-plate"
NAME_SEAT = "tlc120-e39-seat"

# --- sheet and brake ---
THICKNESS = 4.0
BEND_R = 4.0  # inside radius, equal to thickness
BEND_K = 0.4  # ANSI K, same as the hydrofoil blank
BEND_ANGLE = 90.0
DIE_V = 32.0  # 8 x thickness

# MEASURE. Inner pad higher than the outer pad, mm. Not a Toyota drawing.
FLOOR_STEP = 20.0
# Straight web between the bend tangents. Inner stays formable on V32.
INNER_WEB = 28.0
OUTER_WEB = INNER_WEB + FLOOR_STEP

# Flanges. Short, solid, one hole row. A long slotted flange folds.
FOOT = 40.0
TOP = 40.0
# Hole center, mm from the bend tangent, on both flanges.
HOLE_FROM_TANGENT = 18.0
# Metal past each hole center, along the rail.
END_MARGIN = 25.0
# Metal past each seat-hole line, on the tie plate.
PLATE_MARGIN = 28.0

# Center distance along one rail between the two floor-bolt holes.
# Measured on the TLC 120 BMW-seat rails.
FLOOR_PITCH = 520.0

# Prado bolt 90119-10921, Toyota 90119-10 series: M10. Confirm on the car.
FLOOR_BOLT_D = 10.5
# E39 rail screw on the RealOEM rail diagram is M10 (52108162348).
E39_BOLT_D = 10.5

# Center distance between the hole of one rail and the hole of the other.
# Measured on the TLC 120 BMW-seat rails.
FLOOR_WIDTH = 420.0

SHOW_BRACKET = {"roll": 0.0, "elevation": -18.0, "azimuth": 70.0, "zoom": 1.15}
SHOW_PLATE = {"roll": 0.0, "elevation": -55.0, "azimuth": 25.0, "zoom": 1.05}
SHOW_SEAT = {"roll": 0.0, "elevation": -24.0, "azimuth": 18.0, "zoom": 0.88}


def _ba() -> float:
    """Bend allowance along the neutral axis, 90°, ANSI K."""
    return math.radians(BEND_ANGLE) * (BEND_R + BEND_K * THICKNESS)


def rail_length() -> float:
    return FLOOR_PITCH + 2.0 * END_MARGIN


def hole_y() -> float:
    """Hole center on the formed flange, toward -Y from the web."""
    return -(BEND_R + HOLE_FROM_TANGENT)


def _heights(web: float) -> dict[str, float]:
    z_web0 = THICKNESS + BEND_R
    z_web1 = z_web0 + web
    z_under = THICKNESS + 2.0 * BEND_R + web
    z_top = 2.0 * THICKNESS + 2.0 * BEND_R + web
    return {"web0": z_web0, "web1": z_web1, "under": z_under, "top": z_top}


def top_z(web: float) -> float:
    return _heights(web)["top"]


def flat_width(web: float) -> float:
    """Developed width: two straight flanges, web, two bend allowances."""
    straight_foot = FOOT - BEND_R
    return straight_foot + _ba() + web + _ba() + TOP


def _section(web: float) -> cq.Workplane:
    """C-channel in the YZ plane. Flanges extend toward -Y, web at y = 0..T."""
    h = _heights(web)
    return (
        cq.Workplane("YZ")
        .moveTo(-FOOT, 0)
        .lineTo(-BEND_R, 0)
        .radiusArc((THICKNESS, h["web0"]), -(BEND_R + THICKNESS))
        .lineTo(THICKNESS, h["web1"])
        .radiusArc((-BEND_R, h["top"]), -(BEND_R + THICKNESS))
        .lineTo(-BEND_R - TOP, h["top"])
        .lineTo(-BEND_R - TOP, h["under"])
        .lineTo(-BEND_R, h["under"])
        .radiusArc((0, h["web1"]), BEND_R)
        .lineTo(0, h["web0"])
        .radiusArc((-BEND_R, THICKNESS), BEND_R)
        .lineTo(-FOOT, THICKNESS)
        .close()
    )


def _hole(x: float, y: float, diameter: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(x, y)
        .circle(diameter / 2.0)
        .extrude(z1 - z0)
    )


def _stations(pitch: float) -> tuple[float, float]:
    return (-pitch / 2.0, pitch / 2.0)


def build_bracket(web: float) -> cq.Workplane:
    if web < 24.0:
        raise RuntimeError(f"web {web:.0f} mm falls into a V{DIE_V:.0f} die")
    h = _heights(web)
    length = rail_length()
    body = _section(web).extrude(length).translate((-length / 2.0, 0, 0))
    cut = None
    y = hole_y()
    for x in _stations(FLOOR_PITCH):
        hole = _hole(x, y, FLOOR_BOLT_D, -1.0, THICKNESS + 1.0)
        cut = hole if cut is None else cut.union(hole)
    for x in _stations(FLOOR_PITCH):
        hole = _hole(x, y, E39_BOLT_D, h["under"] - 1.0, h["top"] + 1.0)
        cut = cut.union(hole)
    part = body.cut(cut)
    _audit_bracket(part.val(), web)
    return part


def _inside(shape: cq.Shape, x: float, y: float, z: float) -> bool:
    return shape.isInside(cq.Vector(x, y, z))


def _edge_ok(center: float, limit: float, diameter: float) -> bool:
    """True when the hole edge is at least 2 x thickness from a wall or tip."""
    return abs(center - limit) - diameter / 2.0 >= 2.0 * THICKNESS - 0.05


def _audit_bracket(shape: cq.Shape, web: float) -> None:
    if not shape.isValid():
        raise RuntimeError("bracket is not a valid solid")
    if len(shape.Solids()) != 1:
        raise RuntimeError("bracket must be one solid")
    h = _heights(web)
    y = hole_y()
    z_top_mid = (h["under"] + h["top"]) / 2.0
    # Holes are open. The flange between them stays solid: no slot.
    for x in _stations(FLOOR_PITCH):
        if _inside(shape, x, y, THICKNESS / 2.0):
            raise RuntimeError("floor hole is filled")
    for x in _stations(FLOOR_PITCH):
        if _inside(shape, x, y, z_top_mid):
            raise RuntimeError("E39 hole is filled")
    if not _inside(shape, 0, y, THICKNESS / 2.0):
        raise RuntimeError("bottom flange between the holes is missing")
    if not _inside(shape, 0, y, z_top_mid):
        raise RuntimeError("top flange between the holes is missing")
    if not _inside(shape, 0, 2.0, (h["web0"] + h["web1"]) / 2.0):
        raise RuntimeError("web is missing")
    if _inside(shape, 0, y, (THICKNESS + h["under"]) / 2.0):
        raise RuntimeError("channel between the feet is filled")
    if not _edge_ok(y, -BEND_R, FLOOR_BOLT_D):
        raise RuntimeError("hole too close to the bend")
    if not _edge_ok(y, -FOOT, FLOOR_BOLT_D):
        raise RuntimeError("floor hole too close to the tip")
    if not _edge_ok(y, -BEND_R - TOP, E39_BOLT_D):
        raise RuntimeError("E39 hole too close to the tip")
    half = rail_length() / 2.0
    for x in _stations(FLOOR_PITCH):
        if not _edge_ok(x, math.copysign(half, x), FLOOR_BOLT_D):
            raise RuntimeError("hole too close to the rail end")
    bb = shape.BoundingBox()
    if abs(bb.zmax - h["top"]) > 0.2:
        raise RuntimeError(f"top face {bb.zmax:.2f} != {h['top']:.2f}")


def build_outer() -> cq.Workplane:
    return build_bracket(OUTER_WEB)


def build_inner() -> cq.Workplane:
    return build_bracket(INNER_WEB)


def build_plate() -> cq.Workplane:
    """Flat diaphragm. Four holes on the measured floor centers."""
    length = FLOOR_PITCH + 2.0 * END_MARGIN
    width = FLOOR_WIDTH + 2.0 * PLATE_MARGIN
    plate = (
        cq.Workplane("XY")
        .box(length, width, THICKNESS)
        .translate((0, FLOOR_WIDTH / 2.0, THICKNESS / 2.0))
    )
    cut = None
    for x in _stations(FLOOR_PITCH):
        for y in (0.0, FLOOR_WIDTH):
            hole = _hole(x, y, E39_BOLT_D, -1.0, THICKNESS + 1.0)
            cut = hole if cut is None else cut.union(hole)
    part = plate.cut(cut)
    _audit_plate(part.val())
    return part


def _audit_plate(shape: cq.Shape) -> None:
    if not shape.isValid():
        raise RuntimeError("tie plate is not a valid solid")
    if len(shape.Solids()) != 1:
        raise RuntimeError("tie plate must be one solid")
    for x in _stations(FLOOR_PITCH):
        for y in (0.0, FLOOR_WIDTH):
            if _inside(shape, x, y, THICKNESS / 2.0):
                raise RuntimeError("tie-plate hole is filled")
    if not _inside(shape, 0, FLOOR_WIDTH / 2.0, THICKNESS / 2.0):
        raise RuntimeError("tie plate is missing between the holes")
    bb = shape.BoundingBox()
    if abs(bb.zlen - THICKNESS) > 0.2:
        raise RuntimeError("tie plate thickness is wrong")


def _place_pair() -> tuple[cq.Shape, cq.Shape]:
    """Outer at y=0, inner at FLOOR_WIDTH. Top flanges point toward the seat."""
    shift = -hole_y()
    outer = build_outer().val().mirror("XZ")
    outer = outer.translate(cq.Vector(0, -shift, 0))
    inner = build_inner().val().translate(cq.Vector(0, FLOOR_WIDTH + shift, FLOOR_STEP))
    return outer, inner


def _seat_body(rail_z: float) -> cq.Shape:
    """Visual E39 seat. Proportions, not a scanned BMW surface."""
    mid_y = FLOOR_WIDTH / 2.0
    span = FLOOR_WIDTH + 70.0
    cushion_z = rail_z
    cushion = (
        cq.Workplane("XY")
        .box(490, span, 78)
        .translate((20, mid_y, cushion_z + 39))
        .edges("|Z")
        .fillet(18)
    )
    bolster = (
        cq.Workplane("XY")
        .box(420, 36, 36)
        .translate((10, mid_y + span / 2.0 - 10, cushion_z + 78))
    )
    bolster_r = bolster.mirror("XZ", basePointVector=(0, mid_y, 0))
    thigh = (
        cq.Workplane("XY")
        .box(70, span - 80, 28)
        .translate((230, mid_y, cushion_z + 70))
        .edges("|Y")
        .fillet(8)
    )
    hinge = cq.Vector(-200, mid_y, cushion_z + 40)
    axis = hinge + cq.Vector(0, 1, 0)
    back = (
        cq.Workplane("XY")
        .box(78, span - 20, 600)
        .translate((-200, mid_y, cushion_z + 40 + 270))
        .val()
        .rotate(hinge, axis, -20)
    )
    head = (
        cq.Workplane("XY")
        .box(90, 230, 140)
        .translate((-200, mid_y, cushion_z + 40 + 540 + 50))
        .edges("|Y")
        .fillet(16)
        .val()
        .rotate(hinge, axis, -20)
    )
    seat = cushion.union(bolster).union(bolster_r).union(thigh)
    return seat.val().fuse(back).fuse(head)


def build_seat() -> cq.Workplane:
    outer, inner = _place_pair()
    z_top = top_z(OUTER_WEB)
    if abs((top_z(INNER_WEB) + FLOOR_STEP) - z_top) > 0.2:
        raise RuntimeError("bracket tops are not level")
    plate = build_plate().val().translate(cq.Vector(0, 0, z_top))
    # Floor pads, so the step is visible. Not a body panel.
    outer_pad = (
        cq.Workplane("XY")
        .box(rail_length() + 40.0, 160, 8)
        .translate((0, -20, -4))
        .val()
    )
    inner_pad = (
        cq.Workplane("XY")
        .box(rail_length() + 40.0, 160, 8)
        .translate((0, FLOOR_WIDTH + 20, FLOOR_STEP - 4))
        .val()
    )
    step = (
        cq.Workplane("XY")
        .box(rail_length() + 40.0, 12, FLOOR_STEP)
        .translate((0, FLOOR_WIDTH - 66, FLOOR_STEP / 2.0))
        .val()
    )
    rail_h = 22.0
    rails = []
    for y in (0.0, FLOOR_WIDTH):
        rails.append(
            cq.Workplane("XY")
            .box(FLOOR_PITCH + 40.0, 34, rail_h)
            .translate((0, y, z_top + THICKNESS + rail_h / 2.0))
            .val()
        )
    seat = _seat_body(z_top + THICKNESS + rail_h)
    if seat.BoundingBox().zmin < FLOOR_STEP:
        raise RuntimeError("seat intersects the inner floor pad")
    solids = [outer_pad, inner_pad, step, outer, inner, plate, *rails, seat]
    return cq.Workplane("XY").newObject(solids)


def build_flat(web: float) -> cq.Workplane:
    width = flat_width(web)
    length = rail_length()
    plate = (
        cq.Workplane("XY")
        .box(length, width, THICKNESS)
        .translate((0, width / 2.0, 0))
    )
    foot_y = FOOT + hole_y()
    top_start = (FOOT - BEND_R) + 2.0 * _ba() + web
    top_y = top_start + ((-BEND_R) - hole_y())
    cuts = []
    for x in _stations(FLOOR_PITCH):
        cuts.append(_hole(x, foot_y, FLOOR_BOLT_D, -THICKNESS, THICKNESS * 2))
    for x in _stations(FLOOR_PITCH):
        cuts.append(_hole(x, top_y, E39_BOLT_D, -THICKNESS, THICKNESS * 2))
    cut = cuts[0]
    for extra in cuts[1:]:
        cut = cut.union(extra)
    return plate.cut(cut)


def post_dxf_for(path: Path, web: float, label: str) -> None:
    """Flat blank. CUT is the laser. BEND lines are the brake, do not cut them."""
    import ezdxf
    from ezdxf import colors
    from cadquery import exporters

    exporters.exportDXF(build_flat(web).section(), str(path), approx="arc")
    doc = ezdxf.readfile(str(path))
    if "CUT" not in doc.layers:
        doc.layers.add("CUT", color=colors.RED)
    if "BEND" not in doc.layers:
        doc.layers.add("BEND", color=colors.YELLOW)
    msp = doc.modelspace()
    for ent in msp:
        ent.dxf.layer = "CUT"
    ba = _ba()
    y1 = FOOT - BEND_R
    y2 = y1 + ba + web
    length = rail_length()
    note = (
        f"{label}  BEND 90deg x2  Rin {BEND_R:.0f}  V{DIE_V:.0f}  "
        f"web {web:.0f}  holes only  do not cut"
    )
    msp.add_text(note, dxfattribs={"layer": "BEND", "height": 4}).set_placement(
        (-length / 2.0 + 8.0, 6.0)
    )
    x0 = -length / 2.0 + 2.0
    x1 = length / 2.0 - 2.0
    for y in (y1, y2):
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "BEND"})
    doc.saveas(str(path))


def post_dxf_plate(path: Path) -> None:
    """Laser plate. No bend lines."""
    import ezdxf
    from ezdxf import colors

    doc = ezdxf.readfile(str(path))
    if "CUT" not in doc.layers:
        doc.layers.add("CUT", color=colors.RED)
    msp = doc.modelspace()
    for ent in msp:
        ent.dxf.layer = "CUT"
    msp.add_text(
        "TIE PLATE  4 mm  no bend  4 holes",
        dxfattribs={"layer": "CUT", "height": 4},
    ).set_placement((-FLOOR_PITCH / 2.0, -PLATE_MARGIN + 6.0))
    doc.saveas(str(path))


class Outer:
    NAME = NAME_OUTER
    SHOW = SHOW_BRACKET

    @staticmethod
    def build() -> cq.Workplane:
        return build_outer()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        del clamp
        _audit_bracket(shape, OUTER_WEB)

    @staticmethod
    def post_dxf(path: Path) -> None:
        post_dxf_for(path, OUTER_WEB, "OUTER door side")


class Inner:
    NAME = NAME_INNER
    SHOW = SHOW_BRACKET

    @staticmethod
    def build() -> cq.Workplane:
        return build_inner()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        del clamp
        _audit_bracket(shape, INNER_WEB)

    @staticmethod
    def post_dxf(path: Path) -> None:
        post_dxf_for(path, INNER_WEB, "INNER tunnel side")


class Plate:
    NAME = NAME_PLATE
    SHOW = SHOW_PLATE

    @staticmethod
    def build() -> cq.Workplane:
        return build_plate()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        del clamp
        _audit_plate(shape)

    @staticmethod
    def post_dxf(path: Path) -> None:
        post_dxf_plate(path)


class Seat:
    NAME = NAME_SEAT
    SHOW = SHOW_SEAT

    @staticmethod
    def build() -> cq.Workplane:
        return build_seat()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        del clamp
        if not shape.isValid():
            raise RuntimeError("seat assembly solid is invalid")

    @staticmethod
    def post_dxf(path: Path) -> None:
        # The section of the whole seat is not a laser file.
        path.unlink(missing_ok=True)
