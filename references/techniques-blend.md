# Blend modes

See: `image-compose/references/INDEX.md`
See: `cli_anything.gimp.core.layers.BLEND_MODES`
See: `cli_anything.gimp.core.export._blend_with_mode`

## Human idiom

GIMP docs and old "Focus Group" tutorials treat three modes as the basic kit: Multiply, Screen, Soft Light (a soft Overlay).
Use a mode on a whole layer. Lower opacity after the mode, not instead of it.

## What each mode is for

| Mode | Does | Use |
|---|---|---|
| `multiply` | Darkens. Black stays. White vanishes. | Shadows, print ink, dirty a highlight |
| `screen` | Lightens. White stays. Black vanishes. | Glow, haze, add a light leak |
| `overlay` | Contrast. Midtones move less. | Punch a flat photo |
| `soft_light` | Gentler overlay | Grade without clipping |
| `hard_light` | Harsh overlay | Graphic poster hit |
| `darken` / `lighten` | Pick darker/lighter pixel | Remove a white or black backdrop, crude |
| `difference` | Abs of subtract | Align two frames; not a look |
| `color_dodge` / `color_burn` | Blow or crush | Neon, grit. Easy to clip |
| `addition` / `subtract` | Linear add/sub | Effects, not photos |
| `grain_merge` / `grain_extract` | ± 0.5 offset | Texture plates |

GIMP note: in some docs Overlay and Soft Light were identical in old math. This harness implements them as different formulas in `_blend_with_mode`.

## Harness map

```
cli-anything-gimp --json --project ABS layer set 0 mode multiply
cli-anything-gimp --json --project ABS layer set 0 opacity 0.55
```

`layer set INDEX mode VALUE` and `layer set INDEX blend_mode VALUE` both work.

No per-channel blend. No "blend if" sliders.

## Codegraph

- `cli_anything.gimp.core.layers.BLEND_MODES`
- `cli_anything.gimp.core.layers.set_layer_property` `prop in {mode, blend_mode}`
- `cli_anything.gimp.core.export._blend_with_mode`

## Sources

- https://docs.gimp.org/3.2/en/gimp-concepts-layer-modes.html
- https://developer.gimp.org/core/algorithm/compositing/
- https://www.gimp.org/tutorials/community/Focus_Group/
