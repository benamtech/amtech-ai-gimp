#!/usr/bin/env python3
"""Non-deterministic style runner for cli-anything-gimp.

    uv run --with pillow python run_style.py --list
    uv run --with pillow python run_style.py --style swiss-poster --photo /abs/a.jpg
    uv run --with pillow python run_style.py --family viral --photo /abs/a.jpg
    uv run --with pillow python run_style.py --random --photo /abs/a.jpg --seed 7

Each styles/<id>.json is a recipe. The runner samples ranges, picks copy,
places the photo, draws overlay type, renders, prints JSON.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
# In the amtech-computer-use-graphics repo the style recipes live at the
# bundle root `styles/` (this file lives in `scripts/`). Fall back to the
# legacy in-skill `scripts/styles/` location for back-compat.
STYLES = HERE / "styles" if (HERE / "styles").is_dir() else HERE.parent / "styles"
CLI = shutil.which("cli-anything-gimp") or str(Path.home() / ".local/bin/cli-anything-gimp")
sys.path.insert(0, str(HERE))
from ensure_fonts import resolve_font  # noqa: E402
from brand import load_brand  # noqa: E402


def sample(rng: random.Random, spec):
    if isinstance(spec, dict) and "choices" in spec:
        return sample(rng, rng.choice(spec["choices"]))
    if isinstance(spec, dict) and "range" in spec:
        lo, hi = spec["range"]
        if isinstance(lo, int) and isinstance(hi, int):
            return rng.randint(lo, hi)
        return rng.uniform(float(lo), float(hi))
    if isinstance(spec, list) and spec and not isinstance(spec[0], (str, int, float)):
        return [sample(rng, x) for x in spec]
    return spec


def interpolate(text: str, slots: dict[str, str]) -> str:
    out = text
    for k, v in slots.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def run_cli(project: Path, args: list[str]) -> dict:
    proc = subprocess.run(
        [CLI, "--json", "--project", str(project), *args],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(f"failed: {args}")
    text = proc.stdout.strip()
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {"raw": text}


def commons_url(title: str) -> str:
    api = (
        "https://commons.wikimedia.org/w/api.php?action=query"
        f"&titles={quote(title)}&prop=imageinfo&iiprop=url&format=json"
    )
    req = Request(api, headers={"User-Agent": "HermesAgent/1.0"})
    with urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    page = next(iter(data["query"]["pages"].values()))
    if "missing" in page or not page.get("imageinfo"):
        raise SystemExit(f"commons miss: {title}")
    return page["imageinfo"][0]["url"].split("?", 1)[0]


def load_photo(src: str, dest: Path) -> None:
    p = Path(src)
    if p.exists():
        dest.write_bytes(p.read_bytes())
        return
    if src.startswith("File:"):
        url = commons_url(src)
        req = Request(url, headers={"User-Agent": "HermesAgent/1.0"})
        with urlopen(req, timeout=180) as resp:
            dest.write_bytes(resp.read())
        return
    raise SystemExit(f"photo not found: {src}")


def list_styles() -> list[dict]:
    rows = []
    for path in sorted(STYLES.glob("*.json")):
        data = json.loads(path.read_text())
        rows.append({"id": data.get("id", path.stem), "family": data.get("family", "?"),
                     "title": data.get("title", path.stem), "file": path.name})
    return rows


def fit_cover(src: Path, dest: Path, w: int, h: int, rng: random.Random, jitter) -> None:
    from PIL import Image
    img = Image.open(src).convert("RGB")
    scale = max(w / img.width, h / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    jx = jitter[0] if jitter else 0
    jy = jitter[1] if jitter else 0
    left = max(0, min(nw - w, (nw - w) // 2 + rng.randint(-jx, jx)))
    top = max(0, min(nh - h, (nh - h) // 2 + rng.randint(-jy, jy)))
    img.crop((left, top, left + w, top + h)).save(dest, quality=95)


def pillow_grade(panel: Path, w: int, h: int, ops: dict, inset_src: str | None) -> None:
    """Looks the harness cannot draw: lift, circle inset, ring."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
    img = Image.open(panel).convert("RGB")
    if ops.get("contrast"):
        img = ImageEnhance.Contrast(img).enhance(float(ops["contrast"]))
    if ops.get("color"):
        img = ImageEnhance.Color(img).enhance(float(ops["color"]))
    if ops.get("bottom_lift"):
        lift = Image.new("RGB", (w, h), (0, 0, 0))
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        top = int(h * float(ops.get("lift_start", 0.45)))
        for y in range(top, h):
            a = int(255 * ((y - top) / max(1, h - top)) ** 1.4)
            draw.line([(0, y), (w, y)], fill=min(255, a))
        img = Image.composite(lift, img, mask)
    inset = ops.get("circle_inset")
    if inset and inset_src:
        src = Path(inset_src)
        tmp = panel.parent / "_inset.bin"
        if src.exists() or str(inset_src).startswith("File:"):
            load_photo(str(inset_src), tmp)
            face = Image.open(tmp).convert("RGB")
            d = int(min(w, h) * float(inset.get("d", 0.32)))
            side = min(face.width, face.height)
            lft = (face.width - side) // 2
            top = (face.height - side) // 2
            face = face.crop((lft, top, lft + side, top + side)).resize((d, d), Image.Resampling.LANCZOS)
            cx = int(w * float(inset.get("cx", 0.78)))
            cy = int(h * float(inset.get("cy", 0.22)))
            ring = int(inset.get("ring", 10))
            ring_color = inset.get("ring_color", "#f15a22")
            canvas = img.convert("RGBA")
            disc = Image.new("RGBA", (d + ring * 2, d + ring * 2), (0, 0, 0, 0))
            dd = ImageDraw.Draw(disc)
            dd.ellipse((0, 0, d + ring * 2 - 1, d + ring * 2 - 1), fill=ring_color)
            mask = Image.new("L", (d, d), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
            face_r = face.convert("RGBA")
            face_r.putalpha(mask)
            disc.paste(face_r, (ring, ring), face_r)
            canvas.paste(disc, (cx - d // 2 - ring, cy - d // 2 - ring), disc)
            img = canvas.convert("RGB")
    img.save(panel, quality=95)


def apply_style(style: dict, photo: str, out_dir: Path, rng: random.Random,
                photo2: str | None = None, copy_overrides: dict | None = None,
                font_override: str | None = None) -> dict:
    w, h = sample(rng, style["canvas"])
    bg = sample(rng, style.get("background", "#0b1220"))
    out_dir.mkdir(parents=True, exist_ok=True)
    sid = style["id"]
    project = out_dir / f"{sid}.gimp-cli.json"
    poster = out_dir / f"{sid}.png"
    raw = out_dir / f"{sid}-src.bin"
    panel = out_dir / f"{sid}-panel.jpg"
    load_photo(photo, raw)
    jitter = style.get("photo", {}).get("offset_jitter", [24, 24])
    fit_cover(raw, panel, w, h, rng, jitter)
    if style.get("pillow"):
        pillow_grade(panel, w, h, style["pillow"], photo2)

    if project.exists():
        project.unlink()
    subprocess.run(
        [CLI, "--json", "project", "new", "--width", str(w), "--height", str(h),
         "--mode", "RGB", "--background", str(bg), "-o", str(project)],
        check=True, capture_output=True, text=True,
    )
    run_cli(project, ["layer", "add-from-file", str(panel), "--name", "photo"])
    ox = int(sample(rng, style.get("photo", {}).get("offset_x", 0)))
    oy = int(sample(rng, style.get("photo", {}).get("offset_y", 0)))
    run_cli(project, ["layer", "set", "0", "offset_x", str(ox)])
    run_cli(project, ["layer", "set", "0", "offset_y", str(oy)])
    if style.get("photo", {}).get("blend"):
        run_cli(project, ["layer", "set", "0", "mode", sample(rng, style["photo"]["blend"])])
    if style.get("photo", {}).get("opacity") is not None:
        run_cli(project, ["layer", "set", "0", "opacity", str(sample(rng, style["photo"]["opacity"]))])
    for filt in style.get("filters", []):
        name = filt["name"]
        args = ["filter", "add", name, "--layer", "0"]
        for k, v in (filt.get("param") or {}).items():
            args.extend(["--param", f"{k}={sample(rng, v)}"])
        run_cli(project, args)

    run_cli(project, ["layer", "new", "--name", "copy", "--type", "image",
                      "--width", str(w), "--height", str(h), "--fill", "transparent"])

    if font_override:
        style["font"] = font_override
    if style.get("font"):
        style["font"] = resolve_font(style["font"])
    slots = {}
    for key, spec in (style.get("copy") or {}).items():
        slots[key] = sample(rng, spec if isinstance(spec, dict) else {"choices": spec})
    if copy_overrides:
        for k, v in copy_overrides.items():
            slots[k] = v

    for rect in style.get("rects", []):
        x1 = int(eval_num(rect["x1"], w, h, rng))
        y1 = int(eval_num(rect["y1"], w, h, rng))
        x2 = int(eval_num(rect["x2"], w, h, rng))
        y2 = int(eval_num(rect["y2"], w, h, rng))
        fill = sample(rng, rect.get("fill", "#000000"))
        run_cli(project, ["draw", "rect", "--layer", "0",
                          "--x1", str(x1), "--y1", str(y1),
                          "--x2", str(x2), "--y2", str(y2), "--fill", str(fill)])

    for t in style.get("texts", []):
        text = interpolate(sample(rng, t.get("text", "")), slots)
        x = int(eval_num(t.get("x", 48), w, h, rng))
        y = int(eval_num(t.get("y", 80), w, h, rng))
        size = int(sample(rng, t.get("size", 24)))
        color = sample(rng, t.get("color", "#f6f1e8"))
        cmd = ["draw", "text", "--layer", "0", "--text", text,
               "--x", str(x), "--y", str(y),
               "--size", str(size), "--color", str(color)]
        font = t.get("font") or style.get("font")
        if font:
            cmd.extend(["--font", resolve_font(str(font))])
        run_cli(project, cmd)

    result = run_cli(project, ["export", "render", str(poster), "--overwrite"])
    result["style"] = sid
    result["seed_note"] = "non-deterministic unless --seed is set"
    result["poster"] = str(poster)
    return result


def eval_num(expr, w, h, rng: random.Random):
    if isinstance(expr, (int, float)):
        return expr
    if isinstance(expr, dict):
        return sample(rng, expr)
    if isinstance(expr, str):
        return eval(expr, {"__builtins__": {}}, {"W": w, "H": h, "int": int, "float": float, "min": min, "max": max})
    return 0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--style")
    p.add_argument("--family")
    p.add_argument("--random", action="store_true")
    p.add_argument("--photo", default="File:The_Earth_seen_from_Apollo_17.jpg")
    p.add_argument("--photo2", default=None, help="optional second still (circle inset)")
    p.add_argument("--out", default=str(Path.home() / "Pictures" / "cli-anything-poster" / "styles"))
    p.add_argument("--seed", type=int)
    p.add_argument("--font", default=None, help="Impact / family name / absolute TTF path")
    p.add_argument("--brand", default=None, help="brand id or path to compact JSON")
    p.add_argument("--set", dest="sets", action="append", default=[],
                   help="override copy slot, e.g. --set l1=THE RIZZLER")
    args = p.parse_args()

    if args.list or (not args.style and not args.family and not args.random):
        rows = list_styles()
        print(json.dumps(rows, indent=2))
        print(f"count={len(rows)}", file=sys.stderr)
        return

    rng = random.Random(args.seed)
    catalog = {r["id"]: r for r in list_styles()}
    if args.style:
        sid = args.style
    elif args.family:
        pool = [r["id"] for r in list_styles() if r["family"] == args.family]
        if not pool:
            raise SystemExit(f"no styles in family {args.family}")
        sid = rng.choice(pool)
    else:
        sid = rng.choice(list(catalog))
    style = json.loads((STYLES / f"{sid}.json").read_text())
    if args.brand or style.get("brand"):
        brand = load_brand(args.brand or style.get("brand"))
        style.setdefault("_brand", brand)
        c = brand.get("c") or {}
        if c.get("k"):
            style["background"] = c["k"]
        if brand.get("font"):
            style["font"] = brand["font"]
        if isinstance(style.get("pillow"), dict) and c.get("mag"):
            inset = style["pillow"].setdefault("circle_inset", {})
            inset["ring_color"] = c["mag"]
    overrides = {}
    for item in args.sets:
        if "=" not in item:
            raise SystemExit(f"--set needs KEY=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        overrides[k.strip()] = v
    result = apply_style(style, args.photo, Path(args.out), rng, photo2=args.photo2,
                         copy_overrides=overrides or None, font_override=args.font)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
