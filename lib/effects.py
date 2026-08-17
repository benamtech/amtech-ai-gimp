"""The effect library — every image primitive the composer can apply.

Canonical implementation of the amtech-computer-use-graphics effect vocabulary. Consolidates
the proven rg_kit.py + build_rizzler.py effects into one self-contained
module (imports only stdlib, PIL, and lib.brand / lib.fonts).

Effects are grouped:
  - type      : font helpers, line fitting, stacked text
  - geometry  : cover-crop, rotate, flip
  - grade     : posterize, solarize, invert, grayscale, sepia, contrast,
                saturation, brightness, sharpen, autocontrast, equalize
  - blur/edge : blur, unsharp, find_edges, emboss, contour
  - glitch    : channel offset (warhol/glitch), scanline shift
  - warhol    : warhol flats, hue clamp to a brand palette
  - lift      : bottom lift, brand-color lift
  - texture   : grain, scanlines, halftone, crt, vignette, torn, splatter
  - composite : cover, circle sticker, ring, stripe, masthead, url plate

Every function returns a new image (no in-place surprises) unless noted.
"""
from __future__ import annotations

import colorsys
import inspect
import random
from pathlib import Path

from PIL import (
    Image,
    ImageChops,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
)

from .brand import hex_rgb
from .fonts import resolve_font


# ── type ──────────────────────────────────────────────────────────────────────

def font(spec: str | None, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(resolve_font(spec or "Impact"), size)


def impact(size: int) -> ImageFont.FreeTypeFont:
    return font("Impact", size)


def fit_line(text: str, max_w: int, start: int, min_size: int = 28,
             stroke: int = 0, spec: str | None = None) -> ImageFont.FreeTypeFont:
    """Shrink `text` until it fits max_w (accounting for stroke)."""
    budget = max(40, max_w - 2 * stroke)
    size = start
    while size >= min_size:
        f = font(spec, size)
        if f.getlength(text) <= budget:
            return f
        size -= 2
    return font(spec, min_size)


def line_advance(fnt: ImageFont.FreeTypeFont, stroke: int = 7, extra: int = 10) -> int:
    """True glyph height + stroke so stacked Impact lines never collide."""
    a, d = fnt.getmetrics()
    return a + d + stroke * 2 + extra


def stroke_text(draw, xy, text, fnt, fill, stroke="#000000", width=7, anchor="mm"):
    draw.text(xy, text, font=fnt, fill=fill, stroke_width=width,
              stroke_fill=stroke, anchor=anchor)


def draw_text_shadow(draw, xy, text, fnt, fill, shadow_offset=(3, 3),
                     shadow_color=(0, 0, 0), anchor="la"):
    sx, sy = shadow_offset
    draw.text((xy[0] + sx, xy[1] + sy), text, font=fnt, fill=shadow_color, anchor=anchor)
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def stack_lines(draw, lines, cx: int, y0: int, max_w: int, bottom: int,
                stroke: int = 7, spec: str | None = None) -> None:
    """lines = [(text, color, start_size), ...]. Shrinks if the stack hits bottom."""
    fitted = [
        (t, c, fit_line(t, max_w, s, 26, stroke=stroke, spec=spec), stroke)
        for t, c, s in lines
    ]
    total = sum(line_advance(f, st) for _, _, f, st in fitted)
    while total > (bottom - y0) and any(f.size > 28 for _, _, f, _ in fitted):
        fitted = [
            (t, c, fit_line(t, max_w, max(26, f.size - 4), 26, stroke=st, spec=spec), st)
            for t, c, f, st in fitted
        ]
        total = sum(line_advance(f, st) for _, _, f, st in fitted)
    y = y0
    for text, col, fnt, st in fitted:
        stroke_text(draw, (cx, y + fnt.getmetrics()[0] // 2), text, fnt, col, width=st)
        y += line_advance(fnt, st)


# ── geometry ──────────────────────────────────────────────────────────────────

def cover_crop(im: Image.Image, w: int, h: int, focus=(0.5, 0.38)) -> Image.Image:
    """Scale to cover the target box, crop toward the focus point."""
    im = im.convert("RGB")
    sw, sh = im.size
    scale = max(w / sw, h / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    x1 = max(0, min(nw - w, cx - w // 2))
    y1 = max(0, min(nh - h, cy - h // 2))
    return im.crop((x1, y1, x1 + w, y1 + h))


def rotate(im: Image.Image, angle: float, expand: bool = True) -> Image.Image:
    return im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=expand)


def flip_h(im: Image.Image) -> Image.Image:
    return ImageOps.mirror(im)


def flip_v(im: Image.Image) -> Image.Image:
    return ImageOps.flip(im)


# ── grade ─────────────────────────────────────────────────────────────────────

def posterize(im: Image.Image, bits: int = 3) -> Image.Image:
    return ImageOps.posterize(im.convert("RGB"), bits)


def solarize(im: Image.Image, threshold: int = 128) -> Image.Image:
    return ImageOps.solarize(im.convert("RGB"), threshold)


def invert(im: Image.Image) -> Image.Image:
    return ImageOps.invert(im.convert("RGB"))


def grayscale(im: Image.Image) -> Image.Image:
    return ImageOps.grayscale(im.convert("RGB"))


def sepia(im: Image.Image) -> Image.Image:
    g = ImageOps.grayscale(im.convert("RGB"))
    return ImageOps.colorize(g, black=(40, 26, 13), white=(255, 240, 214))


def contrast(im: Image.Image, factor: float = 1.0) -> Image.Image:
    return ImageEnhance.Contrast(im.convert("RGB")).enhance(factor)


def saturation(im: Image.Image, factor: float = 1.0) -> Image.Image:
    return ImageEnhance.Color(im.convert("RGB")).enhance(factor)


def brightness(im: Image.Image, factor: float = 1.0) -> Image.Image:
    return ImageEnhance.Brightness(im.convert("RGB")).enhance(factor)


def sharpen(im: Image.Image, factor: float = 1.5) -> Image.Image:
    return ImageEnhance.Sharpness(im.convert("RGB")).enhance(factor)


def autocontrast(im: Image.Image, cutoff: float = 0) -> Image.Image:
    return ImageOps.autocontrast(im.convert("RGB"), cutoff)


def equalize(im: Image.Image) -> Image.Image:
    return ImageOps.equalize(im.convert("RGB"))


# ── blur / edge ───────────────────────────────────────────────────────────────

def blur(im: Image.Image, radius: float = 2) -> Image.Image:
    return im.filter(ImageFilter.GaussianBlur(radius))


def unsharp(im: Image.Image, radius: float = 2, percent: int = 150,
            threshold: int = 3) -> Image.Image:
    return im.filter(ImageFilter.UnsharpMask(radius, percent, threshold))


def find_edges(im: Image.Image) -> Image.Image:
    return im.convert("RGB").filter(ImageFilter.FIND_EDGES)


def emboss(im: Image.Image) -> Image.Image:
    return im.convert("RGB").filter(ImageFilter.EMBOSS)


def contour(im: Image.Image) -> Image.Image:
    return im.convert("RGB").filter(ImageFilter.CONTOUR)


# ── glitch ────────────────────────────────────────────────────────────────────

def channel_offset(im: Image.Image, dx=(6, -8), dy=(-3, 4), keep_red=True) -> Image.Image:
    """RGB channel shift glitch. Shifts green/blue (red stays to avoid outlaw
    scarlet fringes on posterized skin)."""
    r, g, b = im.convert("RGB").split()
    g = ImageChops.offset(g, dx[0], dy[0])
    b = ImageChops.offset(b, dx[1], dy[1])
    return Image.merge("RGB", (r, g, b))


# ── warhol ────────────────────────────────────────────────────────────────────

def warhol(im: Image.Image, bits: int = 3, color: float = 1.45,
           contrast_f: float = 1.28) -> Image.Image:
    im = ImageOps.posterize(im.convert("RGB"), bits)
    im = ImageEnhance.Color(im).enhance(color)
    im = ImageEnhance.Contrast(im).enhance(contrast_f)
    r, g, b = im.split()
    g = ImageChops.offset(g, 6, -3)
    b = ImageChops.offset(b, -8, 4)
    return Image.merge("RGB", (r, g, b))


def clamp_hues(im: Image.Image, palette: list[str], skin_keep=True,
               mix: float = 0.55) -> Image.Image:
    """Snap saturated chroma to the nearest palette hue (brand color clamp).
    Keeps skin tones and greys. palette = list of hex colors."""
    targets = [(colorsys.rgb_to_hsv(*[c / 255 for c in hex_rgb(h)])[0], hex_rgb(h))
               for h in palette]
    src = list(im.convert("RGB").getdata())
    out = []
    for r, g, b in src:
        mx, mn = max(r, g, b), min(r, g, b)
        if mx < 18 or (mx - mn) < 28:
            out.append((r, g, b))
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        deg = h * 360
        if skin_keep and 15 <= deg <= 50 and s < 0.55 and 0.25 < v < 0.92:
            out.append((r, g, b))
            continue
        _, rgb = min(targets, key=lambda t: min(abs(h - t[0]), 1 - abs(h - t[0])))
        out.append(tuple(int(rgb[i] * mix + (r, g, b)[i] * (1 - mix)) for i in range(3)))
    im2 = Image.new("RGB", im.size)
    im2.putdata(out)
    return im2


# ── lift ──────────────────────────────────────────────────────────────────────

def bottom_lift(im: Image.Image, start=0.40, strength=0.35,
                color=(255, 230, 0)) -> Image.Image:
    """Gradient lift from the lower portion of the frame (warhol yellow lift)."""
    w, h = im.size
    base = im.convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y0 = int(h * start)
    for i in range(28):
        frac = i / 27
        y = y0 + int((h - y0) * frac * 0.82)
        a = int(strength * 255 * (0.18 + 0.82 * frac))
        d.rectangle([0, y, w, y + 2], fill=(*color, a))
    return Image.alpha_composite(base, ov).convert("RGB")


def color_lift(im: Image.Image, color: str, start=0.42, strength=0.38) -> Image.Image:
    """bottom_lift with a brand hex color."""
    return bottom_lift(im, start=start, strength=strength, color=hex_rgb(color))


# ── texture ───────────────────────────────────────────────────────────────────

def grain(im: Image.Image, n=7000, seed=7, alpha=28, max_v=22) -> Image.Image:
    rng = random.Random(seed)
    noise = Image.new("RGBA", im.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    w, h = im.size
    for _ in range(n):
        v = rng.randint(0, max_v)
        nd.point((rng.randint(0, w - 1), rng.randint(0, h - 1)), fill=(v, v, v, alpha))
    return Image.alpha_composite(im.convert("RGBA"), noise).convert("RGB")


def scanlines(im: Image.Image, gap=4, alpha=70) -> Image.Image:
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w, h = im.size
    for y in range(0, h, gap):
        d.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def crt(im: Image.Image, gap=4, alpha=70, curvature=False) -> Image.Image:
    """Scanlines + subtle green channel lift (CRT feel)."""
    im = scanlines(im, gap, alpha)
    r, g, b = im.split()
    g = ImageChops.offset(g, 1, 0)
    return Image.merge("RGB", (r, g, b))


def halftone(im: Image.Image, dot=6, saturate=True) -> Image.Image:
    """Cheap halftone: posterize to near-binary then overlay a dot grid mask."""
    im = ImageOps.grayscale(im.convert("RGB"))
    im = ImageOps.posterize(im, 2)
    im = ImageOps.autocontrast(im)
    w, h = im.size
    mask = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(mask)
    for y in range(0, h, dot):
        for x in range(0, w, dot):
            d.ellipse((x, y, x + dot - 1, y + dot - 1), fill=0)
    return Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), im.convert("RGB"), mask)


def vignette(im: Image.Image, strength=0.5, color=(0, 0, 0)) -> Image.Image:
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-w * 0.25, -h * 0.25, w * 1.25, h * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) // 6))
    black = Image.new("RGB", (w, h), color)
    return Image.composite(black, im.convert("RGB"), ImageOps.invert(mask.point(
        lambda p: int(p * strength))))


def torn(im: Image.Image, edge="bottom", steps=40, seed=7) -> Image.Image:
    """Rough torn-paper edge by chewing off a ragged strip along one edge."""
    rng = random.Random(seed)
    w, h = im.size
    base = im.convert("RGBA")
    mask = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(mask)
    if edge == "bottom":
        prev = rng.randint(h // 3, h // 2)
        for x in range(0, w, max(1, w // steps)):
            nxt = rng.randint(h // 3, h // 2)
            d.polygon([(x, prev), (x + w // steps, nxt),
                       (x + w // steps, h), (x, h)], fill=0)
            prev = nxt
    elif edge == "top":
        prev = rng.randint(h // 3, h // 2)
        for x in range(0, w, max(1, w // steps)):
            nxt = rng.randint(h // 3, h // 2)
            d.polygon([(x, prev), (x + w // steps, nxt),
                       (x + w // steps, 0), (x, 0)], fill=0)
            prev = nxt
    base.putalpha(mask)
    return base


def splatter(im: Image.Image, n=400, seed=11, color=(0, 0, 0), max_r=14) -> Image.Image:
    rng = random.Random(seed)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w, h = im.size
    for _ in range(n):
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        r = rng.randint(1, max_r)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*color, rng.randint(60, 200)))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


# ── composite ─────────────────────────────────────────────────────────────────

def ring(d: int, width: int, color: str) -> Image.Image:
    disc = Image.new("RGBA", (d + width * 2, d + width * 2), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse(
        (0, 0, d + width * 2 - 1, d + width * 2 - 1), outline=color, width=width)
    return disc


def circle_sticker(src: Image.Image, d: int, ring_w: int, ring_color: str,
                   focus=(0.5, 0.45), bg="#000000") -> Image.Image:
    """Circular crop of a face with a colored ring on a dark backing disc."""
    face = cover_crop(src.convert("RGB"), d, d, focus=focus)
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
    disc = Image.new("RGBA", (d + ring_w * 2, d + ring_w * 2), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse((0, 0, d + ring_w * 2 - 1, d + ring_w * 2 - 1), fill=ring_color)
    dd.ellipse((4, 4, d + ring_w * 2 - 5, d + ring_w * 2 - 5), fill=bg)
    face_r = face.convert("RGBA")
    face_r.putalpha(mask)
    disc.paste(face_r, (ring_w, ring_w), face_r)
    return disc


def stripe(draw, w: int, h: int, frac: float = 0.06, color: str = "#DEFF2E"):
    draw.rectangle([0, 0, int(w * frac), h], fill=color)


def masthead(draw, w: int, brand: dict):
    """Brand masthead: black bar + brand color keyline + name + URL."""
    from .brand import hex_rgb as _h
    name = brand.get("name", "BRAND")
    url = (brand.get("url") or "").upper()
    c = brand.get("c") or {}
    lime = c.get("lime") or c.get("w") or "#DEFF2E"
    cyan = c.get("cyan") or c.get("w") or "#2FF3FF"
    k = c.get("k") or "#000000"
    draw.rectangle([0, 0, w, 56], fill=k)
    draw.rectangle([0, 56, w, 62], fill=lime)
    draw.text((16, 28), name, font=impact(28), fill=lime, anchor="lm")
    if url:
        draw.text((w - 16, 28), url, font=impact(18), fill=cyan, anchor="rm")


def url_plate(draw, w: int, h: int, label: str, fill="#2FF3FF", text_fill="#000000"):
    f = fit_line(label, int(w * 0.62), 22, 16, stroke=0)
    tw = int(f.getlength(label) + 36)
    x1 = (w - tw) // 2
    y1, y2 = h - 52, h - 12
    draw.rectangle([x1, y1, x1 + tw, y2], fill=fill)
    draw.text((w // 2, (y1 + y2) // 2), label, font=f, fill=text_fill, anchor="mm")


# ── compositing / craft (brand-agnostic, image→image) ────────────────────────
# These are the "hand-made graphics" primitives: duotone, mosaic, xerox, relief,
# glitch-slice, anaglyph, waterline submerge, tint, and a two-image blend. Each
# takes colors as plain args (hex or rgb) so any brand palette can drive them.

def duotone(im: Image.Image, dark="#000000", light="#FFFFFF") -> Image.Image:
    """Map grayscale to a two-color ramp (dark shadow → light highlight)."""
    g = ImageOps.grayscale(im.convert("RGB"))
    return ImageOps.colorize(g, black=_rgb(dark), white=_rgb(light))


def mosaic(im: Image.Image, tile: int = 18) -> Image.Image:
    """Pixelate: shrink to a coarse grid, stretch back (mosaic / censor look)."""
    w, h = im.size
    small = im.resize((max(1, w // tile), max(1, h // tile)), Image.Resampling.BILINEAR)
    return small.resize((w, h), Image.Resampling.NEAREST)


def xerox(im: Image.Image, contrast: float = 2.0, grain_n: int = 3000, seed: int = 9) -> Image.Image:
    """1-bit photocopy: harsh threshold + grain. A 'body as a copy of itself' look."""
    g = ImageEnhance.Contrast(ImageOps.autocontrast(ImageOps.grayscale(im.convert("RGB")))).enhance(contrast)
    g = g.point(lambda p: 255 if p > 128 else 0)
    return grain(g.convert("RGB"), n=grain_n, seed=seed, alpha=60, max_v=40)


def relief(im: Image.Image, amount: float = 0.35) -> Image.Image:
    """Emboss relief blended back into the source (sculpted stone look)."""
    return Image.blend(im.convert("RGB"), im.convert("RGB").filter(ImageFilter.EMBOSS), amount)


def slice_glitch(im: Image.Image, n: int = 14, max_shift: int = 40, seed: int = 7) -> Image.Image:
    """Horizontal slice glitch: shift each band sideways by a seeded amount."""
    rng = random.Random(seed)
    im = im.convert("RGB"); W, H = im.size
    band = max(2, H // n)
    out = Image.new("RGB", (W, H), (0, 0, 0))
    for i in range(n):
        y0 = i * band; y1 = min(H, (i + 1) * band)
        strip = im.crop((0, y0, W, y1))
        dx = rng.randint(-max_shift, max_shift)
        out.paste(strip, (dx, y0))
    return out


def color_split(im: Image.Image, dx: int = 8, dy: int = 0) -> Image.Image:
    """Anaglyph channel split (real RGB separation, keep the red channel)."""
    r, g, b = im.convert("RGB").split()
    g = ImageChops.offset(g, dx, dy)
    b = ImageChops.offset(b, -dx, -dy)
    return Image.merge("RGB", (r, g, b))


def waterline(im: Image.Image, frac: float = 0.55, dark="#0A0E1A", glow="#2FF3FF") -> Image.Image:
    """Submerge the lower portion: dark water + a faint glowing reflection line."""
    im = im.convert("RGB"); W, H = im.size; y = int(H * frac)
    top = im.crop((0, 0, W, y))
    below = im.crop((0, y, W, H)).convert("L").point(lambda p: int(p * 0.5))
    below = ImageOps.colorize(below, black=_rgb(dark), white=_rgb(dark))
    out = Image.new("RGB", (W, H), _rgb(dark)); out.paste(top, (0, 0)); out.paste(below, (0, y))
    ImageDraw.Draw(out).line([(0, y), (W, y)], fill=_rgb(glow), width=3)
    return out


def tint(im: Image.Image, color: str = "#0A0E1A", amount: float = 0.4) -> Image.Image:
    """Blend a solid color over the image (grade toward a mood)."""
    return Image.blend(im.convert("RGB"), Image.new("RGB", im.size, _rgb(color)), amount)


def lead_lines(im: Image.Image, dark="#0A0E1A", light="#2FF3FF") -> Image.Image:
    """Stained-glass: find edges as lead lines over a posterized color plate."""
    edges = im.convert("RGB").filter(ImageFilter.FIND_EDGES)
    plate = ImageOps.posterize(im.convert("RGB"), 3)
    return Image.blend(plate, edges, 0.5)


def blend(a: Image.Image, b: Image.Image, mode: str = "screen") -> Image.Image:
    """Blend two images of (possibly) different size; cover-crops b to a."""
    a = a.convert("RGB"); b = b.convert("RGB")
    if a.size != b.size:
        b = cover_crop(b, *a.size)
    if mode == "screen":
        return ImageChops.screen(a, b)
    if mode == "multiply":
        return ImageChops.multiply(a, b)
    if mode == "lighter":
        return ImageChops.lighter(a, b)
    if mode == "overlay":
        return ImageChops.overlay(a, b)
    if mode == "soft_light":
        return ImageChops.soft_light(a, b)
    if mode == "difference":
        return ImageChops.difference(a, b)
    return Image.blend(a, b, 0.5)


# ── procedural overlays (image → image; draw-based, still deterministic) ─────

def perspective_grid(im: Image.Image, horizon: float = 0.55, color="#2FF3FF",
                     alpha: int = 30, n_h: int = 12, n_v: int = 17, width: int = 2) -> Image.Image:
    """Vaporwave/synthwave perspective grid over the image (vanishing-point lines)."""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    W, H = im.size; hy = int(H * horizon); vp = (W // 2, hy)
    col = _rgb(color)
    for i in range(n_v + 1):
        x = int(W * i / n_v)
        d.line([(x, H), vp], fill=(*col, alpha), width=width)
    for i in range(n_h + 1):
        t = i / n_h; y = H - (H - hy) * (t ** 2)
        d.line([(0, y), (W, y)], fill=(*col, alpha), width=width)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def starfield(im: Image.Image, n: int = 900, seed: int = 7, color="#FFFFFF",
              max_a: int = 160, y_frac: float = 0.7) -> Image.Image:
    """Scatter seeded star dots across the upper portion (cosmic/void)."""
    rng = random.Random(seed)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    W, H = im.size; col = _rgb(color)
    for _ in range(n):
        x = rng.randint(0, W - 1); y = rng.randint(0, int(H * y_frac))
        a = rng.randint(30, max_a); r = rng.choice([1, 1, 1, 2, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*col, a))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def vgradient(w: int, h: int, stops: list) -> Image.Image:
    """Vertical gradient. stops = [(pos0..1, (r,g,b)), ...], ordered."""
    g = Image.new("RGB", (1, h)); gd = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        col = stops[-1][1]
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]; p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = (t - p0) / (p1 - p0) if p1 > p0 else 0
                col = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3)); break
        gd.point((0, y), fill=col)
    return g.resize((w, h))


def _rgb(c) -> tuple:
    if isinstance(c, str):
        from .brand import hex_rgb
        return hex_rgb(c)
    return tuple(c)


# ── recipe sampling ───────────────────────────────────────────────────────────

def filter_kwargs(fn, params: dict) -> dict:
    """Keep only params the effect actually accepts (by signature).

    A style recipe may name a param the effect doesn't have (or spell it
    differently). Passing a bogus kwarg raises TypeError; silently dropping
    `bits`/`factor` (as an earlier version did) silently corrupts output.
    The correct behavior is to pass through every param the function accepts
    and drop only the ones it doesn't — never a hard-coded allowlist.
    """
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return dict(params)
    return {k: v for k, v in params.items() if k in sig.parameters}


def apply_filter(im: Image.Image, name: str, params: dict | None = None) -> Image.Image:
    """Dispatch one named filter through EFFECTS with signature-filtered kwargs.

    Canonical filter application: render.py and library.py both go through
    this so the compose path and the generated-script path agree exactly.
    Unknown names return the image unchanged (never raise).
    """
    fn = EFFECTS.get((name or "").lower())
    if not fn:
        return im
    kwargs = filter_kwargs(fn, params or {})
    return fn(im, **kwargs)


def sample(rng: random.Random, spec):
    """Sample a value from a recipe spec: literal, {"choices": [...]},
    or {"range": [lo, hi]}."""
    if isinstance(spec, dict) and "choices" in spec:
        return sample(rng, rng.choice(spec["choices"]))
    if isinstance(spec, dict) and "range" in spec:
        lo, hi = spec["range"]
        if isinstance(lo, int) and isinstance(hi, int):
            return rng.randint(lo, hi)
        return rng.uniform(float(lo), float(hi))
    if isinstance(spec, list) and spec and not isinstance(spec[0], (str, int, float)):
        return [sample(rng, x) for x in spec]
    return spec


# Map of effect name -> callable for dispatch from style `fx` lists.
EFFECTS = {
    "posterize": posterize, "solarize": solarize, "invert": invert,
    "grayscale": grayscale, "sepia": sepia, "contrast": contrast,
    "saturation": saturation, "brightness": brightness, "sharpen": sharpen,
    "autocontrast": autocontrast, "equalize": equalize,
    "blur": blur, "gaussian_blur": blur, "unsharp": unsharp,
    "unsharp_mask": unsharp, "find_edges": find_edges, "emboss": emboss,
    "contour": contour, "channel_offset": channel_offset, "warhol": warhol,
    "clamp_hues": clamp_hues, "bottom_lift": bottom_lift, "color_lift": color_lift,
    "grain": grain, "scanlines": scanlines, "crt": crt, "halftone": halftone,
    "vignette": vignette, "torn": torn, "splatter": splatter,
    # compositing / craft
    "duotone": duotone, "mosaic": mosaic, "xerox": xerox, "relief": relief,
    "slice_glitch": slice_glitch, "color_split": color_split, "waterline": waterline,
    "tint": tint, "lead_lines": lead_lines, "perspective_grid": perspective_grid,
    "starfield": starfield,
}
