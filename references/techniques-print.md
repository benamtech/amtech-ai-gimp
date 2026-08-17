# Print: bleed, trim, safe

See: `image-compose/references/techniques-grids.md`

## Human idiom

Trim is where the blade aims.
Bleed is extra image past the trim so a miss does not show paper.
Safe (margin) is inside the trim so type is not cut if the blade misses the other way.

Common: 0.125 in (3 mm) bleed. Safe 0.125 in inside trim.
Hardcover wraps need much more (printers quote ~0.8 in on covers). Ask the printer.

## Agent translation

The harness has no bleed box.
If they ask for print:

1. Canvas = trim + 2×bleed in pixels (at the named DPI).
2. Keep type inside the safe rect.
3. Let the photo run to the canvas edge (that is the bleed).
4. Say the pixel math in the note.

Example: 1600×2000 trim at 300 dpi, 0.125 in bleed → add 38 px per side → canvas 1676×2076.
Type stays ≥ 38+38 px from the canvas edge.

## Sources

- Mixam bleed support
- Vista / print-shop explainers: safety, trim, bleed
- GraphicDesign.SE: why safe exists if bleed exists
