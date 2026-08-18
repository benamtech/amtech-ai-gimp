# RETARD GLOBAL — Meme Factory

Drop in copy + images, get brand-locked Instagram memes. One format, hundreds
of stills, fully deterministic (same recipe + seed = same pixels).

## The format

Every RG meme is the same card (1:1 `rg-meme`, or 4:5 `rg-meme-45`). The exact
colors below were reverse-engineered from the reference pixels — the full spec
(with pixel evidence) is `docs/RG-FORMAT-SPEC.md`:

1. **Clean photo** — a real still, lightly graded (contrast/saturation only, no
   deep-fry, no hue-clamp).
2. **Bottom fade** — a smooth fade-to-black in the lower half (`fade_gradient`)
   so the headline reads. Not a box; a gradient.
3. **Masthead** — top-left magenta (`#FD2EFF`) block, text-only wordmark lock:
   **lime** `RETARD GLOBAL` + **white** `RETARDGLOBAL.COM`. No logo PNG.
4. **Headline** — stacked Impact, lime `#DEFF2E`, thick black stroke, **large and
   tightly stacked** (first line ~130px, rest ~110px, lines "touch"). The block
   fills from its top down to just above the footer.
5. **Footer** — `RETARDGLOBAL.COM` in **white** (not cyan), centered bottom, with
   equal space above and below.
6. **Corner logo** — the world-map logo (`assets/logos/logo-worldmap.png`, or
   the computer CRT logo) pasted top-right, ~13% width, its bottom edge aligned
   with the masthead banner's bottom edge, black keyline.

There is no other format. "Wanted for double homicide" and "starts taking
Ozempic" are the same meme with different words and a different photo.

## Quick start (single meme)

```bash
python3 run.py generate --style rg-meme --brand retardglobal \
  --source sources/the-rizzler.jpg \
  --set l1="THE RIZZLER" --set l2="STARTS TAKING" --set l3="OZEMPIC" \
  --seed 7
```

## Bulk (10s–100s of captions)

Write one caption per line (optionally `| image | image2 | @style`):

```
THE RIZZLER starts taking OZEMPIC | the-rizzler.jpg
Chester Stone wanted for double homicide | chester-stone-face.png
```

Then:

```bash
python3 run.py meme --copy captions.txt --out out/rg
```

- The meta-generator wraps each caption into headline lines, resolves images,
  and emits a per-item one-shot script + PNG.
- Missing images resolve via a subject→image map, or `--find-images`
  (best-effort search):

```bash
python3 run.py meme --copy captions.txt --images images.json --find-images --out out/rg
```

`images.json` maps subject → still (path/URL), matched case-insensitively as a
substring of the caption:

```json
{ "the rizzler": "the-rizzler.jpg", "chester stone": "chester-stone-face.png" }
```

Two images per caption stitch side-by-side into the photo area (driven by image
count, not copy).

### Mass variation (the cross product)

For "a ton" of memes from one captions file — every caption rendered across
multiple styles AND multiple seeds (masthead lime/orange + texture variety):

```bash
python3 generate_memes.py captions.txt --images images.json \
  --styles rg-meme,rg-meme-45,rg-meme-popout --seeds 3 --out out/rg-batch
```

`images.json` maps a subject substring to a still, or to `[still, popout_still]`
(the second still feeds the popout styles). Popout styles skip automatically
when no second still is present. Deterministic seed per (caption, style, seed).
See `examples/captions-rg.txt` + `examples/images-rg.json`.

## Templates, looks, canvases

- `rg-meme` — 1:1 (Instagram feed). The default.
- `rg-meme-45` — 4:5 portrait. Same grammar.
- `rg-banner` — 1920×675 RETARD wordmark banner. It **uses the bundled banner
  assets** (`assets/banners/banner-lime.png` / `banner-orange.png`, the real
  3000×1055 wordmark + serif-footer stills) as its `source`; the seed picks
  lime vs orange. No re-rendered text — the actual asset is the output.

## Brand assets (bundled, deterministic)

The brand's real image assets live in the repo so scripts can use them without
re-fetching:

```
assets/
├── logos/
│   ├── logo-worldmap.png   # 8-bit world map + "RETARD GLOBAL" pixel text (lime field, black art)
│   └── logo-computer.png   # CRT monitor + lime globe + big black "R" (no text)
└── banners/
    ├── banner-lime.png     # RETARD wordmark + serif footer on hi-vis lime (3000×1055)
    └── banner-orange.png   # same, orange retro variant
```

The meme templates paste a **corner logo badge** (`logo_badge` in the style's
`pillow` block: `asset`, `corner`, `size`, `margin`, `bottom`) — default the
world-map logo top-right, bottom-aligned to the masthead. `rg-banner` pulls the
banner asset via a style-level `source` (`{"choices": [...]}`, seed-sampled).

Looks live in the **technique catalog** (`run.py techniques`), not as separate
templates:

- `clean-tabloid` — the default grade (what rg-meme references).
- `deep-fried-ragebait` — optional grit look (clamp hues + anaglyph + grain).
  Reference it from a one-shot or a future style when a loud/glitchy meme is
  wanted.

Named look / canvas = `--style <id>`. If none is named, use `rg-meme`.

## Sourcing real stills (never stock stand-ins)

Named faces are real stills. Ladder (see `references/image-search.md`):
news `og:image` → fxtwitter `?name=orig` → Bing `murl` → Commons.

- The Rizzler (Christian Joseph) → `sources/the-rizzler-origin.jpg` (iconic
  origin "rizz face"), `sources/the-rizzler-knicks.jpg` (hand-on-chin at a
  Knicks game), `sources/the-rizzler-superhero.jpg` (red-carpet superhero
  costume). **NEVER use the Jimmy Fallon image.**
- Chester Stone → `sources/chester-stone-hi-vis-hat.jpg` (couch, yellow
  "RETARD" hat), `sources/chester-stone-gmfd-hat.jpg` (selfie in the hi-vis
  GMFD hat), `sources/chester-stone-face.png` (+ `-face2.png`, store triptych),
  from therealchesterstone.com.

Tag every fetched still so the corpus is searchable:

```bash
python3 run.py tag --src sources/x.jpg --tags "face,man,hat" --note "..." --url "the URL you fetched"
```

## Agent launch (the whole point)

An agent in this repo, given natural language:

> "i need a retardglobal style instagram meme
>  copy: 'Chester Stone joins mossad for 3 racks'
>  with image of chester stone [optional link]"

does:

1. Source a real still of Chester Stone (or use the link).
2. Wrap the copy into headline lines.
3. `python3 run.py generate --style rg-meme --brand retardglobal --source <still> --set l1=... --seed N`
4. `vision_analyze` the PNG; iterate until every string reads.

Deterministic, reproducible, no flags named by the human.
