# CLAUDE.md — amtech-computer-use-graphics (Claude Code entry)

@AGENTS.md

This directory is a self-contained, deterministic, non-generative image
composer. Read AGENTS.md for the full working agreement, AUTHORITY.md for the
authority map, and CODEGRAPH.md for the module graph. The playbook your skills
load is skills/meme-maker/SKILL.md.

Quick start (no build step):

```bash
python3 run.py doctor
python3 run.py compose --style instagram-ragebait-warhol-glitch \
  --brand retardglobal --source <src> --set l1=HEADLINE --seed 7
```

Native GIMP 3 batch is optional and auto-detected; the Pillow path is the
stable default and needs only `pillow`.
