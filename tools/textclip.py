#!/usr/bin/env python3
"""Put TikTok Classic text on a whole clip (the text is on screen for the full duration, as in P011) and check the result.

Usage:
  textclip.py render <clip.mp4> --text "line one/line two/…" --out final.mp4 [--y 0.665] [--size 0.0238] [--weight 500] [--stroke 0.08] [--fill #ffffff]
  textclip.py check  <final.mp4> [--box X Y W H]      structure of the finished file → <out folder>/video_check.json

- render: scales and centre-crops to 1080x1920 (9:16), 30 fps, draws the text once (white, thin black outline, centred,
  straight quotes turned curly, "/" = forced line break, "//" = a blank line) and burns it in for the whole clip. Silent output (-an): add the sound in TikTok.
- check: duration, cut count (should be 0 for a one-shot format), largest frame-to-frame jump, motion in the subject zone.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import overlay  # noqa: E402  (curly quotes)
import portable  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920


def ffmpeg():
    return portable.exe("ffmpeg")


def draw_text(text, y, size, weight, stroke, fill="#ffffff"):
    font = ImageFont.truetype(str(ROOT / "assets" / "fonts" / f"TikTokSans-{weight}.ttf"), round(H * size))
    lines = [l.strip() for l in overlay.curly(text).split("/")]
    line_h = round(font.size * 1.3)
    top = round(H * y - line_h * len(lines) / 2)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fill_rgba = tuple(int(fill.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    boxes = []
    for i, line in enumerate(lines):
        x = (W - overlay.measure_mixed(line, font)) / 2
        y_top = top + i * line_h
        overlay.draw_mixed(layer, (x, y_top), line, font, fill_rgba, stroke_width=round(font.size * stroke), stroke_fill=(0, 0, 0, 255))
        boxes.append(ImageDraw.Draw(layer).textbbox((x, y_top), line, font=font))
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    return layer, [round(x0 / W * 100, 1), round(y0 / H * 100, 1), round((x1 - x0) / W * 100, 1), round((y1 - y0) / H * 100, 1)], len(lines)


def render(a):
    layer, box, n = draw_text(a.text, a.y, a.size, a.weight, a.stroke, a.fill)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    png = out.with_suffix(".text.png")
    layer.save(png)
    fc = f"[0:v]fps=30,scale={W}:-2:flags=lanczos,crop={W}:{H}[b];[b][1:v]overlay=0:0:format=auto[v]"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", a.clip, "-i", str(png), "-filter_complex", fc, "-map", "[v]", "-an",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", str(out)], check=True)
    (out.parent / "text_box.json").write_text(json.dumps({"lines": n, "box_pct": box, "y": a.y, "size": a.size, "weight": a.weight, "stroke": a.stroke, "fill": a.fill}, indent=1))
    print(f"{out}  text: {n} lines, box {box} (x, y, w, h in % of the frame)")


def check(a):
    p = Path(a.video)
    cap = cv2.VideoCapture(str(p))
    fps = cap.get(cv2.CAP_PROP_FPS)
    g = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g.append(cv2.cvtColor(cv2.resize(f, (216, 384), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32))
    n = len(g)
    d = np.array([np.abs(g[i] - g[i - 1]).mean() for i in range(1, n)])
    cuts = int((d > max(np.median(d) * 8, 6.0)).sum())
    zone = [np.abs(g[i][60:330, 20:200] - g[i - 1][60:330, 20:200]).mean() for i in range(1, n)]
    res = {"video": str(p), "seconds": round(n / fps, 2), "fps": fps, "size": [int(cap.get(3)), int(cap.get(4))],
           "cuts": cuts, "max_frame_jump": round(float(d.max()), 2), "subject_zone_motion": round(float(np.mean(zone)), 2)}
    checks = [("one shot, no cuts", cuts == 0, f"{cuts} cuts, largest frame-to-frame jump {res['max_frame_jump']}"),
              ("9:16 at 1080x1920", res["size"] == [1080, 1920], f"{res['size']}"),
              ("the subject moves (not a frozen image)", res["subject_zone_motion"] > 0.2, f"mean frame change {res['subject_zone_motion']}")]
    res["checks"] = [{"check": c, "ok": bool(o), "detail": t} for c, o, t in checks]
    res["verdict"] = "pass" if all(o for _, o, _ in checks) else "FAIL"
    (p.parent / "video_check.json").write_text(json.dumps(res, indent=1))
    print(f"video check: {res['verdict'].upper()} · {res['seconds']} s")
    for c, o, t in checks:
        print(f"  {'ok  ' if o else 'FAIL'} {c}: {t}")
    sys.exit(0 if res["verdict"] == "pass" else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("clip")
    r.add_argument("--text", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--y", type=float, default=0.665)
    r.add_argument("--size", type=float, default=0.0238)
    r.add_argument("--weight", default="500", choices=["500", "700"])
    r.add_argument("--stroke", type=float, default=0.08, help="outline width as a share of the font size; 0 = no outline")
    r.add_argument("--fill", default="#ffffff", help="text colour, e.g. #fcffb0")
    c = sub.add_parser("check")
    c.add_argument("video")
    a = ap.parse_args()
    render(a) if a.cmd == "render" else check(a)


if __name__ == "__main__":
    main()
