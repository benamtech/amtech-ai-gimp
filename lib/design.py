"""Design rules — reviewed guidance for combinations that actually look good.

Deterministic rendering guarantees *correctness*, not *taste*. A brand lock
records *what* a palette is; it does not say whether a given text-on-background
pair is legible, whether two colors will vibrate, whether an effect suits the
image it is applied to, or whether two seeded "variants" are actually distinct.

This module encodes those rules as small, pure, testable predicates. It is the
"review" layer: feed it a resolved composition (or a brand, or two colors, or
two seeds) and it returns findings — never silent, never opinion-as-fact
beyond a documented threshold.

Rules (all reviewed, all documented inline):
  1. contrast      — WCAG-relative luminance; text must clear a floor.
  2. harmony       — near-duplicate palette entries and forbidden-hue hits.
  3. pairing       — effect <-> image-type fit (a curated table).
  4. variants      — two variants must differ on a *visible* axis, not just
                     RNG noise (grain seed / glitch offset are invisible at
                     poster size, so they never count as "distinct").

Nothing here imports Pillow. It operates on hex strings, RGB tuples, and the
`resolved` dict shape produced by lib.compose.resolve().
"""
from __future__ import annotations

import colorsys


# ── 1. contrast ──────────────────────────────────────────────────────────────

def _srgb(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def contrast_ratio(fg: str | tuple, bg: str | tuple) -> float:
    """WCAG contrast ratio between two colors (1.0 .. 21.0)."""
    fg = hex_rgb(fg) if isinstance(fg, str) else tuple(fg)
    bg = hex_rgb(bg) if isinstance(bg, str) else tuple(bg)
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def legible(fg: str | tuple, bg: str | tuple, large: bool = False) -> bool:
    """WCAG AA: >= 4.5 for body text, >= 3.0 for large text (>= 18pt/14pt bold)."""
    return contrast_ratio(fg, bg) >= (3.0 if large else 4.5)


def best_foreground(bg: str | tuple, candidates: list[str]) -> str:
    """Pick the candidate with the highest contrast against `bg`."""
    return max(candidates, key=lambda c: contrast_ratio(c, bg))


# ── 2. harmony ───────────────────────────────────────────────────────────────

def _hsv(h: str) -> tuple[float, float, float]:
    return colorsys.rgb_to_hsv(*[c / 255 for c in hex_rgb(h)])


def near_duplicates(hexes: list[str], tol: float = 0.08) -> list[tuple[str, str]]:
    """Pairs of palette colors too close to tell apart (HSV distance < tol)."""
    out = []
    for i in range(len(hexes)):
        for j in range(i + 1, len(hexes)):
            h1, s1, v1 = _hsv(hexes[i])
            h2, s2, v2 = _hsv(hexes[j])
            dh = min(abs(h1 - h2), 1 - abs(h1 - h2))
            d = (dh ** 2 + (s1 - s2) ** 2 + (v1 - v2) ** 2) ** 0.5
            if d < tol:
                out.append((hexes[i], hexes[j]))
    return out


def forbidden_hits(hexes: list[str], brand: dict) -> list[str]:
    """Palette colors that fall on the brand's forbid list (by name/substring)."""
    forbid = brand.get("forbid") or []
    hits = []
    for h in hexes:
        for f in forbid:
            if f and f.lower() in h.lower():
                hits.append(h)
                break
    return hits


# ── 3. effect <-> image-type pairing ─────────────────────────────────────────
#
# Curated by review, not by formula: which treatments suit which source classes.
# "image type" is a coarse, deliberate classification the author names (the
# program cannot see the image). Each entry maps a source class to (good, avoid).

PAIRINGS: dict[str, tuple[list[str], list[str]]] = {
    # a face/portrait: keep skin tones, avoid harsh edges / flattening
    "portrait": (["duotone", "color_lift", "grain", "vignette", "solarize"],
                 ["find_edges", "emboss", "halftone", "xerox", "posterize"]),
    # stone / statue / architecture: high-key marble, relief, glitch
    "sculpture": (["duotone", "relief", "emboss", "posterize", "channel_offset",
                   "waterline", "mosaic"],
                  ["warhol", "clamp_hues", "crt"]),
    # dark / cosmic / void: keep it dark, add signal lines, stars
    "void": (["vignette", "stars", "grain", "grid", "glow", "tint"],
             ["warhol", "posterize", "halftone", "sepia"]),
    # ocean / sky / landscape: horizon grids, waterline, warm duotone
    "landscape": (["duotone", "waterline", "grid", "bottom_lift", "color_lift"],
                  ["xerox", "find_edges", "emboss"]),
    # texture / circuit / coral / machine: screen-blend double exposure
    "texture": (["clamp_hues", "blend", "mosaic", "halftone", "scanlines"],
                ["relief", "emboss", "vignette"]),
}


def pairing_fit(effect: str, image_type: str) -> tuple[bool, str]:
    """Whether an effect suits an image type. Returns (ok, reason)."""
    if image_type not in PAIRINGS:
        return True, f"unknown image type {image_type!r} (no rule; author's call)"
    good, avoid = PAIRINGS[image_type]
    if effect in avoid:
        return False, f"{effect!r} is on the avoid list for {image_type!r} (see {good})"
    if effect in good:
        return True, f"{effect!r} is recommended for {image_type!r}"
    return True, f"{effect!r} is neutral for {image_type!r}"


# ── 4. variant distinctness ──────────────────────────────────────────────────
#
# The failure this guards: seeding a "variant" that only perturbs grain() or
# channel_offset()/slice_glitch() noise. At 1080² those are imperceptible, so
# the two outputs look identical and the "variants" are worthless.

NOISE_ONLY_EFFECTS = {"grain", "channel_offset", "slice_glitch", "scanlines",
                      "splatter", "vignette"}


def variant_axis_delta(a: dict, b: dict) -> list[str]:
    """Name the axes on which two resolved compositions *visibly* differ.

    Compares canvas, background, filters (name + non-noise params), copy slots,
    and rect/text geometry. Noise-only effects (grain, glitch) are ignored so
    a difference there does not count as "distinct".
    """
    diffs = []
    if a.get("canvas") != b.get("canvas"):
        diffs.append("canvas")
    if a.get("background") != b.get("background"):
        diffs.append("background")

    fa = _visible_filters(a.get("filters", []))
    fb = _visible_filters(b.get("filters", []))
    if fa != fb:
        diffs.append("filters")

    if a.get("copy") != b.get("copy"):
        diffs.append("copy")

    if a.get("texts") != b.get("texts") or a.get("rects") != b.get("rects"):
        diffs.append("layout")
    return diffs


def _visible_filters(filters: list[dict]) -> list[tuple]:
    """Filters reduced to their visible identity: name + non-noise params."""
    out = []
    for f in filters:
        name = (f.get("name") or "").lower()
        p = f.get("param") or {}
        if name in NOISE_ONLY_EFFECTS:
            continue
        out.append((name, tuple(sorted((k, str(v)) for k, v in p.items()))))
    return out


def variants_distinct(a: dict, b: dict) -> tuple[bool, str]:
    """Are two resolved variants actually different to the eye?"""
    diffs = variant_axis_delta(a, b)
    if diffs:
        return True, f"distinct on: {', '.join(diffs)}"
    return False, "no visible difference (only noise/seed changed)"


# ── review: one entry point ──────────────────────────────────────────────────

def review_resolved(resolved: dict, image_type: str | None = None) -> list[str]:
    """Return a list of design findings for a resolved composition.

    Findings are human-readable strings (empty list = clean). Covers contrast
    of every text against the background, near-duplicate palette entries when
    a brand is loaded, forbidden-hue hits, and effect<->image pairing when an
    `image_type` is supplied.
    """
    findings: list[str] = []

    bg = resolved.get("background", "#000000")
    for t in resolved.get("texts", []):
        if t.get("type") == "stack":
            lines = t.get("lines", [])
        else:
            lines = [t]
        for ln in lines:
            color = ln.get("color")
            if not color:
                continue
            large = int(ln.get("size", 0)) >= 32
            if not legible(color, bg, large=large):
                ratio = contrast_ratio(color, bg)
                findings.append(
                    f"low contrast: {color} on {bg} = {ratio:.2f}:1 "
                    f"(need {'3.0' if large else '4.5'}:1) for {ln.get('text', '')!r}"
                )

    brand = resolved.get("brand")
    if brand:
        hexes = list((brand.get("c") or {}).values())
        for a, b in near_duplicates(hexes):
            findings.append(f"near-duplicate palette colors: {a} vs {b}")
        for h in forbidden_hits(hexes, brand):
            findings.append(f"palette color {h} hits brand forbid list")

    if image_type:
        for f in resolved.get("filters", []):
            name = (f.get("name") or "").lower()
            ok, reason = pairing_fit(name, image_type)
            if not ok:
                findings.append(f"effect/pairing: {reason}")

    return findings


def review_brand(brand: dict) -> list[str]:
    """Review a brand document's palette for legibility + harmony issues."""
    findings: list[str] = []
    hexes = list((brand.get("c") or {}).values())
    for a, b in near_duplicates(hexes):
        findings.append(f"near-duplicate palette colors: {a} vs {b}")
    for h in forbidden_hits(hexes, brand):
        findings.append(f"palette color {h} hits brand forbid list")
    # every color should be readable as text on at least one other palette color
    if hexes:
        for h in hexes:
            others = [x for x in hexes if x != h]
            if others and all(not legible(h, o) for o in others):
                findings.append(
                    f"palette color {h} has no legible partner in the palette"
                )
    return findings
