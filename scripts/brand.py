"""Load compact brand JSON for compose jobs.

Search order (first hit wins):
  1. --brand path / BRAND_FILE env
  2. <cwd>/brands/<id>.json
  3. <cwd>/*.brand.json
  4. ~/Pictures/cli-anything-poster/brands/<id>.json
  5. this skill's brands/<id>.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_BRANDS = HERE.parent / "brands"
POSTER_BRANDS = Path.home() / "Pictures" / "cli-anything-poster" / "brands"


def load_brand(name: str = "retardglobal", path: str | None = None) -> dict:
    if path:
        p = Path(path).expanduser()
        if p.exists():
            return json.loads(p.read_text())
        raise SystemExit(f"brand file missing: {p}")
    env = os.environ.get("BRAND_FILE")
    if env and Path(env).exists():
        return json.loads(Path(env).read_text())
    key = name.lower().replace(" ", "").replace("_", "")
    candidates = [
        Path.cwd() / "brands" / f"{name}.json",
        *Path.cwd().glob("*.brand.json"),
        POSTER_BRANDS / f"{name}.json",
        SKILL_BRANDS / f"{name}.json",
    ]
    for p in candidates:
        if p.exists() and key in p.stem.lower().replace("_", ""):
            return json.loads(p.read_text())
    for p in candidates:
        if p.exists():
            return json.loads(p.read_text())
    raise SystemExit(f"brand not found: {name}")


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
