# LIMITS

Honest report from the 2026-08-16 stress test.
Work notes live in `/home/georgej/AMTECH/gimp-hermes-grok-test/notes/`.
Final stills live in this folder.

## What the skill handled

- One compose script per poster. The harness printed. Vision checked the PNG.
- Commons `imageinfo` URL resolve. Guessed hash `…/commons/6/6a/STS-125_Atlantis_undocking.jpg` returned HTTP 404.
- Given title `File:STS-125_Atlantis_undocking.jpg` is missing. Search found `File:STS115 Atlantis undock ISS.jpg` (public domain, 3032×2009).
- Full-width landscape crop. Dark band for type on a busy still.
- Long unwrapped headline clipped at the right. Pass B wrapped the same words. All words then showed.
- Draw on a small photo layer at x=800 vanished. JSON still held the strings. Vision caught the miss. Pass B put the same strings on a full-canvas overlay. They showed.
- Negative `offset_x` / `offset_y` work. Earth inset at `(-36, 640)` cut the left edge. Poster 3 Earth at `(-80, -40)` cut the top-left.
- `export render` JSON reported `method=pillow` when `draw_ops` existed. All three finals: pillow.
- `project new --help` and `draw text --help` match `agent-native-image-compose/references/cli-anything-gimp.md`.

## What the harness cannot do

- Wrap text. There is no wrap flag. You break lines.
- Native `gimp -i -b` / `gimp-console -i -b` in 20 s. Both exit 124. GIMP 3.2.4 asked for `--batch-interpreter`. Do not retry. Stay on Pillow.
- One-shot `session undo` after a compose script. Undo lives in RAM (`cli_anything.gimp.core.session.Session._undo_stack`). A new process starts empty. Error: `Nothing to undo.`
- `Session.save_session` writes the project JSON only. It does not write the undo list. The docstring is wrong.

## What I had to work around

- STS-125 title 404. Used STS-115 undock still instead.
- Session truth: one-shot CLI failed. Same-process probe (`scripts/session_undo_probe.py`, same global Session as the REPL) did change pixels.
  - mutate sha256 `b494d41d…` (Voyager gone)
  - undo sha256 `0bf3cd13…` (Voyager back; matches final)
  - redo sha256 `b494d41d…` (matches mutate)
- Pass-A evidence files kept beside the finals so the miss is on disk, not only in chat.

## Probe log

| Probe | Result | Evidence |
|---|---|---|
| cli-anything-gimp present | PASS | `/home/georgej/.local/bin/cli-anything-gimp` |
| project new / draw text help match | PASS | `notes/01-probes.md` |
| Guessed Commons hash | PASS as fail (404) | curl -sI |
| Commons API | PASS | `probes/commons-api.json` |
| Draw on small photo vs overlay | PASS (broke, then fixed) | `poster2-tiny-trap-pass-a.png` vs final |
| gimp batch ≤20s | HANG / FAIL (124) | `probes/gimp-batch.txt` |
| vision vs JSON | DISAGREE on purpose | JSON had headline; PNG did not |
| Long unwrapped headline | CLIP | `poster1-landscape-pass-a.png` |
| Negative offset | PASS | layer 0 offset_x=-36 / -80 |
| session undo/redo pixels | FAIL one-shot; PASS same-process | `poster3-session-hashes.json` |
| export method=pillow | PASS | all three render JSON |

## Proposed skill patch

Add this to `agent-native-image-compose` pitfalls:

> Session undo/redo is process-local. A compose script that calls the CLI once per draw starts a new process each time. `session undo` then says "Nothing to undo." To test undo, keep one process (REPL, or Click `cli.main` in a loop). Do not tell the agent that a second terminal call will undo the last script.

Also fix the harness docstring in `Session.save_session`: it does not persist undo history.

## Final files

- `/home/georgej/Pictures/cli-anything-poster/limits/poster1-landscape.png`
- `/home/georgej/Pictures/cli-anything-poster/limits/poster2-tiny-trap.png`
- `/home/georgej/Pictures/cli-anything-poster/limits/poster3-stack.png`
- matching `.gimp-cli.json` and `compose_*.py` in the same folder
