# Technique index (load one file, not this whole tree)

Do not inline this corpus into the system prompt.
Do not `skill_view` every file.
Read this index, pick 1–2 files that match the ask, then load those.

Pattern: `skill_view(name='image-compose', file_path='references/<file>.md')`

## How a large corpus lives in a skill

- SKILL.md = trigger + loop + hard rules (~200 lines max).
- `references/INDEX.md` = routing table (this file).
- One file per idiom. Each file is a node.
- Edges are the `See` lines (`image-compose/references/X.md#heading`).
- Human tutorials stay as citations. The node is the agent translation.
- If the harness cannot do a Photoshop move, the node says so and names the workaround.

## Load router

| User says / you see | Load |
|---|---|
| paste a photo + headline, any size | SKILL.md only |
| magazine, masthead, cover lines, baseline grid | `formats.md` + `techniques-grids.md` + `techniques-type.md` |
| Swiss / International Typographic Style | `techniques-grids.md` |
| book / album / movie poster | `techniques-covers.md` |
| YouTube thumb, face crop, giant type | `techniques-thumbs.md` |
| breaking / ticker / lower-third / ragebait look | `formats.md` + `techniques-viral.md` |
| brand lock / retardglobal / lime-mag-cyan | skill `brands/` + `scripts/brand.py` |
| two photos that must look like one scene | `techniques-composite.md` |
| multiply / screen / overlay / soft light | `techniques-blend.md` |
| mask, fade, luminosity, clip to shape | `techniques-masks.md` |
| bright / contrast / sharpen / blur / crop | `techniques-adjust.md` |
| bleed, trim, safe zone, print | `techniques-print.md` |
| rule of thirds, leading lines, frame-in-frame | `formats.md` |
| harness broke / undo / wrap / GIMP hang | `harness-limits.md` |
| find / search / source a photo / named face | `image-search.md` |
| taste, hierarchy, color, "make it look good" | `design-canon.md` |
| reusable effect pipeline / technique / treatment | `lib/technique.py` + `run.py techniques` |

## Harness capability (truth)

Present:

- `layer add-from-file` / `layer new` / `layer set` (`offset_x`, `offset_y`, `opacity`, `mode`)
- Blend modes: `cli_anything.gimp.core.layers.BLEND_MODES`
  `normal multiply screen overlay soft_light hard_light difference darken lighten color_dodge color_burn addition subtract grain_merge grain_extract`
- `draw text` / `draw rect` (layer-local, no wrap)
- Filters: brightness contrast saturation sharpness autocontrast equalize invert posterize solarize grayscale sepia gaussian_blur box_blur unsharp_mask smooth find_edges emboss contour detail rotate flip_h flip_v resize crop
- `export render` Pillow path when `draw_ops` exist

Absent (do not pretend):

- Layer masks, clipping masks, luminosity masks
- Curves / Levels / Color Balance / HSL pickers
- Gradient tool (fake a gradient with stacked rects + opacity)
- Warp, liquify, content-aware fill
- Fonts: pass a TTF path, or a name `run_style.py` can resolve (`Impact`). Anton is not Impact.
- Auto text wrap
- Persistent undo across processes

Pillow pre-pass is allowed: crop, resize, grade, and write a new JPEG, then `layer add-from-file`. Say that you did it.

## Graph (edges)

```
INDEX
  ├─ formats.md ── type.md, grids.md, viral.md, covers.md
  ├─ techniques-composite.md ── blend.md, masks.md, adjust.md
  ├─ techniques-blend.md ── export._blend_with_mode
  ├─ techniques-masks.md ── (mostly "cannot"; Pillow alpha pre-pass)
  ├─ techniques-type.md ── draw.text, formats.md
  ├─ techniques-grids.md ── type.md, print.md
  ├─ techniques-covers.md ── grids.md, type.md, print.md
  ├─ techniques-thumbs.md ── type.md, viral.md
  ├─ techniques-viral.md ── formats.md, scripts/styles/
  ├─ scripts/styles/*.json ── scripts/run_style.py
  ├─ techniques-adjust.md ── filter.add
  ├─ techniques-print.md ── grids.md
  └─ harness-limits.md
```

## Citation rule

Each technique file lists sources at the bottom.
Cite the human tutorial. Translate to harness ops. Do not copy a Photoshop click path as if the CLI had that menu.
