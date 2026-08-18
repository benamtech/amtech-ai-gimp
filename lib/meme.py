"""RG meme meta-generator — captions + images → hundreds of brand-locked stills.

One template, many memes. The copy is just copy: there is NO semantic
classification and no per-copy-type templates. Given N captions (plus optional
images), this generator:

  * wraps each caption into stacked Impact headline lines (the first line is
    the punch, rendered big by the style),
  * resolves images — explicit per-line images, a subject→image map, or a
    best-effort search — and stitches a 2-image pair side-by-side into the
    photo area (driven by image *count*, not by what the copy says),
  * drives `batch` (mode=generate) against ONE RG template with a seeded
    texture axis, emitting a standalone one-shot script per still.

This is the "non-deterministic script generator": it writes the manifest; the
program writes the per-item one-shot scripts.

Caption file (plain text, one per line):

    <caption> [| <image> [| <image2>]] [| @<style>]

or a JSON list of {"caption","image","image2","style","name"} objects.

Images resolve in order: explicit per-line image → subject→image map
(`--images`) → best-effort search (`--find-images`).
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from . import CACHE_DIR, OUT_DIR
from .batch import render_batch


def slugify(text: str, max_words: int = 5) -> str:
    """'Chester Stone wanted for X' -> 'chester-stone-wanted-for'."""
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    return "-".join(words[:max_words]) or "meme"


def wrap_headline(text: str, max_lines: int = 6, max_chars: int = 20) -> list[str]:
    """Uppercase + greedy word wrap into short Impact headline lines."""
    words = (text or "").upper().split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [" ".join(lines[max_lines - 1:])]
    return lines


def _parse_fields(line: str) -> dict:
    """Parse '<caption> [| image [| image2]] [| @style]' into a dict."""
    parts = [p.strip() for p in line.split("|")]
    caption = parts[0].strip() if parts else ""
    images: list[str] = []
    style = None
    for p in parts[1:]:
        if not p:
            continue
        if p.startswith("@"):
            style = p[1:].strip()
        else:
            images.append(p)
    return {"caption": caption, "image": images[0] if images else None,
            "image2": images[1] if len(images) > 1 else None, "style": style}


def load_captions(path: str) -> list[dict]:
    p = Path(path).expanduser()
    if not p.exists():
        raise SystemExit(f"captions file not found: {p}")
    if p.suffix.lower() == ".json":
        data = json.loads(p.read_text())
        raw = data if isinstance(data, list) else data.get("items", [])
        return [{"caption": it.get("caption", ""), "image": it.get("image"),
                 "image2": it.get("image2"), "style": it.get("style"),
                 "name": it.get("name")} for it in raw]
    items = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        items.append(_parse_fields(line))
    return items


def _subject_of(caption: str, keys: list[str]) -> str | None:
    low = caption.lower()
    for k in keys:
        if k.lower() in low:
            return k
    return None


def _canvas_of(style_id: str) -> tuple[int, int]:
    from .style import load_style
    c = load_style(style_id).get("canvas")
    if isinstance(c, list) and len(c) == 2:
        return int(c[0]), int(c[1])
    return 1080, 1080


def stitch_pair(a: Path, b: Path, w: int, h: int, divider: str = "#DEFF2E",
                out_dir: Path | None = None, name: str = "pair") -> Path:
    """Composite two stills side-by-side (each cover-cropped to half) with a
    thin center divider. Returns a temp PNG for the photo area."""
    from PIL import Image, ImageDraw
    from . import effects
    out_dir = out_dir or CACHE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    hw = w // 2
    canvas = Image.new("RGB", (w, h), "#000000")
    canvas.paste(effects.cover_crop(Image.open(a).convert("RGB"), hw, h), (0, 0))
    canvas.paste(effects.cover_crop(Image.open(b).convert("RGB"), hw, h), (hw, 0))
    ImageDraw.Draw(canvas).rectangle([hw - 2, 0, hw + 2, h], fill=divider)
    out = out_dir / f"{name}-pair.png"
    canvas.save(out, "PNG")
    return out


def _resolve_to_file(spec: str) -> Path:
    from .source import resolve
    return resolve(spec)


def _search_image(query: str, out_dir: Path, name: str) -> Path | None:
    from . import search
    try:
        cand = search.best_still(query)
        if not cand:
            return None
        return search.download_candidate(cand, dest_dir=out_dir, name=f"{name}-src")
    except Exception:  # noqa: BLE001
        return None


def build_items(captions: list[dict], image_map: dict, find_images: bool,
                base_seed: int, out_dir: Path, default_style: str) -> tuple[list[dict], list[str]]:
    """Turn captions into batch-manifest items. Returns (items, warnings)."""
    from .brand import load_brand
    cast: list[str] = []
    try:
        cast = load_brand("retardglobal").get("cast", [])
    except SystemExit:
        pass
    map_keys = list((image_map or {}).keys()) + [c for c in cast if c not in (image_map or {})]

    items: list[dict] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for idx, cap in enumerate(captions):
        caption = cap.get("caption") or ""
        if not caption:
            continue
        style = cap.get("style") or default_style

        name = cap.get("name") or slugify(caption)
        base = name
        n = 2
        while name in seen:
            name = f"{base}-{n}"
            n += 1
        seen.add(name)

        lines = wrap_headline(caption)
        set_ = {"url": "RETARDGLOBAL.COM"}
        for i in range(6):
            set_[f"l{i+1}"] = lines[i] if i < len(lines) else ""

        # resolve images: explicit per-line → subject map → optional search
        imgs = [x for x in (cap.get("image"), cap.get("image2")) if x]
        subject = _subject_of(caption, map_keys)
        if not imgs and subject:
            val = (image_map or {}).get(subject)
            if val:
                imgs = val if isinstance(val, list) else [val]
        if not imgs and find_images and subject:
            found = _search_image(subject, out_dir, name)
            if found:
                imgs = [str(found)]

        source = None
        if len(imgs) == 1:
            source = _resolve_to_file(imgs[0])
        elif len(imgs) >= 2:
            w, h = _canvas_of(style)
            source = stitch_pair(_resolve_to_file(imgs[0]),
                                 _resolve_to_file(imgs[1]), w, h,
                                 out_dir=out_dir, name=name)
        if not source:
            warnings.append(f"{name}: no image resolved — rendering text-only "
                            f"(caption: {caption[:48]})")

        items.append({
            "name": name,
            "source": str(source) if source else None,
            "seed": base_seed + idx,
            "set": set_,
            "style": style,
        })
    return items, warnings


def render_memes(captions_path: str, style: str = "rg-meme", brand: str = "retardglobal",
                 image_map: dict | None = None, find_images: bool = False,
                 seed: int = 7, out_dir: Path | None = None,
                 limit: int | None = None) -> dict:
    """Captions + images → a batch of brand-locked stills (+ per-item scripts)."""
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    captions = load_captions(captions_path)
    items, warnings = build_items(captions, image_map or {}, find_images, seed,
                                  out_dir, style)

    # group by style (a line may override the style via `@<id>`), render each
    groups: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        groups[it.pop("style", style)].append(it)

    manifest = {"style": style, "brand": brand, "mode": "generate",
                "engine": "pillow", "items": items}
    manifest_path = out_dir / "rg-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    counts = []
    for grp_style, grp_items in groups.items():
        res = render_batch(grp_style, {"items": grp_items}, brand=brand,
                           out_dir=out_dir, mode="generate", engine="pillow",
                           limit=limit)
        counts.extend(res.get("items", []))

    return {"style": style, "brand": brand, "count": len(counts),
            "out_dir": str(out_dir), "manifest": str(manifest_path),
            "warnings": warnings, "items": counts}
