#!/usr/bin/env python3
"""1:1 McFlurry machine indictment — large Impact, RG lock, hat sticker."""
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
OUT = Path(__file__).resolve().parent.parent / "out" / "fuji-mcflurry-rg.png"
S = 1080


def main() -> None:
    im = cover(Image.open(SRC), S, S, focus=(0.48, 0.30))
    im = warhol(im, 3)
    im = lime_lift(im, 0.38, 0.36)
    im = grain(im, 7000, 3)
    draw = ImageDraw.Draw(im)
    lime_stripe(draw, S, S, 0.065)
    masthead(draw, S)

    sticker = circle_sticker(Image.open(STICK), int(S * 0.28), 14, CYAN, focus=(0.5, 0.38))
    im.paste(sticker, (S - sticker.size[0] - 24, 78), sticker)
    draw = ImageDraw.Draw(im)

    draw.rectangle([70, 400, 280, 468], fill=MAG)
    draw.text((175, 434), "NEWS", font=impact(36), fill=K, anchor="mm")

    lines = [
        ("TOKYO POLICE", W, 56),
        ("SAY FUJIMOTO", W, 54),
        ("LAUNDERED", MAG, 78),
        ("$4.2M THROUGH", LIME, 50),
        ("A MCFLURRY", LIME, 74),
        ("MACHINE", LIME, 88),
    ]
    stack_lines(draw, lines, S // 2 + 10, 490, S - 160, S - 90, stroke=6)

    url_plate(draw, S, S, "ONLY ON RETARDGLOBAL.COM")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, "PNG")
    print(OUT, im.size)


if __name__ == "__main__":
    main()
