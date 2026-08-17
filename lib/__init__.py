#!/usr/bin/env python3
"""amtech-computer-use-graphics — a deterministic, non-generative image composer.

A self-contained, agent-agnostic program that turns a recipe
(brand + style + source + copy + seed) into a finished still via
Pillow, with optional native-GIMP and cli-anything-gimp engines.

Nothing here depends on a specific agent runtime (Hermes, Claude Code,
Codex, etc.). Agents discover the workflow through AGENTS.md and
skills/meme-maker/SKILL.md, then drive this library directly.
"""
from __future__ import annotations

from pathlib import Path

__version__ = "0.1.2"

# Product / authorship metadata (AMTECH)
PRODUCT = "amtech-computer-use-graphics"
AUTHOR = "Benjamin Palaskas"
ORG = "AMTECH"
CONTACT_EMAIL = "ben@amtechai.com"
CONTACT_URL = "https://amtechai.com"

# The bundle root is the parent of this lib/ directory.
ROOT = Path(__file__).resolve().parent.parent

ASSETS = ROOT / "assets"
FONTS_DIR = ASSETS / "fonts"
BRANDS_DIR = ROOT / "brands"
STYLES_DIR = ROOT / "styles"
SOURCES_DIR = ROOT / "sources"
REFERENCES_DIR = ROOT / "references"
SCHEMAS_DIR = ROOT / "schemas"
TEMPLATES_DIR = ROOT / "templates"
OUT_DIR = ROOT / "out"
CACHE_DIR = ROOT / "cache"

# A still job may also read/write these legacy locations so the program
# remains compatible with prior compose work.
LEGACY_POSTER_DIR = Path.home() / "Pictures" / "cli-anything-poster"

# Cross-platform home fonts dir (mirrors the Hermes skill convention).
USER_FONTS_DIR = Path.home() / ".local" / "share" / "fonts" / "image-compose"


def ensure_dirs() -> None:
    for d in (OUT_DIR, CACHE_DIR, FONTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


__all__ = [
    "__version__",
    "PRODUCT",
    "AUTHOR",
    "ORG",
    "CONTACT_EMAIL",
    "CONTACT_URL",
    "ROOT",
    "ASSETS",
    "FONTS_DIR",
    "BRANDS_DIR",
    "STYLES_DIR",
    "SOURCES_DIR",
    "REFERENCES_DIR",
    "SCHEMAS_DIR",
    "TEMPLATES_DIR",
    "OUT_DIR",
    "CACHE_DIR",
    "LEGACY_POSTER_DIR",
    "USER_FONTS_DIR",
    "ensure_dirs",
]
