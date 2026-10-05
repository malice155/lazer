#!/usr/bin/env python3
"""Build parametric parts to cad/out/*.step for КОМПАС."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib import export_solid, verify_step  # noqa: E402
from parts import (  # noqa: E402
    demo_bracket,
    granta_bmw_seat_rail,
    hydrofoil_demo,
    tlc120_bmw_comfort,
    tlc120_bmw_seat_rail,
    tohatsu_m98_hydrofoil,
)

PARTS = {
    demo_bracket.NAME: demo_bracket,
    hydrofoil_demo.NAME: hydrofoil_demo,
    tohatsu_m98_hydrofoil.NAME: tohatsu_m98_hydrofoil,
    tohatsu_m98_hydrofoil.CLAMP_NAME: tohatsu_m98_hydrofoil.ClampPart,
    granta_bmw_seat_rail.NAME: granta_bmw_seat_rail,
    granta_bmw_seat_rail.PAIR_NAME: granta_bmw_seat_rail.Pair,
    tlc120_bmw_seat_rail.NAME: tlc120_bmw_seat_rail,
    tlc120_bmw_seat_rail.PAIR_NAME: tlc120_bmw_seat_rail.Pair,
    tlc120_bmw_comfort.NAME_BRACKET: tlc120_bmw_comfort.Bracket,
    tlc120_bmw_comfort.NAME_PLATE: tlc120_bmw_comfort.Plate,
    tlc120_bmw_comfort.NAME_FRAME: tlc120_bmw_comfort.Frame,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Export CadQuery parts to STEP/STL")
    parser.add_argument(
        "name",
        nargs="?",
        default="all",
        choices=[*PARTS.keys(), "all"],
        help="Part id (default: all)",
    )
    args = parser.parse_args()
    names = list(PARTS) if args.name == "all" else [args.name]
    for name in names:
        mod = PARTS[name]
        part = mod.build()
        if hasattr(mod, "audit"):
            mod.audit(part.val(), clamp=name.endswith("clamp"))
        paths = export_solid(part, name, **getattr(mod, "SHOW", {}))
        if "dxf" in paths and hasattr(mod, "post_dxf"):
            mod.post_dxf(paths["dxf"])
            if not paths["dxf"].exists():
                del paths["dxf"]
        verify_step(paths["step"])
        bb = part.val().BoundingBox()
        nsolids = len(part.solids().vals())
        solid_note = f"  solids={nsolids}" if nsolids > 1 else ""
        print(
            f"{name}: STEP {paths['step'].name}  "
            f"{bb.xlen:.1f}×{bb.ylen:.1f}×{bb.zlen:.1f} mm  "
            f"{paths['step'].stat().st_size} bytes{solid_note}"
        )
        extra = f"  DXF {paths['dxf'].name}" if "dxf" in paths else ""
        print(f"  → КОМПАС: {paths['step']}{extra}")
    if tohatsu_m98_hydrofoil.NAME in names:
        print(
            "MEASURE before cutting metal: LEG_NOTCH_W, AV_PLATE_W, AV_PLATE_THICK "
            "on the real Tohatsu 9.8 anti-cav plate. Defaults are not factory CAD."
        )
    if tlc120_bmw_seat_rail.NAME in names or tlc120_bmw_seat_rail.PAIR_NAME in names:
        pitch = tlc120_bmw_seat_rail.max_floor_pitch()
        print(
            "MEASURE before cutting metal: Prado 120 floor-bolt pitch "
            f"(slot accepts up to {pitch:.1f} mm) and the distance between "
            "the two bolt lines. FLOOR_WIDTH in the pair STEP is a placeholder."
        )
    if (
        tlc120_bmw_comfort.NAME_BRACKET in names
        or tlc120_bmw_comfort.NAME_PLATE in names
        or tlc120_bmw_comfort.NAME_FRAME in names
    ):
        print(
            "Measured centers only: "
            f"{tlc120_bmw_comfort.FLOOR_PITCH:.0f} mm along a rail, "
            f"{tlc120_bmw_comfort.FLOOR_WIDTH:.0f} mm between rails. "
            "Hole diameter and floor step are not measured, so holes are "
            "not cut. DXF layer CENTER is not a cut. Die V32, gooseneck."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
