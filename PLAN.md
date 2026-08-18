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

## Reverse-engineering round (the pixels, not a guess)

6. Masthead colors are DERIVED, not guessed (pixel-sampled from the reference
   JPGs): "RETARD GLOBAL" = **lime** `#DEFF2E`, "RETARDGLOBAL.COM" = **white**,
   on a **magenta** `#FD2EFF` block. Both text colors were flipped in earlier
   sessions. The masthead is **text-only** — the logo PNGs are NOT in the meme
   (they belong to `rg-banner` / standalone badges).
7. Footer = **white** `RETARDGLOBAL.COM`, not cyan. Cyan's brand role is
   cta/url/frame; the examples render the footer URL white on black.
8. The `compose` path's unconditional brand hue-clamp (`clamp_hues` in
   `prep_panel`) was the deep-fry bug — the `generate` path never did it, so
   the two paths disagreed. Fixed: gated behind an opt-in `"clamp_hues": true`
   style flag (default OFF), so clean is the default on both paths. The fried
   look remains opt-in via `techniques/deep-fried-ragebait.json`.

## Round 2 — text scale, tight stack, and the brand assets (user-corrected)

9. Headline is **large and tightly stacked**, not "first line huge, rest small
   with gaps". Impact's ascent+descent metrics add ~1.8× dead vertical space per
   line; `stack_lines` gained a `gap` param (bbox-height + 2×stroke + gap, so
   lines "touch") and a `fill` param (grow the block uniformly to fill the band
   down to the footer). Sizes: l1=130, l2+=110 (close in size — deliberately
   below the 1.5× hierarchy rule, per the user).
10. Every meme now embeds a **corner logo badge** — the world-map logo (or CRT
    computer logo) from `assets/logos/`, pasted top-right at ~13% width, its
    bottom edge aligned with the masthead banner's bottom edge.
    The masthead stays text-only; the badge is where the brand *assets* land.
11. **Never use the Jimmy Fallon image** of The Rizzler. Indexed non-Fallon
    stills: `the-rizzler-origin.jpg`, `the-rizzler-knicks.jpg`,
    `the-rizzler-superhero.jpg` (red-carpet costume).
12. All RG brand assets are now bundled in the repo (`assets/logos/`,
    `assets/banners/`) so scripts reference them deterministically instead of
    the external `retardglobal-assets/` dir. `rg-banner` uses the actual banner
    stills as its `source` (seed-sampled lime/orange) via a new style-level
    `source` field in `resolve()` — no more re-rendering the wordmark as text.

Full spec + pixel evidence: `docs/RG-FORMAT-SPEC.md`.
