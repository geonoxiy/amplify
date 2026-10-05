#!/usr/bin/env python3
"""Hook + numbered list in white boxes over a photo or clip: the "authority scene tip list" look (P016).

The text sits on white boxes with black text, the way Instagram and TikTok draw text with a background: a hook box near
the top and a list below it, over the person's chest. Text is always drawn in code, never by the AI model.

Usage:
  boxlist.py render <spec.json> --bg <image or video> --out <file.png | file.mp4> [--seconds N]
  boxlist.py check <spec.json>

spec.json:
  {"hook": "in case nobody told you...",           text of the hook ("/" = line break)
   "hook_style": "box" | "condensed",              box: TikTok Sans bold in a white box; condensed: Barlow Condensed
   "items": ["drink water first", "…"],            the list, in order (numbers are added unless "numbered": false)
   "list_style": "block" | "lines",                block: one white panel; lines: a white strip behind each line
   "hook_y": 0.11, "list_y": 0.40,                 top of the hook and of the list, as a share of the height
   "hook_size": 0.030, "size": 0.0205,             font sizes as a share of the height
   "list_width": 0.66, "align": "left" | "center", width the list wraps at, as a share of the width
   "allowed_caps": ["Bolt", "Pharmacy", "UK"]}     capitalised words check won't warn about (brand names)

A video background is scaled and cropped to 1080x1920 at 30 fps, silent, and looped if --seconds is longer than the
clip (readers need about a second per short list item). check enforces the project's text rule (no em dash, en dash,
colon or semicolon), warns on capitals, and fails a list that runs into the bottom fifth, where the app covers it.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from overlay import draw_mixed, fit, measure_mixed  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H = 1080, 1920
INK, PAPER = (17, 17, 17, 255), (255, 255, 255, 255)
BANNED = {"—": "em dash", "–": "en dash", ":": "colon", ";": "semicolon"}


def ffmpeg():
    try:
        import portable
        return str(portable.exe("ffmpeg"))
    except Exception:
        return "ffmpeg"


def font(kind, px):
    f = {"box": "TikTokSans-700.ttf", "condensed": "BarlowCondensed-SemiBold.ttf", "list": "TikTokSans-500.ttf"}[kind]
    return ImageFont.truetype(str(FONTS / f), px)


def wrap(text, f, max_w):
    lines = []
    for part in text.split("/"):
        words, line = part.strip().split(), ""
        for w in words:
            trial = f"{line} {w}".strip()
            if line and measure_mixed(trial, f) > max_w:
                lines.append(line)
                line = w
            else:
                line = trial
        lines.append(line)
    return lines


def rounded(draw, box, r, fill):
    draw.rounded_rectangle([round(v) for v in box], radius=round(r), fill=fill)


def draw_block(img, lines_per_item, f, top, align):
    """One white panel holding every item."""
    pad, gap, lh = f.size * 0.55, f.size * 0.42, f.size * 1.22
    rows = [line for item in lines_per_item for line in item]
    width = max(measure_mixed(r, f) for r in rows) + 2 * pad
    height = len(rows) * lh + (len(lines_per_item) - 1) * gap + 2 * pad
    x0 = (W - width) / 2
    rounded(ImageDraw.Draw(img), (x0, top, x0 + width, top + height), f.size * 0.3, PAPER)
    y = top + pad
    for item in lines_per_item:
        for line in item:
            x = x0 + pad if align == "left" else (W - measure_mixed(line, f)) / 2
            draw_mixed(img, (x, y), line, f, INK)
            y += lh
        y += gap
    return (x0, top, width, height)


def draw_lines(img, lines_per_item, f, top, align):
    """A white strip behind each line, touching the next one, like a text background."""
    padx, pady = f.size * 0.42, f.size * 0.16
    lh, gap = f.size * 1.18 + 2 * pady, f.size * 0.35
    draw = ImageDraw.Draw(img)
    rows = [line for item in lines_per_item for line in item]
    left = (W - max(measure_mixed(r, f) for r in rows)) / 2 - padx
    y, x_min, x_max = top, W, 0
    for item in lines_per_item:
        for line in item:
            w = measure_mixed(line, f)
            x = left + padx if align == "left" else (W - w) / 2
            rounded(draw, (x - padx, y, x + w + padx, y + lh + 1), f.size * 0.22, PAPER)
            draw_mixed(img, (x, y + pady), line, f, INK)
            x_min, x_max = min(x_min, x - padx), max(x_max, x + w + padx)
            y += lh
        y += gap
    return (x_min, top, x_max - x_min, y - gap - top)


def layer(spec):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    boxes = {}
    hf = font(spec.get("hook_style", "box"), round(spec.get("hook_size", 0.030) * H))
    hook_lines = wrap(spec["hook"], hf, W * spec.get("hook_width", 0.80))
    pad, lh = hf.size * 0.45, hf.size * 1.18
    hw = max(measure_mixed(line, hf) for line in hook_lines) + 2 * pad
    hh = len(hook_lines) * lh + 2 * pad - hf.size * 0.1
    x0, y0 = (W - hw) / 2, spec.get("hook_y", 0.11) * H
    rounded(ImageDraw.Draw(img), (x0, y0, x0 + hw, y0 + hh), hf.size * 0.18, PAPER)
    for i, line in enumerate(hook_lines):
        draw_mixed(img, ((W - measure_mixed(line, hf)) / 2, y0 + pad + i * lh), line, hf, INK)
    boxes["hook"] = (x0, y0, hw, hh)

    lf = font("list", round(spec.get("size", 0.0205) * H))
    max_w = W * spec.get("list_width", 0.66)
    items = [f"{i}. {t}" if spec.get("numbered", True) else t for i, t in enumerate(spec["items"], 1)]
    per_item = [wrap(t, lf, max_w) for t in items]
    draw = draw_lines if spec.get("list_style", "block") == "lines" else draw_block
    top = max(spec.get("list_y", 0.40) * H, y0 + hh + lf.size)
    boxes["list"] = draw(img, per_item, lf, top, spec.get("align", "left"))
    pct = {k: [round(v / (W if i % 2 == 0 else H) * 100, 1) for i, v in enumerate(b)] for k, b in boxes.items()}
    return img, pct


def text_problems(spec):
    text = " ".join([spec["hook"], *spec["items"]])
    errors = [f"{name} ({ch!r})" for ch, name in BANNED.items() if ch in text]
    allowed = set(spec.get("allowed_caps", []))
    caps = sorted({w for w in re.findall(r"\b\w*[A-Z]\w*\b", text) if w not in allowed})
    return errors, caps


def check(a):
    spec = json.loads(Path(a.spec).read_text())
    errors, caps = text_problems(spec)
    _, pct = layer(spec)
    ok = not errors and pct["list"][1] + pct["list"][3] <= 80
    print(json.dumps({"ok": ok, "banned_punctuation": errors, "capitals": caps, "boxes_pct": pct,
                      "note": "the list must end above 80% of the height (the app covers the bottom fifth with the "
                              "caption and buttons)"}, indent=1))
    sys.exit(0 if ok else 1)


def render(a):
    spec = json.loads(Path(a.spec).read_text())
    errors, _ = text_problems(spec)
    if errors:
        sys.exit("text breaks the style rule: " + ", ".join(errors))
    img, pct = layer(spec)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bg = Path(a.bg)
    if bg.suffix.lower() in (".mp4", ".mov", ".webm", ".m4v"):
        png = out.with_suffix(".text.png")
        img.save(png)
        loop = ["-stream_loop", "-1"] if a.seconds else []
        dur = ["-t", str(a.seconds)] if a.seconds else []
        fc = (f"[0:v]fps=30,scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}[b];"
              "[b][1:v]overlay=0:0:format=auto[v]")
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", *loop, "-i", str(bg), "-i", str(png),
                        "-filter_complex", fc, "-map", "[v]", "-an", *dur, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "17", "-movflags", "+faststart", str(out)], check=True)
    else:
        base = fit(Image.open(bg).convert("RGB")).convert("RGBA")
        Image.alpha_composite(base, img).convert("RGB").save(out)
    (out.parent / f"{out.stem}_boxes.json").write_text(json.dumps({"spec": str(a.spec), "boxes_pct": pct}, indent=1))
    print(f"{out}  hook box {pct['hook']}  list box {pct['list']}  (x, y, w, h in % of the frame)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("spec")
    r.add_argument("--bg", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--seconds", type=float, help="video length; loops the clip if it is shorter")
    c = sub.add_parser("check")
    c.add_argument("spec")
    a = ap.parse_args()
    {"render": render, "check": check}[a.cmd](a)


if __name__ == "__main__":
    main()
