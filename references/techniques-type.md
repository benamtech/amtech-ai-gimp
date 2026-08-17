# Type hierarchy

See: `image-compose/references/INDEX.md`
See: `image-compose/references/formats.md`
See: `cli-anything-gimp/draw.text`

## Human idiom

Magazine covers: masthead, then primary cover line, then secondary lines.
Body text sits on a baseline grid. Display type may break the grid on purpose.
One type family, two weights, is enough. A third size is a deck or a credit.

Read it at arm's length. If you cannot, enlarge or add a panel.

## Sizes that usually work (start points, not laws)

| Role | px on 1080-wide | px on 1600-wide |
|---|---|---|
| Kicker | 16–20 | 16–22 |
| Headline | 40–64 | 44–72 |
| Deck | 18–24 | 20–26 |
| Credit | 12–16 | 13–16 |

Break lines in the script. The harness does not wrap.
`draw text` is layer-local. Draw on a canvas-sized overlay.

Viral / meme / “Impact type” means the Impact TTF from `scripts/ensure_fonts.py`.
Anton is not Impact. Do not treat it as a stand-in.

## Contrast

Busy photo + light type = fail.
Draw a rect band first (`draw rect --x1 --y1 --x2 --y2 --fill`).
Gold kicker `#f4d27a`, paper head `#f6f1e8`, mute deck `#d7dde8`, credit `#9aa4b2` on `#0b1220` is a known-good set from the poster tests.

## Harness map

```
draw text --layer 0 --text "LINE" --x 48 --y 200 --size 44 --color "#f6f1e8"
```

No tracking, no leading, no paragraph box.
Fake leading with `y += int(size * 1.2)`.

## Codegraph

- `cli-anything-gimp/draw.text`
- `agent-native-image-compose/SKILL.md` overlay rule
- `image-compose/templates/compose_any.py`

## Sources

- Mixam / Publitas / Sheridan magazine-cover hierarchy notes
- r/graphic_design baseline-grid critiques
