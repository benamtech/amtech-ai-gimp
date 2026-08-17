# Composite two or more stills

See: `image-compose/references/INDEX.md`
See: `image-compose/references/techniques-blend.md`
See: `image-compose/references/techniques-masks.md`

## Human idiom

A composite is one picture made from several photographs.
Forum consensus (r/photoshop, years of critique): match lighting, match perspective, match color/tone. If those three fail, no blend mode will save it.

Also match: sharpness, grain, and the implied lens. A wide lens and a long lens in one frame look fake.

## Procedure (agent)

1. Name the light. One key direction. If sources disagree, grade the odd one before you stack.
2. Name the horizon / vanishing. If horizons fight, crop or rotate the guest (`filter add rotate` or Pillow).
3. Match mean brightness and saturation on the guest (`filter add brightness|contrast|saturation` or a Pillow pre-pass).
4. Place with `layer set offset_x/offset_y`. Negative offsets crop.
5. Soften the join. The harness has no mask. Workarounds:
   - pre-cut a PNG with alpha in Pillow
   - hide the seam under a `draw rect` panel
   - drop opacity on the guest
   - put the guest in a frame (inset) so a hard edge is honest
6. `vision_analyze`. Look for a halo, a second sun, or a horizon kink.

## Harness map

- Stack: `layer add-from-file` twice. Top index is 0 after each add.
- Fade: `layer set INDEX opacity 0.6`
- Grade: `filter add brightness -l N -p factor=1.1`
- Cannot: paint a mask, match 3D perspective, invent contact shadows that wrap a form.

## Codegraph

- `cli_anything.gimp.core.layers.add_layer`
- `cli_anything.gimp.core.export._composite_layer`
- `cli-anything-gimp/layer.set` `opacity` `mode` `offset_x` `offset_y`

## Sources

- r/photoshop "three most important things… lighting, perspective and colour" (multiple threads, 2017–2025)
- r/photoshop "match lighting, perspective, tone, color, textures"
- Phlearn / Aaron Nace composite lectures (human tutorial; we do not click PS)
