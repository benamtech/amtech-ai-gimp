# examples/

Provenance and runnable demos for the program. The supported entry point is
always `run.py` (see the root README). These files show how the looks were
first made.

## Runnable (fresh clone, uses bundled `sources/`)

- `batch-fuji.json` — the batch demo. Renders four Fujimoto stills from one
  template:

  ```bash
  python3 run.py batch --manifest examples/batch-fuji.json --out out/
  ```

- `compose_fuji_grimace_rg.py`, `compose_fuji_mcflurry_rg.py`,
  `compose_fuji_wallet_rg.py`, `compose_fuji_xerox_rg.py` — the original
  one-shot scripts that made the four Fujimoto stills. They import
  `lib.rg_kit` and read the bundled `sources/`. Run any of them from the repo
  root; output lands in `out/`.

## Legacy provenance (not runnable on a fresh clone)

- `build_rizzler.py`, `build_rizzler_glitch.py`,
  `compose_rizzler_ragebait.py` — the earliest ragebait stills, written before
  the program was consolidated. They reference a historical `/tmp/rizzler-src/`
  scratch directory and the old `image-compose` skill path
  (`~/.hermes/skills/creative/image-compose/scripts`). Kept as a record of the
  workflow's origin, not as runnable code.
- `compose.py` — the Sholes typewriter poster, a direct `cli-anything-gimp`
  driver with the original author's `~/Pictures/cli-anything-poster` output
  path. Kept as a record of the cli-anything-gimp workflow.

The current way to make any of these looks is `run.py compose` / `run.py
generate` / `run.py batch` with a style recipe (e.g. `fuji-ragebait`).
