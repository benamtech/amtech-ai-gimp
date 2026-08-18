# Changelog

All notable changes to amtech-computer-use-graphics are tracked here.

## [0.2.1] — 2026-08-17

### Added — brand-asset overlays + mass generation

- `masthead_banner` effect (`lib/effects.py`): paste a bundled banner asset
  flush into a corner at a width fraction and return its rendered height, so a
  sibling element can bottom-align to it. Driven from a style's `pillow` block
  (`masthead_banner` + seed-sampled `masthead_banner_asset`).
- `logo_badge` / `corner_badge` now accept `bottom: "banner"` — a relative
  anchor that pins the badge's bottom edge to the rendered masthead-banner
  height instead of a hardcoded pixel offset, so alignment survives canvas and
  aspect-ratio changes.
- `generate_memes.py` — a mass-generator that renders the cross product of
  {captions} × {styles} × {seeds} as brand-locked stills (popout styles
  auto-skip without a second still). Sample inputs in `examples/`.

### Fixed — `compose` and `generate` now agree pixel-for-pixel

- `compose.prep_panel` wrote its intermediate panel as a lossy JPEG; it now
  writes a lossless PNG, removing the quality loss on sharp pixel-art edges
  (logos/badges) and the divergence from the lossless `generate` path.
- `library.emit_script` now emits the opt-in brand `clamp_hues` step (matching
  `compose`'s prep_panel order) and emits `masthead_banner`/`logo_badge`
  *before* the technique filters — they were emitted after, so brand-asset
  overlays graded inconsistently between the two paths.
- Result: `compose` and `generate` produce byte-identical output for the same
  recipe + seed, restoring the documented "same recipe == same pixels"
  invariant across both engines.

## [0.2.0] — 2026-08-17

### Added — universal technique catalog + design canon

- `techniques/` — a growing catalog of reusable, brand-agnostic effect
  pipelines (duotone marble, gold mandorla, vaporwave grid, xerox ghost,
  cosmic void, solarized specter, etc.), each tagged by image type / family /
  era / tags. `run.py techniques` searches it; `run.py technique-new`
  scaffolds a new entry; `run.py catalog` now indexes it. The catalog is meant
  to grow forever — every reusable look becomes a technique file.
- `lib/technique.py` — catalog loader/search/validate/create + schema
  (`schemas/technique.schema.json`).
- `lib/effects.py` — 11 new compositing/craft primitives promoted to the
  canonical library and registered in `EFFECTS`: `duotone`, `mosaic`, `xerox`,
  `relief`, `slice_glitch`, `color_split`, `waterline`, `tint`, `lead_lines`,
  `blend`, `perspective_grid`, `starfield`, `vgradient`.
- `references/design-canon.md` — a century of pre-AI graphic design
  (1930s–2010s movement map) + non-style-specific taste rules + boundary-push
  guidance + the reliability contract. Load this for "make it look good".
- `lib/design.py` — compositional taste checks: `hierarchy_ok` (headline must
  dominate), `palette_size_ok` (≤4 accent colors), `review_composition`
  (full taste review). `run.py review` now reports hierarchy + color count too.
- `lib/fonts.py` — `SYSTEM_SPECS` fallback for serif / sans-condensed /
  mono-bold faces via fontconfig, so brand banner footers resolve on a bare
  system without a hardcoded path.

### Changed — out-of-box agent usability + naming

- **Renamed the skill** `meme-maker` → `computer-use-graphics` (dir, name,
  plugin registration, and every reference). The program is not just memes:
  it is any hand-made graphic.
- **Human gives a vision, not a spec.** AGENTS.md + SKILL.md now lead with the
  contract: the user describes the picture ("an old punk zine", "clean and
  swiss"), the agent infers canvas / era / palette / type and never makes the
  user name a style, font, or flag. The loop now includes a "review, then push
  one axis further" step.
- `examples/batch-fuji.json` now points at bundled `sources/` (runnable on a
  fresh clone) instead of a personal Pictures dir.

### Removed — personal attribution

- Dropped the "George (georgej)" attribution from AUTHORS.md and all hardcoded
  `/home/georgej/...` paths (examples, references, notes). Everything is
  portable (`~`, `Path.home()`).

### Fixed

- `catalog.md/json` regenerated cleanly (no project-specific brand baked in).

## [0.1.2] — 2026-08-17

### Fixed — effect dispatch silently dropped params

`lib/render.py:_apply_filter` filtered out `bits`/`factor` from every effect's
kwargs before dispatching, so `posterize(bits=4)` and `contrast(factor=1.5)`
rendered as their defaults — a real correctness bug that also made seeded
"variants" look identical (the grade never actually changed). Effect dispatch
now goes through a single canonical path, `lib/effects.py:apply_filter`, which
signature-filters kwargs (pass through everything the effect accepts, drop only
what it doesn't). `render` and `library` share it, so the compose path and the
generated-script path agree exactly.

- `lib/effects.py`: added `filter_kwargs()` and `apply_filter()` (canonical
  dispatch); `library._filtered_kwargs` now delegates to it.
- `lib/render.py`: `_apply_filter` routes EFFECTS names through
  `effects.apply_filter` and keeps only the genuinely-legacy fallback names
  (`sharpness`, `smooth`, `detail`, `flip_h/v`, `rotate`, `resize`, `crop`,
  `box_blur`).
- `lib/compose.py`: `_eval` no longer swallows bad expressions as `0`; it
  raises with the offending expression (and added `round` to the eval namespace).

### Added — a design-rules layer (`lib/design.py` + `review` command)

Determinism is not taste. A new advisory review layer encodes rules for
combinations that actually look good, surfaced via `run.py review`:

- **contrast** — WCAG relative-luminance ratio; `legible(fg, bg, large=…)`.
- **harmony** — near-duplicate palette entries, forbidden-hue hits, and
  palette colors with no legible partner.
- **pairing** — a curated effect↔image-type table (portrait/sculpture/void/
  landscape/texture) with recommended + avoid lists.
- **variants** — `variants_distinct(a, b)` reports whether two resolved
  compositions differ on a *visible* axis (canvas/background/filters/copy/
  layout), ignoring noise-only effects (grain, glitch), so a seeded "variant"
  that only perturbs noise is correctly flagged as identical.

`run.py review --brand X` reviews a brand doc; `--style S [--brand B]
[--source …] [--image-type portrait|sculpture|void|landscape|texture] [--seed N]`
reviews a resolved composition. Docs (AUTHORITY.md, CODEGRAPH.md,
SKILL.md) updated.

## [0.1.1] — 2026-08-17

### Added — styles as reusable templates + batch automation

The headline feature: **styles now work as drop-in templates**, and a new
**batch** path renders dozens or hundreds of stills from a single manifest
where the LLM/agent writes only the unique parts (captions + data). This is
the "non-deterministic-scripts-first agentic programming paradigm": the
template (layout, effects, brand, fonts, color rhythm) is baked into a style;
the unique copy is a one-line-per-image override.

- **`batch` command** (`run.py batch`) + `lib/batch.py`: render N images from
  one `--style` (+ optional `--brand`) against a manifest of per-item copy
  overrides, sources, and seeds. Manifest is either a JSON list of items
  (`--style`/`--brand`/`--source` on the CLI) or a self-contained JSON object
  carrying `style`/`brand`/`defaults`/`items`. Each item renders to
  `<out>/<name>.png` (and, in `generate` mode, an emitted `compose_<name>.py`
  script). This is how you automate 10s/100s of images: write the captions,
  not the scripts.
- **Stacked headline blocks** in the style schema (`texts[]` with
  `"type": "stack"`): a list of `(text, color, size)` lines laid out with
  glyph metrics via `effects.stack_lines` — never `y += size`. This is what
  lets the `fuji-ragebait` style reproduce the stacked-Impact viral look from
  a JSON template instead of a hand-written script.
- **Brand-name/url/lock slots**: `{brand_name}`, `{brand_url}`, `{brand_lock}`,
  `{brand_hat}` are now auto-injected as copy slots whenever a brand is
  loaded, so a style's masthead/plate text can be brand-agnostic. A style is
  now genuinely reusable "with any brand or no brand."
- **Per-text anchor + stroke**: text blocks accept `anchor` (`la`/`lm`/`mm`/
  `rm`/…) and `stroke` + `stroke_color`, so masthead/plate/pill text can be
  positioned the way the viral stills require.
- **`lift_color`**: the `pillow.bottom_lift` op now honors a `lift_color`
  hex, so a brand lift (e.g. retardglobal lime lift) is expressible in a
  recipe instead of only in code.
- **`fuji-ragebait` style** (`styles/fuji-ragebait.json`): the canonical
  1:1 viral template (cover → warhol → brand lift → stripe → masthead →
  circle sticker → pill → stacked Impact headlines → url plate), parameterized
  so the same recipe renders the grimace/wallet/xerox/mcflurry stills with
  only copy overrides.
- **`examples/batch-fuji.json`**: a demo manifest reproducing the four
  Fujimoto stills from the one template.

### Changed

- `lib/compose.py`: `resolve()` now injects brand slots, resolves `stack`
  text blocks, and threads `anchor`/`stroke`/`stroke_color`/`lift_color`.
- `lib/render.py`: `_apply_draw_ops` renders `stack` and stroke-text ops.
- `lib/library.py`: `emit_script()` emits `effects.stack_lines` for stacks and
  respects `anchor`/`lift_color`, so generated scripts stay faithful.
- `lib/cli.py`: added the `batch` subcommand.
- Docs (`skills/computer-use-graphics/SKILL.md`, `AGENTS.md`, `README.md`) document the
  template + batch workflow and the "write captions, not scripts" contract.

## [0.1.0] — initial

- Deterministic non-generative image composer: Pillow (primary), native GIMP 3
  batch (optional), cli-anything-gimp CLI (optional).
- Brand-lock documents, style recipes (70+ seeds), source acquisition
  (local → URL → Commons API → web search), registry tagging, catalog,
  `compose` (project-JSON) and `generate` (script-of-scripts) paths.
