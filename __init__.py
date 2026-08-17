"""amtech-computer-use-graphics plugin — skill pack. No model tools.

The program is a plain Python package driven by `run.py`; the plugin only
registers the bundled open Agent Skill so Hermes (and any skill-capable
runtime) can discover the workflow.

Register with ctx.register_skill(name, path) so it loads as
`plugin:computer-use-graphics`.
"""
from pathlib import Path


def register(ctx=None):
    if ctx is not None and hasattr(ctx, "register_skill"):
        skill_dir = Path(__file__).resolve().parent / "skills" / "computer-use-graphics"
        if skill_dir.exists():
            ctx.register_skill("computer-use-graphics", str(skill_dir))
    return None
