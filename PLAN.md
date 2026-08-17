# RETARD GLOBAL — Instagram Meme Factory (final plan + decisions)

Goal: a drop-in factory for RETARD GLOBAL Instagram memes. Drop in copy (1 line
or 1000) plus images (links or subject names), get brand-locked stills 1:1 with
the reference examples in `/home/georgej/Desktop/retardglobal-assets/`.

## The one template (not per-copy-type)

Decision (after two rounds of correction): there is exactly ONE meme format.
"Chester Stone wanted for double homicide" and "The Rizzler starts taking
Ozempic" are the SAME meme — one layout, one brand grammar. The copy is just
copy; the images are just images. No semantic classification, no per-copy-type
templates.

The format = **example 4** (clean photo + headline over a subtle bottom
gradient) + **retardglobal branding** (magenta masthead, lime Impact headline,
cyan footer):

- clean photo (mild contrast/saturation — NOT deep-fried, NOT glitched)
- smooth fade-to-black in the lower half (`fade_gradient`) — NOT a hard box
- top-left masthead "RETARD GLOBAL / RETARDGLOBAL.COM" on magenta
- stacked lime Impact headline (first line big = the punch), black stroke
- footer "RETARDGLOBAL.COM" (cyan)

Variety comes from the copy + image + seed (grain), plus a named canvas
(1:1 vs 4:5) or a named look — never from the meaning of the sentence.

## Deliverables (what exists now)

Brand (`brands/retardglobal.json`, superset):
- palette + orange banner-only color, canvas presets, banner/footer/logo
  metadata, recurring cast, template map (meme / meme_45 / banner).

Styles (family `retardglobal`):
- `rg-meme` (1080x1080) — the canonical template.
- `rg-meme-45` (1080x1350) — portrait canvas variant.
- `rg-banner` (1920x640) — the RETARD wordmark banner (lime/orange + serif footer).

Techniques (the catalog, brand-agnostic):
- `clean-tabloid` — the default grade (referenced by rg-meme / rg-meme-45).
- `deep-fried-ragebait` — optional grit look (kept in the catalog, not default).

Engine:
- `lib/effects.py:fade_gradient` — new smooth bottom-fade effect (bottom_lift
  draws sparse bands; fade_gradient draws contiguous rows = smooth).
- `lib/compose.py` — a style may now declare `"technique": "<id>"`; its effect
  pipeline is inlined as the base filters. This is how the technique catalog
  feeds rendering.
- `lib/meme.py` + `run.py meme` — the meta-generator: captions + images →
  wrapped headline lines + stitched pairs → batch (mode=generate, per-item
  one-shot scripts).

## The agent-launch contract

Anyone's agent, inside this repo, can be told:

    "i need a retardglobal style instagram meme
     copy: 'The Rizzler starts taking Ozempic'
     with image of chester stone [<optional link>]"

and it will: source a real still if no link is given → wrap the copy → render
`rg-meme` → vision-verify. No script names, no font paths, no harness talk.
Full recipe in `docs/RETARDGLOBAL-MEMES.md` + `skills/computer-use-graphics/SKILL.md`.

## Decisions log (why, so future edits don't undo it)

1. ONE template. Rejected the multi-archetype design (breaking/wanted/quote/vs)
   — the user: copy types are not different templates.
2. Gradient, not black box. Rejected the solid black strip — the user: example 4
   uses a slight gradient.
3. Clean, not deep-fried. Rejected clamp_hues+color_split+grain as the default
   — the user: the photos aren't deep-fried. Kept deep-fried as an optional
   technique.
4. The grade lives in the technique catalog (`clean-tabloid`), referenced by the
   style via `"technique"` — the single most under-leveraged asset in v0.2.0.
5. Image sourcing: real stills only (never stock stand-ins). The Rizzler =
   LADbible/Betches og:image; Chester Stone = therealchesterstone.com store
   triptych. Both tagged into `sources/registry`.
