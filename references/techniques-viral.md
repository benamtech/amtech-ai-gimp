# Viral / ticker / ragebait grammar

See: `image-compose/references/formats.md`
See: `image-compose/references/INDEX.md`

## Human idiom

The cheap news still: red or blue urgency bar, BREAKING or LIVE, lower-third ticker, tight crop, short claim, high heat.
IG ragebait: NEWS pill, circle inset, giant stacked orange/white words.
Canva / Kapwing sell this as a meme template. Use the grammar as art.

## Type

Viral / meme / ragebait type is **Impact**. Not Anton. Anton looks like a movie poster, not a 2012 meme.
`scripts/ensure_fonts.py` installs `Impact.ttf`. Styles set `"font": "Impact"`.
`--font Impact` on `run_style.py`. Never silently swap Anton in.

## Layout

- Top or bottom bar, 64–96 px, `#c1121f` or `#0b3d91`
- Word BREAKING / LIVE / NEWS, 20–28 px, white
- Headline 36–64 px Impact, lines you wrap
- Ticker strip, 28 px, smaller type
- Hero photo full-bleed behind
- Optional circle inset (`--photo2`), LIVE pill, timestamp
- Warhol-glitch: posterize + RGB offset + yellow strip + magenta ring. No museum lecture.

## Contrast

Posterized skin eats orange type. Double-draw a 4–6 px black offset, then the orange.
Do not drop a solid black slab that chops the face. `bottom_lift` from ~0.36 is enough.

## Harness map

Overlay rects + text. Same overlay rule as every other poster.
`--set l1=... --set l2=...` overrides recipe copy so leftover NASA lines do not print.
Named person still: Bing / news scrape. Commons only for objects.

## Sources

- Canva / Kapwing breaking-news meme templates (layout only)
- Public posts that warn: a viral urgent claim is not proof
