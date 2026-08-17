#!/usr/bin/env python3
"""1:1 grimace shake — large Impact, RG lock, popout cup sticker."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image, ImageDraw
from lib.rg_kit import (
    B, CYAN, K, LIME, MAG, W, circle_sticker, cover, grain,
    impact, lime_lift, lime_stripe, masthead, stack_lines, url_plate, warhol,
)

SRC = Path(__file__).resolve().parent.parent / "sources" / "fuji_mcd2.jpg"
STICK = Path(__file__).resolve().parent.parent / "sources" / "cup_mid.jpg"
OUT = Path(__file__).resolve().parent.parent / "out" / "fuji-grimace-rg.png"
S = 1080


def main() -> None:
    im = cover(Image.open(SRC), S, S, focus=(0.52, 0.32))
    im = warhol(im, 3)
    im = lime_lift(im, 0.40, 0.40)
    im = grain(im, 6500, 11)
    draw = ImageDraw.Draw(im)
    lime_stripe(draw, S, S, 0.065)
    masthead(draw, S)

    sticker = circle_sticker(Image.open(STICK), int(S * 0.30), 14, MAG, focus=(0.45, 0.55))
    im.paste(sticker, (S - sticker.size[0] - 28, 78), sticker)
    draw = ImageDraw.Draw(im)

    # magenta NEWS tab
    draw.rectangle([70, 430, 310, 500], fill=MAG)
    draw.text((190, 465), "BREAKING", font=impact(32), fill=K, anchor="mm")

    lines = [
        ("FUJIMOTO", LIME, 108),
        ("DRINKS THE LAST", W, 56),
        ("GRIMACE SHAKE", MAG, 78),
        ("IN ASIA", CYAN, 92),
    ]
    stack_lines(draw, lines, S // 2 + 8, 520, S - 170, S - 90, stroke=7)

    url_plate(draw, S, S, B["lock"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, "PNG")
    print(OUT, im.size)


if __name__ == "__main__":
    main()
