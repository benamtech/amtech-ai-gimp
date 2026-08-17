#!/usr/bin/env python3
"""Install compose fonts. Impact is the viral/meme face — not Anton.

    uv run --with pillow python ensure_fonts.py
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

FONTS_DIR = Path.home() / ".local" / "share" / "fonts" / "image-compose"
UA = "HermesAgent/1.0 (image-compose fonts)"

# Family name (lowercase) -> (filename, url). Impact is required for ragebait.
CATALOG = {
    "impact": (
        "Impact.ttf",
        "https://raw.githubusercontent.com/sophilabs/macgifer/master/static/font/impact.ttf",
    ),
}

ALIASES = {
    "impact": "Impact.ttf",
    "anton": "Anton-Regular.ttf",
    "archivoblack": "ArchivoBlack-Regular.ttf",
    "archivo black": "ArchivoBlack-Regular.ttf",
    "bangers": "Bangers-Regular.ttf",
}


def ensure_dir() -> Path:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    return FONTS_DIR


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    if dest.stat().st_size < 10_000:
        dest.unlink(missing_ok=True)
        raise SystemExit(f"font too small: {dest}")


def ensure_named(name: str) -> Path:
    key = name.strip().lower()
    ensure_dir()
    if key in CATALOG:
        fname, url = CATALOG[key]
        dest = FONTS_DIR / fname
        if not dest.exists() or dest.stat().st_size < 10_000:
            download(url, dest)
        return dest
    if key in ALIASES:
        dest = FONTS_DIR / ALIASES[key]
        if dest.exists():
            return dest
        raise SystemExit(f"font file missing: {dest}")
    raise SystemExit(f"unknown font: {name}")


def resolve_font(spec: str | None) -> str:
    """Turn 'Impact', a family name, or a path into an absolute TTF path."""
    if not spec:
        spec = "Impact"
    p = Path(spec).expanduser()
    if p.exists() and p.is_file():
        return str(p)
    key = spec.strip().lower()
    if key.endswith(".ttf") or key.endswith(".otf"):
        cand = FONTS_DIR / Path(spec).name
        if cand.exists():
            return str(cand)
    try:
        return str(ensure_named(spec))
    except SystemExit:
        # last try: FONTS_DIR / as-written
        cand = FONTS_DIR / spec
        if cand.exists():
            return str(cand)
        raise


def main() -> None:
    paths = {}
    for name in CATALOG:
        paths[name] = str(ensure_named(name))
    for alias, fname in ALIASES.items():
        p = FONTS_DIR / fname
        if p.exists():
            paths[alias] = str(p)
    print("fonts_dir", FONTS_DIR)
    for k, v in sorted(paths.items()):
        print(f"{k}\t{v}")
    if "impact" not in {k.lower() for k in paths}:
        sys.exit(2)


if __name__ == "__main__":
    main()
