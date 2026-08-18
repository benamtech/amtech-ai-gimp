# NEXT SESSION — Fix the Chester Stone / Retard Global meme batch

Run this from `/home/georgej/Desktop/meme-maker-cli` (amtech-computer-use-graphics).
Read AGENTS.md, `docs/RG-FORMAT-SPEC.md`, `docs/RETARDGLOBAL-MEMES.md`, and the
skill `deterministic-image-composition` first. The previous session's renders
are in `out/chester/` — the benchmark image is **`out/chester/mossad-hi-vis-popout.png`**
("CHESTER STONE / JOINS MOSSAD / FOR 3 RACKS" with the Mossad seal popout): it is
considered AMAZING and is the gold standard for everything except the issues
below. Keep its photo choice, grade, popout placement, footer, and general
layout EXACTLY as-is. Do NOT redesign the format — fix the four issues below
and re-render.

## Issue 1 — Headline text still not large enough; border slightly thinner

The stacked Impact headline reads well but is not big enough, and the black
stroke is too thick.

- Stroke: currently `8` in the stack block (`styles/rg-meme.json`,
  `rg-meme-45.json` and all variants). Reduce to **~5-6** (slightly thinner border).
- Text: make it **just a bit wider/larger** two ways:
  1. Bump the stack base sizes: first line ~130 → **~150**, rest ~110 → **~130**
     (1:1; scale proportionally for 4:5). Widen `max_w` from `int(W-80)` to
     `int(W-40)` so long lines have room.
  2. **Bias copy wrapping to ~50% more characters/words per line on average.**
     Current wraps average ~13 chars/line (e.g. CHESTER STONE / JOINS MOSSAD /
     FOR 3 RACKS). Re-wrap to average ~20 chars/line, i.e. fewer, longer lines
     per meme (e.g. CHESTER STONE JOINS / MOSSAD FOR 3 RACKS). With
     `"fill": true` the stack grows lines to occupy the band, so fewer lines =
     bigger glyphs. This single change does most of the work.
- Keep `gap: 2`, `fill: true`, `y0`/`bottom` band, lime `#DEFF2E` fill.
- Watch for clipping: after the size bump, vision-verify every line fits
  `max_w` (no letter cut at the edges) and lines don't collide with the footer.
  The stack's fit/shrink logic should handle overflow, but check.

## Issue 2 — Left top-corner: use the REAL retard banner asset, or match its density

The magenta masthead box reads too empty — the box is NOT too big, the TEXT
inside is too small. The real brand banner lives at
`assets/banners/banner-lime.png` (3000x1055, hi-vis lime, "RETARD" wordmark
filling ~90-95% of the width and ~60-65% of the height + a small serif footer
line) and `assets/banners/banner-orange.png` (same, orange).

Preferred: **paste the real banner asset** (`banner-lime.png`; seed can pick
lime/orange like rg-banner does) as the left-side masthead element.

If the real asset is NOT used, the left masthead must look just like it: the
text **"RETARD GLOBAL" must fill 80-95% of the box in BOTH width and height**
(huge type, tiny margins — currently 52px in a 46%-wide x 112px box leaves big
gaps). Note the asset says "RETARD" (6 chars) while "RETARD GLOBAL" is 12
chars, so either widen the box slightly, use the real asset, or make the text
as large as fits without clipping — the density rule (80-95% fill) is the
requirement, not the exact box dimensions.

## Issue 3 — Right corner badge: flush to the right corner, bottom-aligned to the left banner

The top-right logo badge (`logo_badge` in the styles' `pillow` block — the
worldmap `logo-worldmap.png` or CRT `logo-computer.png` asset):

- Must sit **against the right corner** — currently `margin: 0.03` (32px
  inset); change to **margin ~0** so it touches the right edge, just like the
  banner sits at the left edge.
- Its **bottom edge must line up with the bottom edge of the left-side
  banner/masthead** — currently `bottom: 112` matches the old masthead height;
  if the left side becomes the taller real banner asset, set the badge `bottom`
  to that banner's rendered height so the two bottom edges align.
- Everything else about the badge stays (size ~0.13, black keyline).

## Issue 4 — Chanel popout image: stop over-deliberating

The Chanel bag crop used last time (`sources/popout-chanel-bags.jpg`) was not
good. Do NOT burn the session on sourcing it — **any generic real image of a
Chanel bag, or of a woman with a Chanel bag, is fine.** There is already
`sources/chanel-bags-shop-aedea4d4.jpg` in the repo (unused) — try it first.
If it's no good, grab the first decent real one: news og:image → Commons →
Openverse → Bing murl. Credit the URL, tag it, move on. Same rule applies to
any other popout still: first decent real image wins, no long deliberation.

## Keep (everything else)

- Clean-tabloid grade (contrast 1.12 / saturation 1.08, fade_gradient, NO
  deep-fry, NO hue-clamp). No Fallon/rizzler photos, no stock stand-ins for
  named people.
- Popout sticker mechanism (`circle_inset` + `--photo2`, sticker at cx .76 /
  cy .30 so it clears the badge; ring color `#FD2EFF`). The Mossad seal popout
  is the model — keep the seal as-is.
- The 4 captions: "Chester Stone joins mossad for 3 racks", "Chester stone
  buys his bitch 20 Chanel bags", "Chester Stone wanted for double homicide",
  "Chester Stone crashes out and smacks his baby mama ouch" — re-wrap the
  lines per Issue 1.2, don't change the words.
- The variation matrix: render across the 6 styles (rg-meme worldmap badge,
  rg-meme-computer CRT badge, rg-meme-nobadge, rg-meme-45, rg-meme-popout,
  rg-meme-45-popout) via the manifests in `manifests/` (batch is one
  style-per-run — loop the manifests). Popouts only where a second pic lands
  the joke (chanel bags, baby mama; mossad seal stays).
- Real stills of Chester Stone: `sources/chester-stone-*.jpg/png` (hi-vis hat,
  GMFD hat, face, face2).

## Verify + deliver

- Re-render ALL 15 items (edit the style JSONs + manifests, keep `out/`
  gitignored — never commit `out/`).
- vision-verify EVERY render: every headline line verbatim, masthead/banner
  text, footer; check no line is clipped at the sides and the badge/banner
  bottom edges align.
- Show a before/after comparison on the mossad meme (old vs new) — that one
  must go from "great" to "perfect": bigger headline, thinner stroke, real
  banner density on the left, badge flush right + bottom-aligned.
- Commit and push the style/manifest/source changes when done.
