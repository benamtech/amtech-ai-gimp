"""RETARD GLOBAL brand lock + Warhol-glitch helpers for 1:1 stills."""
from __future__ import annotations

import random

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps

from .brand import hex_rgb, load_brand
from .fonts import resolve_font

B = load_brand("retardglobal")
C = B["c"]
LIME, MAG, CYAN, K, W = C["lime"], C["mag"], C["cyan"], C["k"], C["w"]
IMPACT = resolve_font(B.get("font", "Impact"))


def impact(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(IMPACT, size)


def fit_line(text: str, max_w: int, start: int, min_size: int = 28, stroke: int = 0):
    budget = max(40, max_w - 2 * stroke)
    size = start
    while size >= min_size:
        f = impact(size)
        if f.getlength(text) <= budget:
            return f
        size -= 2
    return impact(min_size)


def cover(im: Image.Image, w: int, h: int, focus=(0.5, 0.38)) -> Image.Image:
    im = im.convert("RGB")
    sw, sh = im.size
    scale = max(w / sw, h / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    x1 = max(0, min(nw - w, cx - w // 2))
    y1 = max(0, min(nh - h, cy - h // 2))
    return im.crop((x1, y1, x1 + w, y1 + h))


def kill_outlaw_hues(im: Image.Image) -> Image.Image:
    """Keep sat chroma inside lime/mag/cyan. Skin + greys stay."""
    import colorsys
    lime, mag, cyan = hex_rgb(LIME), hex_rgb(MAG), hex_rgb(CYAN)
    src = list(im.convert("RGB").getdata())
    out = []
    for r, g, b in src:
        mx, mn = max(r, g, b), min(r, g, b)
        if mx < 18 or (mx - mn) < 28:
            out.append((r, g, b))
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        deg = h * 360
        # keep skin (warm low-sat oranges)
        if 15 <= deg <= 50 and s < 0.55 and 0.25 < v < 0.92:
            out.append((r, g, b))
            continue
        # snap sat chroma to nearest brand hue
        targets = ((0.17, lime), (0.83, mag), (0.52, cyan))
        _, rgb = min(targets, key=lambda t: min(abs(h - t[0]), 1 - abs(h - t[0])))
        # mix so we don't flatten to solid neon
        out.append(tuple(int(rgb[i] * 0.55 + (r, g, b)[i] * 0.45) for i in range(3)))
    im2 = Image.new("RGB", im.size)
    im2.putdata(out)
    return im2


def warhol(im: Image.Image, bits: int = 3) -> Image.Image:
    im = ImageOps.posterize(im.convert("RGB"), bits)
    im = ImageEnhance.Color(im).enhance(1.45)
    im = ImageEnhance.Contrast(im).enhance(1.28)
    r, g, b = im.split()
    # offset green/blue only — red-channel shift makes outlaw scarlet fringes
    g = ImageChops.offset(g, 6, -3)
    b = ImageChops.offset(b, -8, 4)
    return Image.merge("RGB", (r, g, b))


def lime_lift(im: Image.Image, start=0.42, strength=0.38) -> Image.Image:
    w, h = im.size
    rgb = hex_rgb(LIME)
    base = im.convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y0 = int(h * start)
    for i in range(28):
        frac = i / 27
        y = y0 + int((h - y0) * frac * 0.82)
        a = int(strength * 255 * (0.18 + 0.82 * frac))
        d.rectangle([0, y, w, y + 2], fill=(*rgb, a))
    return Image.alpha_composite(base, ov).convert("RGB")


def grain(im: Image.Image, n=7000, seed=7) -> Image.Image:
    rng = random.Random(seed)
    noise = Image.new("RGBA", im.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    w, h = im.size
    for _ in range(n):
        nd.point((rng.randint(0, w - 1), rng.randint(0, h - 1)), fill=(rng.randint(0, 22),) * 3 + (28,))
    return Image.alpha_composite(im.convert("RGBA"), noise).convert("RGB")


def circle_sticker(src: Image.Image, d: int, ring: int, ring_hex: str, focus=(0.5, 0.45)) -> Image.Image:
    face = cover(src.convert("RGB"), d, d, focus=focus)
    mask = Image.new("L", (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
    disc = Image.new("RGBA", (d + ring * 2, d + ring * 2), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse((0, 0, d + ring * 2 - 1, d + ring * 2 - 1), fill=ring_hex)
    dd.ellipse((4, 4, d + ring * 2 - 5, d + ring * 2 - 5), fill=K)
    face_r = face.convert("RGBA")
    face_r.putalpha(mask)
    disc.paste(face_r, (ring, ring), face_r)
    return disc


def stroke_text(draw, xy, text, fnt, fill, stroke=K, width=7, anchor="mm"):
    draw.text(xy, text, font=fnt, fill=fill, stroke_width=width, stroke_fill=stroke, anchor=anchor)


def line_advance(fnt, stroke: int = 7, extra: int = 10) -> int:
    """True glyph height + stroke so stacked Impact lines never collide."""
    a, d = fnt.getmetrics()
    return a + d + stroke * 2 + extra


def stack_lines(draw, lines, cx: int, y0: int, max_w: int, bottom: int, stroke: int = 7) -> None:
    """lines = [(text, color, start_size), ...]. Shrinks if the stack would hit bottom."""
    fitted = [(t, c, fit_line(t, max_w, s, 26, stroke=stroke), stroke) for t, c, s in lines]
    total = sum(line_advance(f, st) for _, _, f, st in fitted)
    while total > (bottom - y0) and any(f.size > 28 for _, _, f, _ in fitted):
        fitted = [
            (t, c, fit_line(t, max_w, max(26, f.size - 4), 26, stroke=st), st)
            for t, c, f, st in fitted
        ]
        total = sum(line_advance(f, st) for _, _, f, st in fitted)
    y = y0
    for text, col, fnt, st in fitted:
        stroke_text(draw, (cx, y + fnt.getmetrics()[0] // 2), text, fnt, col, width=st)
        y += line_advance(fnt, st)


def masthead(draw, w):
    draw.rectangle([0, 0, w, 56], fill=K)
    draw.rectangle([0, 56, w, 62], fill=LIME)
    f = impact(28)
    draw.text((16, 28), B["name"], font=f, fill=LIME, anchor="lm")
    draw.text((w - 16, 28), B["url"].upper(), font=impact(18), fill=CYAN, anchor="rm")


def url_plate(draw, w, h, label=None):
    label = label or B["lock"]
    f = fit_line(label, int(w * 0.62), 22, 16, stroke=0)
    tw = int(f.getlength(label) + 36)
    x1 = (w - tw) // 2
    y1, y2 = h - 52, h - 12
    draw.rectangle([x1, y1, x1 + tw, y2], fill=CYAN)
    draw.text((w // 2, (y1 + y2) // 2), label, font=f, fill=K, anchor="mm")


def lime_stripe(draw, w, h, frac=0.07):
    draw.rectangle([0, 0, int(w * frac), h], fill=LIME)
