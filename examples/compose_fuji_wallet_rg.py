#!/usr/bin/env python3
"""1:1 $FUJI wallet still — CRT scan + RGB offset, cup/profile sticker."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageDraw
from lib.rg_kit import (
    B, CYAN, K, LIME, MAG, W, circle_sticker, cover, grain,
    impact, lime_lift, lime_stripe, masthead, stack_lines, url_plate, warhol,
)

SRC = Path(__file__).resolve().parent.parent / "sources" / "fuji_mcd1.jpg"
STICK = Path(__file__).resolve().parent.parent / "sources" / "fuji_profile.jpg"
OUT = Path(__file__).resolve().parent.parent / "out" / "fuji-wallet-rg.png"
S = 1080


def scanlines(im: Image.Image, gap=4, a=70) -> Image.Image:
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w, h = im.size
    for y in range(0, h, gap):
        d.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def main() -> None:
    im = cover(Image.open(SRC), S, S, focus=(0.48, 0.28))
    im = warhol(im, 4)
    im = lime_lift(im, 0.44, 0.30)
    im = scanlines(im)
    im = grain(im, 5000, 9)
    draw = ImageDraw.Draw(im)
    lime_stripe(draw, S, S, 0.06)
    masthead(draw, S)

    sticker = circle_sticker(Image.open(STICK), int(S * 0.26), 12, LIME, focus=(0.5, 0.38))
    im.paste(sticker, (S - sticker.size[0] - 22, 80), sticker)
    draw = ImageDraw.Draw(im)

    draw.rectangle([70, 410, 340, 478], fill=CYAN)
    draw.text((205, 444), "ALERT", font=impact(34), fill=K, anchor="mm")

    lines = [
        ("HE LOST", W, 72),
        ("THE $FUJI", LIME, 84),
        ("WALLET", LIME, 90),
        ("INSIDE A", W, 46),
        ("TOKYO", MAG, 76),
        ("MCDONALDS", MAG, 64),
    ]
    stack_lines(draw, lines, S // 2 + 8, 500, S - 160, S - 90, stroke=6)

    url_plate(draw, S, S, B["lock"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, "PNG")
    print(OUT, im.size)


if __name__ == "__main__":
    main()
