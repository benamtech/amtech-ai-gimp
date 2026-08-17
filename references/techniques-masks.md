# Masks (mostly absent)

See: `image-compose/references/INDEX.md`
See: `image-compose/references/techniques-composite.md`

## Human idiom

A raster mask is a second gray image stuck to a layer. Black hides. White shows. Gray is partial.
A clipping mask limits paint to the pixels of the layer below.
A luminosity mask is a selection from the bright (or dark) parts of the photo.

Photopea and Photoshop tutorials all say the same thing. The harness does not have any of these.

## What you can do instead

1. **Pre-cut alpha.** In Pillow, build an RGBA. White=keep. Write PNG. `layer add-from-file`.
2. **Hard crop.** `filter add crop -l N -p left= -p top= -p right= -p bottom=`
3. **Hide under a panel.** `draw rect` on the overlay. Honest graphic, not a fake blend.
4. **Opacity.** Whole-layer only. `layer set N opacity 0.4`
5. **Screen / multiply a plate.** A black-bg highlight plate on `screen` is the old "no mask" trick.

## Do not

Do not tell the user you added a layer mask.
Do not invent `layer mask` CLI flags.

## Codegraph

- Absent in `cli_anything.gimp.core.layers`
- Alpha respected in `cli_anything.gimp.core.export._composite_layer` if the source PNG has it

## Sources

- https://www.photopea.com/learn/masks
- r/photoshop clipping-mask and luminosity-mask threads (workaround only)
