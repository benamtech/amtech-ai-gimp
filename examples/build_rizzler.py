#!/usr/bin/env python3
"""RETARDGLOBAL.COM Instagram ragebait still — 1080×1350, Warhol-glitch style.

Layout (final):
  - Canvas 1080×1350, dark purple base #120018
  - Yellow stripe left edge (~8% width)
  - Main photo: sportskeeda.jpg, posterized + saturated, with glitch channel offset
  - McChicken circle inset: TOP-RIGHT corner, hot-pink (#ff2bd6) outline
  - Bottom stacked text (Impact, orange + black shadow):
        THE RIZZLER
        BITCH SLAPS HIS DAD
        AFTER HE EATS THE LAST MCCHICKEN
  - Bottom-center: cyan bar with white RETARDGLOBAL.COM
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

# ── paths ────────────────────────────────────────────────────────────────────
FONT_DIR = Path.home() / ".local" / "share" / "fonts" / "image-compose"
IMPACT_TTF = FONT_DIR / "Impact.ttf"

PHOTO_MAIN = Path("/tmp/rizzler-src/sportskeeda.jpg")
PHOTO_CIRCLE = Path("/tmp/rizzler-src/2ea21b65.bin")

OUT = Path("/home/georgej/Pictures/cli-anything-poster/retardglobal-rizzler.png")

# ── canvas ───────────────────────────────────────────────────────────────────
W, H = 1080, 1350
BASE_BG = (0x12, 0x00, 0x18)  # #120018

canvas = Image.new("RGB", (W, H), BASE_BG)

# ── helpers ───────────────────────────────────────────────────────────────────
def load_ttf(name: str) -> ImageFont.FreeTypeFont:
    p = Path(name)
    if not p.exists():
        p = IMPACT_TTF
    return ImageFont.truetype(str(p), 1)

def impact(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(IMPACT_TTF), size)

def draw_text_shadow(draw, xy, text, font, fill, shadow_offset=(3, 3),
                     shadow_color=(0, 0, 0), anchor="la"):
    """Draw text with a black shadow offset for readability."""
    sx, sy = shadow_offset
    draw.text((xy[0] + sx, xy[1] + sy), text, font=font,
              fill=shadow_color, anchor=anchor)
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)

def posterize(img: Image.Image, bits: int = 3) -> Image.Image:
    """Posterize to N bits per channel."""
    levels = 2 ** bits
    return ImageOps.posterize(img, bits)

def apply_warhol_glitch(img: Image.Image) -> Image.Image:
    """Posterize, saturate, and apply subtle RGB channel offset for glitch."""
    # posterize
    img = posterize(img, bits=3)
    # saturation boost
    img = ImageEnhance.Color(img).enhance(1.6)
    # contrast
    img = ImageEnhance.Contrast(img).enhance(1.35)

    # channel offset glitch: split, shift, merge
    r, g, b = img.split()
    # shift red and blue slightly in opposite directions
    r = ImageOps.expand(r, border=2, fill=0)
    r = r.crop((2, 0, 2 + W, H))
    b = ImageOps.expand(b, border=2, fill=0)
    b = b.crop((-2, 0, -2 + W, H))
    merged = Image.merge("RGB", (r, g, b))
    return merged

def add_bottom_lift(img: Image.Image, start_frac: float = 0.40,
                    lift_color=(255, 230, 0), strength: float = 0.35) -> Image.Image:
    """Warhol-style yellow lift on lower portion."""
    w, h = img.size
    result = img.copy().convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    y0 = int(h * start_frac)
    # gradient-ish lift via stacked translucent rects
    for i in range(20):
        frac = i / 20.0
        y = y0 + int((h - y0) * frac * 0.75)
        alpha = int(strength * 255 * (0.3 + 0.7 * frac))
        od.rectangle([0, y, w, y + 1], fill=(*lift_color, alpha))
    return Image.alpha_composite(result, overlay).convert("RGB")

# ── 1. Main photo: load, grade, place ────────────────────────────────────────
main_src = Image.open(PHOTO_MAIN).convert("RGB")
# resize to canvas, cover-crop
main_src = ImageOps.fit(main_src, (W, H), method=Image.Resampling.LANCZOS,
                         centering=(0.5, 0.5))
main_graded = apply_warhol_glitch(main_src)
main_graded = add_bottom_lift(main_graded, start_frac=0.40, lift_color=(255, 230, 0))

# slight random offset for glitch feel (deterministic from seed)
import random
rng = random.Random(42)
ox = rng.randint(-12, 12)
oy = rng.randint(-6, 6)
canvas.paste(main_graded, (ox, oy))

# ── 2. Yellow stripe along left edge ─────────────────────────────────────────
draw = ImageDraw.Draw(canvas)
stripe_w = int(W * 0.08)
draw.rectangle([0, 0, stripe_w, H], fill=(255, 230, 0))  # #FFE600

# ── 3. McChicken circle inset — TOP-RIGHT ───────────────────────────────────
mc_src = Image.open(PHOTO_CIRCLE).convert("RGB")
# crop to square centered
mw, mh = mc_src.size
side = min(mw, mh)
left = (mw - side) // 2
top = (mh - side) // 2
mc_sq = mc_src.crop((left, top, left + side, top + side))

# circle crop
mc_circle = ImageOps.fit(mc_sq, (side, side), method=Image.Resampling.LANCZOS)
mask = Image.new("L", (side, side), 0)
md = ImageDraw.Draw(mask)
md.ellipse([0, 0, side - 1, side - 1], fill=255)
mc_circle.putalpha(mask)

# size: 28% of canvas width
d = int(W * 0.28)
mc_resized = mc_circle.resize((d, d), Image.Resampling.LANCZOS)

# position: top-right, inset from edges
cx = W - d - int(W * 0.04)   # 4% from right edge
cy = int(H * 0.04)            # 4% from top edge

# hot-pink outline via a slightly larger ring behind
ring_color = (0xff, 0x2b, 0xd6)
ring_w = 10
ring = Image.new("RGBA", (d + ring_w * 2, d + ring_w * 2), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring)
rd.ellipse([ring_w, ring_w, d + ring_w * 2 - 1, d + ring_w * 2 - 1],
           outline=ring_color, width=ring_w)
ring = ring.convert("RGB")

# paste ring then circle
canvas.paste(ring, (cx - ring_w, cy - ring_w))
canvas.paste(mc_resized, (cx, cy), mc_resized)

# ── 4. Bottom stacked text — Impact, orange + black shadow ──────────────────
text_x = int(W * 0.06)  # left-aligned, ~6% in
line1 = "THE RIZZLER"
line2 = "BITCH SLAPS HIS DAD"
line3 = "AFTER HE EATS THE LAST MCCHICKEN"

# font sizes — fit roughly within canvas (larger this round)
s1 = 96
s2 = 84
s3 = 56

font1 = impact(s1)
font2 = impact(s2)
font3 = impact(s3)

# baseline positions — stack from bottom up
# bottom text block occupies roughly bottom 24% of canvas, ABOVE the cyan bar
bar_h = 42
bar_w = 340
bar_x = (W - bar_w) // 2
bar_y = H - bar_h - 4   # cyan bar sits at very bottom edge

base_y = bar_y - 70      # text block sits above the cyan bar

# measure text
def text_size(txt, font):
    bbox = font.getbbox(txt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

tw1, th1 = text_size(line1, font1)
tw2, th2 = text_size(line2, font2)
tw3, th3 = text_size(line3, font3)

# stack: line3 at bottom, then line2, then line1
y3 = base_y
y2 = y3 - th2 - 8
y1 = y2 - th1 - 8

orange = (255, 255, 255)  # white this round
shadow_off = (5, 5)        # thicker black halo = border

draw_text_shadow(draw, (text_x, y1), line1, font1, orange,
                 shadow_offset=shadow_off, anchor="la")
draw_text_shadow(draw, (text_x, y2), line2, font2, orange,
                 shadow_offset=shadow_off, anchor="la")
draw_text_shadow(draw, (text_x, y3), line3, font3, orange,
                 shadow_offset=shadow_off, anchor="la")

# ── 5. RETARDGLOBAL.COM — white text on cyan bar, bottom-center ─────────────
# (bar geometry defined above alongside text block positioning)
cyan = (0x00, 0xe5, 0xff)
draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
               fill=cyan, outline=None)

domain_font = impact(22)
domain_text = "RETARDGLOBAL.COM"
btw, bth = text_size(domain_text, domain_font)
domain_x = bar_x + (bar_w - btw) // 2
domain_y = bar_y + (bar_h - bth) // 2 - 2
draw.text((domain_x, domain_y), domain_text, font=domain_font,
          fill=(255, 255, 255), anchor="la")

# ── 6. subtle overall grain / texture (warhol feel) ─────────────────────────
# slight noise via a very low-opacity noise layer
noise = Image.new("RGBA", (W, H), (0, 0, 0, 0))
nd = ImageDraw.Draw(noise)
import random as _rnd
_rnd.seed(7)
for _ in range(6000):
    x = _rnd.randint(0, W - 1)
    y = _rnd.randint(0, H - 1)
    v = _rnd.randint(0, 20)
    nd.point((x, y), fill=(v, v, v, 30))
canvas = Image.alpha_composite(canvas.convert("RGBA"), noise).convert("RGB")

# ── save ──────────────────────────────────────────────────────────────────────
OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, "PNG")
print(f"saved: {OUT}")
print(f"size: {canvas.size}")
print(f"bytes: {OUT.stat().st_size}")
