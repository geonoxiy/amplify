#!/usr/bin/env python3
"""Render and check a progress-tracker workout reel (pillar P009): hard cuts between animated clips, with the title,
the tracker of muscle icons and the exercise name drawn in code (never by the AI model).

Usage:
  reel.py frames <spec.json>    compose each shot's first frame (art on the card background, top and bottom left empty)
                                → <run>/raw/frames/shotN.png. Feed these to `kie.py video --first-frame`.
  reel.py render <spec.json>    cut the clips to the shot length, draw the overlay, encode <run>/output/reel.mp4 (silent)
                                + <run>/output/reel_timing.json (cuts, tick times, text changes)
  reel.py check  <spec.json>    re-measure the finished MP4 from its pixels and compare it with the pillar → output/video_check.json

Spec (paths relative to the project root):
  {"run": "content-bank/P009-…/runs/run-01_…", "canvas": [1080, 1920], "fps": 30,
   "theme": {…cards.py theme…}, "title": "The Perfect Upper Traps Workout",
   "title_ref": "The Perfect Pull Workout",          # the source title; sets the title size (46.4% of the frame width)
   "icon": {"art": "path.png", "crop_top": 0.62},    # tracker icon, repeated 6 times
   "layout": {"art_box": [8, 42, 84, 38], "tracker_box": [5.6, 18.1, 91.6, 8.9], "title_y": 14.0, "name_y": 29.3},
   "timing": {"shot": 2.7, "tick_at": 1.2, "title_in": [0.15, 0.9]},
   "shots": [{"name": "…", "reps": "2-3 x 8-12", "still": "path.png", "clip": "raw/clipN.mp4", "prompt": "…"}],
   "sources": ["content-bank/P009-…/originals/<id>/analysis/frames"]}   # for the near-duplicate check
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards  # noqa: E402
import portable  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
S = 2  # overlay supersampling


def load(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    spec["_run"] = ROOT / spec["run"]
    spec["_theme"] = {**cards.DEFAULT_THEME, **spec.get("theme", {})}
    return spec


def ffmpeg():
    return portable.exe("ffmpeg")


# ---------------------------------------------------------------- frames
def cmd_frames(spec):
    W, H = spec["canvas"]
    out_dir = spec["_run"] / "raw" / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, shot in enumerate(spec["shots"], 1):
        card = cards.Card(ROOT, spec["canvas"], spec["_theme"])
        art, _ = card.load_art(shot["still"])
        card.place_art(art, spec["layout"]["art_box"], align="center-bottom")
        p = out_dir / f"shot{i}.png"
        card.finish(p)
        print(p)


# ---------------------------------------------------------------- overlay layers
def font_for_width(path, text, width_px):
    size = 100
    f = ImageFont.truetype(path, size)
    return ImageFont.truetype(path, max(int(size * width_px / f.getlength(text)), 8))


def to_rgba_array(img):
    small = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    a = np.asarray(small).astype(np.float32)
    return a[..., :3], a[..., 3:] / 255.0


class Layers:
    def __init__(self, spec):
        self.W, self.H = spec["canvas"]
        self.t = spec["_theme"]
        self.spec = spec
        lay = spec["layout"]
        self.hfont_path = self.t["heading_font"]
        ref_w = 0.464 * self.W * S
        self.title_font = font_for_width(self.hfont_path, spec["title_ref"], ref_w)
        self.title = self.draw_title(spec["title"], lay["title_y"])
        icon_art, _ = cards.Card(ROOT, spec["canvas"], self.t).load_art(spec["icon"]["art"], spec["icon"].get("crop_top"))
        self.icon = Image.fromarray(cv2.cvtColor(icon_art, cv2.COLOR_BGR2RGB))
        self.tracker = [self.draw_tracker(n) for n in range(len(spec["shots"]) + 1)]
        self.names = [self.draw_name(s["name"], s["reps"], lay["name_y"]) for s in spec["shots"]]

    def canvas(self):
        return Image.new("RGBA", (self.W * S, self.H * S), (0, 0, 0, 0))

    def draw_title(self, text, y_pct):
        im = self.canvas()
        d = ImageDraw.Draw(im)
        d.text((self.W * S / 2, self.H * S * y_pct / 100), text, font=self.title_font, fill=cards.hex_rgb(self.t["ink"]) + (255,), anchor="mm")
        return to_rgba_array(im)

    def draw_tracker(self, ticks):
        lay = self.spec["layout"]["tracker_box"]
        x, y, w, h = [v * S for v in (lay[0] / 100 * self.W, lay[1] / 100 * self.H, lay[2] / 100 * self.W, lay[3] / 100 * self.H)]
        shadow = self.canvas()
        ImageDraw.Draw(shadow).rounded_rectangle((x, y + 4 * S, x + w, y + h + 4 * S), radius=14 * S, fill=(0, 0, 0, 70))
        shadow = shadow.filter(ImageFilter.GaussianBlur(7 * S))
        im = Image.alpha_composite(shadow, self.canvas())
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x, y, x + w, y + h), radius=14 * S, fill=(255, 255, 255, 255))
        n = len(self.spec["shots"])
        cell = w / n
        icon_h = h * 0.50
        k = icon_h / self.icon.height
        ic = self.icon.resize((max(int(self.icon.width * k), 1), int(icon_h)), Image.LANCZOS)
        r = h * 0.085
        for i in range(n):
            cx = x + cell * (i + 0.5)
            im.paste(ic, (int(cx - ic.width / 2), int(y + h * 0.08)))
            cy = y + h * 0.08 + icon_h + h * 0.12 + r
            if i < ticks:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cards.hex_rgb(self.t["accent"]) + (255,))
                d.line([(cx - r * 0.5, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.42), (cx + r * 0.55, cy - r * 0.4)],
                       fill=(255, 255, 255, 255), width=int(r * 0.28), joint="curve")
            else:
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255), outline=(200, 204, 206, 255), width=max(int(r * 0.16), 1))
        return to_rgba_array(im)

    def draw_name(self, name, reps, y_pct):
        im = self.canvas()
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(self.hfont_path, int(self.title_font.size * 0.86))
        ink = cards.hex_rgb(self.t["ink"]) + (255,)
        d.text((self.W * S / 2, self.H * S * y_pct / 100), name, font=f, fill=ink, anchor="mm")
        d.text((self.W * S / 2, self.H * S * (y_pct + 3.0) / 100), reps, font=f, fill=ink, anchor="mm")
        return to_rgba_array(im)


def blend(base, layer, alpha_scale=1.0, rows=None):
    rgb, a = layer
    a = a * alpha_scale
    r0, r1 = rows
    base[r0:r1] = base[r0:r1] * (1 - a[r0:r1]) + rgb[r0:r1] * a[r0:r1]


# ---------------------------------------------------------------- render
def cmd_render(spec):
    W, H = spec["canvas"]
    fps, tm = spec["fps"], spec["timing"]
    layers = Layers(spec)
    shot_len, tick_at = tm["shot"], tm["tick_at"]
    fade0, fade1 = tm["title_in"]
    out_dir = spec["_run"] / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "reel.mp4"
    total = int(round(shot_len * len(spec["shots"]) * fps))
    proc = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                             "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-movflags", "+faststart", str(out)],
                            stdin=subprocess.PIPE)
    caps = [cv2.VideoCapture(str(spec["_run"] / s["clip"])) for s in spec["shots"]]
    for c, s in zip(caps, spec["shots"]):
        if not c.isOpened():
            sys.exit(f"cannot open {s['clip']}")
    frames_in = [int(c.get(cv2.CAP_PROP_FRAME_COUNT)) for c in caps]
    fps_in = [c.get(cv2.CAP_PROP_FPS) or 24 for c in caps]
    cache = {}
    timing = {"fps": fps, "shot_seconds": shot_len, "cuts": [], "ticks": [], "texts": []}
    prev_i = 0
    top_rows = (0, int(H * 0.36))
    for n in range(total):
        t = n / fps
        i = min(int(t // shot_len), len(spec["shots"]) - 1)
        t_in = t - i * shot_len
        idx = min(int(round(t_in * fps_in[i])), frames_in[i] - 1)
        if (i, idx) not in cache:
            caps[i].set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, fr = caps[i].read()
            if not ok:
                sys.exit(f"could not read frame {idx} of clip {i + 1}")
            fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
            if fr.shape[1] != W or fr.shape[0] != H:
                fr = cv2.resize(fr, (W, H), interpolation=cv2.INTER_CUBIC)
            cache = {(i, idx): fr}
        base = cache[(i, idx)].astype(np.float32).copy()
        ticks = i + (1 if t_in >= tick_at else 0)
        fade = float(np.clip((t - fade0) / (fade1 - fade0), 0, 1)) if i == 0 else 1.0
        blend(base, layers.title, fade, top_rows)
        blend(base, layers.tracker[ticks], fade, top_rows)
        blend(base, layers.names[i], 1.0, (0, int(H * 0.36)))
        proc.stdin.write(np.clip(base, 0, 255).astype(np.uint8).tobytes())
        if i != prev_i:
            prev_i = i
            timing["cuts"].append(round(t, 3))
            timing["texts"].append({"t": round(t, 3), "name": spec["shots"][i]["name"]})
        if n == 0:
            timing["texts"].append({"t": 0.0, "name": spec["shots"][0]["name"]})
        if abs(t_in - tick_at) < 0.5 / fps:
            timing["ticks"].append({"t": round(t, 3), "count": i + 1})
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    (out_dir / "reel_timing.json").write_text(json.dumps(timing, indent=1))
    print(f"{out}  ({total / fps:.1f} s, {len(timing['cuts'])} cuts)")


# ---------------------------------------------------------------- check
def read_gray(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames, rgb_keep = [], []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(cv2.resize(fr, (216, 384), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32))
        rgb_keep.append(fr if len(frames) % 15 == 1 else None)
    return fps, frames, rgb_keep


def cmd_check(spec):
    import imagehash
    out_dir = spec["_run"] / "output"
    mp4 = out_dir / "reel.mp4"
    fps, gray, keep = read_gray(mp4)
    n = len(gray)
    diffs = np.array([np.abs(gray[i] - gray[i - 1]).mean() for i in range(1, n)])
    # a hard cut is a frame-to-frame jump far above the movement inside a shot
    thr = max(np.median(diffs) * 8, 6.0)
    raw_cuts = [i for i, d in enumerate(diffs, 1) if d > thr]
    # a clip's first frame often jumps to its second, right after a real cut: count detections within 0.25 s as one cut
    cuts = [c for k, c in enumerate(raw_cuts) if k == 0 or c - raw_cuts[k - 1] > 0.25 * fps]
    bounds = [0] + cuts + [n]
    shots = [round((b - a) / fps, 2) for a, b in zip(bounds, bounds[1:])]
    motion = []
    for a, b in zip(bounds, bounds[1:]):
        seg = [np.abs(gray[i][100:300] - gray[i - 1][100:300]).mean() for i in range(a + 1, b)]
        motion.append(round(float(np.mean(seg)), 2) if seg else 0)
    H = gray[0].shape[0]
    bottom_ink = round(float(np.mean([(np.abs(g[int(H * 0.8):] - np.median(g[int(H * 0.8):])) > 25).mean() for g in gray])) * 100, 2)
    checks = []

    def add(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    total = round(n / fps, 2)
    add("length 16 to 16.8 s (pillar range; a longer variant exists)", 15.5 <= total <= 17.5, f"{total} s")
    add("6 shots, 5 hard cuts", len(cuts) == 5, f"{len(cuts)} cuts at {[round(c / fps, 2) for c in cuts]} s")
    add("shot lengths 2.4 to 3.1 s", all(2.3 <= s <= 3.2 for s in shots), f"{shots}")
    add("every clip moves (not a frozen image)", all(m > 0.15 for m in motion), f"mean frame change in the art zone per shot: {motion}")
    add("bottom 20% left empty", bottom_ink < 1.0, f"{bottom_ink}% of bottom-fifth pixels differ from the background")
    hashes = [imagehash.phash(Image.fromarray(cv2.cvtColor(k, cv2.COLOR_BGR2RGB))) for k in keep if k is not None]
    best = (99, "")
    for d in spec.get("sources", []):
        for f in sorted((ROOT / d).glob("*.jpg")):
            h = imagehash.phash(Image.open(f))
            for oh in hashes:
                if int(oh - h) < best[0]:
                    best = (int(oh - h), f"{Path(d).parent.parent.name}/{f.name}")
    if spec.get("sources"):
        add("no near-duplicate of a source frame (hash distance above 10)", best[0] > 10, f"closest {best[0]} bits ({best[1]}); source frames include their overlay and tracker")
    else:
        add("no near-duplicate of a source frame", False, "not checked: no source frames listed in the spec")
    result = {"video": str(mp4.relative_to(ROOT)), "fps": fps, "frames": n, "checks": checks,
              "verdict": "pass" if all(c["ok"] for c in checks) else "FAIL"}
    (out_dir / "video_check.json").write_text(json.dumps(result, indent=1))
    print(f"video check: {result['verdict'].upper()}")
    for c in checks:
        print(f"  {'ok  ' if c['ok'] else 'FAIL'} {c['check']}: {c['detail']}")
    sys.exit(0 if result["verdict"] == "pass" else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["frames", "render", "check"])
    ap.add_argument("spec")
    a = ap.parse_args()
    spec = load(a.spec)
    {"frames": cmd_frames, "render": cmd_render, "check": cmd_check}[a.cmd](spec)


if __name__ == "__main__":
    main()
