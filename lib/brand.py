"""Brand system: load, validate, list, and create brand JSON files.

A brand is a compact JSON document that locks a visual identity —
palette, typeface, canvas presets, role mapping, forbidden hues, and
an effect vocabulary. Brands are the single source of truth for a
"brand-locked" compose job.

Brand JSON shape (see schemas/brand.schema.json):

    {
      "id": "retardglobal",            # lowercase, no spaces (slug)
      "name": "RETARD GLOBAL",         # display name
      "url": "retardglobal.com",       # masthead URL / domain
      "lock": "ONLY ON RETARDGLOBAL.COM",  # footer plate text (optional)
      "tag": "",                       # optional subtitle/tagline
      "hat": "RETARD",                 # optional hat/logo word
      "font": "Impact",                # primary typeface (family name)
      "canvas": {"ig": [1080, 1080], "yt": [2560, 1440]},
      "c": {"lime": "#DEFF2E", ...},   # named colors (hex)
      "role": {"lime": "headline/band", ...},  # color -> semantic role
      "mix": {"lime": [45, 55], ...},  # optional usage-weight ranges
      "type": {"on_sat": "k", "on_k": "w", "stroke": "k", "keyline": "w"},
      "forbid": ["red", "gold", ...],  # hues/words to avoid
      "fx": ["torn", "halftone", ...], # effect vocabulary
      "cta": ["REAL OR FAKE", ...]     # optional call-to-action options
    }

Search order for load_brand(name): explicit path -> BRAND_FILE env ->
<cwd>/brands/ -> bundle brands/ -> legacy Pictures dir.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import BRANDS_DIR, LEGACY_POSTER_DIR


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower().replace(" ", "").replace("_", ""))


def _search_candidates(name: str) -> list[Path]:
    key = _slug(name)
    legacy = LEGACY_POSTER_DIR / "brands"
    candidates = [
        Path.cwd() / "brands" / f"{name}.json",
        *Path.cwd().glob("*.brand.json"),
        BRANDS_DIR / f"{name}.json",
        *BRANDS_DIR.glob("*.json"),
        legacy / f"{name}.json",
        *legacy.glob("*.json"),
    ]
    # First pass: name match. Second pass: any brand at all (fallback).
    matched = [p for p in candidates if p.exists() and key in _slug(p.stem)]
    if matched:
        return matched
    return [p for p in candidates if p.exists()]


def load_brand(name: str = "retardglobal", path: str | None = None) -> dict:
    """Load a brand document. Raises SystemExit with a clear message if absent."""
    if path:
        p = Path(path).expanduser()
        if p.exists():
            return json.loads(p.read_text())
        raise SystemExit(f"brand file missing: {p}")

    import os
    env = os.environ.get("BRAND_FILE")
    if env and Path(env).exists():
        return json.loads(Path(env).read_text())

    for p in _search_candidates(name):
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError as e:
            raise SystemExit(f"brand JSON invalid: {p}: {e}")

    raise SystemExit(
        f"brand not found: {name}. Known brands: {', '.join(list_brand_ids()) or '(none)'}"
    )


def list_brands() -> list[dict]:
    rows = []
    seen = set()
    for p in sorted(BRANDS_DIR.glob("*.json")):
        if p.stem.startswith("_"):
            continue
        if p.stem in seen:
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        seen.add(p.stem)
        rows.append({
            "id": data.get("id", p.stem),
            "name": data.get("name", p.stem),
            "font": data.get("font", "Impact"),
            "colors": sorted((data.get("c") or {}).keys()),
            "file": str(p),
        })
    return rows


def list_brand_ids() -> list[str]:
    return [b["id"] for b in list_brands()]


def validate_brand(data: dict) -> list[str]:
    """Return a list of problems (empty == valid)."""
    problems = []
    if not isinstance(data, dict):
        return ["brand must be a JSON object"]
    if not data.get("id"):
        problems.append("missing 'id'")
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["id"]):
        problems.append("'id' must be a lowercase slug (a-z, 0-9, single hyphens)")
    if not data.get("name"):
        problems.append("missing 'name'")
    c = data.get("c")
    if c is not None and not isinstance(c, dict):
        problems.append("'c' must be a map of name -> hex color")
    elif isinstance(c, dict):
        for k, v in c.items():
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(v)):
                problems.append(f"color '{k}' must be #rrggbb, got {v!r}")
    if "forbid" in data and not isinstance(data["forbid"], list):
        problems.append("'forbid' must be a list")
    if "fx" in data and not isinstance(data["fx"], list):
        problems.append("'fx' must be a list")
    return problems


def create_brand(
    id: str,
    name: str,
    url: str = "",
    colors: dict | None = None,
    font: str = "Impact",
    canvas: dict | None = None,
    lock: str = "",
    forbid: list | None = None,
    fx: list | None = None,
    out_dir: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Create a new brand document. Writes to <out_dir>/<id>.json."""
    doc = {
        "id": id,
        "name": name,
        "url": url or f"{id}.com",
        "lock": lock or f"ONLY ON {url.upper()}" if url else "",
        "tag": "",
        "hat": "",
        "font": font,
        "canvas": canvas or {"ig": [1080, 1080], "yt": [2560, 1440]},
        "c": colors or {"k": "#000000", "w": "#FFFFFF"},
        "role": {k: "" for k in (colors or {"k": 0, "w": 0})},
        "type": {"on_sat": "k", "on_k": "w", "stroke": "k", "keyline": "w"},
        "forbid": forbid or [],
        "fx": fx or [],
        "cta": [],
    }
    problems = validate_brand(doc)
    if problems:
        raise SystemExit("brand invalid: " + "; ".join(problems))

    out_dir = out_dir or BRANDS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{id}.json"
    if dest.exists() and not overwrite:
        raise SystemExit(f"brand already exists: {dest} (pass overwrite=True to replace)")
    dest.write_text(json.dumps(doc, indent=2) + "\n")
    return dest


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def nearest_color(hex_color: str, brand: dict) -> str:
    """Map a hex to the nearest color in the brand palette (brand lock).

    Used to remap a style's own accent colors onto the brand's palette:
    e.g. a yellow stripe becomes the brand's lime, a red becomes mag.
    White/black text snap to the brand's w/k. If the brand has no palette,
    return the input unchanged.
    """
    c = brand.get("c") or {}
    if not c:
        return hex_color
    try:
        target = hex_rgb(hex_color)
    except (ValueError, IndexError):
        return hex_color
    best = min(
        c.values(),
        key=lambda h: sum((a - b) ** 2 for a, b in zip(hex_rgb(h), target)),
    )
    return best


def palette_hexes(brand: dict, skip=("k", "w")) -> list[str]:
    """Brand accent palette (excluding neutrals) for hue-clamping the photo."""
    c = brand.get("c") or {}
    return [v for k, v in c.items() if k not in skip]
