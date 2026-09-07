"""Export helpers: CadQuery solid → STEP (КОМПАС), STL, SVG, PNG."""

from __future__ import annotations

from pathlib import Path

import cadquery as cq
from cadquery import exporters
from cadquery.vis import show

OUT_DIR = Path(__file__).resolve().parent / "out"


def export_solid(
    part: cq.Workplane,
    stem: str,
    *,
    screenshot: bool = True,
    roll: float = -25,
    elevation: float = -40,
    azimuth: float = 0,
    zoom: float = 1.05,
) -> dict[str, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {
        "step": OUT_DIR / f"{stem}.step",
        "stl": OUT_DIR / f"{stem}.stl",
        "svg": OUT_DIR / f"{stem}.svg",
        "png": OUT_DIR / f"{stem}.png",
    }
    exporters.export(part, str(paths["step"]))
    exporters.export(part, str(paths["stl"]))
    exporters.export(part, str(paths["svg"]))
    if screenshot:
        show(
            part,
            screenshot=str(paths["png"]),
            interact=False,
            width=1280,
            height=720,
            bgcolor=(0.12, 0.14, 0.18),
            roll=roll,
            elevation=elevation,
            azimuth=azimuth,
            zoom=zoom,
        )
    return paths


def verify_step(path: Path) -> cq.Workplane:
    imported = cq.importers.importStep(str(path))
    solids = imported.solids().vals()
    if not solids:
        raise RuntimeError(f"STEP has no solids: {path}")
    return imported
