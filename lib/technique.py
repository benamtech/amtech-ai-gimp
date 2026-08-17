"""Technique catalog — a growing library of reusable, brand-agnostic treatments.

A "technique" is a named recipe of effects (and optional layout notes) that
captures *how* to make a class of image, independent of any brand or copy. It
is the "always-growing catalog of sophisticated effects and techniques for
AI-driven hand-made computer graphics": every time the program (or an agent
driving it) lands on a look worth reusing, that look becomes a technique file
here, tagged so anyone can find it later by what it *does*, not what brand it
was for.

Shape (see schemas/technique.schema.json):

    {
      "id": "duotone-marble",
      "title": "Duotone marble relief",
      "family": "grade",                       # grade|glitch|texture|composite|type
      "era": ["1970s"],                        # optional design-movement echoes
      "image_types": ["sculpture", "portrait"],# from lib.design.PAIRINGS
      "tags": ["duotone", "relief", "stone", "mono"],
      "effects": [{"name": "duotone", "param": {"dark": "#0A0E1A", "light": "#F0EBDF"}},
                  {"name": "relief", "param": {"amount": 0.4}}],
      "note": "High-key marble: duotone first, then relief for depth.",
      "source": {"provenance": "amtech campaign", "credit": ""}
    }

The catalog is searched by image type, family, era, or tag. It is the "floor"
for the effect pipeline — a style recipe or one-shot script may layer layout
and type on top of a technique.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ROOT

TECHNIQUES_DIR = ROOT / "techniques"


def _files() -> list[Path]:
    if not TECHNIQUES_DIR.exists():
        return []
    return sorted(TECHNIQUES_DIR.glob("*.json"))


def list_techniques() -> list[dict]:
    rows = []
    for p in _files():
        if p.stem.startswith("_"):
            continue
        try:
            d = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        rows.append({
            "id": d.get("id", p.stem),
            "title": d.get("title", p.stem),
            "family": d.get("family", "?"),
            "image_types": d.get("image_types", []),
            "tags": d.get("tags", []),
            "era": d.get("era", []),
            "file": p.name,
        })
    return rows


def load_technique(technique_id: str) -> dict:
    p = TECHNIQUES_DIR / f"{technique_id}.json"
    if not p.exists():
        known = ", ".join(r["id"] for r in list_techniques()) or "(none)"
        raise SystemExit(f"technique not found: {technique_id}. Known: {known}")
    return json.loads(p.read_text())


def find_techniques(image_type: str | None = None, family: str | None = None,
                    tag: str | None = None, era: str | None = None) -> list[dict]:
    """Filter the catalog by any combination of image type / family / tag / era."""
    rows = list_techniques()
    out = []
    for r in rows:
        if image_type and image_type not in r["image_types"]:
            continue
        if family and r["family"] != family:
            continue
        if tag and tag not in r["tags"]:
            continue
        if era and era not in r["era"]:
            continue
        out.append(r)
    return out


def validate_technique(d: dict) -> list[str]:
    problems = []
    if not isinstance(d, dict):
        return ["technique must be a JSON object"]
    if not d.get("id"):
        problems.append("missing 'id'")
    if not d.get("title"):
        problems.append("missing 'title'")
    for f in d.get("effects", []):
        if not isinstance(f, dict) or not f.get("name"):
            problems.append("each effect needs a 'name'")
    return problems


def create_technique(
    id: str,
    title: str,
    family: str = "grade",
    image_types: list | None = None,
    tags: list | None = None,
    era: list | None = None,
    effects: list | None = None,
    note: str = "",
    provenance: str = "",
    credit: str = "",
    overwrite: bool = False,
) -> Path:
    """Scaffold a new technique entry in the catalog."""
    doc = {
        "id": id, "title": title, "family": family,
        "image_types": image_types or [],
        "tags": tags or [], "era": era or [],
        "effects": effects or [],
        "note": note,
        "source": {"provenance": provenance, "credit": credit},
    }
    problems = validate_technique(doc)
    if problems:
        raise SystemExit("technique invalid: " + "; ".join(problems))
    TECHNIQUES_DIR.mkdir(parents=True, exist_ok=True)
    dest = TECHNIQUES_DIR / f"{id}.json"
    if dest.exists() and not overwrite:
        raise SystemExit(f"technique already exists: {dest} (pass overwrite=True)")
    dest.write_text(json.dumps(doc, indent=2) + "\n")
    return dest
