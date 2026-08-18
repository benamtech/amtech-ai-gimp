# RETARD GLOBAL — Meme Format Spec (derived from the reference pixels)

This is the concrete build spec for the single RG meme format, reverse-engineered
from `/home/georgej/Desktop/retardglobal-assets/` with `vision_analyze` +
pixel-level color sampling (Pillow). It supersedes any earlier guess. When the
images and this doc disagree, trust the images — but this doc records what the
pixels actually showed.

## Sources inspected

- `meme-example-1--rg-branded.jpg` (912x1136) — RG tabloid, magenta masthead.
- `meme-example-2-great-use-of-effeccts-rg-branded.jpg` (976x1056) — RG, same masthead grammar.
- `meme-example-3-good-effects-ok-rg-branded.jpg` (335x480) — RG, low-res, same masthead.
- `meme-example-4-...png` (797x800) — the clean non-RG "GBS" format (the layout that
  performs). Provides the *grammar* (photo → headline → footer), NOT the RG identity.

## Pixel findings (authoritative, not guessed)

| Element | Finding | Source |
|---|---|---|
| Masthead block | solid MAGENTA rectangle, sharp corners, top-left | ex1 fill `#FB01D7`, ex3 `#F116BC` (JPEG noise around the brand `#FD2EFF`) |
| "RETARD GLOBAL" (masthead) | **LIME** text (`#DEFF2E`-family), Impact, uppercase | ex1/ex2 crops both show lime wordmark |
| "RETARDGLOBAL.COM" (masthead) | **WHITE** text, smaller, uppercase | ex1/ex2 crops |
| Masthead type | **text-only — NO logo image** | all crops: pure text |
| Headline | **LIME**, uniform (NOT alternating white/accent), Impact, thick black stroke, first line biggest | ex1 rows624-1079: lime 20151px, white 0 |
| Footer | "RETARDGLOBAL.COM" **WHITE**, centered bottom | ex1/ex2/ex3 footer rows: white text on black |
| Gradient | smooth fade-to-black in the lower half | ex1 headline zone ~black, no hard box edge |
| Divider line | **none** in RG examples | ex1/ex2 (the thin line + "GBS" call-sign + speaker icon are example-4's *channel* identity, not RG) |
| NEWS pill | **none** in RG examples — the magenta masthead IS the branding | ex1/ex2 |

### What this means

The RG meme masthead is a **text-only wordmark lock**:

```
[ ─────────── MAGENTA #FD2EFF ─────────── ]
  RETARD GLOBAL      (LIME  #DEFF2E, Impact, ~44px)
  RETARDGLOBAL.COM   (WHITE #FFFFFF, Impact, ~20px)
```

No logo PNG, no icon. The wordmark + hi-vis lime + magenta are the brand assets
embedded in the meme. The separate logo files (8-bit world-map grid, CRT "R")
are brand marks for the **banner** (`rg-banner`) and standalone badge use — the
meme examples deliberately keep the masthead text-only.

## The single format (1:1 `rg-meme` / 4:5 `rg-meme-45`)

1. **Photo** — full-bleed cover-crop, CLEAN grade: contrast ~1.12, saturation
   ~1.08. NO hue-clamp, NO glitch, NO deep-fry.
2. **Gradient** — `fade_gradient` start 0.45 → black, strength 0.85 (smooth
   contiguous rows, not a banded `bottom_lift`, not a box).
3. **Masthead** — top-left magenta block (`#FD2EFF`, ~46% width × ~112px),
   lime "RETARD GLOBAL" + white "RETARDGLOBAL.COM".
4. **Headline** — stacked Impact, lime `#DEFF2E`, black stroke (8px), **tightly
   stacked** (`gap=2`, lines "touch") and **large, close-in-size**: first line
   ~130px, the rest ~110px (first line only slightly bigger — deliberately below
   the 1.5× hierarchy rule; the user wants close sizes). `fill=true` grows the
   block to occupy the band down to the footer, and long copy shrinks to fit.
5. **Footer** — "RETARDGLOBAL.COM" WHITE, centered ~28px, with equal space
   above and below (the headline block ends just above it).
6. **Corner logo badge** — the world-map logo (or computer CRT logo) pasted in
   the top-right corner, ~13% of width, its bottom edge aligned with the
   masthead banner's bottom edge, black keyline. This is how
   the RG brand *assets* are embedded in every meme (the masthead stays
   text-only).

Variety = copy + photo + seed. Named canvas (1:1 vs 4:5) or named look
(`deep-fried-ragebait` technique) — never a per-copy-type template.

## Hard rules re-asserted (what previous sessions got wrong)

- Masthead wordmark is **lime**, footer is **white** (both were flipped before).
- Photos are **clean** — the `compose` path must not hue-clamp by default.
- One format only. "Wanted for double homicide" == "starts taking Ozempic".
- **Never use the Jimmy Fallon image** of The Rizzler (any Fallon still). The
  indexed non-Fallon Rizzler stills are `the-rizzler-origin.jpg`,
  `the-rizzler-knicks.jpg`, `the-rizzler-superhero.jpg` (red-carpet costume).
