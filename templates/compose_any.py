#!/usr/bin/env python3
"""Format-agnostic compose via cli-anything-gimp.

Copy this file. Set CANVAS, SOURCES, COPY, and overlay draws.
Run: uv run --with pillow python compose_any.py

Local files in SOURCES skip Commons. Commons titles must be File:… strings.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote

OUT = Path.home() / "Pictures" / "cli-anything-poster"
PROJECT = OUT / "compose.gimp-cli.json"
POSTER = OUT / "compose.png"
CLI = shutil.which("cli-anything-gimp") or str(Path.home() / ".local/bin/cli-anything-gimp")

CANVAS = (1080, 1350)
BACKGROUND = "#0b1220"

# Each source: local Path, or a Commons title starting with "File:"
SOURCES = [
    # Path.home() / "Downloads" / "ref.jpg",
    # "File:The_Earth_seen_from_Apollo_17.jpg",
]

KICKER = "KICKER"
HEADLINES = ["HEADLINE LINE ONE", "HEADLINE LINE TWO"]
DECK = ["Deck line."]
CREDIT = "Credit: source + license."


def run(args: list[str]) -> dict:
    proc = subprocess.run(
        [CLI, "--json", "--project", str(PROJECT), *args],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(f"failed: {args}")
    text = proc.stdout.strip()
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {"raw": text}


def commons_url(title: str) -> str:
    api = (
        "https://commons.wikimedia.org/w/api.php?action=query"
        f"&titles={quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    )
    req = urllib.request.Request(api, headers={"User-Agent": "HermesAgent/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page or not page.get("imageinfo"):
        raise SystemExit(f"commons miss: {title}")
    return page["imageinfo"][0]["url"].split("?", 1)[0]


def fetch(src, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    if isinstance(src, Path):
        dest.write_bytes(Path(src).read_bytes())
        return
    url = commons_url(str(src))
    req = urllib.request.Request(url, headers={"User-Agent": "HermesAgent/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())


def main() -> None:
    if not Path(CLI).exists():
        raise SystemExit("cli-anything-gimp not on PATH")
    OUT.mkdir(parents=True, exist_ok=True)
    w, h = CANVAS
    if PROJECT.exists():
        PROJECT.unlink()
    subprocess.run(
        [CLI, "--json", "project", "new", "--width", str(w), "--height", str(h),
         "--mode", "RGB", "--background", BACKGROUND, "-o", str(PROJECT)],
        check=True,
    )
    from PIL import Image
    for i, src in enumerate(SOURCES):
        raw = OUT / f"src-{i}.bin"
        fetch(src, raw)
        img = Image.open(raw).convert("RGB")
        img.save(OUT / f"src-{i}.jpg", quality=95)
        run(["layer", "add-from-file", str(OUT / f"src-{i}.jpg"), "--name", f"src{i}"])
        # Caller edits offsets after a vision pass.
        run(["layer", "set", "0", "offset_x", "0"])
        run(["layer", "set", "0", "offset_y", "0"])
    run(["layer", "new", "--name", "copy", "--type", "image",
         "--width", str(w), "--height", str(h), "--fill", "transparent"])
    overlay = "0"
    y = 80
    run(["draw", "text", "--layer", overlay, "--text", KICKER,
         "--x", "48", "--y", str(y), "--size", "18", "--color", "#f4d27a"])
    y += 50
    for line in HEADLINES:
        run(["draw", "text", "--layer", overlay, "--text", line,
             "--x", "48", "--y", str(y), "--size", "40", "--color", "#f6f1e8"])
        y += 52
    for line in DECK:
        run(["draw", "text", "--layer", overlay, "--text", line,
             "--x", "48", "--y", str(y), "--size", "20", "--color", "#d7dde8"])
        y += 34
    run(["draw", "text", "--layer", overlay, "--text", CREDIT,
         "--x", "48", "--y", str(h - 48), "--size", "14", "--color", "#9aa4b2"])
    result = run(["export", "render", str(POSTER), "--overwrite"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
