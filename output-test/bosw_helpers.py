"""BOSW brand helpers — shared across output-test/ compose scripts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops
from lib.brand import load_brand, hex_rgb
from lib.fonts import resolve_font
from lib.effects import (
    grain, vignette, sepia, halftone, posterize, find_edges, emboss,
    bottom_lift, cover_crop, torn, scanlines, stack_lines, fit_line,
    stroke_text, draw_text_shadow, font as _font
)

BOSW = load_brand("bureau-of-stolen-weather")
C = {k: hex_rgb(v) for k, v in (BOSW.get("c") or {}).items()}
PAPER = C.get("paper", (232, 228, 216))
INK = C.get("ink", (26, 28, 30))
FOG = C.get("fog", (91, 122, 140))
STORM = C.get("storm", (31, 78, 90))
RUST = C.get("rust", (196, 85, 42))
BRASS = C.get("brass", (176, 141, 87))

# ── Font map (ttf path → PIL can load by path) ──────────────────────────
def _f(family, style="Regular"):
    """Resolve a system font by family + style to a ttf path."""
    import subprocess
    try:
        out = subprocess.check_output(
            ["fc-match", "-f", "%{file}", f"{family}:style={style}"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        if out and os.path.exists(out):
            return out
    except Exception:
        pass
    return None

# Primary faces
F_ARCHIVO = resolve_font("Archivo Black")        # bundled: heavy display sans
F_ANTON = resolve_font("Anton")                   # bundled: condensed bold
F_SERIF_REG = _f("Noto Serif") or resolve_font("Archivo Black")
F_SERIF_BOLD = _f("Noto Serif", "Bold") or F_SERIF_REG
F_SERIF_BLACK = _f("Noto Serif", "Black") or F_SERIF_BOLD
F_SERIF_EXTRABOLD = _f("Noto Serif", "ExtraBold") or F_SERIF_BLACK
F_SERIF_COND_BOLD = _f("Noto Serif", "Condensed Bold") or F_SERIF_BOLD
F_SANS_REG = _f("Noto Sans") or F_ARCHIVO
F_SANS_BOLD = _f("Noto Sans", "Bold") or F_ARCHIVO
F_SANS_BLACK = _f("Noto Sans", "Black") or F_ARCHIVO
F_SANS_EXTRABOLD = _f("Noto Sans", "ExtraBold") or F_SANS_BLACK
F_SANS_COND = _f("Noto Sans", "Condensed") or F_SANS_REG
F_SANS_COND_BOLD = _f("Noto Sans", "Condensed Bold") or F_SANS_BOLD
F_SANS_EXCOND = _f("Noto Sans", "ExtraCondensed") or F_SANS_COND
F_SANS_EXCOND_BLACK = _f("Noto Sans", "ExtraCondensed Black") or F_SANS_BLACK
F_SANS_SEMICOND = _f("Noto Sans", "SemiCondensed") or F_SANS_REG
F_MONO = _f("Noto Sans Mono") or _f("Droid Sans Mono") or F_SANS_COND
F_MONO_COND_BOLD = _f("Noto Sans Mono", "Condensed Bold") or F_MONO
F_DROID_SERIF = _f("Droid Serif") or F_SERIF_REG
F_DROID_SERIF_BOLD = _f("Droid Serif", "Bold") or F_SERIF_BOLD
F_DROID_SANS = _f("Droid Sans") or F_SANS_REG
F_DROID_SANS_BOLD = _f("Droid Sans", "Bold") or F_SANS_BOLD
F_DROID_MONO = _f("Droid Sans Mono") or F_MONO

# ── Canvas ──────────────────────────────────────────────────────────────
def canvas(w, h, bg=PAPER):
    return Image.new("RGB", (w, h), bg)

def draw(img):
    return ImageDraw.Draw(img)

# ── Text helpers ────────────────────────────────────────────────────────
def tt(face, size):
    return ImageFont.truetype(face, size)
def tb(text, face, size):
    return int(tt(face, size).getlength(text))

def dt(d, xy, text, face, size, fill=INK, anchor="lt", stroke=None, stroke_w=0):
    f = tt(face, size)
    kw = {"font": f, "fill": fill, "anchor": anchor}
    if stroke and stroke_w:
        kw["stroke_width"] = stroke_w; kw["stroke_fill"] = stroke
    d.text(xy, text, **kw)

def dtr(d, x, y, w, text, face, size, fill=INK, anchor="lt"):
    """Draw text right-aligned within width w from x."""
    tw = tb(text, face, size)
    dt(d, (x + w - tw, y), text, face, size, fill, anchor="lt")

def dtc(d, x, y, w, text, face, size, fill=INK):
    """Draw text centered within width w from x."""
    tw = tb(text, face, size)
    dt(d, (x + (w - tw) // 2, y), text, face, size, fill, anchor="lt")

# ── Geometry ─────────────────────────────────────────────────────────────
def rule(d, x1, y1, x2, y2, fill=INK, width=2):
    d.line([(x1, y1), (x2, y2)], fill=fill, width=width)
def hrule(d, y, w, x=0, fill=INK, width=1):
    d.line([(x, y), (x + w, y)], fill=fill, width=width)
def vrule(d, x, y, h, fill=INK, width=1):
    d.line([(x, y), (x, y + h)], fill=fill, width=width)

def box(d, x, y, w, h, fill=None, outline=INK, width=1):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=outline, width=width)

# ── Grid ─────────────────────────────────────────────────────────────────
def grid(d, x, y, w, h, cols, rows, stroke=FOG, width=1):
    for i in range(cols + 1):
        xx = x + (w * i // cols)
        d.line([(xx, y), (xx, y + h)], fill=stroke, width=width)
    for i in range(rows + 1):
        yy = y + (h * i // rows)
        d.line([(x, yy), (x + w, yy)], fill=stroke, width=width)

# ── Registration marks ───────────────────────────────────────────────────────
def reg_marks(d, w, h, pad=40):
    for cx, cy in [(pad, pad), (w-pad, pad), (pad, h-pad), (w-pad, h-pad)]:
        d.line([(cx-16, cy), (cx+16, cy)], fill=INK, width=1)
        d.line([(cx, cy-16), (cx, cy+16)], fill=INK, width=1)

# ── Stamp ───────────────────────────────────────────────────────────────────
def rubber_stamp(img, cx, y, text, face, size, fill=RUST, rot=-2.5):
    w = int(tt(face, size).getlength(text)) + 60
    s = Image.new("RGBA", (w, size + 30), (0,0,0,0))
    sd = ImageDraw.Draw(s)
    sd.rectangle([2, 2, w-3, size+27], outline=fill, width=3)
    tw2 = int(tt(face, size).getlength(text))
    sd.text(((w-tw2)//2, 10), text, font=tt(face, size), fill=fill)
    s = s.rotate(rot, expand=True, resample=Image.Resampling.BICUBIC)
    img.paste(s, (cx - s.width//2, y - s.height//2), s)
    return s

def classification_stripe(d, w, y, label, fill=RUST):
    d.rectangle([0, y, w, y+32], fill=fill)
    tw = tb(label, F_SANS_COND_BOLD, 18)
    dt(d, ((w-tw)//2, y+8), label, F_SANS_COND_BOLD, 18, fill=PAPER)

# ── Color swatch ────────────────────────────────────────────────────────
def swatch(d, x, y, size, rgb, label=None):
    d.rectangle([x, y, x+size, y+size], fill=rgb, outline=INK, width=1)
    if label:
        dt(d, (x+size+8, y+size//2-6), label, F_MONO, 14, fill=INK, anchor="lm")