"""Adapter rail: old BMW seat onto Toyota Land Cruiser Prado 120 floor bolts.

J120 / TLC 120 / Lexus GX 470 (2002–2009), front seats. Each seat uses four
floor bolts, two per rail. The catalog callout on the seat track is
90119-10921 (bolt with washer). Toyota's 90119-10 series is M10; confirm the
bolt in hand (usually a 14 mm head, pitch 1.25) before cutting.

No published center-to-center drawing was found. The floor side is one long
slot so both bolts of a rail pass as long as their centers are within
SLOT_LEN - SLOT_W. The pair spacing is a placeholder, not a floor measurement.

One rail, four times: two per seat, driver and passenger. Belt buckle stays
on the body. This plate is not a belt anchorage.
"""

from __future__ import annotations

import cadquery as cq

NAME = "tlc120-bmw-seat-rail"
PAIR_NAME = "tlc120-bmw-seat-pair"

# MEASURE. Clearance for M10 (90119-10921). Not a thread drawing.
FLOOR_BOLT_D = 10.5

# MEASURE. Both floor bolts of one rail share this slot.
# Max center distance = SLOT_LEN - FLOOR_BOLT_D.
SLOT_LEN = 460.0
SLOT_W = FLOOR_BOLT_D

# MEASURE on the BMW rail. Slots sit this far off the floor-bolt line.
SLOT_Y = 36.0
BMW_SLOT_LEN = 400.0
BMW_SLOT_W = 10.5  # M8 or M10

# MEASURE between the two floor bolt lines, then edit. The number below
# only spaces the pair STEP so both rails are visible.
FLOOR_WIDTH = 440.0

LENGTH = 520.0
WIDTH = 120.0
THICKNESS = 5.0  # steel. Raises the seat by this much.
CORNER_FILLET = 8.0

SHOW = {"roll": 0.0, "elevation": -75.0, "azimuth": 20.0, "zoom": 1.05}
SHOW_PAIR = {"roll": 0.0, "elevation": -62.0, "azimuth": 25.0, "zoom": 0.9}


def max_floor_pitch() -> float:
    return SLOT_LEN - FLOOR_BOLT_D


def _inside(shape: cq.Shape, x: float, y: float, z: float) -> bool:
    return shape.isInside(cq.Vector(x, y, z))


def _through(shape: cq.Shape, x: float, y: float) -> bool:
    top = THICKNESS / 2.0 - 0.3
    return not _inside(shape, x, y, top) and not _inside(shape, x, y, -top)


def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
    """Floor slot and BMW slots are through, with metal left between them."""
    del clamp
    if not shape.isValid():
        raise RuntimeError("TLC rail is not a valid solid")
    n = len(shape.Solids())
    if n not in (1, 2):
        raise RuntimeError(f"expected 1 rail or a pair, got {n} solids")
    if not _through(shape, 0.0, 0.0):
        raise RuntimeError("floor slot is not through")
    if not _through(shape, 0.0, SLOT_Y):
        raise RuntimeError("BMW slot is not through")
    gap_y = SLOT_Y - BMW_SLOT_W / 2.0 - SLOT_W / 2.0
    if gap_y < 2.0 * THICKNESS:
        raise RuntimeError(f"BMW slot too close to floor slot: {gap_y:.1f} mm")
    if not _inside(shape, 0.0, SLOT_W / 2.0 + gap_y / 2.0, 0.0):
        raise RuntimeError("web between slots is missing")
    end_margin = (LENGTH - SLOT_LEN) / 2.0
    if end_margin < 2.0 * THICKNESS:
        raise RuntimeError(f"floor slot too close to the end: {end_margin:.1f} mm")
    side_margin = WIDTH / 2.0 - (SLOT_Y + BMW_SLOT_W / 2.0)
    if side_margin < 2.0 * THICKNESS:
        raise RuntimeError(f"BMW slot too close to the edge: {side_margin:.1f} mm")
    # Metal past the rounded end of the floor slot.
    if not _inside(shape, SLOT_LEN / 2.0 + 2.0, 0.0, 0.0):
        raise RuntimeError("end of the rail is missing")


def build() -> cq.Workplane:
    plate = (
        cq.Workplane("XY")
        .box(LENGTH, WIDTH, THICKNESS)
        .edges("|Z")
        .fillet(CORNER_FILLET)
    )
    # both=True: the box is centered on z=0, a one-sided extrude leaves a pocket.
    floor = (
        cq.Workplane("XY")
        .slot2D(SLOT_LEN, SLOT_W, 0.0)
        .extrude(THICKNESS + 2.0, both=True)
    )
    bmw = (
        cq.Workplane("XY")
        .pushPoints([(0.0, SLOT_Y), (0.0, -SLOT_Y)])
        .slot2D(BMW_SLOT_LEN, BMW_SLOT_W, 0.0)
        .extrude(THICKNESS + 2.0, both=True)
    )
    part = plate.cut(floor).cut(bmw)
    audit(part.val())
    return part


def build_pair() -> cq.Workplane:
    """One seat. Spacing is FLOOR_WIDTH, which still has to be measured."""
    rail = build().val()
    other = rail.translate(cq.Vector(0.0, FLOOR_WIDTH, 0.0))
    return cq.Workplane("XY").newObject([rail, other])


class Pair:
    NAME = PAIR_NAME
    SHOW = SHOW_PAIR

    @staticmethod
    def build() -> cq.Workplane:
        return build_pair()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        audit(shape, clamp=clamp)
