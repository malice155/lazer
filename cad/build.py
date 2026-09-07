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
from parts import demo_bracket, hydrofoil_demo, tohatsu_m98_hydrofoil  # noqa: E402

PARTS = {
    demo_bracket.NAME: demo_bracket,
    hydrofoil_demo.NAME: hydrofoil_demo,
    tohatsu_m98_hydrofoil.NAME: tohatsu_m98_hydrofoil,
    tohatsu_m98_hydrofoil.CLAMP_NAME: tohatsu_m98_hydrofoil.ClampPart,
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
        paths = export_solid(part, name, **getattr(mod, "SHOW", {}))
        if "dxf" in paths and hasattr(mod, "post_dxf"):
            mod.post_dxf(paths["dxf"])
        verify_step(paths["step"])
        bb = part.val().BoundingBox()
        print(
            f"{name}: STEP {paths['step'].name}  "
            f"{bb.xlen:.1f}×{bb.ylen:.1f}×{bb.zlen:.1f} mm  "
            f"{paths['step'].stat().st_size} bytes"
        )
        extra = f"  DXF {paths['dxf'].name}" if "dxf" in paths else ""
        print(f"  → КОМПАС: {paths['step']}{extra}")
    if tohatsu_m98_hydrofoil.NAME in names:
        print(
            "MEASURE before cutting metal: LEG_NOTCH_W, AV_PLATE_W, AV_PLATE_THICK "
            "on the real Tohatsu 9.8 anti-cav plate. Defaults are not factory CAD."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
