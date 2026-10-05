"""Frame for the BMW seat on a Prado 120 floor. Measured hole centers only.

The seat label reads Brose, 52107459217-04, C80325-101, 10462425, 15.02.21.
Parts listings for 52107459217 call it a left comfort seat frame and show it
on the X5/X6/X7/XM family. The label does not name the chassis, and this
file does not either. It is not an E39 seat.

MEASURED, center to center, from the rails in the shop:
  520 mm along one rail between the floor-bolt holes
  420 mm between the two rails

Not measured, so not in the solid: floor step, bolt diameter, the Brose
frame's own hole pitch. Hole centers are DXF marks on layer CENTER.
Both rails are the same part until a step is measured.

SHOP, not a dimension of the car: 4 mm sheet, two 90° bends, Rin 4 mm,
die V32, web 28 mm so the wall clears that die. Promecam tang 13 mm.
The R47 punch in dxf/ is a different tool. A gooseneck clears the second bend.
The plate is laser only.
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq

NAME_BRACKET = "tlc120-bmw-comfort-bracket"
NAME_PLATE = "tlc120-bmw-comfort-plate"
NAME_FRAME = "tlc120-bmw-comfort-frame"

# --- MEASURED, mm, center to center ---
FLOOR_PITCH = 520.0
FLOOR_WIDTH = 420.0

# --- CITED, not used as geometry ---
SEAT_LABEL = "52107459217-04"

# --- SHOP. Not a measurement of the car or the seat. ---
THICKNESS = 4.0
BEND_R = 4.0
BEND_K = 0.4
BEND_ANGLE = 90.0
DIE_V = 32.0
# Straight web between the bend tangents. 24 mm is the V32 limit.
WEB = 28.0
FOOT = 40.0
TOP = 40.0
# Center of the future hole, mm from the bend tangent.
HOLE_FROM_TANGENT = 18.0
# Metal past each center, along the rail.
END_MARGIN = 25.0
PLATE_MARGIN = 28.0

SHOW_BRACKET = {"roll": 0.0, "elevation": -18.0, "azimuth": 70.0, "zoom": 1.05}
SHOW_PLATE = {"roll": 0.0, "elevation": -55.0, "azimuth": 25.0, "zoom": 1.0}
SHOW_FRAME = {"roll": 0.0, "elevation": -28.0, "azimuth": 32.0, "zoom": 0.95}


def _ba() -> float:
    """Bend allowance along the neutral axis, 90°, ANSI K."""
    return math.radians(BEND_ANGLE) * (BEND_R + BEND_K * THICKNESS)


def rail_length() -> float:
    return FLOOR_PITCH + 2.0 * END_MARGIN


def hole_y() -> float:
    """Center on the formed flange, toward -Y from the web."""
    return -(BEND_R + HOLE_FROM_TANGENT)


def _heights(web: float) -> dict[str, float]:
    z_web0 = THICKNESS + BEND_R
    z_web1 = z_web0 + web
    z_under = THICKNESS + 2.0 * BEND_R + web
    z_top = 2.0 * THICKNESS + 2.0 * BEND_R + web
    return {"web0": z_web0, "web1": z_web1, "under": z_under, "top": z_top}


def top_z() -> float:
    return _heights(WEB)["top"]


def flat_width() -> float:
    """Developed width: two straight flanges, web, two bend allowances."""
    return (FOOT - BEND_R) + _ba() + WEB + _ba() + TOP


def _stations(pitch: float) -> tuple[float, float]:
    return (-pitch / 2.0, pitch / 2.0)


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


def _inside(shape: cq.Shape, x: float, y: float, z: float) -> bool:
    return shape.isInside(cq.Vector(x, y, z))


def build_bracket() -> cq.Workplane:
    if WEB < 24.0:
        raise RuntimeError(f"web {WEB:.0f} mm falls into a V{DIE_V:.0f} die")
    if HOLE_FROM_TANGENT < 2.0 * THICKNESS:
        raise RuntimeError("hole center is inside the bend zone")
    if END_MARGIN < 2.0 * THICKNESS:
        raise RuntimeError("hole center is too close to the rail end")
    length = rail_length()
    part = _section(WEB).extrude(length).translate((-length / 2.0, 0, 0))
    _audit_bracket(part.val())
    return part


def _audit_bracket(shape: cq.Shape) -> None:
    if not shape.isValid():
        raise RuntimeError("bracket is not a valid solid")
    if len(shape.Solids()) != 1:
        raise RuntimeError("bracket must be one solid")
    h = _heights(WEB)
    y = hole_y()
    z_top_mid = (h["under"] + h["top"]) / 2.0
    # Centers stay solid: the diameter was not measured, so nothing is cut.
    for x in _stations(FLOOR_PITCH):
        if not _inside(shape, x, y, THICKNESS / 2.0):
            raise RuntimeError("floor center was cut")
        if not _inside(shape, x, y, z_top_mid):
            raise RuntimeError("top center was cut")
    if not _inside(shape, 0, 2.0, (h["web0"] + h["web1"]) / 2.0):
        raise RuntimeError("web is missing")
    if _inside(shape, 0, y, (THICKNESS + h["under"]) / 2.0):
        raise RuntimeError("channel between the feet is filled")
    bb = shape.BoundingBox()
    if abs(bb.xlen - rail_length()) > 0.2:
        raise RuntimeError(f"length {bb.xlen:.1f} != {rail_length():.1f}")
    if abs(bb.zmax - h["top"]) > 0.2:
        raise RuntimeError(f"top face {bb.zmax:.2f} != {h['top']:.2f}")


def build_plate() -> cq.Workplane:
    """Flat plate across the two rails. No holes: diameter is not measured."""
    length = rail_length()
    width = FLOOR_WIDTH + 2.0 * PLATE_MARGIN
    plate = (
        cq.Workplane("XY")
        .box(length, width, THICKNESS)
        .translate((0, FLOOR_WIDTH / 2.0, THICKNESS / 2.0))
    )
    _audit_plate(plate.val())
    return plate


def _audit_plate(shape: cq.Shape) -> None:
    if not shape.isValid():
        raise RuntimeError("plate is not a valid solid")
    if len(shape.Solids()) != 1:
        raise RuntimeError("plate must be one solid")
    for x in _stations(FLOOR_PITCH):
        for y in (0.0, FLOOR_WIDTH):
            if not _inside(shape, x, y, THICKNESS / 2.0):
                raise RuntimeError("plate center was cut")
    bb = shape.BoundingBox()
    if abs(bb.zlen - THICKNESS) > 0.2:
        raise RuntimeError("plate thickness is wrong")
    if abs(bb.xlen - rail_length()) > 0.2:
        raise RuntimeError("plate length is wrong")


def build_frame() -> cq.Workplane:
    """Two rails and the plate. No seat body: the seat was not measured."""
    shift = -hole_y()
    left = build_bracket().val().mirror("XZ").translate(cq.Vector(0, -shift, 0))
    right = build_bracket().val().translate(cq.Vector(0, FLOOR_WIDTH + shift, 0))
    plate = build_plate().val().translate(cq.Vector(0, 0, top_z()))
    return cq.Workplane("XY").newObject([left, right, plate])


def _flat_center_ys() -> tuple[float, float]:
    foot_y = FOOT + hole_y()
    top_start = (FOOT - BEND_R) + 2.0 * _ba() + WEB
    top_y = top_start + ((-BEND_R) - hole_y())
    return foot_y, top_y


def build_flat() -> cq.Workplane:
    width = flat_width()
    length = rail_length()
    return (
        cq.Workplane("XY")
        .box(length, width, THICKNESS)
        .translate((0, width / 2.0, 0))
    )


def _add_center_layers(doc) -> None:
    from ezdxf import colors

    if "CUT" not in doc.layers:
        doc.layers.add("CUT", color=colors.RED)
    if "BEND" not in doc.layers:
        doc.layers.add("BEND", color=colors.YELLOW)
    if "CENTER" not in doc.layers:
        doc.layers.add("CENTER", color=colors.CYAN)


def _cross(msp, x: float, y: float) -> None:
    arm = 4.0
    attrib = {"layer": "CENTER"}
    msp.add_line((x - arm, y), (x + arm, y), dxfattribs=attrib)
    msp.add_line((x, y - arm), (x, y + arm), dxfattribs=attrib)


def post_dxf_bracket(path: Path) -> None:
    """Flat blank. CUT is the laser. BEND and CENTER are not cut."""
    import ezdxf
    from cadquery import exporters

    exporters.exportDXF(build_flat().section(), str(path), approx="arc")
    doc = ezdxf.readfile(str(path))
    _add_center_layers(doc)
    msp = doc.modelspace()
    for ent in msp:
        ent.dxf.layer = "CUT"
    ba = _ba()
    y1 = FOOT - BEND_R
    y2 = y1 + ba + WEB
    length = rail_length()
    msp.add_text(
        f"BEND 90deg x2  Rin {BEND_R:.0f}  V{DIE_V:.0f}  web {WEB:.0f}  do not cut",
        dxfattribs={"layer": "BEND", "height": 4},
    ).set_placement((-length / 2.0 + 8.0, 6.0))
    x0 = -length / 2.0 + 2.0
    x1 = length / 2.0 - 2.0
    for y in (y1, y2):
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "BEND"})
    foot_y, top_y = _flat_center_ys()
    for x in _stations(FLOOR_PITCH):
        _cross(msp, x, foot_y)
        _cross(msp, x, top_y)
    msp.add_text(
        "CENTER do not cut. Hole diameter not measured.",
        dxfattribs={"layer": "CENTER", "height": 4},
    ).set_placement((-length / 2.0 + 8.0, foot_y + 8.0))
    doc.saveas(str(path))


def post_dxf_plate(path: Path) -> None:
    """Laser plate. Outline only. Centers are not holes."""
    import ezdxf

    doc = ezdxf.readfile(str(path))
    _add_center_layers(doc)
    msp = doc.modelspace()
    for ent in msp:
        ent.dxf.layer = "CUT"
    for x in _stations(FLOOR_PITCH):
        for y in (0.0, FLOOR_WIDTH):
            _cross(msp, x, y)
    msp.add_text(
        "PLATE  4 mm  no bend  CENTER do not cut  diameter not measured",
        dxfattribs={"layer": "CENTER", "height": 4},
    ).set_placement((-FLOOR_PITCH / 2.0, -PLATE_MARGIN + 6.0))
    doc.saveas(str(path))


class Bracket:
    NAME = NAME_BRACKET
    SHOW = SHOW_BRACKET

    @staticmethod
    def build() -> cq.Workplane:
        return build_bracket()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        del clamp
        _audit_bracket(shape)

    @staticmethod
    def post_dxf(path: Path) -> None:
        post_dxf_bracket(path)


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


class Frame:
    NAME = NAME_FRAME
    SHOW = SHOW_FRAME

    @staticmethod
    def build() -> cq.Workplane:
        return build_frame()

    @staticmethod
    def audit(shape: cq.Shape, *, clamp: bool = False) -> None:
        del clamp
        if not shape.isValid():
            raise RuntimeError("frame is invalid")

    @staticmethod
    def post_dxf(path: Path) -> None:
        path.unlink(missing_ok=True)
