#!/usr/bin/env python3
"""
RG meme mass-generator — captions + images -> a ton of brand-locked memes.

One script, hundreds of stills. Feed it a list of captions (one per line) and
an optional subject->image map, and it renders the cross product of
{captions} x {styles} x {seeds} as RETARD GLOBAL meme cards — fully
deterministic (same inputs = same pixels), brand-locked, no flags named by the
human beyond the copy and the pictures.

Usage:
  python3 generate_memes.py captions.txt --images images.json --out out/rg-batch
  python3 generate_memes.py captions.txt --styles rg-meme,rg-meme-45 --seeds 3

Captions file (plain text, one per line; optional fields after a `|`):
    <caption> [| <image> [| <image2>]] [| @<style>]

Images map (JSON) maps a subject substring -> still path, or [still, popout_still]:
    { "chester stone": "sources/chester-stone-face.png",
      "the rizzler": ["sources/the-rizzler-origin.jpg", "sources/popout-mossad-seal.png"] }

Styles default to the full RG family. Popout styles (rg-meme-popout,
rg-meme-45-popout) only render when a second still (photo2) is present — the
image2 field or the map's second element. Each caption renders at N seeds so
the hi-vis lime/orange masthead and any seeded texture vary.

Determinism: seed = base_seed + caption_idx*100 + style_idx*10 + seed_i.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib import OUT_DIR  # noqa: E402
from lib.compose import compose  # noqa: E402
from lib.meme import load_captions, slugify, wrap_headline  # noqa: E402
from lib.source import resolve as resolve_source  # noqa: E402

# The full RETARD GLOBAL meme family, in render order.
RG_STYLES = [
    "rg-meme",
    "rg-meme-45",
    "rg-meme-computer",
    "rg-meme-nobadge",
    "rg-meme-popout",
    "rg-meme-45-popout",
]
POPOUT_STYLES = {"rg-meme-popout", "rg-meme-45-popout"}


def load_image_map(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).expanduser().read_text())


def resolve_images(caption: dict, image_map: dict) -> tuple[str | None, str | None]:
    """Return (source, photo2) for a caption, resolved from explicit fields or the map."""
    imgs = [x for x in (caption.get("image"), caption.get("image2")) if x]
    subject = None
    if not imgs:
        low = (caption.get("caption") or "").lower()
        for key in image_map:
            if key.lower() in low:
                subject = key
                break
        if subject:
            val = image_map[subject]
            imgs = val if isinstance(val, list) else [val]
    if not imgs:
        return None, None
    source = str(resolve_source(imgs[0]))
    photo2 = str(resolve_source(imgs[1])) if len(imgs) > 1 else None
    return source, photo2


def build_jobs(captions: list[dict], image_map: dict, styles: list[str],
               seeds: int, base_seed: int) -> list[dict]:
    jobs = []
    for ci, cap in enumerate(captions):
        caption = cap.get("caption") or ""
        if not caption:
            continue
        source, photo2 = resolve_images(cap, image_map)
        if not source:
            print(f"  ! skip '{caption[:40]}': no image resolved", file=sys.stderr)
            continue
        lines = wrap_headline(caption)
        set_ = {"url": "RETARDGLOBAL.COM"}
        for i in range(6):
            set_[f"l{i + 1}"] = lines[i] if i < len(lines) else ""
        base_name = cap.get("name") or slugify(caption)
        for si, style in enumerate(styles):
            if style in POPOUT_STYLES and not photo2:
                continue
            for seed_i in range(seeds):
                seed = base_seed + ci * 100 + si * 10 + seed_i
                jobs.append({
                    "name": f"{base_name}-{style.replace('rg-meme', '').strip('-') or '1x1'}-s{seed}",
                    "style": style,
                    "source": source,
                    "photo2": photo2 if style in POPOUT_STYLES else None,
                    "set": set_,
                    "seed": seed,
                })
    return jobs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate a ton of brand-locked RETARD GLOBAL memes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[0],
    )
    ap.add_argument("captions", help="captions file: txt (one per line) or JSON list")
    ap.add_argument("--images", default=None, help="subject->image map JSON")
    ap.add_argument("--styles", default=",".join(RG_STYLES),
                    help="comma-separated style ids (default: all RG styles)")
    ap.add_argument("--seeds", type=int, default=1, help="seed variations per caption")
    ap.add_argument("--base-seed", type=int, default=7, help="starting seed")
    ap.add_argument("--out", default=None, help="output directory (default: out/rg-batch)")
    ap.add_argument("--brand", default="retardglobal")
    ap.add_argument("--limit", type=int, default=None, help="cap total renders")
    args = ap.parse_args(argv)

    out_dir = Path(args.out).expanduser() if args.out else OUT_DIR / "rg-batch"
    out_dir.mkdir(parents=True, exist_ok=True)

    styles = [s.strip() for s in args.styles.split(",") if s.strip()]
    captions = load_captions(args.captions)
    image_map = load_image_map(args.images)

    jobs = build_jobs(captions, image_map, styles, args.seeds, args.base_seed)
    if args.limit:
        jobs = jobs[: args.limit]

    print(f"captions={len(captions)} styles={styles} seeds={args.seeds} "
          f"-> {len(jobs)} renders -> {out_dir}")

    ok = 0
    for job in jobs:
        try:
            res = compose(
                job["style"], brand_id=args.brand, source=job["source"],
                photo2=job["photo2"], copy_overrides=job["set"],
                seed=job["seed"], out_dir=out_dir, engine="pillow",
            )
            src_png = out_dir / f"{job['style']}.png"
            dst_png = out_dir / f"{job['name']}.png"
            if src_png.exists():
                src_png.replace(dst_png)
            ok += 1
            print(f"  [{ok:3d}/{len(jobs)}] {job['name']}.png  seed={job['seed']}  {job['style']}")
        except SystemExit as e:
            print(f"  ! {job['name']}: {e}", file=sys.stderr)

    print(f"\ndone: {ok}/{len(jobs)} rendered -> {out_dir}")
    return 0 if ok == len(jobs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
