"""Deterministic composer: recipe -> concrete composition -> still.

Turns a recipe (style JSON + optional brand + source + copy + seed) into a
finished image. Deterministic: the same inputs produce the same pixels.

Pipeline:
  resolve()  -> sample every spec value against a seeded RNG into a concrete
                dict (canvas, bg, font, filters, pillow ops, copy, rects, texts)
  build_project() -> shape that dict into a cli-anything-gimp project JSON
  compose()  -> build_project + render via lib.render

This is the project-JSON path. The script-of-scripts path (lib.library) emits
a one-shot script from the same resolved dict instead.
"""
from __future__ import annotations

import random
from pathlib import Path

from . import OUT_DIR
from .brand import load_brand, hex_rgb
from .effects import sample
from .fonts import resolve_font
from .render import render_project
from .source import resolve as resolve_source
from .style import load_style


def _eval(expr, w: int, h: int, rng: random.Random):
    if isinstance(expr, (int, float)):
        return expr
    if isinstance(expr, dict):
        return sample(rng, expr)
    if isinstance(expr, str):
        try:
            return eval(expr, {"__builtins__": {}},
                        {"W": w, "H": h, "int": int, "float": float,
                         "min": min, "max": max, "round": round})
        except Exception as e:  # noqa: BLE001
            raise SystemExit(
                f"bad expression in style: {expr!r} ({e}). "
                f"Allowed: int/float/W/H/min/max/round."
            ) from e
    raise SystemExit(f"unhandled expression type in style: {type(expr).__name__}: {expr!r}")


def resolve(
    style_id: str,
    brand_id: str | None = None,
    source: str | None = None,
    photo2: str | None = None,
    copy_overrides: dict | None = None,
    font_override: str | None = None,
    seed: int | None = None,
) -> dict:
    """Resolve a style (+brand) into concrete values. Deterministic via seed."""
    style = load_style(style_id)
    rng = random.Random(seed)

    canvas_spec = style.get("canvas", [1080, 1350])
    canvas = sample(rng, canvas_spec)
    if isinstance(canvas, list):
        w, h = int(canvas[0]), int(canvas[1])
    else:
        w, h = int(canvas), int(canvas)

    bg = sample(rng, style.get("background", "#0b1220"))
    font_spec = font_override or style.get("font") or "Impact"

    brand = None
    if brand_id or style.get("brand"):
        brand = load_brand(brand_id or style.get("brand"))
        c = brand.get("c") or {}
        if c.get("k"):
            bg = c["k"]
        if brand.get("font"):
            font_spec = brand["font"]

    resolved = {
        "style_id": style_id,
        "brand": brand,
        "brand_id": brand.get("id") if brand else None,
        "canvas": [w, h],
        "background": bg,
        "font": resolve_font(font_spec),
        "seed": seed,
        "source": source,
        "photo2": photo2,
    }

    # photo placement
    photo = style.get("photo", {})
    resolved["photo"] = {
        "offset_x": int(sample(rng, photo.get("offset_x", 0))),
        "offset_y": int(sample(rng, photo.get("offset_y", 0))),
        "jitter": photo.get("offset_jitter", [0, 0]),
        "blend": sample(rng, photo["blend"]) if photo.get("blend") else None,
        "opacity": sample(rng, photo["opacity"]) if photo.get("opacity") is not None else None,
    }

    # filters (sample params)
    resolved["filters"] = []
    for f in style.get("filters", []):
        params = {k: sample(rng, v) for k, v in (f.get("param") or {}).items()}
        resolved["filters"].append({"name": f["name"], "param": params})

    resolved["pillow"] = {k: sample(rng, v) for k, v in (style.get("pillow") or {}).items()}

    # copy slots
    slots = {}
    for key, spec in (style.get("copy") or {}).items():
        slots[key] = sample(rng, spec if isinstance(spec, dict) else {"choices": spec})
    for k, v in (copy_overrides or {}).items():
        slots[k] = v
    # Brand-aware slots: a style's masthead/plate text can reference the loaded
    # brand's name/url/lock/hat, so one template works with any brand (or none).
    if brand:
        slots.setdefault("brand_name", brand.get("name", ""))
        slots.setdefault("brand_url", (brand.get("url") or "").upper())
        slots.setdefault("brand_lock", brand.get("lock", ""))
        slots.setdefault("brand_hat", brand.get("hat", brand.get("name", "")))
    resolved["copy"] = slots

    # rects
    rects = []
    for r in style.get("rects", []):
        rects.append({
            "x1": int(_eval(r["x1"], w, h, rng)),
            "y1": int(_eval(r["y1"], w, h, rng)),
            "x2": int(_eval(r["x2"], w, h, rng)),
            "y2": int(_eval(r["y2"], w, h, rng)),
            "fill": sample(rng, r.get("fill", "#000000")),
        })
    resolved["rects"] = rects

    # texts (interpolate copy slots). Two shapes:
    #   plain text  -> {"type":"text", text,x,y,size,color,font,anchor,stroke,stroke_color}
    #   stacked     -> {"type":"stack", cx,y0,max_w,bottom,stroke,font,lines:[{text,color,size}]}
    texts = []
    for t in style.get("texts", []):
        if t.get("type") == "stack":
            lines = []
            for ln in t.get("lines", []):
                txt = ln.get("text", "")
                for k, v in slots.items():
                    txt = txt.replace("{" + k + "}", str(v))
                if not str(txt).strip():
                    continue  # empty line -> skip, so one template can vary line count
                lines.append({
                    "text": txt,
                    "color": sample(rng, ln.get("color", "#ffffff")),
                    "size": int(sample(rng, ln.get("size", 40))),
                })
            texts.append({
                "type": "stack",
                "cx": int(_eval(t.get("cx", t.get("x", "int(W*0.5)")), w, h, rng)),
                "y0": int(_eval(t.get("y0", t.get("y", "int(H*0.5)")), w, h, rng)),
                "max_w": int(_eval(t.get("max_w", "int(W-160)"), w, h, rng)),
                "bottom": int(_eval(t.get("bottom", "int(H-90)"), w, h, rng)),
                "stroke": int(t.get("stroke", 7)),
                "font": resolve_font(str(t.get("font") or font_spec)),
                "lines": lines,
            })
            continue
        text = sample(rng, t.get("text", ""))
        if isinstance(text, str):
            for k, v in slots.items():
                text = text.replace("{" + k + "}", str(v))
        texts.append({
            "type": "text",
            "text": text,
            "x": int(_eval(t.get("x", 48), w, h, rng)),
            "y": int(_eval(t.get("y", 80), w, h, rng)),
            "size": int(sample(rng, t.get("size", 24))),
            "color": sample(rng, t.get("color", "#f6f1e8")),
            "font": resolve_font(str(t.get("font") or font_spec)),
            "anchor": t.get("anchor", "la"),
            "stroke": int(t.get("stroke", 6)),
            "stroke_color": t.get("stroke_color", "#000000"),
        })
    resolved["texts"] = texts

    # Brand lock: remap style accent colors onto the brand palette.
    if brand:
        from .brand import nearest_color
        resolved["rects"] = [
            {**r, "fill": nearest_color(r["fill"], brand)} for r in rects
        ]
        remapped_texts = []
        for t in texts:
            if t.get("type") == "stack":
                remapped_texts.append({
                    **t,
                    "lines": [{**ln, "color": nearest_color(ln["color"], brand)}
                              for ln in t["lines"]],
                })
            else:
                remapped_texts.append({**t, "color": nearest_color(t["color"], brand)})
        resolved["texts"] = remapped_texts
        ci = resolved["pillow"].get("circle_inset")
        if ci and ci.get("ring_color"):
            ci["ring_color"] = nearest_color(ci["ring_color"], brand)

    return resolved


def build_project(resolved: dict, panel: Path) -> dict:
    w, h = resolved["canvas"]
    draw_ops = []
    for r in resolved["rects"]:
        draw_ops.append({"type": "rect", **r})
    for t in resolved["texts"]:
        # resolved texts already carry a "type" ("text" or "stack"); pass through.
        draw_ops.append(dict(t))

    photo_layer = {
        "id": 0, "name": "photo", "type": "image",
        "source": str(panel), "width": w, "height": h,
        "offset_x": resolved["photo"]["offset_x"],
        "offset_y": resolved["photo"]["offset_y"],
        "opacity": resolved["photo"]["opacity"] or 1.0,
        "visible": True, "blend_mode": resolved["photo"]["blend"] or "normal",
        "fill": None,
        "filters": resolved["filters"],
        "draw_ops": [],
    }
    copy_layer = {
        "id": 1, "name": "copy", "type": "image",
        "source": None, "width": w, "height": h,
        "offset_x": 0, "offset_y": 0, "opacity": 1.0, "visible": True,
        "blend_mode": "normal", "fill": "transparent",
        "filters": [], "draw_ops": draw_ops,
    }
    return {
        "name": resolved["style_id"],
        "version": "1.0",
        "canvas": {"width": w, "height": h, "background": resolved["background"],
                   "color_mode": "RGB", "dpi": 72},
        "layers": [photo_layer, copy_layer],
        "guides": [], "selection": None,
        "metadata": {"software": "amtech-computer-use-graphics 0.1.2"},
    }


def prep_panel(source: str, resolved: dict, dest_dir: Path, photo2: str | None = None) -> Path:
    """Resolve source, cover-crop to canvas, apply pillow ops, write panel JPG."""
    from PIL import Image
    from . import effects
    from .brand import palette_hexes
    w, h = resolved["canvas"]
    src = resolve_source(source)
    im = effects.cover_crop(Image.open(src).convert("RGB"), w, h)

    # Brand lock: clamp outlaw hues to the brand palette before grading.
    brand = resolved.get("brand")
    if brand:
        pal = palette_hexes(brand)
        if pal:
            im = effects.clamp_hues(im, pal)

    ops = resolved.get("pillow", {})
    if ops.get("contrast"):
        im = effects.contrast(im, float(ops["contrast"]))
    if ops.get("color"):
        im = effects.saturation(im, float(ops["color"]))
    if ops.get("bottom_lift"):
        start = float(ops.get("lift_start", 0.45))
        strength = float(ops.get("lift_strength", 0.35))
        lift_color = ops.get("lift_color")
        if lift_color:
            im = effects.bottom_lift(im, start=start, strength=strength,
                                     color=hex_rgb(str(lift_color)))
        else:
            im = effects.bottom_lift(im, start=start, strength=strength)

    # circle inset sticker (e.g. the ragebait face in a colored ring)
    inset = ops.get("circle_inset")
    if inset and photo2:
        try:
            face = Image.open(resolve_source(photo2)).convert("RGB")
            d = int(min(w, h) * float(inset.get("d", 0.28)))
            ring_w = int(inset.get("ring", 12))
            ring_color = inset.get("ring_color", "#ff2bd6")
            sticker = effects.circle_sticker(face, d, ring_w, ring_color)
            cx = int(w * float(inset.get("cx", 0.80)))
            cy = int(h * float(inset.get("cy", 0.18)))
            im.paste(sticker, (cx - sticker.size[0] // 2, cy - sticker.size[1] // 2),
                     sticker)
        except Exception as e:  # noqa: BLE001
            print(f"circle_inset skipped: {e}", file=__import__("sys").stderr)

    dest_dir.mkdir(parents=True, exist_ok=True)
    panel = dest_dir / f"{resolved['style_id']}-panel.jpg"
    im.save(panel, quality=95)
    return panel


def compose(
    style_id: str,
    brand_id: str | None = None,
    source: str | None = None,
    photo2: str | None = None,
    copy_overrides: dict | None = None,
    font_override: str | None = None,
    seed: int | None = None,
    out_dir: Path | None = None,
    engine: str = "pillow",
) -> dict:
    """End-to-end deterministic compose. Returns render result + metadata."""
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    resolved = resolve(style_id, brand_id, source, photo2, copy_overrides,
                       font_override, seed)

    if not resolved["source"]:
        raise SystemExit("compose needs --source (a local path, URL, File: title, or bundled name)")

    panel = prep_panel(resolved["source"], resolved, out_dir, photo2=resolved.get("photo2"))
    project = build_project(resolved, panel)
    out = out_dir / f"{style_id}.png"
    result = render_project(project, out, engine=engine)
    result["style"] = style_id
    result["brand"] = resolved.get("brand_id")
    result["seed"] = seed
    result["resolved"] = resolved
    result["project"] = project
    return result
