#!/usr/bin/env python3
"""One-shot: Warhol-glitch IG ragebait still. Custom copy, local stills."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageChops

SKILL_SCRIPTS = Path("/home/georgej/.hermes/skills/creative/image-compose/scripts")
sys.path.insert(0, str(SKILL_SCRIPTS))
from run_style import apply_style  # noqa: E402

HERO_SRC = Path("/tmp/rizzler-src/sportskeeda.jpg")
INSET_SRC = Path("/tmp/rizzler-src/2ea21b65.bin")
WORK = Path("/tmp/rizzler-src")
OUT = Path("/home/georgej/Pictures/cli-anything-poster")
STYLE_PATH = SKILL_SCRIPTS / "styles" / "instagram-ragebait-warhol-glitch.json"
FONT = "Impact"


def rgb_glitch(src: Path, dest: Path) -> None:
    img = Image.open(src).convert("RGB")
    r, g, b = img.split()
    r = ImageChops.offset(r, 14, -6)
    b = ImageChops.offset(b, -18, 8)
    glitched = Image.merge("RGB", (r, g, b))
    glitched = ImageEnhance.Color(glitched).enhance(1.55)
    glitched = ImageEnhance.Contrast(glitched).enhance(1.25)
    glitched.save(dest, quality=95)


def main() -> None:
    hero = WORK / "hero_glitch.jpg"
    rgb_glitch(HERO_SRC, hero)
    style = json.loads(STYLE_PATH.read_text())
    style["font"] = FONT
    style["copy"] = {
        "handle": ["@ORBITFEED"],
        "pill": ["NEWS"],
        "l1": ["THE RIZZLER"],
        "l2": ["BITCH SLAPS HIS DAD"],
        "l3": ["AFTER HE EATS"],
        "l4": ["THE LAST MCCHICKEN"],
    }
    style["pillow"]["lift_start"] = 0.36
    style["pillow"]["bottom_lift"] = True
    style["photo"]["offset_y"] = -40
    # Yellow strip + magenta NEWS bar only (type sits on the lift)
    style["rects"] = [
        {"x1": 0, "y1": 0, "x2": "int(W*0.08)", "y2": "H", "fill": "#ffe600"},
        {"x1": "int(W*0.36)", "y1": "int(H*0.50)", "x2": "int(W*0.64)", "y2": "int(H*0.555)", "fill": "#ff2bd6"},
    ]
    style["texts"] = [
        {"text": "{handle}", "x": "int(W*0.58)", "y": 16, "size": 18, "color": "#00ffff"},
        {"text": "{pill}", "x": "int(W*0.445)", "y": "int(H*0.510)", "size": 24, "color": "#ffffff"},
        {"text": "{l1}", "x": 30, "y": "int(H*0.575)", "size": 68, "color": "#000000"},
        {"text": "{l1}", "x": 24, "y": "int(H*0.570)", "size": 68, "color": "#ff5a00"},
        {"text": "{l2}", "x": 30, "y": "int(H*0.670)", "size": 46, "color": "#000000"},
        {"text": "{l2}", "x": 24, "y": "int(H*0.665)", "size": 46, "color": "#ffffff"},
        {"text": "{l3}", "x": 30, "y": "int(H*0.755)", "size": 42, "color": "#000000"},
        {"text": "{l3}", "x": 24, "y": "int(H*0.750)", "size": 42, "color": "#ff5a00"},
        {"text": "{l4}", "x": 30, "y": "int(H*0.840)", "size": 50, "color": "#000000"},
        {"text": "{l4}", "x": 24, "y": "int(H*0.835)", "size": 50, "color": "#ffffff"},
    ]
    rng = random.Random(42)
    result = apply_style(style, str(hero), OUT / "styles", rng, photo2=str(INSET_SRC))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
