# AUTHORITY.md — the authority map

Which file owns which concern, and the precedence order when two sources
disagree. This is the single source of truth for resolving conflicts in a
codebase that *generates* code at runtime.

## Concern → authoritative owner

| Concern | Owner | Notes |
|---|---|---|
| Brand identity (palette, font, forbid, fx) | `brands/<id>.json` | The compact brand doc wins over any style or script default. |
| Style / layout recipe | `styles/<id>.json` | A recipe is a *floor*, not a lock. A one-shot script may diverge. |
| Effect implementations | `lib/effects.py` | Canonical effect code. `lib/rg_kit.py` is a bundled legacy kit; prefer `effects`. |
| Effect dispatch (filters) | `lib/effects.py` `apply_filter()` | Signature-filtered kwargs; `render` and `library` both route through it. |
| Design rules (taste) | `lib/design.py` | Contrast, harmony, effect↔image pairing, variant distinctness. Advisory findings. |
| Font resolution | `lib/fonts.py` | Impact auto-downloads; others must exist (bundled or installed). |
| Brand loading/creation | `lib/brand.py` | Search order below. |
| Source acquisition | `lib/source.py` | Local → URL → Commons API → web search. |
| Render engine selection | `lib/render.py` | Pillow (default) → native GIMP 3 → cli-anything-gimp. |
| Script generation (self-modify) | `lib/library.py` | Emits one-shot scripts to `out/`, runs them. |
| Batch rendering (manifest-driven) | `lib/batch.py` | One style/brand template × N items → `<out>/<name>.png`. |
| CLI surface | `run.py` + `lib/cli.py` | One entry point, argparse + optional REPL. |
| Agent-facing playbook | `skills/meme-maker/SKILL.md` | What agent runtimes load. |
| Universal working agreement | `AGENTS.md` | Codex/Cursor/Aider/… read this. |
| Claude Code agreement | `CLAUDE.md` | Imports AGENTS.md. |
| Schemas (contracts) | `schemas/*.json` | brand, style, source, project, recipe. |
| Technique corpus | `references/*.md` | Routed via `references/INDEX.md`. |
| Capability matrix | `capability-matrix.json` | Effect/technique catalog + style-schema union (regenerated from references + styles). |

## Brand search order (first hit wins)

1. Explicit `--brand <path>` / `BRAND_FILE` env
2. `<cwd>/brands/<id>.json`
3. `<cwd>/*.brand.json`
4. bundle `brands/<id>.json`
5. legacy `~/Pictures/cli-anything-poster/brands/<id>.json`

## Font search order (first hit wins)

1. Absolute existing path (pass-through)
2. bundle `assets/fonts/<name>`
3. `~/.local/share/fonts/image-compose/<name>`
4. download (Impact only)

## Precedence rules when sources disagree

1. **A named face wins over a generic still.** If the user names a person,
   scrape a real still; never substitute a stock/Pexels face.
2. **User-passed file wins over everything.** A pasted/local path beats a URL,
   a search result, or a bundled source.
3. **Copy override (`--set l1=…`) wins over a recipe's default copy.** Leftover
   recipe copy (e.g. NASA / Rizzler / PUFFY lines) must never leak into a new
   job.
4. **A brand lock wins over a style's own colors.** If a style JSON sets
   `background` or a ring color but a brand is loaded, the brand's hexes and
   forbid list take precedence.
5. **The PNG wins over the project JSON.** If the exported pixels disagree
   with the saved state, trust the pixels (draw ops are render-time).
6. **`lib/effects.py` wins over `lib/rg_kit.py`.** `rg_kit.py` ships for
   backward compatibility with existing compose scripts; new code imports
   `lib.effects`.

## When to edit what

- New color/face/forbid → create or edit a `brands/<id>.json` (use
  `run.py brand-new --id ... --name ...`), then validate it.
- New layout/recipe → create a `styles/<id>.json` (use `run.py style-new`).
- Both brands and styles are authored, validated, and versioned in-repo; both
  are reusable inputs to `compose` and `generate`. Authoring them is a
  first-class use of this program, not a side effect.
- New effect primitive → add a function to `lib/effects.py`, then reference it
  from a style's `fx` list or a one-shot script.
- New design rule (contrast / harmony / pairing / variant distinctness) →
  add a predicate to `lib/design.py` and surface it in `review_resolved()`.
- New backend → add a strategy to `lib/render.py`.
- New agent runtime → add a manifest (see README § "Agent targets") and point
  it at `skills/meme-maker/SKILL.md`. Do not fork the skill body per runtime.
