#!/usr/bin/env python3
"""The local half of the Reddit / Letterboxd screenshot method (doc/Screenshot Capture Method (Reddit and Letterboxd).md).

The browser half (Claude in Chrome: window size, screenshots, the round-trip download into ~/Downloads) is a procedure in
that doc and in the skill. Once a source screenshot is on disk, this tool does the deterministic steps.

Usage:
  shots.py crop <source.png> --box L T R B --out <card.png> [--bg 14,17,19] [--pad 26] [--scrollbar 14]
      Crop one card out of a screenshot, auto-trim to the content bounds (pixels that differ from the page background),
      add a fixed pad, and rebuild the image from raw pixels so no metadata carries over. Give the box generous vertical slack.
      --bg is the page background: Reddit dark mode 14,17,19; for Letterboxd pass the page's own colour.
  shots.py blur <image.png> --box L T R B [--box ...] [--mode pixelate|black|blur] [--out <file>]
      Offline fallback: hide the given regions of a finished screenshot or card (usernames, avatars) and rebuild it without
      metadata. Default mode pixelate (coarse blocks, then a light blur: not reversible). Use it only when the in-page blur
      (tools/blur_usernames.js) missed something; boxes are in the image's own pixels. Edits in place unless --out is given.
  shots.py strip <file.png> [...]
      Rebuild PNGs in place from raw pixels and verify Image.info is empty.
  shots.py check <folder> --site reddit|letterboxd
      Check a finished idea folder: 9 images (00_title.png + reply_1..8.png or review_1..8.png), each a clean PNG without
      metadata and not blank; caption.txt in the Hook / Caption / (Source, Reddit only) / exactly 3 hashtags format with no em-dashes;
      the folder name (Reddit: a 3-word summary, no punctuation).
"""
import argparse
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageStat

EM_DASH = "—"


def rebuild(im):
    """A fresh RGB image from raw pixels: nothing from the source's .info (ICC profile, dpi, text chunks) survives."""
    return Image.fromarray(np.asarray(im.convert("RGB")))


def crop(a):
    im = Image.open(a.source).convert("RGB")
    l, t, r, b = a.box
    r = min(r, im.width - a.scrollbar)  # the scrollbar sliver Chrome renders at the right edge
    c = im.crop((l, t, r, b))
    bg = Image.new("RGB", c.size, tuple(int(v) for v in a.bg.split(",")))
    bbox = ImageChops.difference(c, bg).point(lambda p: 255 if p > 10 else 0).getbbox()
    if bbox:
        left, top, right, bottom = bbox
        c = c.crop((max(0, left - a.pad), max(0, top - a.pad), min(c.width, right + a.pad), min(c.height, bottom + a.pad)))
    else:
        print("  warning: nothing differs from the background colour in this box; kept the box as is")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rebuild(c).save(out, "PNG")
    print(f"{out}  {c.width}x{c.height}")


def blur(a):
    from PIL import ImageFilter
    im = Image.open(a.image).convert("RGB")
    for l, t, r, b in a.box:
        l, t, r, b = max(l, 0), max(t, 0), min(r, im.width), min(b, im.height)
        if r <= l or b <= t:
            sys.exit(f"box {l},{t},{r},{b} is empty or outside the {im.width}x{im.height} image")
        region = im.crop((l, t, r, b))
        if a.mode == "black":
            region = Image.new("RGB", region.size, (0, 0, 0))
        elif a.mode == "blur":
            region = region.filter(ImageFilter.GaussianBlur(max(region.height // 3, 6)))
        else:
            w, h = max(region.width // a.block, 1), max(region.height // a.block, 1)
            region = region.resize((w, h), Image.BILINEAR).resize((r - l, b - t), Image.NEAREST).filter(ImageFilter.GaussianBlur(2))
        im.paste(region, (l, t))
    out = Path(a.out or a.image)
    out.parent.mkdir(parents=True, exist_ok=True)
    rebuild(im).save(out, "PNG")
    print(f"{out}  {len(a.box)} region(s) hidden ({a.mode})")


def strip(a):
    bad = 0
    for f in a.files:
        rebuild(Image.open(f)).save(f, "PNG")
        info = Image.open(f).info
        print(f"{f}  info={info}")
        bad += bool(info)
    sys.exit(1 if bad else 0)


def check(a):
    folder = Path(a.folder)
    fails, warns = [], []
    stem = "reply" if a.site == "reddit" else "review"
    expected = ["00_title.png"] + [f"{stem}_{i}.png" for i in range(1, 9)]
    for name in expected:
        p = folder / name
        if not p.exists():
            fails.append(f"missing {name}")
            continue
        try:
            im = Image.open(p)
            fmt, info, size = im.format, dict(im.info), im.size
            rgb = im.convert("RGB")
        except Exception as e:  # noqa: BLE001
            fails.append(f"{name}: cannot open ({e})")
            continue
        if fmt != "PNG":
            fails.append(f"{name}: not a PNG ({fmt})")
        if info:
            fails.append(f"{name}: carries metadata {list(info)} (run `shots.py strip`)")
        if min(size) < 200:
            fails.append(f"{name}: only {size[0]}x{size[1]}, looks cut off")
        if max(ImageStat.Stat(rgb).stddev) < 3:
            fails.append(f"{name}: looks blank (a poster that had not loaded?)")
    extra = sorted(p.name for p in folder.glob("*.png") if p.name not in expected)
    if extra:
        warns.append(f"extra images not in the 9: {extra}")
    cap = folder / "caption.txt"
    if not cap.exists():
        fails.append("missing caption.txt")
    else:
        text = cap.read_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not any(l.startswith("Hook:") and len(l) > 6 for l in lines):
            fails.append("caption.txt: no `Hook:` line")
        if not any(l.startswith("Caption:") and len(l) > 9 for l in lines):
            fails.append("caption.txt: no `Caption:` line")
        src = [l for l in lines if l.startswith("Source:")]
        if a.site == "reddit" and not (src and re.match(r"Source: r/\w+", src[0])):
            fails.append("caption.txt: Reddit needs a `Source: r/<subreddit>` line")
        if a.site == "letterboxd" and src:
            fails.append("caption.txt: a Letterboxd caption has no `Source:` line")
        tags = re.findall(r"#\w+", lines[-1]) if lines else []
        if len(tags) != 3 or re.sub(r"#\w+|\s", "", lines[-1]):
            fails.append(f"caption.txt: the last line must be exactly 3 hashtags (found {len(tags)})")
        if EM_DASH in text:
            fails.append("caption.txt: contains an em-dash (the style rule is none)")
    if a.site == "reddit":
        words = folder.name.split()
        if len(words) != 3 or re.search(r"[^\w ]", folder.name):
            warns.append(f"folder name {folder.name!r}: Reddit folders are a 3-word summary with no punctuation")
    print(f"{a.site} folder {folder.name!r}: {'FAIL' if fails else 'PASS'} ({len(expected)} images expected)")
    for f in fails:
        print(f"  FAIL: {f}")
    for w in warns:
        print(f"  warn: {w}")
    sys.exit(1 if fails else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crop")
    c.add_argument("source")
    c.add_argument("--box", type=int, nargs=4, required=True, metavar=("L", "T", "R", "B"))
    c.add_argument("--out", required=True)
    c.add_argument("--bg", default="14,17,19")
    c.add_argument("--pad", type=int, default=26)
    c.add_argument("--scrollbar", type=int, default=14)
    bl = sub.add_parser("blur")
    bl.add_argument("image")
    bl.add_argument("--box", type=int, nargs=4, action="append", required=True, metavar=("L", "T", "R", "B"))
    bl.add_argument("--mode", choices=["pixelate", "black", "blur"], default="pixelate")
    bl.add_argument("--block", type=int, default=10, help="pixelate block size in pixels")
    bl.add_argument("--out")
    s = sub.add_parser("strip")
    s.add_argument("files", nargs="+")
    k = sub.add_parser("check")
    k.add_argument("folder")
    k.add_argument("--site", choices=["reddit", "letterboxd"], required=True)
    a = ap.parse_args()
    {"crop": crop, "blur": blur, "strip": strip, "check": check}[a.cmd](a)


if __name__ == "__main__":
    main()
