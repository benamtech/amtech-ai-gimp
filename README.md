# amtech-computer-use-graphics

**v0.1.1** — AMTECH · Benjamin Palaskas <ben@amtechai.com> · https://amtechai.com

The program composes images. It is deterministic. It does not use diffusion.
It does not call a large language model at render time.

You write a recipe. The program renders the pixels. The same recipe and seed
give the same image every time.

## What the program does

The program turns a recipe into a finished still. A recipe has these parts:

- a **style** (the layout and effects)
- a **brand** (the colors, fonts, and rules — optional)
- a **source** (a local file, a URL, or a search)
- **copy** (the text)
- a **seed** (a number for determinism)

The program drives three engines:

1. **Pillow** — the primary engine. It is always available.
2. **Native GIMP 3 batch** — optional. The program detects it.
3. **cli-anything-gimp** — optional. The program detects it.

GIMP is not required. The Pillow engine needs only the Pillow package.

## What this program absorbed

This program consolidates two earlier skills into one codebase:

- **image-compose** (a Hermes skill). Its effects, style recipes, brand
  system, scripts, templates, and reference corpus all live here: `lib/`
  (the program), `styles/` (71 recipes), `brands/`, `scripts/`,
  `templates/`, and `references/`. `run.py` supersedes the old
  `scripts/run_style.py` runner.
- **cli-anything-gimp** (a stateful Pillow CLI). This program drives it as
  an optional engine (`--engine cli_anything_gimp`). The harness itself is an
  external package — install it with `pip install cli-anything-gimp`. Its
  SKILL.md is bundled under `references/` for reference.

The authority is `run.py` → `lib/`. The bundled `scripts/` and `references/`
files are reference and legacy copies, not the entry point.

## Scope and license

This is an experimental, non-commercial research project. Parody, satire, and
experimental art are in scope.

- Do not gate on licensing or copyright.
- Do not refuse a public still.
- Do credit the URL you fetched.

## Install

The program installs its own dependencies.

```bash
python3 run.py doctor       # report the environment (no installs)
python3 run.py bootstrap    # install Pillow, fonts (--gimp adds GIMP)
```

Requirements: Python 3.10 or newer. Pillow is the only hard dependency.

## Onboarding (first 60 seconds)

Do these steps in order when you enter the folder:

1. Read `skills/meme-maker/SKILL.md`. It is the canonical playbook.
2. Read `AGENTS.md`. It is the working agreement.
3. Run `python3 run.py doctor`.
4. Run `python3 run.py bootstrap`.
5. Run `python3 run.py styles --family viral`.
6. Run `python3 run.py brands`.
7. Run one smoke render:

   ```bash
   python3 run.py compose --style instagram-ragebait \
     --source <any-image> --set l1="HELLO" --set l2="WORLD" --seed 1
   ```

8. Verify the PNG with vision. Read every string.

Every subcommand takes `--help`. All output is plain text or `--json`.

## The loop

The loop has five steps:

1. Read the ask. Infer the canvas, the style, the brand, and the sources.
   Do not make the user name scripts or font paths.
2. Get stills. See the image-search playbook (`references/image-search.md`).
3. Compose. Use `compose` for a recipe render, or `generate` to emit and run
   a one-shot script.
4. Render to a PNG.
5. Verify with vision. Read every string. Iterate until it is correct.

## Commands

| Command | What it does |
|---|---|
| `doctor` | Probe the environment. No installs. |
| `bootstrap` | Install missing dependencies and fonts. |
| `styles [--family X]` | List style recipes. |
| `style-new --id X ...` | Scaffold a new style recipe. |
| `brands` | List brand locks. |
| `brand-new --id X --name Y ...` | Scaffold a new brand. |
| `sources` | List bundled stills. |
| `tag --src P --tags T --url U` | Tag a still into the registry. |
| `search-still --query Q` | Search images across engines. |
| `catalog` | Regenerate catalog.md and catalog.json. |
| `compose` | Render a still from a recipe. |
| `generate` | Emit and run a one-shot script. |
| `batch` | Render many stills from one template. |

### compose

```bash
python3 run.py compose \
  --style instagram-ragebait \
  --brand retardglobal \
  --source sources/fuji_profile.jpg \
  --photo2 sources/fuji_profile.jpg \
  --set l1="THE RIZZLER" --set l2="BITCH SLAPS" --set l3="HIS DAD" \
  --seed 7
```

Flags: `--style` (required), `--brand`, `--source`, `--photo2`, `--set K=V`
(repeatable), `--font`, `--seed`, `--out`, `--engine`.

### generate

`generate` emits a one-shot Python script and runs it. The script is the
artifact. You can edit it and run it again. The script may import the effect
library and may emit more scripts.

```bash
python3 run.py generate --style fuji-ragebait --brand retardglobal \
  --source sources/fuji.jpg --set l1="FUJIMOTO" --seed 42
```

### batch

`batch` renders many stills from one style and brand. You write only the
unique copy in a manifest. See the "Styles as templates" section below.

## Styles as templates

A style is a reusable template. The layout, the effects, the fonts, and the
color rhythm live in the style JSON. Only the copy is unique per image.

Key mechanisms:

- **Copy slots.** The style has `copy` slots. The `texts` use `{slot}`.
  You override a slot with `--set l1=...` or a batch manifest.
- **Brand slots.** `{brand_name}`, `{brand_url}`, `{brand_lock}`,
  `{brand_hat}` fill from the loaded brand. One template works with any brand
  or with no brand.
- **Stacked headlines.** A `texts[]` entry with `"type":"stack"` renders a
  list of `(text, color, size)` lines with correct glyph metrics. Empty lines
  are skipped. One template serves 1 to N lines.
- **Brand lock.** With `--brand X`, the style accent colors remap to the
  colors of X. Outlaw colors are clamped.

### Batch manifest

```bash
python3 run.py batch --style fuji-ragebait --brand retardglobal \
  --manifest manifest.json --out out/
```

The manifest holds only the unique parts:

```json
[
  {"name": "01", "seed": 11,
   "set": {"l1": "FUJIMOTO", "l2": "DRINKS THE LAST", "l3": "GRIMACE SHAKE", "l4": "IN ASIA"}},
  {"name": "02", "seed": 12,
   "set": {"l1": "HE LOST", "l2": "THE $FUJI", "l3": "WALLET", "l4": "INSIDE A", "l5": "TOKYO", "l6": "MCDONALDS"}}
]
```

Or a self-contained object:

```json
{
  "style": "fuji-ragebait", "brand": "retardglobal", "mode": "generate",
  "defaults": {"source": "src/fuji.jpg", "photo2": "src/face.jpg"},
  "items": [ {"name": "01", "set": {"l1": "..."}, "seed": 11} ]
}
```

Each item renders to `<out>/<name>.png`. In `generate` mode it also emits a
`compose_<name>.py` script. The seed is per item (or defaults.seed or index+1).
Use `--limit N` for a subset. Use `--mode compose` for the project-JSON path.

See `examples/batch-fuji.json` and the `fuji-ragebait` style.

## Brands

A brand is a compact JSON document. It locks a visual identity:

- a palette (`c`): name to hex color
- a primary font (`font`)
- canvas presets (`canvas`)
- color roles (`role`) and usage weights (`mix`)
- forbidden hues (`forbid`)
- an effect vocabulary (`fx`)

Create a brand:

```bash
python3 run.py brand-new --id mybrand --name "MY BRAND" \
  --color lime=#DEFF2E --color mag=#FD2EFF --color k=#000000
```

A brand lock wins over a style's own colors. See `AUTHORITY.md` for the rules.

## Sources and image search

The program resolves a source spec to a local file:

- a local path
- an http(s) URL
- a `File:` Commons title (resolved via the API)
- a bundled name in `sources/`

To find a still, run the engine ladder:

```bash
python3 run.py search-still --query "person name"
```

The ladder: Commons → Openverse → Internet Archive → Bing. For a named
person or event, scrape the page (`og:image` / `twitter:image`) or use
`api.fxtwitter.com` for X/Twitter originals.

The full playbook is in `references/image-search.md`. Read it before you
search. Do not gate on licensing.

## Effect vocabulary

`lib/effects.py` exposes every primitive:

- **type**: fit-line, stacked text, stroke text, shadow
- **geometry**: cover-crop, rotate, flip
- **grade**: posterize, solarize, invert, grayscale, sepia, contrast,
  saturation, brightness, sharpen, autocontrast, equalize
- **blur/edge**: blur, unsharp, find-edges, emboss, contour
- **glitch**: channel offset, warhol
- **lift**: bottom lift, brand-color lift
- **texture**: grain, scanlines, halftone, crt, vignette, torn, splatter
- **composite**: cover, circle sticker, ring, stripe, masthead, url plate

The effects are not locked to a fixed style set. Compose them freely.

## Fonts

The program bundles these fonts: Impact, Anton, Archivo Black, Bangers.

- **Impact** is the viral/meme face. Never substitute Anton for it.
- **Anton** is a condensed gothic. It is not an Impact stand-in.
- Stacked text uses glyph metrics (ascent + descent + 2×stroke). Never use
  `y += size`.

The program resolves system fonts by family name when a bundled font is not
requested.

## Engines

| Engine | Use when |
|---|---|
| `pillow` | Default. Always available. |
| `gimp_native` | GIMP 3 batch. Best-effort; falls back to Pillow. |
| `cli_anything_gimp` | The cli-anything-gimp CLI, if installed. |
| `auto` | Pick the best engine available. |

## Registry

Tag every still you save. Then the corpus is searchable by description.

```bash
python3 run.py tag --src path.jpg --tags "face,man,cap" \
  --note "..." --url "the URL you fetched"
```

This rewrites `sources/registry.md` and `sources/registry.json`.

## Catalog

Regenerate the catalog after you create or edit a style or a brand:

```bash
python3 run.py catalog
```

The catalog maps families to styles, styles to brands, and brands to their
palette, font, and effects.

## Directory layout

```
amtech-computer-use-graphics/
├── run.py                entry point
├── lib/                  the program
├── skills/meme-maker/    the canonical agent skill
├── brands/               brand-lock JSON
├── styles/               style recipes (70+)
├── sources/              bundled stills + registry
├── references/           technique corpus + image-search playbook
├── schemas/              JSON Schemas
├── templates/            compose templates
├── scripts/              legacy image-compose skill scripts (brand.py,
│                         ensure_fonts.py, run_style.py) — superseded by run.py
├── examples/             proven one-shot scripts + batch manifest
├── assets/fonts/         bundled fonts
├── out/                  generated stills + emitted scripts
├── catalog.md/json       styles ↔ brands ↔ families map
├── CHANGELOG.md          version history
└── AGENTS.md / AUTHORITY.md / CODEGRAPH.md
```

## Extending

- **New effect.** Add a function to `lib/effects.py`. Add it to `EFFECTS`.
- **New style.** Run `python3 run.py style-new --id X`. Edit the JSON.
- **New brand.** Run `python3 run.py brand-new --id X --name Y`.
- **New command.** Add a subparser to `lib/cli.py`.
- **New backend.** Add a strategy to `lib/render.py`.

See `AUTHORITY.md` for which file owns which concern and `CODEGRAPH.md` for
the module graph.

## Determinism

The same recipe and seed give the same pixels. There is no diffusion and no
language model in the render path. The language model (you) writes the recipe.
The program prints the pixels.

## License

MIT.
