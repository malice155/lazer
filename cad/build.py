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
from parts import demo_bracket, hydrofoil_demo  # noqa: E402

PARTS = {
    demo_bracket.NAME: demo_bracket,
    hydrofoil_demo.NAME: hydrofoil_demo,
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
        verify_step(paths["step"])
        bb = part.val().BoundingBox()
        print(
            f"{name}: STEP {paths['step'].name}  "
            f"{bb.xlen:.1f}×{bb.ylen:.1f}×{bb.zlen:.1f} mm  "
            f"{paths['step'].stat().st_size} bytes"
        )
        print(f"  → open in КОМПАС: {paths['step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
