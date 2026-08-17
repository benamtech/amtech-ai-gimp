# Harness limits (2026-08-16 test)

Full write-up: `~/Pictures/cli-anything-poster/limits/LIMITS.md`

- `draw text` does not wrap. Break lines in the script.
- Guessed Commons hash 404s. Use `action=query&prop=imageinfo`.
- Draw ops are layer-local. Text at x=800 on a 480px photo layer vanishes. JSON still lists it.
- `gimp -i -b` / `gimp-console` hung (exit 124 in 20 s). Stay on Pillow when `draw_ops` exist. Expect `method=pillow`.
- `session undo` is RAM-only (`Session._undo_stack`). One-shot CLI after a compose script: `Nothing to undo.` Same-process / REPL undo does change pixels.
- `save_session` writes the project JSON, not the undo list.
- Negative offsets work and will clip the layer.
