"""Font resolution. Impact is the viral/meme face — not Anton.

Resolution order:
  1. absolute/existing path (pass-through)
  2. bundled assets/fonts/ (self-contained — no external dependency)
  3. ~/.local/share/fonts/image-compose/ (legacy Hermes convention)
  4. download (Impact only; other families must already be present)

Impact is required for ragebait / meme type. Anton is a condensed gothic
and must never be silently substituted for Impact.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

from . import FONTS_DIR, USER_FONTS_DIR

UA = "amtech-computer-use-graphics/0.1.1 (font installer)"

# family (lowercase) -> (filename, download url). Only Impact auto-downloads.
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


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    if dest.stat().st_size < 10_000:
        dest.unlink(missing_ok=True)
        raise SystemExit(f"font too small: {dest}")


def _find_local(fname: str) -> Path | None:
    for base in (FONTS_DIR, USER_FONTS_DIR):
        p = base / fname
        if p.exists() and p.stat().st_size >= 10_000:
            return p
    return None


def resolve_font(spec: str | None) -> str:
    """Turn 'Impact', a family name, or a path into an absolute TTF path."""
    if not spec:
        spec = "Impact"
    p = Path(spec).expanduser()
    if p.exists() and p.is_file():
        return str(p)

    key = spec.strip().lower()

    if key.endswith(".ttf") or key.endswith(".otf"):
        found = _find_local(Path(spec).name)
        if found:
            return str(found)

    if key in CATALOG:
        fname, url = CATALOG[key]
        dest = FONTS_DIR / fname
        if not dest.exists() or dest.stat().st_size < 10_000:
            FONTS_DIR.mkdir(parents=True, exist_ok=True)
            _download(url, dest)
        return str(dest)

    if key in ALIASES:
        found = _find_local(ALIASES[key])
        if found:
            return str(found)
        raise SystemExit(f"font file missing: {ALIASES[key]} (not bundled, not installed)")

    # last try: as-written filename in either fonts dir
    found = _find_local(spec)
    if found:
        return str(found)
    raise SystemExit(f"unknown font: {spec}")


def ensure_fonts() -> dict[str, str]:
    """Ensure Impact is present; return a map of family -> abs path."""
    paths: dict[str, str] = {}
    for name in CATALOG:
        paths[name] = resolve_font(name)
    for alias, fname in ALIASES.items():
        found = _find_local(fname)
        if found:
            paths[alias] = str(found)
    return paths


def main() -> int:
    paths = ensure_fonts()
    print("fonts_dir", FONTS_DIR)
    for k in sorted(paths):
        print(f"{k}\t{paths[k]}")
    if "impact" not in {k.lower() for k in paths}:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
