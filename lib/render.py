"""Render engine abstraction.

Three strategies, in order of preference:
  1. pillow            — stable default, needs only Pillow (always available)
  2. gimp_native       — GIMP 3 batch (auto-detected; PDB is version-fragile)
  3. cli_anything_gimp — the cli-anything-gimp CLI (optional, if installed)

A project is a JSON document matching the cli-anything-gimp shape (see
schemas/project.schema.json). render_project() picks the engine and returns a
result dict with `output`, `method`, and engine diagnostics.

GIMP 3 batch (verified): the recipe is
    gimp --no-interface --no-data --no-fonts --quit \
         --batch-interpreter=plug-in-script-fu-eval -b '(proc)' ...
GIMP 2.x's bare `-i -b` hangs under GIMP 3. Always pass --batch-interpreter
and --quit. GIMP 3 PDB procedure names differ from 2.x (script-fu-message ->
gimp-message, etc.), so the native path is best-effort with a hard fallback
to Pillow.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import (
    Image,
    ImageChops,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageOps,
)

from . import CACHE_DIR, OUT_DIR

# Blend modes Pillow can approximate via channel ops / compositing.
_BLEND_MODES = {
    "normal", "multiply", "screen", "overlay", "soft_light", "hard_light",
    "difference", "darken", "lighten", "color_dodge", "color_burn",
    "addition", "subtract", "grain_merge", "grain_extract",
}


def _gimp_bin() -> str | None:
    return shutil.which("gimp") or shutil.which("gimp-console")


def _cli_bin() -> str | None:
    return shutil.which("cli-anything-gimp") or str(Path.home() / ".local/bin/cli-anything-gimp")


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe() -> dict:
    """Detect available engines without rendering anything."""
    info = {"pillow": _pillow_version()}
    g = _gimp_bin()
    info["gimp_native"] = bool(g)
    info["gimp_bin"] = g
    if g:
        # verify the batch recipe actually works (cheap, cached)
        info["gimp_batch_ok"] = _gimp_batch_probe(g)
    c = _cli_bin()
    info["cli_anything_gimp"] = bool(c and Path(c).exists())
    info["cli_bin"] = c
    return info


def _pillow_version() -> str:
    import PIL
    return getattr(PIL, "__version__", "unknown")


def _gimp_batch_probe(bin: str) -> bool:
    marker = CACHE_DIR / ".gimp_batch_ok"
    if marker.exists():
        return True
    try:
        proc = _run([
            bin, "--no-interface", "--no-data", "--no-fonts", "--quit",
            "--batch-interpreter=plug-in-script-fu-eval",
            "-b", '(gimp-message "mmc-probe")',
        ], timeout=40)
        ok = proc.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        ok = False
    if ok:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        marker.write_text("ok")
    return ok


# ── Pillow renderer (primary) ────────────────────────────────────────────────

def _apply_filter(im: Image.Image, filt: dict) -> Image.Image:
    """Apply one filter dict. Canonical path is effects.apply_filter (EFFECTS);
    a small legacy fallback covers names NOT in EFFECTS (sharpness/smooth/detail/
    flip/rotate/resize/crop/box_blur), which the cli-anything-gimp vocab may use."""
    name = (filt.get("name") or "").lower()
    # accept both "param" (style recipes) and "params" (cli-anything-gimp JSON)
    p = filt.get("param") or filt.get("params") or {}
    try:
        from . import effects
        if name in effects.EFFECTS:
            return effects.apply_filter(im, name, p)
        # legacy names below are NOT in EFFECTS; map them explicitly
        if name == "sharpness":
            return ImageEnhance.Sharpness(im.convert("RGB")).enhance(float(p.get("factor", 1.0)))
        if name == "smooth":
            return im.filter(ImageFilter.SMOOTH)
        if name == "detail":
            return im.filter(ImageFilter.DETAIL)
        if name == "flip_h":
            return ImageOps.mirror(im)
        if name == "flip_v":
            return ImageOps.flip(im)
        if name == "rotate":
            return im.rotate(float(p.get("angle", 0)), expand=True)
        if name == "resize":
            return im.resize((int(p.get("width", im.width)), int(p.get("height", im.height))))
        if name == "crop":
            box = p.get("box") or [0, 0, im.width, im.height]
            return im.crop(tuple(int(x) for x in box))
        if name == "box_blur":
            return im.filter(ImageFilter.BoxBlur(int(p.get("radius", 2))))
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"filter {name} failed: {e}; leaving image unchanged\n")
    return im


def _blend(base: Image.Image, top: Image.Image, mode: str) -> Image.Image:
    """Composite `top` over `base` with a blend mode. RGB only."""
    mode = (mode or "normal").lower()
    if mode == "normal":
        return top
    base = base.convert("RGB")
    top = top.convert("RGB")
    if mode == "multiply":
        return ImageChops.multiply(base, top)
    if mode == "screen":
        return ImageChops.screen(base, top)
    if mode == "difference":
        return ImageChops.difference(base, top)
    if mode == "darken":
        return ImageChops.darker(base, top)
    if mode == "lighten":
        return ImageChops.lighter(base, top)
    if mode == "addition":
        return ImageChops.add(base, top)
    if mode == "subtract":
        return ImageChops.subtract(base, top)
    if mode in ("overlay", "soft_light", "hard_light", "color_dodge", "color_burn",
                "grain_merge", "grain_extract"):
        # approximate overlay family with a 50% screen/multiply blend
        return Image.blend(ImageChops.screen(base, top), ImageChops.multiply(base, top), 0.5)
    return top


def _apply_draw_ops(im: Image.Image, ops: list[dict]) -> Image.Image:
    if not ops:
        return im
    draw = ImageDraw.Draw(im)
    from . import effects
    for op in ops:
        t = op.get("type")
        if t == "rect":
            draw.rectangle(
                [int(op.get("x1", 0)), int(op.get("y1", 0)),
                 int(op.get("x2", im.width)), int(op.get("y2", im.height))],
                fill=op.get("fill", "#000000"))
        elif t == "text":
            text = op.get("text", "")
            size = int(op.get("size", 24))
            color = op.get("color", "#f6f1e8")
            fnt = effects.font(op.get("font") or "Impact", size)
            anchor = op.get("anchor") or "la"
            stroke = int(op.get("stroke", 0))
            if stroke > 0:
                draw.text((int(op.get("x", 0)), int(op.get("y", 0))), text,
                          font=fnt, fill=color, anchor=anchor, stroke_width=stroke,
                          stroke_fill=op.get("stroke_color", "#000000"))
            else:
                draw.text((int(op.get("x", 0)), int(op.get("y", 0))), text,
                          font=fnt, fill=color, anchor=anchor)
        elif t == "stack":
            lines = [(ln.get("text", ""), ln.get("color", "#ffffff"),
                      int(ln.get("size", 40))) for ln in op.get("lines", [])]
            effects.stack_lines(
                draw, lines,
                int(op.get("cx", 0)), int(op.get("y0", 0)),
                int(op.get("max_w", im.width)), int(op.get("bottom", im.height)),
                stroke=int(op.get("stroke", 7)),
                spec=op.get("font") or "Impact")
        elif t == "stroke_text":
            effects.stroke_text(
                draw, (int(op.get("x", 0)), int(op.get("y", 0))),
                op.get("text", ""), effects.font(op.get("font") or "Impact", int(op.get("size", 24))),
                op.get("color", "#ffffff"), width=int(op.get("stroke", 7)),
                anchor=op.get("anchor") or "mm")
    return im


def render_pillow(project: dict, out: Path) -> dict:
    """Render a project JSON with Pillow. Returns {output, method, size}."""
    canvas = project.get("canvas", {})
    w = int(canvas.get("width", project.get("width", 1080)))
    h = int(canvas.get("height", project.get("height", 1350)))
    bg = canvas.get("background", project.get("background", "#0b1220"))
    base = Image.new("RGB", (w, h), bg)

    layers = project.get("layers", [])
    for layer in layers:
        if not layer.get("visible", True):
            continue
        opacity = float(layer.get("opacity", 1.0))
        blend = layer.get("blend_mode") or "normal"

        # build the layer image
        source = layer.get("source")
        if source and Path(source).exists():
            im = Image.open(source).convert("RGB")
            lw = int(layer.get("width") or im.width)
            lh = int(layer.get("height") or im.height)
            # cover-fit to the layer box (matches harness panel prep)
            from . import effects
            im = effects.cover_crop(im, lw, lh)
        else:
            lw = int(layer.get("width") or w)
            lh = int(layer.get("height") or h)
            fill = layer.get("fill")
            if fill == "transparent":
                im = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
            else:
                im = Image.new("RGB", (lw, lh), fill or bg)

        for filt in layer.get("filters", []):
            im = _apply_filter(im, filt)

        # draw ops are layer-local: apply to this layer's image before
        # compositing (matches the harness — text on a small layer clips).
        if layer.get("draw_ops"):
            im = _apply_draw_ops(im, layer["draw_ops"])

        # paste at offset, respecting opacity + blend
        ox = int(layer.get("offset_x", 0))
        oy = int(layer.get("offset_y", 0))
        if im.mode == "RGBA":
            # paste with alpha
            base = base.convert("RGBA")
            if opacity < 1.0:
                a = im.split()[3].point(lambda p: int(p * opacity))
                im = im.copy()
                im.putalpha(a)
            base.alpha_composite(im, (ox, oy))
        else:
            if opacity < 1.0:
                im = Image.blend(Image.new("RGB", im.size, bg), im, opacity)
            if blend != "normal":
                # blend against the region under the layer
                region = base.crop((ox, oy, ox + im.width, oy + im.height)).convert("RGB")
                im = _blend(region, im, blend)
            if base.mode == "RGBA" and im.mode != "RGBA":
                im = im.convert("RGBA")
            base.paste(im, (ox, oy))

    base = base.convert("RGB")

    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, "PNG")
    return {"output": str(out), "method": "pillow", "size": list(base.size)}


# ── native GIMP 3 (best-effort) ──────────────────────────────────────────────

def render_gimp_native(project: dict, out: Path) -> dict:
    """Render via GIMP 3 batch. Falls back to Pillow on any failure."""
    bin = _gimp_bin()
    if not bin or not _gimp_batch_probe(bin):
        return render_pillow(project, out)
    # GIMP 3 Script-Fu PDB is version-fragile; delegate the real work to a
    # generated .scm that loads a pre-flattened Pillow render. This keeps the
    # native path honest: GIMP only does the final load/export, Pillow does
    # composition (which is deterministic and correct).
    tmp = render_pillow(project, out)  # produce the deterministic pixels
    flat = out.with_suffix(".flat.png")
    Image.open(out).save(flat, "PNG")
    scm = out.with_suffix(".scm")
    scm.write_text(
        "(let* ((img (car (gimp-file-load RUN-NONINTERACTIVE "
        f"\"{flat}\" \"{flat.name}\")))"
        f" (draw (car (gimp-image-get-layers img))))"
        f" (gimp-file-save RUN-NONINTERACTIVE img draw \"{out}\" \"{out.name}\")"
        " (gimp-quit 0))"
    )
    try:
        proc = _run([bin, "--no-interface", "--no-data", "--no-fonts", "--quit",
                     "--batch-interpreter=plug-in-script-fu-eval",
                     "-b", f'(load "{scm}")'], timeout=120)
        if proc.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return {"output": str(out), "method": "gimp_native", "size": tmp["size"]}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    # fallback: keep the Pillow output
    Image.open(tmp["output"]).save(out, "PNG")
    return {"output": str(out), "method": "pillow", "size": tmp["size"],
            "note": "gimp_native failed; fell back to pillow"}


def render_cli_anything(project: dict, out: Path) -> dict:
    """Render via the cli-anything-gimp CLI, if installed."""
    cli = _cli_bin()
    if not (cli and Path(cli).exists()):
        return render_pillow(project, out)
    proj_file = out.with_suffix(".gimp-cli.json")
    proj_file.write_text(json.dumps(project, indent=2))
    proc = _run([cli, "--json", "export", "render", str(out), "--overwrite",
                 "--project", str(proj_file)], timeout=120)
    if proc.returncode != 0:
        return render_pillow(project, out)
    return {"output": str(out), "method": "cli_anything_gimp"}


def render_project(project: dict, out: Path, engine: str | None = None) -> dict:
    """Pick the engine (or auto-detect) and render."""
    engine = engine or "pillow"
    if engine == "pillow":
        return render_pillow(project, out)
    if engine == "gimp_native":
        return render_gimp_native(project, out)
    if engine == "cli_anything_gimp":
        return render_cli_anything(project, out)
    if engine == "auto":
        info = probe()
        if info.get("gimp_batch_ok"):
            return render_gimp_native(project, out)
        return render_pillow(project, out)
    raise SystemExit(f"unknown engine: {engine} (pillow|gimp_native|cli_anything_gimp|auto)")
