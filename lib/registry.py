"""Image registry: agent-first tagging + a searchable index.

Every still we save gets descriptive tags and lands in the registry, so the
corpus is searchable by description, not filename. Two artifacts are written:

  - sources/registry.md   — human/agent-readable, greppable
  - sources/registry.json — machine-readable (single source of truth)

An entry records: slug, filename, tags, note, source URL (the URL actually
fetched), dimensions, and when it was added.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path

from . import SOURCES_DIR

REGISTRY_JSON = SOURCES_DIR / "registry.json"
REGISTRY_MD = SOURCES_DIR / "registry.md"


def _slug(text: str) -> str:
    out = "".join(c if c.isalnum() else "-" for c in text.lower())
    return out.strip("-")[:40] or "still"


def _hash_bytes(data: bytes, n: int = 8) -> str:
    return hashlib.sha256(data).hexdigest()[:n]


def load_registry() -> list[dict]:
    if REGISTRY_JSON.exists():
        try:
            return json.loads(REGISTRY_JSON.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_registry(entries: list[dict]) -> None:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_JSON.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n")
    _write_md(entries)


def tag_image(
    src: str | Path,
    tags: list[str] | str,
    note: str = "",
    source_url: str = "",
    copy_to_sources: bool = True,
) -> dict:
    """Tag a still and register it. Returns the registry entry."""
    src_p = Path(src).expanduser()
    if not src_p.exists():
        raise SystemExit(f"image not found: {src_p}")

    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    data = src_p.read_bytes()
    ext = src_p.suffix.lower() or ".jpg"
    slug = _slug(" ".join(tags[:3])) or _slug(src_p.stem)
    dest_name = f"{slug}-{_hash_bytes(data)}" + ext

    entry = {
        "file": dest_name,
        "slug": slug,
        "tags": tags,
        "note": note,
        "source_url": source_url,
        "added": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    try:
        from PIL import Image
        with Image.open(src_p) as im:
            entry["width"], entry["height"] = im.size
            entry["format"] = im.format
    except Exception:  # noqa: BLE001
        pass

    if copy_to_sources:
        SOURCES_DIR.mkdir(parents=True, exist_ok=True)
        dest = SOURCES_DIR / dest_name
        if not dest.exists():
            shutil.copyfile(src_p, dest)

    entries = load_registry()
    # replace by filename if re-tagged
    entries = [e for e in entries if e.get("file") != dest_name]
    entries.append(entry)
    save_registry(entries)
    return entry


def _write_md(entries: list[dict]) -> None:
    lines = ["# Image registry", "",
             "Agent-searchable index of every tagged still. Grep for tags, "
             "subjects, or source URLs. Machine source of truth: "
             "`registry.json`.", ""]
    if not entries:
        lines.append("(empty — run `python3 run.py tag --src <path> --tags ...`)")
    else:
        for e in entries:
            tags = ", ".join(e.get("tags", []))
            dims = f"{e.get('width', '?')}x{e.get('height', '?')}"
            lines.append(f"## {e['file']}")
            lines.append(f"- tags: {tags}")
            if e.get("note"):
                lines.append(f"- note: {e['note']}")
            if e.get("source_url"):
                lines.append(f"- source: {e['source_url']}")
            lines.append(f"- dims: {dims} · added: {e.get('added', '')}")
            lines.append("")
    REGISTRY_MD.write_text("\n".join(lines))


def search_registry(query: str) -> list[dict]:
    """Case-insensitive substring search over tags, notes, and source URLs."""
    q = query.lower()
    return [
        e for e in load_registry()
        if q in " ".join(e.get("tags", [])).lower()
        or q in (e.get("note") or "").lower()
        or q in (e.get("source_url") or "").lower()
        or q in (e.get("file") or "").lower()
    ]


def list_registry() -> list[dict]:
    return load_registry()
