# Design canon — taste, movements, and how to push boundaries

This is the *why* behind the pixels. It encodes a century of pre-AI graphic
design (1930s–2010s) so an agent can (a) make tasteful, non-style-specific
decisions, and (b) push past a template into something worth looking at —
without losing the reliability of "the program prints what you asked for."

Load this before a hard design job. It is a floor, not a lock: a strong idea
may break any single rule on purpose. Break one rule deliberately, not all of
them by accident.

See also: `lib/design.py` (the computable rules — contrast, harmony, pairing,
variant distinctness) and `lib/technique.py` (the reusable effect catalog).

---

## 1. Non-style-specific taste (the rules that never go out of style)

These are the design principles any good graphic holds, independent of brand
or era. They apply to a meme, a poster, a cover, or a data graphic.

1. **Hierarchy.** One thing is most important. Make it the biggest, boldest,
   highest-contrast thing. A layout where everything shouts has no message.
   Read it at arm's length; the first element you see should be the point.
2. **Contrast.** Light/dark, big/small, thick/thin, saturated/muted. Contrast
   is what makes a client say "pop". It is also legibility: body text needs
   ~4.5:1 against its field (see `lib.design.legible`).
3. **Alignment.** Everything sits on an edge or a baseline. Flush-left, a
   grid, or a deliberate center — never "roughly where it landed". Ragged
   right beats centered by default; centered is a choice, not a habit.
4. **Proximity.** Related things touch. Unrelated things breathe. Group the
   label with its number, the caption with its image.
5. **Repetition.** Reuse one type family, one accent, one spacing rhythm, one
   motif. Repetition is what makes six images feel like a set.
6. **Whitespace.** The empty space is doing work. A busy background eats type;
   a quiet band holds it. Do not fill every pixel.
7. **Balance.** Symmetry is calm, asymmetry is energy. A heavy subject on one
   side needs a counterweight (type, color, or empty space) on the other.
8. **Unity.** One palette, one type system, one grain, one idea per still.

**Color theory, applied (not academic):**
- **Complementary** (opposite on the wheel) = maximum contrast, use sparingly
  for the one thing that matters.
- **Analogous** (adjacent) = harmonious, calm, cohesive.
- **Triadic** (evenly spaced) = vibrant but balanced; good for three equal
  elements.
- Limit a palette to ~3 colors (plus black/white) to keep hierarchy. Nike's
  black/white/gray + one product color is the model.
- **Type pairing:** geometric sans headline + humanist sans body (clean);
  transitional serif headline + neutral sans body (editorial authority). One
  family, two weights, is enough. A third size is a deck or a credit.

---

## 2. Movements 1930s–2010s (a route map, not a museum)

Each movement is a *grammar*: type, palette, composition, texture. Reach for
one when the ask has a mood; remix them freely. Map to effects via
`lib/effects.py` / `techniques/`.

### 1930s — Art Deco, Constructivism, early Modern
- **Art Deco**: geometric, symmetric, metallic gold/black, stepped forms, thin
  high-contrast serif + chevrons/fans. → duotone gold, relief, clean grids.
- **Constructivism**: diagonal composition, red/black/white, bold sans, photo
  montage, propaganda energy. → posterize, hard contrast, diagonals.

### 1940s — WPA, wartime posters, mid-century seeds
- Flat color fields, screen-printed 2–3 ink, bold sans, big simple symbols.
  → posterize, flat plates, high key. ("Make the flatness a feature.")

### 1950s — Swiss / International Typographic Style, mid-century modern
- Modular grid, sans (Helvetica/Akzidenz), flush-left rag-right, objective,
  few colors, photography as a clean rectangle. **The grid is the idea.**
  → crisp grid, one axis of type, no decoration. (This is the ancestor of
  everything "clean" today.)

### 1960s — Pop, psychedelic, Op art, corporate identity
- **Pop (Warhol)**: flat silkscreen plates, hot colors, repetition, irony.
  → warhol, clamp_hues, screen-print grain.
- **Psychedelic**: liquid type, clashing saturated colors, optical vibration.
  → solarize, color_split, high saturation.
- **Corporate identity (Paul Rand)**: the mark, the grid, restraint.

### 1970s — punk, New Wave, disco, big advertising
- **Punk/zine**: cut-and-paste, xerox texture, ransom-note type, torn edges.
  → xerox, torn, splatter, find_edges.
- **New Wave (Weingart)**: grid, but broken on purpose — oversized type,
  negative letterspacing, layered.
- **Disco/big-ad**: gold, high gloss, oversized serif, warm duotone. → gold,
  bottom_lift, duotone.

### 1980s — Postmodernism, Memphis, neon, MTV
- **Memphis**: clashing pastels + black, squiggles, geometric noise, playful.
- **Neon/vaporwave precursors**: hot magenta/cyan on black, chrome, grid.
  → clamp_hues, perspective_grid, crt, channel offset.

### 1990s — grunge, David Carson, techno/rave, deconstruction
- **Grunge (Ray Gun)**: type as texture, illegibility as style, layered mess.
  → find_edges, xerox, slice_glitch, grain, torn.
- **Techno/rave flyer**: dense, layered, loud, 1-color screen energy.

### 2000s — Web 2.0, glossy, minimalism, Y2K
- Glossy buttons, glass reflections, soft gradients; then a hard swing to
  flat minimalism. → vgradient, soft_light, generous whitespace.

### 2010s — flat design, brutalist web, vaporwave, glitch art
- **Flat**: solid fills, no depth, bold type, 2–3 colors.
- **Brutalist**: raw, monospace, default fonts, exposed structure, no polish.
- **Vaporwave**: pink/purple/cyan, marble busts, grids, Japanese text, CRT.
  → duotone, tint violet, perspective_grid, crt, scanlines.
- **Glitch art**: channel offset, slice, datamosh. → slice_glitch, color_split.

---

## 3. How to push boundaries (without breaking the job)

The goal is *cool pictures*, not compliance. Taste rules are a floor; the best
work breaks one rule on purpose. The discipline is knowing which rule.

- **Push one axis at a time.** If the layout is wild, keep the palette tight.
  If the color is electric, keep the type plain. One risk per still reads as
  bold; three risks read as chaos.
- **Steal the grammar, not the object.** Take the *look* of a movement (a grid,
  a texture, a palette logic) and apply it to a new subject. Do not lift a
  studio lockup or another artist's finished image.
- **Make type do something.** Type is the art, not the label: bent, huge,
  cropped, running off the edge, mostly texture. Break your own lines; the
  harness does not wrap.
- **Layer for a reason.** A double exposure (screen blend), a torn edge, a
  waterline — each layer should be doing work you can name.
- **Verify, then go further.** Render, `vision_analyze`, read every string.
  If it reads, push the crop/heat/contrast one more notch and render again.
  Iteration is where the interesting work is; it is also the safety net that
  keeps the wild stuff from being broken stuff.

## 4. The reliability contract (what "good" must survive)

Taste must never cost correctness. These hold no matter how far you push:

- **Deterministic.** Same recipe + seed = same pixels. No diffusion, no LLM in
  the render path.
- **Legible.** Every intended string readable verbatim (arm's length).
- **No invented pixels.** If an effect is unsupported, use the Pillow
  equivalent and say so.
- **Variant = visible difference.** A "variant" that only changes noise is the
  same image twice (`lib.design.variants_distinct`).
- **Credit the source.** Tag stills into the registry.

---

## Sources (for further reading, translated to harness ops above)

- Figma, "13 graphic design principles" (alignment/contrast/hierarchy/space…)
- Toptal, "The Principles of Design" (contrast/hierarchy/repetition/whitespace)
- wpamelia, "Visual Design Principles" (type scale, 3-color limit, pairing)
- Design Reviewed — graphic design history archive (1940s–50s movements)
- The graphic design school — movement → designer → iconic work index
