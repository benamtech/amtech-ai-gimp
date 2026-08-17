# Changelog

All notable changes to amtech-computer-use-graphics are tracked here.

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
- Docs (`skills/meme-maker/SKILL.md`, `AGENTS.md`, `README.md`) document the
  template + batch workflow and the "write captions, not scripts" contract.

## [0.1.0] — initial

- Deterministic non-generative image composer: Pillow (primary), native GIMP 3
  batch (optional), cli-anything-gimp CLI (optional).
- Brand-lock documents, style recipes (70+ seeds), source acquisition
  (local → URL → Commons API → web search), registry tagging, catalog,
  `compose` (project-JSON) and `generate` (script-of-scripts) paths.
