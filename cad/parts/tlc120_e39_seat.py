"""Bent adapters: BMW E39 seat on a Toyota Prado 120 (TLC 120) floor.

The J120 floor under a front seat is not one plane. The tunnel-side bolts
sit higher than the door-side bolts, so a flat plate leaves the E39 rails
twisted. Each side is a press-brake C-channel: short foot on the Prado
bolts, web for the height, wide top foot for the E39 rail.

OUTER_WEB - INNER_WEB = FLOOR_STEP, so the top faces land on one plane.
Both numbers are MEASURE. No body scan and no E39 surface was found.

Brake: 4 mm steel, two bends 90°, inside radius 4 mm, die V32.
Promecam tang 13 mm. The R47 punch in dxf/ is a different tool.
A gooseneck punch clears the first flange on the second bend.
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

NAME_OUTER = "tlc120-e39-bracket-outer"
NAME_INNER = "tlc120-e39-bracket-inner"
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

# Flanges. Bottom holds the Prado bolts. Top is wider so the E39 rail
# can sit on the floor line or step inboard.
FOOT = 54.0
TOP = 120.0
LENGTH = 520.0

# Prado bolt 90119-10921, Toyota 90119-10 series: M10. Confirm on the car.
FLOOR_BOLT_D = 10.5
# E39 rail screw on the RealOEM rail diagram is M10 (52108162348). An M12
# fillister is also listed; widen the slot if the bolt in hand is M12.
E39_BOLT_D = 10.5
SLOT_LEN = 440.0  # max bolt-center pitch = SLOT_LEN - bolt diameter

# MEASURE. Distance between the two Prado bolt lines. Pair spacing only.
FLOOR_WIDTH = 450.0

SHOW_BRACKET = {"roll": 0.0, "elevation": -18.0, "azimuth": 70.0, "zoom": 1.15}
SHOW_SEAT = {"roll": 0.0, "elevation": -24.0, "azimuth": 18.0, "zoom": 0.88}


def _ba() -> float:
    """Bend allowance along the neutral axis, 90°, ANSI K."""
    return math.radians(BEND_ANGLE) * (BEND_R + BEND_K * THICKNESS)


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


def max_floor_pitch() -> float:
    return SLOT_LEN - FLOOR_BOLT_D


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


def _slot(length: float, width: float, y: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(0, y)
        .slot2D(length, width, 0)
        .extrude(z1 - z0)
    )


def _e39_slot_y() -> list[float]:
    """Three stations on the top flange. First one is above the floor slot."""
    return [-27.0, -67.0, -100.0]


def build_bracket(web: float) -> cq.Workplane:
    if web < 24.0:
        raise RuntimeError(f"web {web:.0f} mm falls into a V{DIE_V:.0f} die")
    h = _heights(web)
    body = _section(web).extrude(LENGTH).translate((-LENGTH / 2.0, 0, 0))
    floor = _slot(SLOT_LEN, FLOOR_BOLT_D, -27.0, -1.0, THICKNESS + 1.0)
    seat_slots = None
    for y in _e39_slot_y():
        cut = _slot(SLOT_LEN, E39_BOLT_D, y, h["under"] - 1.0, h["top"] + 1.0)
        seat_slots = cut if seat_slots is None else seat_slots.union(cut)
    part = body.cut(floor).cut(seat_slots)
    _audit_bracket(part.val(), web)
    return part


def _inside(shape: cq.Shape, x: float, y: float, z: float) -> bool:
    return shape.isInside(cq.Vector(x, y, z))


def _audit_bracket(shape: cq.Shape, web: float) -> None:
    if not shape.isValid():
        raise RuntimeError("bracket is not a valid solid")
    if len(shape.Solids()) != 1:
        raise RuntimeError("bracket must be one solid")
    h = _heights(web)
    # Floor slot is open through the bottom foot. Web beside it stays.
    if _inside(shape, 0, -27.0, THICKNESS / 2.0):
        raise RuntimeError("floor slot is filled")
    if not _inside(shape, 0, 2.0, (h["web0"] + h["web1"]) / 2.0):
        raise RuntimeError("web is missing")
    # E39 slot above the floor line is open through the top foot.
    z_top_mid = (h["under"] + h["top"]) / 2.0
    if _inside(shape, 0, -27.0, z_top_mid):
        raise RuntimeError("E39 slot is filled")
    # Metal remains beside the bend, and the channel between the feet stays open.
    if not _inside(shape, 0, -8.0, THICKNESS / 2.0):
        raise RuntimeError("bottom foot next to the bend is missing")
    if _inside(shape, 0, -27.0, (THICKNESS + h["under"]) / 2.0):
        raise RuntimeError("channel between the feet is filled")
    # 2 x thickness from the slot to the bend tangent and to the tip.
    if -27.0 + FLOOR_BOLT_D / 2.0 > -8.0:
        raise RuntimeError("floor slot too close to the bend")
    bb = shape.BoundingBox()
    if abs(bb.zmax - h["top"]) > 0.2:
        raise RuntimeError(f"top face {bb.zmax:.2f} != {h['top']:.2f}")


def build_outer() -> cq.Workplane:
    return build_bracket(OUTER_WEB)


def build_inner() -> cq.Workplane:
    return build_bracket(INNER_WEB)


def _place_pair() -> tuple[cq.Shape, cq.Shape]:
    """Outer at y=0, inner at FLOOR_WIDTH. Top flanges point toward the seat."""
    outer = build_outer().val().mirror("XZ")
    # Mirror sends the floor slot from y=-27 to y=+27. Shift it onto y=0.
    outer = outer.translate(cq.Vector(0, -27.0, 0))
    inner = build_inner().val().translate(cq.Vector(0, FLOOR_WIDTH + 27.0, FLOOR_STEP))
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
    # Built upright on the back, then reclined with it so the pad stays on the back.
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
    # Floor pads, so the step is visible. Not a body panel.
    outer_pad = (
        cq.Workplane("XY")
        .box(560, 160, 8)
        .translate((0, -20, -4))
        .val()
    )
    inner_pad = (
        cq.Workplane("XY")
        .box(560, 160, 8)
        .translate((0, FLOOR_WIDTH + 20, FLOOR_STEP - 4))
        .val()
    )
    step = (
        cq.Workplane("XY")
        .box(560, 12, FLOOR_STEP)
        .translate((0, FLOOR_WIDTH - 66, FLOOR_STEP / 2.0))
        .val()
    )
    rail_h = 22.0
    rails = []
    for y in (0.0, FLOOR_WIDTH):
        rails.append(
            cq.Workplane("XY")
            .box(470, 34, rail_h)
            .translate((0, y, z_top + rail_h / 2.0))
            .val()
        )
    seat = _seat_body(z_top + rail_h)
    # The seat must clear the high floor.
    if seat.BoundingBox().zmin < FLOOR_STEP:
        raise RuntimeError("seat intersects the inner floor pad")
    solids = [outer_pad, inner_pad, step, outer, inner, *rails, seat]
    return cq.Workplane("XY").newObject(solids)


def build_flat(web: float) -> cq.Workplane:
    width = flat_width(web)
    plate = (
        cq.Workplane("XY")
        .box(LENGTH, width, THICKNESS)
        .translate((0, width / 2.0, 0))
    )
    cuts = []
    cuts.append(_slot(SLOT_LEN, FLOOR_BOLT_D, 27.0, -THICKNESS, THICKNESS * 2))
    top_start = (FOOT - BEND_R) + 2.0 * _ba() + web
    # Same stations as the formed top flange, measured from the bend tangent.
    for formed_y in _e39_slot_y():
        dist = (-BEND_R) - formed_y
        cuts.append(
            _slot(SLOT_LEN, E39_BOLT_D, top_start + dist, -THICKNESS, THICKNESS * 2)
        )
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
    note = (
        f"{label}  BEND 90deg x2  Rin {BEND_R:.0f}  V{DIE_V:.0f}  "
        f"web {web:.0f}  do not cut"
    )
    msp.add_text(note, dxfattribs={"layer": "BEND", "height": 4}).set_placement(
        (-LENGTH / 2.0 + 8.0, 6.0)
    )
    x0 = -LENGTH / 2.0 + 2.0
    x1 = LENGTH / 2.0 - 2.0
    for y in (y1, y2):
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "BEND"})
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
