# Covers (magazine, book, album, movie)

See: `image-compose/references/INDEX.md`
See: `image-compose/references/techniques-grids.md`
See: `image-compose/references/techniques-type.md`
See: `image-compose/references/techniques-print.md`

## Magazine

Masthead (name) is constant across issues.
Date / issue near the masthead.
One hero.
One primary cover line. A few secondary lines.
Barcode / price live in a quiet corner if print.

## Book

Thumbnail first. The cover must read at 80 px on a shop grid.
Title larger than author unless the author is the product.
Leave a safe box for retailer badges. Do not put type on the trim.

## Album

Square (1:1) or 3000×3000 if they ask "digital store".
Title can sit in the art. Spine is a separate job. Do not fake a vinyl spine unless asked.

## Movie poster

Credit block is a dense stack of small caps at the bottom.
One key art. Tagline above the credit block.
Do not steal a studio lockup.

## Harness map

Pick canvas from the ask:

- magazine cover ~ 1080×1350 or 1600×2000
- book ~ 1600×2560 (6×9 at 266 dpi-ish) or whatever they name
- album 1080×1080 or 3000×3000
- movie 1600×2400

Hero layer + overlay type. Credit block = many `draw text` lines, `y += 18`.

Copyright: a cover you make is a new work. Do not lift another book's jacket or a studio one-sheet as if it were yours.

## Sources

- Mixam / Publitas cover structure
- Trade book-cover thumbnail advice (title must survive the shop grid)
- PSU librarian note: covers are copyrightable; do not scrape and reprint
