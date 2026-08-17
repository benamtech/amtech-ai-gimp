"""Catalog: map styles, brands, and their relationships.

Regenerates two artifacts from the live `styles/` and `brands/` directories:

  - catalog.json — machine-readable relationships
  - catalog.md   — human/agent-readable, greppable

Relationships encoded:
  - family -> style ids (+ each style's title)
  - style  -> compatible brand (the brand a style names, if any)
  - brand  -> palette, font, fx vocabulary, forbid list, canvas presets

Run `python3 run.py catalog` after creating or editing a style/brand.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ROOT
from .brand import list_brands, load_brand
from .style import list_styles, list_families

CATALOG_JSON = ROOT / "catalog.json"
CATALOG_MD = ROOT / "catalog.md"


def build() -> dict:
    styles = list_styles()
    families = list_families()
    brands = list_brands()

    brand_map = {b["id"]: b for b in brands}

    # style -> brand relationship: read each style's `brand` field
    style_brand = {}
    for s in styles:
        try:
            data = json.loads((ROOT / "styles" / f"{s['id']}.json").read_text())
        except Exception:  # noqa: BLE001
            data = {}
        if data.get("brand"):
            style_brand[s["id"]] = data["brand"]

    # enrich brand entries with full doc
    brand_detail = {}
    for b in brands:
        try:
            doc = load_brand(b["id"])
            brand_detail[b["id"]] = {
                "name": doc.get("name"),
                "font": doc.get("font"),
                "colors": doc.get("c"),
                "role": doc.get("role"),
                "fx": doc.get("fx"),
                "forbid": doc.get("forbid"),
                "canvas": doc.get("canvas"),
                "url": doc.get("url"),
            }
        except Exception:  # noqa: BLE001
            brand_detail[b["id"]] = {"name": b.get("name")}

    return {
        "generated_by": "amtech-computer-use-graphics catalog",
        "families": {f: [{"id": s, "title": next((x["title"] for x in styles if x["id"] == s), "")}
                        for s in ids] for f, ids in families.items()},
        "style_brand": style_brand,
        "brands": brand_detail,
        "brand_index": {b["id"]: {"name": b["name"], "font": b["font"],
                                  "colors": sorted(b["colors"])} for b in brands},
    }


def write() -> dict:
    data = build()
    CATALOG_JSON.write_text(json.dumps(data, indent=2) + "\n")
    _write_md(data)
    return data


def _write_md(d: dict) -> None:
    lines = ["# Catalog", "",
             "Maps styles ↔ brands ↔ families. Machine source of truth: "
             "`catalog.json`. Regenerate with `python3 run.py catalog`.", ""]
    lines.append("## Families → styles")
    for fam, ids in sorted(d["families"].items()):
        lines.append(f"### {fam}")
        for s in ids:
            sb = d["style_brand"].get(s["id"])
            brand_note = f"  (brand: {sb})" if sb else ""
            lines.append(f"- `{s['id']}` — {s['title']}{brand_note}")
        lines.append("")
    lines.append("## Brands")
    for bid, b in sorted(d["brands"].items()):
        lines.append(f"### {bid} — {b.get('name', '')}")
        if b.get("font"):
            lines.append(f"- font: {b['font']}")
        if b.get("colors"):
            lines.append(f"- palette: {', '.join(f'{k}={v}' for k, v in sorted(b['colors'].items()))}")
        if b.get("role"):
            lines.append(f"- roles: {', '.join(f'{k}={v}' for k, v in sorted(b['role'].items()))}")
        if b.get("fx"):
            lines.append(f"- fx: {', '.join(b['fx'])}")
        if b.get("forbid"):
            lines.append(f"- forbid: {', '.join(b['forbid'])}")
        if b.get("canvas"):
            lines.append(f"- canvas: {json.dumps(b['canvas'])}")
        if b.get("url"):
            lines.append(f"- url: {b['url']}")
        lines.append("")
    CATALOG_MD.write_text("\n".join(lines))


def show() -> dict:
    return build()
