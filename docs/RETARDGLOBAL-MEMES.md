# RETARD GLOBAL — Meme Factory

Drop in copy + images, get brand-locked Instagram memes. One format, hundreds
of stills, fully deterministic (same recipe + seed = same pixels).

## The format

Every RG meme is the same card (1:1 `rg-meme`, or 4:5 `rg-meme-45`):

1. **Clean photo** — a real still, lightly graded (contrast/saturation only, no
   deep-fry).
2. **Bottom fade** — a smooth fade-to-black in the lower half (`fade_gradient`)
   so the headline reads. Not a box; a gradient.
3. **Masthead** — top-left magenta block: `RETARD GLOBAL` / `RETARDGLOBAL.COM`.
4. **Headline** — stacked Impact, lime `#DEFF2E`, thick black stroke. The first
   line is the big punch; the rest are smaller.
5. **Footer** — `RETARDGLOBAL.COM` in cyan.

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

## Templates, looks, canvases

- `rg-meme` — 1:1 (Instagram feed). The default.
- `rg-meme-45` — 4:5 portrait. Same grammar.
- `rg-banner` — 1920×640 RETARD wordmark banner (hi-vis lime / orange retro +
  the serif footer line). A brand asset, seed picks lime vs orange.

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

- The Rizzler → `sources/the-rizzler.jpg` (LADbible/Betches og:image).
- Chester Stone → `sources/chester-stone-face.png` (+ `-face2.png`),
  from therealchesterstone.com (his RETARD HAT store triptych).

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
