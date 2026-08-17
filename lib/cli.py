"""CLI dispatcher for amtech-computer-use-graphics.

    python3 run.py doctor
    python3 run.py bootstrap [--gimp]
    python3 run.py styles [--family viral]
    python3 run.py style-new --id x --family custom --title "..." 
    python3 run.py brands
    python3 run.py brand-new --id x --name "X" --color k=#000000 --color w=#ffffff
    python3 run.py sources
    python3 run.py tag --src path.jpg --tags "face,man" --note "..." --url "..."
    python3 run.py search-still --query "person name"
    python3 run.py catalog
    python3 run.py compose --style X --brand Y --source Z --set l1=... --seed N
    python3 run.py generate --style X --brand Y --source Z --set l1=... --seed N

Every subcommand prints plain text; add --json for machine output.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parse_sets(items: list[str]) -> dict:
    out = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--set needs KEY=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        out[k.strip()] = v
    return out


def _parse_colors(items: list[str]) -> dict:
    out = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--color needs name=#rrggbb, got {item!r}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _print(obj, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, indent=2, default=str))
    elif isinstance(obj, (dict, list)):
        print(json.dumps(obj, indent=2, default=str))
    else:
        print(obj)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="amtech-computer-use-graphics",
                                description="Deterministic non-generative image composer.")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="probe environment (no installs)")

    b = sub.add_parser("bootstrap", help="install missing deps + fonts")
    b.add_argument("--gimp", action="store_true", help="also install GIMP if absent")

    st = sub.add_parser("styles", help="list style recipes")
    st.add_argument("--family", help="filter by family")

    sn = sub.add_parser("style-new", help="scaffold a new style recipe")
    sn.add_argument("--id", required=True)
    sn.add_argument("--family", default="custom")
    sn.add_argument("--title", default="")
    sn.add_argument("--canvas", default="1080,1350", help="W,H")
    sn.add_argument("--background", default="#000000")
    sn.add_argument("--font", default="Impact")

    sub.add_parser("brands", help="list brands")

    bn = sub.add_parser("brand-new", help="scaffold a new brand")
    bn.add_argument("--id", required=True)
    bn.add_argument("--name", required=True)
    bn.add_argument("--url", default="")
    bn.add_argument("--font", default="Impact")
    bn.add_argument("--color", action="append", default=[],
                    help="name=#rrggbb (repeatable)")

    sub.add_parser("sources", help="list bundled stills")

    tg = sub.add_parser("tag", help="tag a still into the registry")
    tg.add_argument("--src", required=True)
    tg.add_argument("--tags", required=True, help="comma-separated")
    tg.add_argument("--note", default="")
    tg.add_argument("--url", default="", help="source URL actually fetched")

    ss = sub.add_parser("search-still", help="multi-engine image search")
    ss.add_argument("--query", required=True)
    ss.add_argument("--limit", type=int, default=12)
    ss.add_argument("--commons-only", action="store_true")

    sub.add_parser("catalog", help="regenerate catalog.md/json from styles + brands")

    rev = sub.add_parser("review", help="design-rule review of a composition or brand")
    rev.add_argument("--style", default=None)
    rev.add_argument("--brand", default=None, help="review a brand doc alone (no --style)")
    rev.add_argument("--source", default=None)
    rev.add_argument("--image-type", default=None,
                     help="portrait|sculpture|void|landscape|texture (for effect pairing)")
    rev.add_argument("--seed", type=int, default=None)

    tc = sub.add_parser("techniques", help="list/search the technique catalog")
    tc.add_argument("--image-type", default=None)
    tc.add_argument("--family", default=None)
    tc.add_argument("--tag", default=None)
    tc.add_argument("--era", default=None)
    tc.add_argument("--show", default=None, help="print one technique's full JSON")

    tn = sub.add_parser("technique-new", help="scaffold a new technique entry")
    tn.add_argument("--id", required=True)
    tn.add_argument("--title", required=True)
    tn.add_argument("--family", default="grade")
    tn.add_argument("--image-type", action="append", default=[])
    tn.add_argument("--tag", action="append", default=[])
    tn.add_argument("--era", action="append", default=[])

    c = sub.add_parser("compose", help="deterministic recipe render")
    c.add_argument("--style", required=True)
    c.add_argument("--brand", default=None)
    c.add_argument("--source", default=None)
    c.add_argument("--photo2", default=None, help="optional second still (circle inset)")
    c.add_argument("--set", dest="sets", action="append", default=[])
    c.add_argument("--font", default=None)
    c.add_argument("--seed", type=int, default=None)
    c.add_argument("--out", default=None)
    c.add_argument("--engine", default="pillow",
                   choices=["pillow", "gimp_native", "cli_anything_gimp", "auto"])

    g = sub.add_parser("generate", help="emit + run a one-shot script (self-modify)")
    g.add_argument("--style", required=True)
    g.add_argument("--brand", default=None)
    g.add_argument("--source", default=None)
    g.add_argument("--photo2", default=None, help="optional second still (circle inset)")
    g.add_argument("--set", dest="sets", action="append", default=[])
    g.add_argument("--font", default=None)
    g.add_argument("--seed", type=int, default=None)
    g.add_argument("--out", default=None)

    bt = sub.add_parser("batch", help="render many stills from one style/brand template")
    bt.add_argument("--style", default=None)
    bt.add_argument("--brand", default=None)
    bt.add_argument("--source", default=None, help="default source for items that omit one")
    bt.add_argument("--photo2", default=None, help="default second still (circle inset)")
    bt.add_argument("--font", default=None)
    bt.add_argument("--seed", type=int, default=None, help="default seed")
    bt.add_argument("--manifest", required=True, help="path to a JSON list or object")
    bt.add_argument("--engine", default="pillow",
                    choices=["pillow", "gimp_native", "cli_anything_gimp", "auto"])
    bt.add_argument("--mode", default="generate", choices=["generate", "compose"])
    bt.add_argument("--out", default=None)
    bt.add_argument("--limit", type=int, default=None, help="render only the first N items")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = args.json

    try:
        if args.cmd == "doctor":
            from .bootstrap import doctor
            _print(doctor(), as_json)

        elif args.cmd == "bootstrap":
            from .bootstrap import bootstrap
            _print(bootstrap(install_gimp=args.gimp), as_json)

        elif args.cmd == "styles":
            from .style import list_styles, styles_by_family
            rows = list_styles()
            if args.family:
                ids = styles_by_family(args.family)
                rows = [r for r in rows if r["id"] in ids]
            _print(rows, as_json)

        elif args.cmd == "style-new":
            from .style import create_style
            w, h = (int(x) for x in args.canvas.split(","))
            out = create_style(args.id, family=args.family, title=args.title,
                               canvas=[w, h], background=args.background, font=args.font)
            _print({"created": str(out)}, as_json)

        elif args.cmd == "brands":
            from .brand import list_brands
            _print(list_brands(), as_json)

        elif args.cmd == "brand-new":
            from .brand import create_brand
            colors = _parse_colors(args.color)
            out = create_brand(args.id, args.name, url=args.url, colors=colors,
                               font=args.font)
            _print({"created": str(out)}, as_json)

        elif args.cmd == "sources":
            from .source import list_sources
            _print(list_sources(), as_json)

        elif args.cmd == "tag":
            from .registry import tag_image
            entry = tag_image(args.src, args.tags, note=args.note, source_url=args.url)
            _print(entry, as_json)

        elif args.cmd == "search-still":
            from .search import search_still
            cands = search_still(args.query, limit=args.limit)
            if args.commons_only:
                cands = [c for c in cands if c["engine"] == "commons"]
            _print(cands, as_json)

        elif args.cmd == "catalog":
            from .catalog import write
            _print(write(), as_json)

        elif args.cmd == "review":
            from .design import review_composition, review_brand
            if args.brand and not args.style:
                from .brand import load_brand
                findings = review_brand(load_brand(args.brand))
                _print({"brand": args.brand, "findings": findings}, as_json)
            elif args.style:
                from .compose import resolve
                resolved = resolve(args.style, brand_id=args.brand,
                                   source=args.source, seed=args.seed)
                findings = review_composition(resolved, image_type=args.image_type)
                _print({"style": args.style, "brand": resolved.get("brand_id"),
                        "findings": findings}, as_json)
            else:
                raise SystemExit("review needs --style (or --brand alone)")

        elif args.cmd == "techniques":
            from .technique import list_techniques, find_techniques, load_technique
            if args.show:
                _print(load_technique(args.show), as_json)
            else:
                _print(find_techniques(image_type=args.image_type, family=args.family,
                                       tag=args.tag, era=args.era), as_json)

        elif args.cmd == "technique-new":
            from .technique import create_technique
            out = create_technique(args.id, args.title, family=args.family,
                                   image_types=args.image_type, tags=args.tag,
                                   era=args.era)
            _print({"created": str(out)}, as_json)

        elif args.cmd == "compose":
            from .compose import compose
            from . import OUT_DIR
            overrides = _parse_sets(args.sets)
            out_dir = Path(args.out) if args.out else OUT_DIR
            result = compose(args.style, brand_id=args.brand, source=args.source,
                             photo2=args.photo2,
                             copy_overrides=overrides or None, font_override=args.font,
                             seed=args.seed, out_dir=out_dir, engine=args.engine)
            _print({k: v for k, v in result.items() if k not in ("resolved", "project")},
                   as_json)

        elif args.cmd == "generate":
            from .library import generate
            from . import OUT_DIR
            overrides = _parse_sets(args.sets)
            out_dir = Path(args.out) if args.out else OUT_DIR
            result = generate(args.style, brand_id=args.brand, source=args.source,
                              photo2=args.photo2,
                              copy_overrides=overrides or None, font_override=args.font,
                              seed=args.seed, out_dir=out_dir)
            _print({k: v for k, v in result.items() if k != "resolved"}, as_json)

        elif args.cmd == "batch":
            from .batch import render_batch, load_manifest
            from . import OUT_DIR
            manifest = load_manifest(args.manifest)
            out_dir = Path(args.out) if args.out else OUT_DIR
            result = render_batch(
                args.style, manifest, brand=args.brand, source=args.source,
                photo2=args.photo2, font=args.font, seed=args.seed,
                engine=args.engine, mode=args.mode, out_dir=out_dir,
                limit=args.limit)
            _print(result, as_json)

        return 0

    except SystemExit as e:
        if e.code:
            print(str(e.code), file=sys.stderr)
            return 2
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
