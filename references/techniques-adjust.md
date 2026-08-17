# Ordinary edits (filters)

See: `image-compose/references/INDEX.md`
See: `cli-anything-gimp/filter.add`

## Human idiom

Before type, fix the still: crop, level, contrast, a little sharpen.
Unsharp mask is sharpen-by-blur. High-pass sharpen is a gray layer on Overlay. The harness has `unsharp_mask` and `overlay`, not a high-pass filter.

## Commands

```
filter add brightness --layer N --param factor=1.1
filter add contrast   --layer N --param factor=1.2
filter add saturation --layer N --param factor=0.85
filter add sharpness  --layer N --param factor=1.3
filter add autocontrast --layer N --param cutoff=0
filter add equalize --layer N
filter add grayscale --layer N
filter add sepia --layer N --param intensity=1.0
filter add gaussian_blur --layer N --param radius=2
filter add unsharp_mask --layer N --param radius=2 --param percent=150 --param threshold=3
filter add rotate --layer N --param angle=2 --param expand=0
filter add flip_h --layer N
filter add crop --layer N --param left=0 --param top=0 --param right=800 --param bottom=600
filter add resize --layer N --param width=1600 --param height=900 --param resample=lanczos
```

Read `filter info NAME` if a param is unclear.
Then `vision_analyze`. Filters persist in JSON even when they look wrong.

## Pillow pre-pass

If you need curves, color temperature, or a vignette, do it in Pillow, write a JPEG, then add that file as the layer. Say so in the credit or the notes.

## Codegraph

- `cli-anything-gimp/filter.add`
- `cli-anything-gimp/filter.list-available`
- Categories: adjustment, blur, stylize, transform
