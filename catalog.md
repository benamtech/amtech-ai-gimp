# Catalog

Maps styles ↔ brands ↔ families. Machine source of truth: `catalog.json`. Regenerate with `python3 run.py catalog`.

## Families → styles
### cover
- `album-cover` — Square album
- `book-cover` — Trade book cover
- `concert-flyer` — Concert flyer
- `event-poster` — Event / lecture poster
- `movie-poster` — One-sheet
- `propaganda` — Propaganda poster
- `wanted-poster` — Wanted / broadside

### editorial
- `lookbook` — Fashion lookbook plate
- `magazine-cover` — Magazine cover
- `newspaper-front` — Broadsheet front
- `portrait-story` — Portrait story 4:5
- `swiss-poster` — Swiss / International Typographic
- `tabloid` — Tabloid scream
- `zine` — Xerox zine cover

### photo
- `contact-sheet` — Contact sheet
- `diptych` — Diptych
- `duotone` — Duotone punch
- `dutch-angle` — Dutch angle
- `edge-map` — Find edges
- `emboss-relief` — Emboss
- `film-rebate` — Film rebate still
- `full-bleed-band` — Full-bleed + type band
- `glitch-shift` — Channel-shift feel (offset)
- `grain-extract` — Grain extract
- `halftone-poster` — Posterize / pop
- `hard-light-hit` — Hard light
- `high-key` — High key
- `inset-corner` — Tiny inset + type field
- `invert-poster` — Invert
- `letterbox` — Cinema letterbox
- `low-key` — Low key
- `minimal-caption` — Quiet caption
- `multiply-grade` — Multiply grade plate
- `overlay-punch` — Overlay contrast
- `polaroid` — Polaroid frame
- `risograph` — Riso misregister feel
- `screen-glow` — Screen glow plate
- `sepia-postcard` — Sepia postcard
- `soft-blur-dream` — Soft blur
- `solarize` — Solarize
- `stack-dual` — Dual stack panel
- `thirds-poster` — Rule-of-thirds type
- `triptych` — Triptych bars
- `unsharp-crisp` — Unsharp punch
- `vhs-label` — VHS sleeve type
- `xerox-punk` — High contrast xerox

### type
- `big-type-only` — Type-led field
- `kinetic-echo` — Kinetic echo type

### viral
- `alert-banner` — Amber / alert banner
- `breaking-full` — Full-screen breaking
- `breaking-lower-third` — Lower-third breaking
- `fuji-ragebait` — 1:1 viral still — warhol + brand lift + sticker + stacked Impact headlines  (brand: retardglobal)
- `ig-post` — Instagram 1:1
- `ig-story` — Story 9:16
- `infographic-stat` — Big number stat
- `instagram-ragebait-rg-lock` — Ragebait + Warhol flats + RG lime/mag/cyan lock, 1:1  (brand: retardglobal)
- `instagram-ragebait-warhol-glitch` — Ragebait + Warhol flats + glitch offset
- `instagram-ragebait` — Instagram portrait ragebait still
- `listicle-cover` — Listicle cover
- `live-badge` — LIVE pill on still
- `lower-third-sport` — Sports lower third
- `meme-impact` — Impact / top-bottom meme
- `newspaper-clipping` — Torn clipping
- `quote-card` — Quote card
- `reaction-split` — Reaction / two-panel
- `red-circle-arrow` — Red circle + slab arrow
- `tiktok-cover` — TikTok cover
- `tweet-card` — Landscape card 16:9
- `two-panel-choice` — Drake / choice two-panel
- `vs-thumb` — VS split thumbnail
- `weather-bug` — Corner bug + chiron
- `yt-thumb` — YouTube thumbnail

## Brands
### bureau-of-stolen-weather — BUREAU OF STOLEN WEATHER
- font: Archivo Black
- palette: brass=#B08D57, fog=#5B7A8C, ink=#1A1C1E, paper=#E8E4D8, rust=#C4552A, storm=#1F4E5A
- roles: brass=registration/filigree/rules, fog=watermark/shadow/secondary-type, ink=headline/type/linework, paper=background, rust=classification-marks/stamps/alerts, storm=deep-accents/plates/borders
- fx: scan, xerox, grain, halftone, torn, vignette, posterize, channel_offset, duotone, sepia, bottom_lift, find_edges, emboss
- forbid: neon, rainbow, pastel, candy-gradients, comic, social-media-energy, red-as-primary, lime, magenta, cyan-drop, impact-font, white-bg, pure-black-bg
- canvas: {"a4": [2480, 3508], "letter": [2550, 3300], "card": [1050, 600], "square": [1080, 1080], "social": [1200, 630], "spec": [2400, 3000], "plaque": [1600, 1000]}
- url: bosw.archive

### retardglobal — RETARD GLOBAL
- font: Impact
- palette: cyan=#2FF3FF, k=#000000, lime=#DEFF2E, mag=#FD2EFF, orange=#FF7F00, w=#FFFFFF
- roles: cyan=cta/url/frame, lime=headline/band, mag=strap/alert, orange=banner-variant-only
- fx: torn, halftone, xerox, scan, crt, splatter-3only, offset, posterize
- forbid: red, gold, purple-blend, navy-accent, rainbow
- canvas: {"ig": [1080, 1080], "ig_portrait": [1080, 1350], "story": [1080, 1920], "yt": [2560, 1440], "banner": [1920, 640]}
- url: retardglobal.com

## Techniques
- `cosmic-void-starfield` — Cosmic void + starfield [procedural] · types: void · era: 2010s, cosmic-horror · tags: stars, void, cosmic, space, abyss, serene
- `duotone-marble-relief` — Duotone marble relief [grade] · types: sculpture, portrait · era: 1970s, greek · tags: duotone, relief, stone, marble, mono, sculptural
- `duotone-waterline` — Duotone waterline submerge [composite] · types: sculpture, portrait, landscape · era: 1970s, yacht-rock · tags: duotone, water, submerge, ocean, reflection, mono
- `gold-mandorla-mosaic` — Gold mandorla (catholic icon) [composite] · types: portrait, sculpture · era: 1930s, byzantine, icon · tags: gold, mosaic, icon, halo, sacred, mandorla
- `organic-computer-screen-blend` — Organic computer (circuit × coral screen blend) [composite] · types: texture · era: 2010s, biopunk · tags: circuit, coral, machine, organic, screen, double-exposure, signal
- `solarized-specter` — Solarized specter (ghost body) [glitch] · types: sculpture, portrait · era: 1970s, psychedelic · tags: solarize, anaglyph, ghost, violet, offset, dream
- `vaporwave-crt-grid` — Vaporwave CRT perspective grid [texture] · types: sculpture, portrait, landscape · era: 1980s, vaporwave, synthwave · tags: vaporwave, crt, grid, retro, purple, scanline
- `xerox-torn-ghost` — Xerox saint (torn photocopy ghost) [glitch] · types: sculpture, portrait · era: 1990s, grunge, zine · tags: xerox, photocopy, torn, ghost, 1-bit, zine, punk
