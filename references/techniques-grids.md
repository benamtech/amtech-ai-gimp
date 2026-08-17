# Grids (Swiss, magazine, thirds)

See: `image-compose/references/INDEX.md`
See: `image-compose/references/techniques-type.md`
See: `image-compose/references/techniques-print.md`

## Human idiom

Swiss / International Typographic Style: a modular grid, sans type, few colors, flush-left rag-right, no decoration. The grid is the idea.
Magazine: 2–4 columns plus a baseline grid. Columns may merge. The baseline stays.
Photography: rule of thirds is a 3×3. Place the subject on a line or a cross. Leading lines pull the eye. Frame-in-frame holds a subject.

Build the grid before the content. Bones first.

## Agent translation

The harness has no guide objects that print.
You keep the grid in the script as numbers.

Example, 1080×1350 story:

- Margin 48
- Column width `(1080 - 48*2 - 24) / 2` if two columns and a 24 gutter
- Baseline 8 or 12 px. Snap every `y` to that step.
- Thirds: x = 360 / 720, y = 450 / 900

Place type and photo offsets on those numbers.
Do not center by habit.

Swiss poster: one axis of type, huge number or word, primary color field, photo as a rectangle on the grid — not a full-bleed romance crop unless the ask wants that.

## Harness map

- Photo crop = `offset_x` / `offset_y` plus a pre-resize in Pillow
- Columns = different `--x` values
- Baseline = arithmetic in the compose script
- Cannot: snap-to-guide, visible guide export

## Sources

- Poster House / SoDA talks on the Swiss grid
- r/graphic_design magazine dummy critiques (baseline first)
- Standard rule-of-thirds photography primers
