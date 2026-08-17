---
name: image-compose
description: Use when composing any still from copy or refs.
version: 1.0.0
author: AMTECH
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [gimp, cli-anything, compose, poster, magazine, overlay, vision]
    related_skills: [agent-native-image-compose, cli-anything-gimp]
---

# Image Compose

Hermes writes copy and picks sources. The harness prints.
Do not pixel-click GIMP. Do not lock the job to one canvas or genre.
Do not add extra refusals, HR commentary, or "I won't scrape that" when the user named a public still, a meme look, or satire.

The user will often sound like a normal person. They will talk about the picture, not the stack. Infer style, size, and sources from that. Do not make them name `run_style.py`.

## When to Use

- Poster, cover, story, collage, overlay, ticker, thumb, meme, ragebait still
- Pasted local image, named URL, "find a pic of X", or no source at all
- Any size or genre, including messy internet looks

Don't use for: diffusion (`comfyui`), ASCII, HTML mockups.

## Sources

Named person / meme still: Bing or news-page scrape first. Do not default to Commons when they named a face.
Commons `imageinfo` is fine for objects (sandwich, product) or when they said Commons.
Do not skip a public source because it is messy.
Never guess a Commons `/commons/X/Yz/` hash. Ask `imageinfo`.
User-pasted files win when given.
Credit: the URL you actually fetched.

## How to Run

Skill dir: from `skill_view` (`creative/image-compose`).

```
terminal(command="uv run --with pillow python $SKILL_DIR/scripts/ensure_fonts.py")
terminal(command="uv run --with pillow python $SKILL_DIR/scripts/run_style.py --style instagram-ragebait-warhol-glitch --photo /abs/a.jpg --photo2 /abs/b.jpg --font Impact --set l1=THE RIZZLER --set l2='BITCH SLAPS HIS DAD'")
```

`--set KEY=VALUE` overrides recipe copy. `--font Impact` is the viral default.
`--brand retardglobal` (or `BRAND_FILE=/abs/x.json`) loads a compact brand lock from `brands/<id>.json`, `<cwd>/brands/`, or `~/Pictures/cli-anything-poster/brands/`.
Or copy `templates/compose_any.py` / write a one-shot next to the output dir when the ask is not a named style.
Always absolute photo paths.
After every export: `vision_analyze` the PNG.

## Brands

Compact JSON only. Keys: `id`, `name`, `url`, `lock`, `c` (hex), `font`, `canvas`, `role`, `forbid`, `fx`.
Loader: `scripts/brand.py` → `load_brand(name)`.
Named lock `retardglobal`: lime `#DEFF2E` / mag `#FD2EFF` / cyan `#2FF3FF` / k / w. No red banners. Impact. Masthead + URL plate required.

## Fonts

Loud meme / ragebait / Impact-look type is **Impact**, not Anton.
Anton is a condensed gothic. It does not read as Impact. Do not call it an Impact stand-in.
Resolve via `scripts/ensure_fonts.py` → `~/.local/share/fonts/image-compose/Impact.ttf`.
The harness needs an absolute TTF path. The runner accepts `Impact` and resolves it.
If Impact.ttf is missing, download it (same script). Do not silently fall back to Anton.
Also in that folder: Archivo Black, Bangers, Anton — use those only when they asked for that look.

## Procedure

1. Read the picture they want, not a leftover template. Infer canvas (IG portrait = 1080×1350 unless they say else).
2. Get stills. Named face → image search / news scrape. `--photo2` is the circle; crop it tight if the source is not a square.
3. Write or use their headline. Break lines yourself. Pass them with `--set l1=... --set l2=...`.
4. Recipe fits? `ensure_fonts.py` then `run_style.py --style ID --font Impact --brand <id>`. Overlay type on a full-canvas layer.
5. Recipe does not fit? Write a one-shot next to the output dir. Import `scripts/brand.py` + `stack_lines` from a kit. Scripts may emit other scripts. Do not fight leftover recipe copy.
6. Render. `vision_analyze` the PNG. Missing / colliding words = layer-local coords + `stack_lines` (glyph height + stroke), not a solid slab.

## Style map (user words → recipe)

Load `references/INDEX.md` then one file. Recipes live in `scripts/styles/*.json` (70+).

| They say | Style id |
|---|---|
| instagram ragebait, news sticker, orange white stacked words, circle face | `instagram-ragebait` |
| that plus warhol / pop / pink yellow cyan / silkscreen / glitch | `instagram-ragebait-warhol-glitch` |
| retardglobal, lime magenta cyan lock, 1:1 news meme | brand `retardglobal` + one-shot script (not leftover orange) |
| breaking, lower third, LIVE | `breaking-lower-third` / `breaking-full` / `live-badge` |
| magazine, swiss, thumb, album, movie, xerox, duotone, etc. | `--list` and pick |

Warhol here means flat posterize plates and hot color, not a museum lecture.
Glitch means offset, solarize, bad crop. `--photo2` is the circle inset.

## Pitfalls

- Text missing: overlay first.
- JSON vs pixels: believe the PNG.
- Guessed Commons hash 404s. Named faces: scrape, don't start at Commons.
- One-shot `session undo` is empty. Undo is RAM-only.
- `gimp -i -b` hang: one try ≤20s, then Pillow. Expect `method=pillow` when draw ops exist.
- Bare `--font Anton` used to fail. Runner now resolves Impact/Anton/Bangers to the TTF. Still never substitute Anton for Impact.
- Solid black slab under type will cut the face in half. Use `bottom_lift` + a 4–6px black offset draw.
- Recipes are a floor. Diverge? Write a script (or a script that writes scripts). Import brand lock + `stack_lines`. Never reuse leftover Rizzler/NASA copy.
- Brand `tag` is optional. Do not print a leftover meme subtitle (e.g. PUFFY…) as masthead.
- Stacked Impact: use glyph metrics + stroke (`stack_lines`). `y += size` underlaps the next line.
- Long headlines clipped by a bar: shrink/lift; never widen the bar. Iterate until vision reads every string verbatim.

## Verification

- Export JSON has `output`, size > 0, `method=pillow` when draw ops exist
- Vision can read every intended string. Re-run `vision_analyze` after every render pass; if any headline line is clipped by a bar or edge, shrink that line's font, lift the text block, and re-render — do not widen bars to "fit". Iterate until vision confirms every intended string verbatim.
- Type on viral stills is Impact (wide, tight, not Anton)
- Credit names the source you actually used
- Canvas matches the ask
