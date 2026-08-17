#!/usr/bin/env python3
"""Instagram portrait: 1080×1350.

- sportskeeda.jpg centered, cover-cropped, posterized + saturated + RGB glitch offset
- warm yellow glow on the bottom half
- top-right McChicken circle inset with hot pink sticker ring
- no headline text; pure photo treatment
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

FONT_DIR = Path.home() / ".local" / "share" / "fonts" / "image-compose"
IMPACT_TTF = FONT_DIR / "Impact.ttf"

PHOTO_MAIN = Path("/tmp/rizzler-src/sportskeeda.jpg")
PHOTO_CIRCLE = Path("/tmp/rizzler-src/2ea21b65.bin")

OUT = Path("/home/georgej/Pictures/cli-anything-poster/rizzler-warhol-glitch-portrait.png")

W, H = 1080, 1350
BASE_BG = (0x12, 0x00, 0x18)


def impact(size: int):
    return ImageFont.truetype(str(IMPACT_TTF), size)


def posterize(img: Image.Image, bits: int = 3) -> Image.Image:
    return ImageOps.posterize(img, bits)


def apply_warhol_glitch(img: Image.Image) -> Image.Image:
    img = posterize(img, bits=3)
    img = ImageEnhance.Color(img).enhance(1.7)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    r, g, b = img.split()
    r = ImageOps.expand(r, border=3, fill=0)
    r = r.crop((3, 0, 3 + W, H))
    b = ImageOps.expand(b, border=3, fill=0)
    b = b.crop((-3, 0, -3 + W, H))
    return Image.merge("RGB", (r, g, b))


def add_bottom_glow(img: Image.Image, start_frac: float = 0.40,
                    glow_color=(255, 230, 0), strength: float = 0.45) -> Image.Image:
    w, h = img.size
    result = img.copy().convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    y0 = int(h * start_frac)
    for i in range(40):
        frac = i / 40.0
        y = y0 + int((h - y0) * frac * 0.8)
        alpha = int(strength * 255 * (0.15 + 0.85 * frac))
        od.rectangle([0, y, w, y + 1], fill=(*glow_color, alpha))
    return Image.alpha_composite(result, overlay).convert("RGB")


def add_grain(img: Image.Image, density: int = 8000, max_val: int = 18, alpha: int = 28, seed: int = 7) -> Image.Image:
    noise = Image.new("RGBA", img.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    import random as _rnd
    _rnd.seed(seed)
    w, h = img.size
    for _ in range(density):
        x = _rnd.randint(0, w - 1)
        y = _rnd.randint(0, h - 1)
        v = _rnd.randint(0, max_val)
        nd.point((x, y), fill=(v, v, v, alpha))
    return Image.alpha_composite(img.convert("RGBA"), noise).convert("RGB")


# Load main photo
main_src = Image.open(PHOTO_MAIN).convert("RGB")
main_src = ImageOps.fit(main_src, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
main_graded = apply_warhol_glitch(main_src)
main_graded = add_bottom_glow(main_graded, start_frac=0.40, glow_color=(255, 230, 0))
main_graded = add_grain(main_graded)

# Slight random offset for glitch feel
import random as _rnd
_rng = _rnd.Random(42)
ox = _rng.randint(-10, 10)
oy = _rng.randint(-6, 6)

canvas = Image.new("RGB", (W, H), BASE_BG)
canvas.paste(main_graded, (ox, oy))

# McChicken circle inset — top-right corner
mc_src = Image.open(PHOTO_CIRCLE).convert("RGB")
mw, mh = mc_src.size
side = min(mw, mh)
left = (mw - side) // 2
top = (mh - side) // 2
mc_sq = mc_src.crop((left, top, left + side, top + side))

d = int(W * 0.26)
mc_resized = mc_sq.resize((d, d), Image.Resampling.LANCZOS)
mask = Image.new("L", (d, d), 0)
ImageDraw.Draw(mask).ellipse([0, 0, d - 1, d - 1], fill=255)
mc_resized.putalpha(mask)

cx = W - d - int(W * 0.05)
cy = int(H * 0.05)

ring_color = (0xFF, 0x2B, 0xD6)
ring_w = 10
ring = Image.new("RGBA", (d + ring_w * 2, d + ring_w * 2), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring)
rd.ellipse([ring_w, ring_w, d + ring_w * 2 - 1, d + ring_w * 2 - 1],
           outline=ring_color, width=ring_w)
ring_rgb = ring.convert("RGB")

canvas.paste(ring_rgb, (cx - ring_w, cy - ring_w))
canvas.paste(mc_resized, (cx, cy), mc_resized)

OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, "PNG")
print(f"saved: {OUT}")
print(f"size: {canvas.size}")
print(f"bytes: {OUT.stat().st_size}")
