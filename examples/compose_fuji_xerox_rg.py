#!/usr/bin/env python3
"""1:1 experimental xerox/offset still — hallway + yellow-hat sticker."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageOps
from lib.rg_kit import (
    B, CYAN, K, LIME, MAG, W, circle_sticker, cover, grain,
    hex_rgb, impact, lime_stripe, masthead, stack_lines, url_plate, warhol,
)

SRC = Path(__file__).resolve().parent.parent / "sources" / "fuji_hall.jpg"
STICK = Path(__file__).resolve().parent.parent / "sources" / "fuji_profile.jpg"
OUT = Path(__file__).resolve().parent.parent / "out" / "fuji-xerox-raid-rg.png"
S = 1080


def xerox_plate(im: Image.Image) -> Image.Image:
    g = ImageOps.autocontrast(ImageOps.grayscale(im))
    g = ImageEnhance.Contrast(g).enhance(1.8)
    # LUT split-tone: darks -> cyan, lights -> lime, mids stay grey
    lime, cyan = hex_rgb(LIME), hex_rgb(CYAN)
    lr, lg, lb = [], [], []
    for v in range(256):
        if v < 90:
            t = v / 90
            lr.append(int(cyan[0] * (0.25 + 0.75 * t) * 0.55))
            lg.append(int(cyan[1] * (0.25 + 0.75 * t) * 0.55))
            lb.append(int(cyan[2] * (0.25 + 0.75 * t) * 0.55))
        elif v > 200:
            lr.append(lime[0]); lg.append(lime[1]); lb.append(lime[2])
        else:
            g2 = int(v * 0.55)
            lr.append(g2); lg.append(g2); lb.append(g2)
    rgb = Image.merge("RGB", (
        g.point(lr),
        g.point(lg),
        g.point(lb),
    ))
    r, gch, b = rgb.split()
    return Image.merge("RGB", (ImageChops.offset(r, 6, 0), gch, ImageChops.offset(b, -6, 0)))


def main() -> None:
    raw = Image.open(SRC).convert("RGB")
    rw, rh = raw.size
    raw = raw.crop((0, 0, rw, int(rh * 0.66)))
    im = cover(raw, S, S, focus=(0.50, 0.28))
    im = xerox_plate(im)
    im = grain(im, 9000, 21)
    draw = ImageDraw.Draw(im)
    lime_stripe(draw, S, S, 0.06)
    masthead(draw, S)

    sticker = circle_sticker(Image.open(STICK), int(S * 0.27), 12, MAG, focus=(0.5, 0.36))
    im.paste(sticker, (S - sticker.size[0] - 22, 80), sticker)
    draw = ImageDraw.Draw(im)

    draw.rectangle([70, 390, 300, 458], fill=MAG)
    draw.text((185, 424), "LIVE", font=impact(36), fill=K, anchor="mm")

    lines = [
        ("FEDS RAID", W, 68),
        ("THE HALLWAY", W, 54),
        ("FUJIMOTO", MAG, 78),
        ("NAMED IN A", W, 44),
        ("RICO CASE", LIME, 82),
        ("OVER ONE BEER", CYAN, 44),
    ]
    stack_lines(draw, lines, S // 2 + 8, 490, S - 160, S - 90, stroke=6)

    url_plate(draw, S, S, B["url"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, "PNG")
    print(OUT, im.size)


if __name__ == "__main__":
    main()
