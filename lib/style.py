"""Style registry: load, list, validate, and scaffold style recipes.

A style recipe is a JSON document (see schemas/style.schema.json) describing a
layout: canvas, background, font, photo placement, filters, pillow ops,
copy slots, rectangles, and text blocks. A recipe is a *floor*, not a lock —
a one-shot script may diverge from it.

Shape (union of the 70+ bundled recipes):

    {
      "id": "instagram-ragebait-warhol-glitch",
      "family": "viral",
      "title": "Ragebait + Warhol flats + glitch offset",
      "canvas": [1080, 1350],          # [w,h] or {"choices": [[w,h],...]}
      "background": "#120018",          # hex or {"choices": [...]}
      "font": "Impact",
      "photo": {"offset_x": {"range": [-18,18]}, "offset_jitter": [0,0], ...},
      "filters": [{"name": "posterize", "param": {"bits": 3}}],
      "pillow": {"contrast": 1.3, "bottom_lift": true, "circle_inset": {...}},
      "copy": {"l1": ["..."], "handle": ["@A", "@B"]},
      "rects": [{"x1": 0, "y1": 0, "x2": "int(W*0.08)", "y2": "H", "fill": "#ffe600"}],
      "texts": [{"text": "{l1}", "x": 24, "y": 80, "size": 34, "color": "#ffe600"}],
      "brand": "retardglobal"           # optional
    }
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import STYLES_DIR


def _list_files() -> list[Path]:
    return sorted(STYLES_DIR.glob("*.json"))


def load_style(style_id: str) -> dict:
    p = STYLES_DIR / f"{style_id}.json"
    if not p.exists():
        raise SystemExit(f"style not found: {style_id}. Known: {', '.join(list_style_ids())}")
    return json.loads(p.read_text())


def list_styles() -> list[dict]:
    rows = []
    for p in _list_files():
        if p.stem.startswith("_"):
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        rows.append({
            "id": data.get("id", p.stem),
            "family": data.get("family", "?"),
            "title": data.get("title", p.stem),
            "file": p.name,
        })
    return rows


def list_style_ids() -> list[str]:
    return [r["id"] for r in list_styles()]


def list_families() -> list[str]:
    fams = {}
    for r in list_styles():
        fams.setdefault(r["family"], []).append(r["id"])
    return fams


def styles_by_family(family: str) -> list[str]:
    return list_families().get(family, [])


def _hex_ok(v: str) -> bool:
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", v))


def validate_style(data: dict) -> list[str]:
    problems = []
    if not isinstance(data, dict):
        return ["style must be a JSON object"]
    if not data.get("id"):
        problems.append("missing 'id'")
    if "canvas" not in data:
        problems.append("missing 'canvas'")
    else:
        c = data["canvas"]
        if isinstance(c, list) and (len(c) != 2 or not all(isinstance(x, int) for x in c)):
            problems.append("'canvas' must be [width, height] or a {choices/range} spec")
    if "background" in data and isinstance(data["background"], str) and not _hex_ok(data["background"]):
        problems.append("'background' must be #rrggbb or a spec")
    for f in data.get("filters", []):
        if not isinstance(f, dict) or not f.get("name"):
            problems.append("each filter needs a 'name'")
    for t in data.get("texts", []):
        if not isinstance(t, dict):
            problems.append("each text must be an object")
        elif t.get("type") == "stack":
            if not t.get("lines"):
                problems.append("a 'stack' text needs a 'lines' list")
        elif "text" not in t:
            problems.append("each text needs a 'text'")
    return problems


def create_style(
    id: str,
    family: str = "custom",
    title: str = "",
    canvas: list | None = None,
    background: str = "#000000",
    font: str = "Impact",
    copy: dict | None = None,
    out_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Scaffold a new style recipe with sensible defaults."""
    doc = {
        "id": id,
        "family": family,
        "title": title or id,
        "canvas": canvas or [1080, 1350],
        "background": background,
        "font": font,
        "photo": {"offset_x": 0, "offset_y": 0, "offset_jitter": [0, 0]},
        "filters": [],
        "pillow": {},
        "copy": copy or {"l1": ["HEADLINE ONE"], "l2": ["HEADLINE TWO"]},
        "rects": [],
        "texts": [
            {"text": "{l1}", "x": 48, "y": "int(H*0.60)", "size": 42, "color": "#ffffff"},
            {"text": "{l2}", "x": 48, "y": "int(H*0.72)", "size": 42, "color": "#ffffff"},
        ],
    }
    problems = validate_style(doc)
    if problems:
        raise SystemExit("style invalid: " + "; ".join(problems))

    out_dir = out_dir or STYLES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{id}.json"
    if dest.exists() and not overwrite:
        raise SystemExit(f"style already exists: {dest} (pass overwrite=True to replace)")
    dest.write_text(json.dumps(doc, indent=2) + "\n")
    return dest
