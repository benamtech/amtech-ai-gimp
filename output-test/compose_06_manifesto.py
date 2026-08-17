"""Image 6: Manifesto Poster — THE WEATHER REMEMBERS WHAT THE SKY FORGOT."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bosw_helpers import *

W, H = 2400, 3000
img = canvas(W, H, STORM)
d = draw(img)

# Source photo (same smog image, processed differently)
SRC = "output-test/sources/nelsons_column_smog_1952.jpg"
if os.path.exists(SRC):
    photo = Image.open(SRC).convert("RGB")
    photo = cover_crop(photo, W, H, focus=(0.5, 0.35))
    # Duotone: grain + storm
    photo = ImageOps.grayscale(photo)
    photo = ImageOps.colorize(photo, black=INK, white=FOG)
    photo = posterize(photo, 3)
    photo = ImageEnhance.Contrast(photo).enhance(1.6)
    photo = grain(photo, n=10000, seed=77, alpha=25, max_v=15)
    photo = vignette(photo, strength=0.6, color=INK)
    img.paste(photo, (0, 0))
    d = draw(img)
    used_src = True
else:
    used_src = False

d = draw(img)

# Massive headline — brutalist
headline = "THE WEATHER\nREMEMBERS\nWHAT THE SKY\nFORGOT"
lines = headline.split("\n")
hs = 160
y = 120
for line in lines:
    tw = tb(line, F_ARCHIVO, hs)
    x = (W - tw) // 2
    # Shadow first
    dt(d, (x+6, y+6), line, F_ARCHIVO, hs, fill=INK+(180,))
    dt(d, (x, y), line, F_ARCHIVO, hs, fill=PAPER)
    y += hs + 20

# Deck — serif authority
y2 = y + 40
deck_lines = [
    "A MANIFESTO OF THE METROLOGICAL-MEMORY DIVISION",
    "BUREAU OF STOLEN WEATHER"
]
for dl in deck_lines:
    dtc(d, 0, y2, W, dl, F_SERIF_EXTRABOLD, 30, fill=BRASS)
    y2 += 40

# Bottom block — institutional
hrule(d, H-280, W-400, 200, BRASS, 1)
dt(d, (200, H-240), "RECOVERED · AUTHENTICATED · ARCHIVED", F_SANS_COND_BOLD, 22, fill=PAPER)
dt(d, (200, H-200), "BOSW.ARCHIVE  ·  CLASS 1-A  ·  EST. 2026", F_SANS_COND, 16, fill=FOG)

if used_src:
    rubber_stamp(img, W-250, H-380, "VERIFIED", F_ARCHIVO, 28, fill=RUST, rot=-3)

# Grain
img = grain(img, n=6000, seed=77, alpha=12, max_v=10)
img.save("output-test/06_manifesto_poster.png")
print(f"Saved output-test/06_manifesto_poster.png ({W}x{H})")