#!/usr/bin/env python3
"""amtech-computer-use-graphics entry point.

    python3 run.py --help

A self-contained, deterministic, non-generative image composer + brand/style
authoring tool. See AGENTS.md for the working agreement, AUTHORITY.md for the
authority map, and CODEGRAPH.md for the module graph.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
