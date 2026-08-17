"""Batch renderer — one style/brand template, many stills.

This is the "write captions, not scripts" automation path. The template (a
style recipe + optional brand lock + shared defaults) is fixed; the manifest
supplies only the *unique* parts per image: copy overrides (`set`), an optional
source/photo2, and a seed. Each item renders independently to `<out>/<name>.png`.

Manifest shapes (both supported):

1. List-of-items (style/brand/defaults on the CLI):
       [ {"name": "grimace", "set": {"a": "FUJIMOTO", ...}, "source": "...", "seed": 11}, ... ]

2. Self-contained object (everything in one file):
       {
         "style": "fuji-ragebait", "brand": "retardglobal", "engine": "pillow",
         "mode": "generate",                                   # or "compose"
         "defaults": {"source": "...", "photo2": "...", "font": null, "seed": 7},
         "items": [ {"name": "...", "set": {...}, "source": "...", "seed": 11}, ... ]
       }

`set` is a map of copy-slot overrides (the unique captions/data). Keys not in
`set` fall back to the style's own copy defaults (or are sampled by seed).

The batch driver is deterministic: item.seed or defaults.seed or (index+1) is
used as the seed, so a run is reproducible.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import OUT_DIR
from .compose import compose
from .library import generate


def _coerce_manifest(raw) -> tuple[dict, list[dict]]:
    """Return (meta, items) from either manifest shape."""
    if isinstance(raw, dict):
        # self-contained object
        meta = {k: v for k, v in raw.items() if k != "items"}
        items = raw.get("items", [])
        if not isinstance(items, list):
            raise SystemExit("manifest 'items' must be a list")
        return meta, items
    if isinstance(raw, list):
        return {}, raw
    raise SystemExit("manifest must be a JSON object or a JSON list")


def _merge(meta: dict, defaults: dict) -> dict:
    """Merge CLI/self-contained meta with a shared `defaults` block."""
    out = dict(meta)
    for k, v in (defaults or {}).items():
        if k == "items":
            continue
        if out.get(k) in (None, "") and v is not None:
            out[k] = v
    return out


def render_batch(
    style: str,
    manifest: dict | list,
    brand: str | None = None,
    source: str | None = None,
    photo2: str | None = None,
    font: str | None = None,
    seed: int | None = None,
    engine: str = "pillow",
    mode: str = "generate",
    out_dir: Path | None = None,
    limit: int | None = None,
) -> dict:
    """Render every manifest item against one style/brand template."""
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    meta, items = _coerce_manifest(manifest)

    # precedence: explicit CLI args > self-contained meta > defaults block
    style = style or meta.get("style")
    brand = brand or meta.get("brand")
    engine = meta.get("engine", engine)
    mode = meta.get("mode", mode)
    defaults = meta.get("defaults", {})

    if not style:
        raise SystemExit("batch needs --style (or 'style' in the manifest)")

    default_source = source or meta.get("source") or defaults.get("source")
    default_photo2 = photo2 or meta.get("photo2") or defaults.get("photo2")
    default_font = font or meta.get("font") or defaults.get("font")
    default_seed = seed if seed is not None else defaults.get("seed")

    results = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise SystemExit(f"manifest item {idx} must be an object, got {item!r}")
        if limit is not None and idx >= limit:
            break

        name = item.get("name") or item.get("id") or f"{style}-{idx + 1:03d}"
        sets = item.get("set") or item.get("copy") or {}
        item_source = item.get("source") or default_source
        item_photo2 = item.get("photo2") or default_photo2
        item_seed = item.get("seed") if item.get("seed") is not None else default_seed
        if item_seed is None:
            item_seed = idx + 1

        if mode == "compose":
            res = compose(style, brand_id=brand, source=item_source,
                          photo2=item_photo2, copy_overrides=sets or None,
                          font_override=default_font, seed=int(item_seed),
                          out_dir=out_dir, engine=engine)
            # compose names the output <style>.png; rename to the item name
            src_png = out_dir / f"{style}.png"
            dst_png = out_dir / f"{name}.png"
            if src_png.exists() and src_png != dst_png:
                src_png.replace(dst_png)
            res["name"] = name
            res["png"] = str(dst_png)
        else:
            res = generate(style, brand_id=brand, source=item_source,
                           photo2=item_photo2, copy_overrides=sets or None,
                           font_override=default_font, seed=int(item_seed),
                           out_dir=out_dir)
            # generate names the output <style>.png + compose_<style>.py; rename
            src_png = out_dir / f"{style}.png"
            dst_png = out_dir / f"{name}.png"
            if src_png.exists() and src_png != dst_png:
                src_png.replace(dst_png)
            src_script = out_dir / f"compose_{style}.py"
            dst_script = out_dir / f"compose_{name}.py"
            if src_script.exists() and src_script != dst_script:
                src_script.replace(dst_script)
            res["name"] = name
            res["png"] = str(dst_png)
            res["script"] = str(dst_script)

        res["seed"] = int(item_seed)
        res["set"] = sets
        # keep the batch result lean: drop the big resolved/project payloads
        res.pop("resolved", None)
        res.pop("project", None)
        res["output"] = res.get("png")
        results.append(res)

    return {
        "style": style,
        "brand": brand,
        "mode": mode,
        "engine": engine,
        "count": len(results),
        "out_dir": str(out_dir),
        "items": results,
    }


def load_manifest(path: str) -> dict | list:
    p = Path(path).expanduser()
    if not p.exists():
        raise SystemExit(f"manifest not found: {p}")
    return json.loads(p.read_text())
