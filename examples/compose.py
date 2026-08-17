#!/usr/bin/env python3
"""One-shot CodeAct composition: public-domain photo + original copy.

Uses cli-anything-gimp as the deterministic execution harness.
Copy and layout were authored by Hermes (this session's LLM), not a template.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

OUT = Path("/home/georgej/Pictures/cli-anything-poster")
OUT.mkdir(parents=True, exist_ok=True)
SRC = OUT / "sholes_typewriter_source.jpg"
PHOTO = OUT / "sholes_panel.jpg"
PROJECT = OUT / "poster.gimp-cli.json"
POSTER = OUT / "the-machine-was-never-the-keyboard.png"
CLI = shutil.which("cli-anything-gimp") or str(Path.home() / ".local/bin/cli-anything-gimp")

# Public-domain Sholes typewriter photo (US PD, published before 1929).
# Wikimedia Commons File:Sholes_typewriter.jpg — real upload path from Commons API.
COMMONS = "https://upload.wikimedia.org/wikipedia/commons/9/9a/Sholes_typewriter.jpg"

HEADLINE_LINES = [
    "THE MACHINE",
    "WAS NEVER",
    "THE KEYBOARD",
]
DECK = (
    "In 1873 Sholes taught steel a language.\n"
    "CLI-Anything asks agents to speak software\n"
    "the same way — commands, not clicks."
)
CREDIT = "Photo: Sholes typewriter, 1873. Public domain. Wikimedia Commons."
KICKER = "HERMES  ·  CLI-ANYTHING  ·  GIMP HARNESS"


def run(args: list[str]) -> dict:
    cmd = [CLI, "--json", "--project", str(PROJECT), *args]
    print("+", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"cli-anything-gimp failed: {args}")
    text = proc.stdout.strip()
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        print(text)
        return {}


def download() -> None:
    req = urllib.request.Request(
        COMMONS,
        headers={"User-Agent": "HermesAgent/1.0 (research composition; local)"},
    )
    print(f"download {COMMONS}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        SRC.write_bytes(resp.read())
    print(f"saved {SRC} ({SRC.stat().st_size} bytes)")


def prepare_panel() -> None:
    from PIL import Image

    img = Image.open(SRC).convert("RGB")
    # Fit the 745x842 plate into a 720-tall left panel without stretching.
    target_h = 820
    ratio = target_h / img.height
    panel = img.resize((max(1, int(img.width * ratio)), target_h), Image.Resampling.LANCZOS)
    panel.save(PHOTO, quality=95)
    print(f"panel {PHOTO} {panel.size}")


def main() -> None:
    download()
    prepare_panel()
    if PROJECT.exists():
        PROJECT.unlink()
    subprocess.run(
        [
            CLI, "--json", "project", "new",
            "--width", "1600", "--height", "900", "--mode", "RGB",
            "--background", "#0b1220", "--name", "typewriter-poster",
            "-o", str(PROJECT),
        ],
        check=True,
    )
    run(["layer", "add-from-file", str(PHOTO), "--name", "sholes-1873"])
    run(["layer", "set", "0", "offset_x", "40"])
    run(["layer", "set", "0", "offset_y", "40"])
    # Draw ops are layer-local. The photo layer is only 725x820, so text at
    # x=820 never appears. Put copy on a full-canvas overlay instead.
    run(["layer", "new", "--name", "copy", "--type", "image", "--width", "1600", "--height", "900", "--fill", "transparent"])
    info = run(["layer", "list"])
    print("layers", json.dumps(info, indent=2))
    overlay = "0"
    run(["draw", "text", "--layer", overlay, "--text", KICKER, "--x", "820", "--y", "90", "--size", "18", "--color", "#f4d27a"])
    for i, line in enumerate(HEADLINE_LINES):
        run(["draw", "text", "--layer", overlay, "--text", line, "--x", "820", "--y", str(150 + i * 58), "--size", "44", "--color", "#f6f1e8"])
    for i, line in enumerate(DECK.split("\n")):
        run(["draw", "text", "--layer", overlay, "--text", line, "--x", "820", "--y", str(380 + i * 42), "--size", "22", "--color", "#d7dde8"])
    run(["draw", "text", "--layer", overlay, "--text", CREDIT, "--x", "820", "--y", "820", "--size", "14", "--color", "#9aa4b2"])
    result = run(["export", "render", str(POSTER), "--overwrite"])
    print(json.dumps(result, indent=2))
    print(f"POSTER={POSTER} exists={POSTER.exists()} size={POSTER.stat().st_size if POSTER.exists() else 0}")


if __name__ == "__main__":
    main()
