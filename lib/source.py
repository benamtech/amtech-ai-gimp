"""Source resolution: turn a still spec into a local file.

Accepted source specs:
  - local path            -> copied (or returned) as-is
  - http(s) URL           -> downloaded to cache/
  - "File:<CommonsTitle>" -> resolved via the Commons imageinfo API, downloaded
  - bundled name          -> looked up in sources/

The Commons API (never guess the /commons/X/Yz/ hash):
    https://commons.wikimedia.org/w/api.php?action=query&titles=<title>
        &prop=imageinfo&iiprop=url|size|mime&format=json

For a *named face/place/object*, the calling agent is expected to search the
web (or an image search) and pass the resolved URL here. This module does not
do free-text search; it resolves concrete references deterministically.
"""
from __future__ import annotations

import json
import shutil
import urllib.request
from pathlib import Path
from urllib.parse import quote

from . import CACHE_DIR, SOURCES_DIR

UA = "amtech-computer-use-graphics/0.1.1 (source resolver)"


def _fetch(url: str, dest: Path) -> Path:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())
    if dest.stat().st_size < 64:
        dest.unlink(missing_ok=True)
        raise SystemExit(f"fetch returned empty: {url}")
    return dest


def commons_url(title: str) -> str:
    """Resolve a 'File:...' Commons title to its direct image URL."""
    api = (
        "https://commons.wikimedia.org/w/api.php?action=query"
        f"&titles={quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    )
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page or not page.get("imageinfo"):
        raise SystemExit(f"commons miss: {title} (check the exact title; "
                         f"use action=query&list=search to find it)")
    return page["imageinfo"][0]["url"].split("?", 1)[0]


def resolve(source: str, dest_dir: Path | None = None, name: str | None = None) -> Path:
    """Resolve a source spec to a local file (downloading if needed)."""
    dest_dir = dest_dir or CACHE_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    p = Path(source).expanduser()
    if p.exists():
        return p

    # bundled source?
    bundled = SOURCES_DIR / source
    if bundled.exists():
        return bundled

    if source.startswith("File:"):
        url = commons_url(source)
        dest = dest_dir / (name or Path(url).name or "commons.bin")
    elif source.startswith(("http://", "https://")):
        url = source
        dest = dest_dir / (name or Path(url.split("?")[0]).name or "download.bin")
    else:
        raise SystemExit(
            f"source not found: {source!r}. Use a local path, a URL, a "
            f"'File:...' Commons title, or a bundled name. Bundled: "
            f"{', '.join(list_sources())}"
        )

    if dest.exists() and dest.stat().st_size >= 64:
        return dest
    return _fetch(url, dest)


def download(source: str, dest_dir: Path | None = None, name: str | None = None) -> Path:
    """Alias for resolve (explicit download semantics)."""
    return resolve(source, dest_dir, name)


def list_sources() -> list[str]:
    if not SOURCES_DIR.exists():
        return []
    return sorted(
        p.name for p in SOURCES_DIR.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
    )


def probe(source: str) -> dict:
    """Resolve and return image metadata (dimensions, format, size)."""
    from PIL import Image
    p = resolve(source)
    with Image.open(p) as im:
        return {"path": str(p), "size": list(im.size), "format": im.format,
                "mode": im.mode, "bytes": p.stat().st_size}
