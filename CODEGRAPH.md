# CODEGRAPH.md — module graph

How the program fits together: modules, import edges, and the
script-emits-script graph. Read before editing `lib/`.

## Entry point

```
run.py  ──>  lib/cli.py:main()  ──>  subcommand handlers (argparse)
```

`run.py` only adds the bundle root to `sys.path` and calls `main`. `lib/cli.py`
imports submodules lazily inside each handler, so `doctor`/`bootstrap` run even
without Pillow.

## Module tree

```
lib/
├── __init__.py    paths + version (ROOT, *_DIR constants, ensure_dirs)
├── brand.py       load/list/validate/create brands + hex helpers + palette
├── fonts.py       font resolution (bundled -> user dir -> download Impact)
├── source.py      source resolution (local -> URL -> Commons -> bundled)
├── search.py      multi-engine image search (commons_search, bing_image_search)
├── registry.py    image tagging -> sources/registry.{md,json}
├── catalog.py     styles/brands/families -> catalog.{md,json}
├── effects.py     THE effect library (type, geometry, grade, glitch, texture,
│                  composite) — the canonical primitives + apply_filter dispatch
├── design.py      design rules: contrast, harmony, effect↔image pairing,
│                  variant distinctness (advisory review; no Pillow)
├── render.py      engine abstraction (pillow | gimp_native | cli_anything_gimp)
├── compose.py     resolve() + build_project() + compose()  (project-JSON path)
├── library.py     emit_script() + generate()  (script-of-scripts path)
├── batch.py       render_batch() + load_manifest()  (manifest-driven bulk render)
└── bootstrap.py   doctor() + bootstrap()  (deps, fonts, GIMP)
```

## Import edges (dependency direction)

```
__init__  (no internal imports — always safe)

brand     -> __init__
fonts     -> __init__
source    -> __init__
search    -> __init__, source (commons_url)
registry  -> __init__
catalog   -> __init__, brand, style
style     -> __init__
effects   -> __init__, brand, fonts
design    -> __init__  (pure; no Pillow, no other lib deps)
render    -> __init__, effects
compose   -> __init__, brand, effects, fonts, render, source, style
library   -> __init__, effects, compose, source
batch     -> __init__, compose, library
bootstrap -> __init__, fonts
cli       -> __init__ (+ lazy imports of all the above)
```

`effects` is the leaf-most substantive module; everything that draws depends on
it. `compose` and `library` are the two orchestration layers; `render` is the
only module that talks to external engines (GIMP binary, cli-anything-gimp).

## The script-emits-script graph (self-modification)

```
recipe (style + brand + source + copy + seed)
        │
        ▼
compose.resolve()  ── deterministic sampling -> resolved dict
        │
        ├──(A)──► build_project() ──► render.render_project() ──► out/<id>.png
        │
        └──(B)──► library.emit_script() ──► out/compose_<id>.py   (standalone)
                        │
                        ▼
                 subprocess run  ──► imports lib.effects ──► out/<id>.png
```

- Path (A) = `compose` command: project-JSON driven, engines via `render`.
- Path (B) = `generate` command: emits a real, editable, re-runnable one-shot
  script; the script is the artifact and may itself import `lib.effects` and
  emit more scripts.

Both paths share `resolve()`, so they produce the same composition for the
same inputs.

## Data flow of a still

```
source spec ─► source.resolve() ─► local file
                                  │
                                  ▼
                       compose.prep_panel(): cover-crop + clamp_hues(brand)
                                              + pillow ops ─► panel.jpg
                                  ▼
                       build_project(): layers + draw_ops
                                  ▼
                       render.render_project(): pillow / gimp / cli-anything
                                  ▼
                       out/<id>.png   +  resolved dict (for emit_script)
```

## Where to add something new

- new effect primitive → `lib/effects.py` (function) + add to `EFFECTS` dict
  so filters and generated scripts can dispatch it.
- new filter name → ensure `render._apply_filter` and `effects.EFFECTS` know it.
- new design rule → `lib/design.py` predicate, surfaced via `review_resolved`.
- new backend → `lib/render.py` strategy + `engine` choice in `compose`.
- new command → `lib/cli.py` subparser + a handler.
- new style/brand → `run.py style-new` / `run.py brand-new`, then `run.py catalog`.
