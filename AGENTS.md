# amtech-computer-use-graphics — AGENTS.md

A self-contained, deterministic, NON-generative image composer. It turns a
recipe (brand + style + source + copy + seed) into a finished still (PNG/JPG)
by driving Pillow (primary), native GIMP 3 batch (optional, auto-detected),
and the `cli-anything-gimp` CLI (optional). It installs its own dependencies
(GIMP, Pillow, fonts) and is fully agent-agnostic: no runtime-specific code.

## Onboarding (first 60 seconds)

When you first enter this folder, do these steps in order. Do not guess flags.

1. Read `skills/meme-maker/SKILL.md`. It is the canonical playbook.
2. Read `AGENTS.md` (this file). It is the working agreement.
3. Run `python3 run.py doctor`. It reports the environment. No installs.
4. Run `python3 run.py bootstrap`. It installs missing dependencies and fonts.
5. Run `python3 run.py styles --family viral`. It lists template styles.
6. Run `python3 run.py brands`. It lists brand locks.
7. Run one smoke render:

   ```bash
   python3 run.py compose --style instagram-ragebait --source <any-image> --set l1="HELLO" --set l2="WORLD" --seed 1
   ```

8. Verify the PNG with vision. Read every string. Fix and re-render if a
   string is missing or clipped.

Every subcommand takes `--help`. All output is plain text or `--json`.

## What this program is

- **An authoring tool for brands and styles, not just a composer.** Users and
  agents use it to *create and edit* brand-lock documents (`run.py brand-new`,
  `brands/<id>.json`) and style recipes (`run.py style-new`,
  `styles/<id>.json`) exactly as much as to render stills. New brands and new
  styles are first-class deliverables, validated against `schemas/`.
- **Deterministic.** Same recipe + seed = same pixels. No diffusion, no LLM
  in the render path. The LLM (you) writes the *recipe*; the program prints.
- **Self-modifying.** The `generate` command writes a fresh, runnable one-shot
  Python script to `out/` and executes it. Scripts are first-class artifacts:
  they can import the effect library, and can themselves emit more scripts.
- **Open-ended.** Not limited to a fixed style set. `styles/` holds 70+ seed
  recipes; any of them can be overridden or ignored, and new ones are trivial
  to author. The effect library (`lib/effects.py`) exposes every primitive.

## Bootstrap (run once)

```bash
python3 run.py doctor        # probe: python, pillow, gimp, fonts
python3 run.py bootstrap     # install missing deps (pillow, Impact font;
                             #   GIMP via apt/pacman if absent)
```

GIMP is *optional*. The Pillow render path is the stable default and needs
only `pillow`. Native GIMP 3 batch is used only when beneficial and detected.

## Core loop

1. **Read the ask** as a normal person describes a picture. Infer canvas,
   style, brand, sources. Do not make them name scripts or font paths.
2. **Sources**: local path, URL, Wikimedia Commons `File:` title (resolve via
   the `imageinfo` API — never guess the `/commons/X/Yz/` hash), or a
   web/image search for a named face/place/object. Never use stock stand-ins
   for a named person. Credit the URL you actually fetched.
3. **Compose** — one of:
   - `python3 run.py compose --style <id> --brand <id> --photo <src> \
     --set l1=... --set l2=... --seed 7`
   - or `python3 run.py generate --intent "..."` to emit + run a one-shot
     script you then edit freely.
4. **Render** to `out/<job>.png`. The export result reports the engine used.
5. **Verify** with vision (any agent's image tool). Every intended string must
   be readable; iterate until it is. Missing/colliding text = layer-local
   coordinates or a wrong text block — fix the script, re-render.

## Templates & batch (write captions, not scripts)

A style is a **reusable template**: layout, effects, fonts, and the color/size
rhythm live in the style JSON; only the copy is unique per image. `{brand_name}`,
`{brand_url}`, `{brand_lock}`, `{brand_hat}` slots auto-fill from any brand, and
`--brand X` remaps accent colors onto X's palette — so one template serves "any
brand or no brand." `texts[]` may use `{"type":"stack", ...}` for glyph-metric
stacked headlines (empty lines skipped).

For dozens/hundreds of images, drive `batch` with a manifest that carries only
the unique parts (per-item `set` of copy overrides + optional source/seed):

```bash
python3 run.py batch --style fuji-ragebait --brand retardglobal \
  --manifest manifest.json --out out/
```

`manifest.json` is a JSON list of `{"name", "set", "source?", "photo2?", "seed?"}`
(or a self-contained object with `style`/`brand`/`defaults`/`items`). See
`examples/batch-fuji.json`. Each item → `<out>/<name>.png` (+ an emitted
`compose_<name>.py` in `generate` mode). Deterministic per-item seed.

## Authoritative docs (load on demand — do not inline everything)

- `AUTHORITY.md` — the **authority map**: which file owns which concern, and
  the search order when sources disagree.
- `CODEGRAPH.md` — the **codegraph**: modules, import edges, and the
  script-emits-script graph. Read it before editing `lib/`.
- `skills/meme-maker/SKILL.md` — the open Agent Skills playbook (this is the
  file every agent runtime actually loads).
- `references/INDEX.md` — routing table into the technique corpus.
- `references/image-search.md` — the encoded image-search playbook (engines,
  endpoints, license stance, anti-patterns). Read before you search.
- `schemas/` — JSON Schemas for brand, style, source, project, and recipe.

## Rules (hard)

- Impact is the viral/meme face. Never substitute Anton. Anton is a condensed
  gothic; it is not an Impact stand-in.
- Stacked Impact text must use glyph metrics (ascent+descent+2×stroke), never
  `y += size` — underlapping lines collide.
- Draw text on a full-canvas overlay, not a small photo layer (layer-local
  coordinates clip). Negative offsets are valid and clip by design.
- No solid black slab that chops the subject. Use a bottom-lift gradient.
- Brand-locked jobs: read the brand JSON first; use its hexes and forbid list.
  A brand `tag`/`subtitle` is optional — never print a leftover meme subtitle
  as a masthead.
- The render path never invents pixels. If a filter or effect is unsupported,
  say so and use the Pillow equivalent — do not fake it.

## CLI reference

```
python3 run.py doctor                          probe environment
python3 run.py bootstrap                       install deps + fonts
python3 run.py styles [--family viral]         list style recipes
python3 run.py style-new --id x --family ...   scaffold a style recipe
python3 run.py brands                          list brands
python3 run.py brand-new --id x --name "..."   scaffold a brand
python3 run.py sources                         list bundled stills
python3 run.py compose ...                     deterministic render (seeded)
python3 run.py generate --intent "..."         emit + run a one-shot script
python3 run.py batch --style X --manifest M    render many stills from one template
```

Pass `--help` on any subcommand. All output is plain text or `--json`.
