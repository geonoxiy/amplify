#!/usr/bin/env python3
"""Numbers that the visual data model (guideline Part 3) marks as "code": measured from pixels, never estimated.

Usage:
  measure.py visual <post or creator folder>   add visual measures (and camera motion for videos) to analysis/measures.json
  measure.py check <post folder>               for units in analysis/fingerprint.json that carry boxes: box validity,
                                               text contrast, safe-zone overlap, and analysis/boxcheck/NN.jpg (boxes drawn on the slide)
  measure.py check --record unit.json --image slide.jpg [--out DIR]     the same for one record file
  measure.py contrast <image> --box X Y W H [--fill #hex]               text-against-background contrast for one box (% of frame)
  measure.py compare <A> <B> [--max 10]        perceptual-hash distance between images (files or folders); flags near-duplicates

Boxes are [x, y, w, h] in % of the frame from the top-left (guideline 3.0).
Bands (soft, sharp, low clutter, ...) are rough and were set on the posts in the content bank. Read the numbers first.
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ZONES_FILE = ROOT / "assets" / "tiktok_safe_zones.json"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}


# ---------- per-frame visual measures ----------

def to_bgr(img):
    return cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def edge_bars(gray, min_pct=3.0):
    """Solid pure-black or pure-white bands along each edge (letterbox / pillarbox), in % of that dimension.
    Dark-mode UI (about luma 17) does not count; a UI screenshot with a truly black or white margin still can, so confirm by eye."""
    h, w = gray.shape

    def run(lines):
        n = 0
        for line in lines:
            if line.std() < 2 and (line.mean() < 8 or line.mean() > 247):
                n += 1
            else:
                break
        return n

    counts = {"top": (run(gray[i] for i in range(h // 3)), h),
              "bottom": (run(gray[h - 1 - i] for i in range(h // 3)), h),
              "left": (run(gray[:, i] for i in range(w // 3)), w),
              "right": (run(gray[:, w - 1 - i] for i in range(w // 3)), w)}
    return {k: (round(n / total * 100, 1) if n / total * 100 >= min_pct else 0.0) for k, (n, total) in counts.items()}


def visual_measures(img):
    """Brightness, contrast, saturation, sharpness, noise, clutter, letterbox bars and perceptual hashes for one image."""
    bgr = to_bgr(img)
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    def long_edge(g, n):
        s = n / max(g.shape)
        return cv2.resize(g, (round(g.shape[1] * s), round(g.shape[0] * s)), interpolation=cv2.INTER_AREA) if s < 1 else g

    sharpness = float(cv2.Laplacian(long_edge(gray, 1024), cv2.CV_64F).var())  # fixed size so posts compare
    kernel = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], np.float32)  # Immerkaer noise estimate, full resolution
    noise = float(np.sqrt(np.pi / 2) * np.abs(cv2.filter2D(gray.astype(np.float32), -1, kernel)[1:-1, 1:-1]).sum()
                  / (6 * (w - 2) * (h - 2)))
    edges = cv2.Canny(cv2.GaussianBlur(long_edge(gray, 512), (3, 3), 0), 100, 200)
    clutter = float((edges > 0).mean() * 100)  # share of pixels on an edge: a proxy for how busy the picture is
    return {
        "brightness_pct": round(float(gray.mean()) / 255 * 100, 1),
        "contrast_pct": round(float(gray.std()) / 255 * 100, 1),
        "saturation_pct": round(float(hsv[..., 1].mean()) / 255 * 100, 1),
        "sharpness": round(sharpness, 1),
        "noise_sigma": round(noise, 2),
        "clutter_pct": round(clutter, 2),
        "bars_pct": edge_bars(gray),
        "phash": str(imagehash.phash(img)),
        "dhash": str(imagehash.dhash(img)),
    }


# ---------- camera motion (videos) ----------

def _grab(cap, t, width=320):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    if not ok:
        return None
    s = width / frame.shape[1]
    return cv2.cvtColor(cv2.resize(frame, (width, round(frame.shape[0] * s))), cv2.COLOR_BGR2GRAY)


def camera_motion(video, start, end, pairs=8, gap=0.15):
    """Estimate camera motion inside one shot with dense optical flow. One global motion (shift, zoom) is fitted to the
    whole frame; what is left over is the subject moving on its own. Rough: it labels the movement, it does not prove it."""
    if end - start < 0.4:
        return None
    cap = cv2.VideoCapture(str(video))
    starts = np.linspace(start + 0.02, max(start + 0.02, end - gap - 0.05), pairs)
    shifts, zooms, rots, resid = [], [], [], []
    for t in starts:
        a, b = _grab(cap, t), _grab(cap, t + gap)
        if a is None or b is None:
            continue
        flow = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        h, w = a.shape
        ys, xs = np.mgrid[4:h:8, 4:w:8]
        x, y = xs.ravel() - w / 2, ys.ravel() - h / 2
        u, v = flow[ys, xs, 0].ravel(), flow[ys, xs, 1].ravel()
        design = np.stack([np.ones_like(x), x, y], 1)
        keep = np.ones(len(x), bool)
        for _ in range(3):  # refit on the pixels that follow the dominant motion, so a large moving subject on a still background doesn't read as camera shake
            cu, *_ = np.linalg.lstsq(design[keep], u[keep], rcond=None)  # u = a0 + a1*x + a2*y
            cv_, *_ = np.linalg.lstsq(design[keep], v[keep], rcond=None)  # v = b0 + b1*x + b2*y
            err = np.hypot(u - design @ cu, v - design @ cv_)
            keep = err <= max(1.5 * np.median(err), 0.3)
            if keep.sum() < 20:
                keep = np.ones(len(x), bool)
                break
        shifts.append((cu[0] / w * 100 / gap, cv_[0] / w * 100 / gap))       # % of width per second
        zooms.append((cu[1] + cv_[2]) / 2 * 100 / gap)                       # % scale change per second
        rots.append(np.degrees((cv_[1] - cu[2]) / 2) / gap)                  # degrees per second
        fit_u, fit_v = design @ cu, design @ cv_
        resid.append(float(np.mean(np.hypot(u - fit_u, v - fit_v)) / w * 100 / gap))
    cap.release()
    if len(shifts) < 3:
        return None
    s = np.array(shifts)
    speed = float(np.mean(np.hypot(s[:, 0], s[:, 1])))
    mean_vec = s.mean(0)
    consistency = float(np.hypot(*mean_vec) / speed) if speed > 1e-6 else 0.0
    zoom = float(np.mean(zooms))
    parts = []
    if speed >= 0.6 and consistency >= 0.6 and np.hypot(*mean_vec) >= 3:
        # the scene moves opposite to the camera: scene going left means the camera pans right
        if abs(mean_vec[0]) >= abs(mean_vec[1]):
            parts.append("pan " + ("right" if mean_vec[0] < 0 else "left"))
        else:
            parts.append("tilt " + ("down" if mean_vec[1] < 0 else "up"))
    if abs(zoom) >= 2:  # test clips: true 5.4 %/s reads 5.2; static, handheld and pan clips read under 1
        parts.append("zoom in / push-in" if zoom > 0 else "zoom out / pull-back")
    if not parts:
        parts.append("handheld" if speed >= 0.6 else "static")
    return {"label": " + ".join(parts), "speed_pct_w_per_s": round(speed, 2), "consistency": round(consistency, 2),
            "zoom_pct_per_s": round(zoom, 2), "rotation_deg_per_s": round(float(np.mean(rots)), 2),
            "subject_motion_pct_w_per_s": round(float(np.mean(resid)), 2), "pairs": len(shifts),
            "note": "rough label from optical flow; static/handheld/pan/zoom thresholds are set on test clips"}


# ---------- text contrast, safe zones, boxes ----------

def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb)


def _rgb(hexstr):
    h = hexstr.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def _luminance(rgb):
    c = np.asarray(rgb, float) / 255
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def text_contrast(img, box, fill=None):
    """Contrast between a text block and what is behind it. Background = median colour of a ring just outside the box.
    Text colour = the given hex, or sampled (mean of the pixels furthest from the background inside the box)."""
    arr = np.asarray(img.convert("RGB")).astype(float)
    H, W = arr.shape[:2]
    x0, y0 = box[0] / 100 * W, box[1] / 100 * H
    x1, y1 = x0 + box[2] / 100 * W, y0 + box[3] / 100 * H
    pad = max(3, 0.6 * min(x1 - x0, y1 - y0))
    ax0, ay0, ax1, ay1 = (max(0, int(x0 - pad)), max(0, int(y0 - pad)), min(W, int(x1 + pad)), min(H, int(y1 + pad)))
    ix0, iy0, ix1, iy1 = int(x0), int(y0), max(int(x0) + 1, int(x1)), max(int(y0) + 1, int(y1))
    mask = np.ones((ay1 - ay0, ax1 - ax0), bool)
    mask[iy0 - ay0:iy1 - ay0, ix0 - ax0:ix1 - ax0] = False
    ring = arr[ay0:ay1, ax0:ax1][mask]
    bg = np.median(ring, axis=0)
    inside = arr[iy0:iy1, ix0:ix1].reshape(-1, 3)
    if fill:
        text, text_src = _rgb(fill), "record"
    else:
        # dominant colour among the pixels clearly unlike the background (a mean would blend the fill with its shadow or outline)
        dist = np.abs(inside - bg).sum(1)
        far = inside[dist > max(60, 0.5 * dist.max())]
        if len(far) < 3:
            far = inside[np.argsort(-dist)[:max(3, len(inside) // 30)]]
        key = (far // 16).astype(int) @ np.array([256, 16, 1])
        vals, counts = np.unique(key, return_counts=True)
        text, text_src = far[key == vals[np.argmax(counts)]].mean(0), "sampled"
    lo, hi = sorted([_luminance(text), _luminance(bg)])
    ratio = (hi + 0.05) / (lo + 0.05)
    return {"bg_hex": _hex(bg), "text_hex": _hex(text), "text_hex_source": text_src, "contrast_ratio": round(ratio, 2),
            "band": "low (<3)" if ratio < 3 else "ok for large text (3-4.5)" if ratio < 4.5 else "good (4.5+)"}


def safe_zone_overlap(box, aspect):
    """Share of the box that lies inside each TikTok UI zone. The zones in assets/tiktok_safe_zones.json are NOT calibrated yet."""
    cfg = json.loads(ZONES_FILE.read_text())
    if abs(aspect - cfg["aspect"]) > 0.05:
        return {"applies": False, "note": f"zones are for 9:16 (aspect {aspect:.2f} here)"}
    x, y, w, h = box
    out = {"applies": True, "calibrated": cfg["calibrated"]}
    for name, (zx, zy, zw, zh) in cfg["zones"].items():
        ox = max(0, min(x + w, zx + zw) - max(x, zx))
        oy = max(0, min(y + h, zy + zh) - max(y, zy))
        out[name] = round(ox * oy / (w * h) * 100, 1) if w * h else 0.0
    return out


def box_problems(box, label):
    if not (isinstance(box, (list, tuple)) and len(box) == 4 and all(isinstance(v, (int, float)) for v in box)):
        return [f"{label}: box is not [x, y, w, h]"]
    x, y, w, h = box
    out = []
    if w <= 0 or h <= 0:
        out.append(f"{label}: width or height is not positive")
    if x < 0 or y < 0 or x + w > 100.5 or y + h > 100.5:
        out.append(f"{label}: box leaves the frame {box}")
    return out


def draw_boxes(img, unit):
    """Draw the recorded boxes on the slide so a misplaced one is easy to see."""
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    font = ImageFont.load_default(size=max(14, W // 60))

    def px(b):
        return (b[0] / 100 * W, b[1] / 100 * H, (b[0] + b[2]) / 100 * W, (b[1] + b[3]) / 100 * H)

    comp = (unit.get("frame") or {}).get("composition") or {}
    for b in comp.get("negative_space") or []:
        if len(b) == 4:
            draw.rectangle(px(b), fill=(120, 120, 120, 40), outline=(120, 120, 120, 160), width=2)
    for i, layer in enumerate((unit.get("frame") or {}).get("layers") or [], 1):
        if isinstance(layer.get("box"), list) and len(layer["box"]) == 4 and layer.get("type") not in ("background", "text-block"):
            draw.rectangle(px(layer["box"]), outline=(40, 110, 255, 230), width=3)
            draw.text((px(layer["box"])[0] + 3, px(layer["box"])[1] + 2), f"L{i} {layer.get('type', '')}", fill=(40, 110, 255, 255), font=font)
    if isinstance(comp.get("subject_box"), list) and len(comp["subject_box"]) == 4:
        draw.rectangle(px(comp["subject_box"]), outline=(255, 140, 0, 230), width=3)
    if isinstance(comp.get("focal"), list) and len(comp["focal"]) == 2:
        fx, fy = comp["focal"][0] / 100 * W, comp["focal"][1] / 100 * H
        draw.line([(fx - 14, fy), (fx + 14, fy)], fill=(255, 0, 0, 255), width=3)
        draw.line([(fx, fy - 14), (fx, fy + 14)], fill=(255, 0, 0, 255), width=3)
    for i, tb in enumerate(unit.get("text_blocks") or [], 1):
        if isinstance(tb.get("box"), list) and len(tb["box"]) == 4:
            draw.rectangle(px(tb["box"]), outline=(0, 170, 70, 255), width=3)
            draw.text((px(tb["box"])[0] + 3, px(tb["box"])[3] + 2), f"T{i}", fill=(0, 140, 60, 255), font=font)
    return img


def check_unit(measure_img, draw_img, unit):
    problems, blocks = [], []
    comp = (unit.get("frame") or {}).get("composition") or {}
    if comp.get("subject_box") is not None:
        problems += box_problems(comp["subject_box"], "subject_box")
    for i, layer in enumerate((unit.get("frame") or {}).get("layers") or [], 1):
        if layer.get("box") is not None:
            problems += box_problems(layer["box"], f"layer {i}")
    aspect = measure_img.width / measure_img.height
    for i, tb in enumerate(unit.get("text_blocks") or [], 1):
        bad = box_problems(tb.get("box"), f"text block {i}")
        problems += bad
        if bad:
            continue
        fill = tb.get("fill") if isinstance(tb.get("fill"), str) and tb["fill"].startswith("#") else None
        row = {"i": i, "text": str(tb.get("text", ""))[:40], "box": tb["box"], "contrast": text_contrast(measure_img, tb["box"], fill),
               "safe_zone": safe_zone_overlap(tb["box"], aspect)}
        sampled = text_contrast(measure_img, tb["box"], None)["text_hex"]
        if fill and float(np.abs(_rgb(fill) - _rgb(sampled)).sum()) > 90:
            row["fill_check"] = f"record says {fill}, pixels in the box suggest {sampled}"
        blocks.append(row)
    return {"problems": problems, "text_blocks": blocks}, draw_boxes(draw_img, unit)


# ---------- commands ----------

def load_post(folder):
    post = json.loads((folder / "post.json").read_text())
    mpath = folder / "analysis" / "measures.json"
    if not mpath.exists():
        sys.exit(f"{folder.name}: run prepare.py first")
    return post, json.loads(mpath.read_text()), mpath


def cmd_visual(folder):
    post, m, mpath = load_post(folder)
    if post["type"] == "slideshow":
        m["visual"] = {f"slide {i}": visual_measures(Image.open(folder / s)) for i, s in enumerate(post["files"]["slides"], 1)}
    else:
        video = folder / post["files"]["video"]
        for shot in m["shots"]:
            frame = Image.open(folder / "analysis" / shot["key_frame"])
            shot["visual"] = visual_measures(frame)  # from the 1024px key frame
            shot["motion"] = camera_motion(video, shot["start"], shot["end"])
    mpath.write_text(json.dumps(m, ensure_ascii=False, indent=2))
    return "visual measures added"


def cmd_check_post(folder):
    post, m, _ = load_post(folder)
    fp_path = folder / "analysis" / "fingerprint.json"
    if not fp_path.exists():
        return "no fingerprint.json yet"
    units = [u for u in json.loads(fp_path.read_text()).get("units", []) if u.get("text_blocks") or (u.get("frame") or {}).get("layers")]
    if not units:
        return "no units use the visual data model yet (old free-text units are skipped)"
    out_dir = folder / "analysis" / "boxcheck"
    out_dir.mkdir(exist_ok=True)
    report = {}
    for u in units:
        n = u["n"]
        if post["type"] == "slideshow":
            measure_p, draw_p = folder / post["files"]["slides"][n - 1], folder / "analysis" / "slides" / f"{n:02}.jpg"
        else:
            measure_p = draw_p = folder / "analysis" / m["shots"][n - 1]["key_frame"]
        res, drawn = check_unit(Image.open(measure_p), Image.open(draw_p), u)
        drawn.save(out_dir / f"{n:02}.jpg", quality=88)
        report[f"unit {n}"] = res
    (folder / "analysis" / "text_measures.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    problems = sum(len(r["problems"]) for r in report.values())
    return f"{len(report)} unit(s) checked, {problems} box problem(s); see analysis/boxcheck/ and analysis/text_measures.json"


def cmd_check_record(record, image, out_dir):
    unit = json.loads(Path(record).read_text())
    im = Image.open(image)
    res, drawn = check_unit(im, im, unit)
    out_dir = Path(out_dir or Path(image).parent)
    out_dir.mkdir(parents=True, exist_ok=True)
    drawn.save(out_dir / (Path(image).stem + "_boxcheck.jpg"), quality=88)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"drawn: {out_dir / (Path(image).stem + '_boxcheck.jpg')}")


def images_in(path):
    p = Path(path)
    return [p] if p.is_file() else sorted(f for f in p.iterdir() if f.suffix.lower() in IMAGE_EXT)


def cmd_compare(a, b, max_dist):
    hashes = {}
    for f in images_in(a) + images_in(b):
        hashes[f] = imagehash.phash(Image.open(f))
    left, right = images_in(a), images_in(b)
    rows = sorted(((hashes[x] - hashes[y], x, y) for x in left for y in right if x != y), key=lambda r: r[0])
    for d, x, y in rows[:15]:
        print(f"{d:>2}  {'NEAR-DUPLICATE' if d <= max_dist else '              '}  {x.name}  ~  {y.name}")
    near = sum(1 for d, _, _ in rows if d <= max_dist)
    print(f"{near} pair(s) at distance <= {max_dist} (of 64 bits; 0 = identical). The threshold is a starting point, check flagged pairs by eye.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("visual"); p.add_argument("folder", type=Path)
    p = sub.add_parser("check"); p.add_argument("folder", nargs="?", type=Path); p.add_argument("--record"); p.add_argument("--image"); p.add_argument("--out")
    p = sub.add_parser("contrast"); p.add_argument("image"); p.add_argument("--box", nargs=4, type=float, required=True); p.add_argument("--fill")
    p = sub.add_parser("compare"); p.add_argument("a"); p.add_argument("b"); p.add_argument("--max", type=int, default=10)
    args = ap.parse_args()

    if args.cmd in ("visual", "check") and args.folder:
        folders = [args.folder] if (args.folder / "post.json").exists() else sorted(p.parent for p in args.folder.glob("*/post.json"))
        if not folders:
            sys.exit(f"No downloaded posts in {args.folder}")
        for f in folders:
            try:
                print(f"  {f.name}  {(cmd_visual if args.cmd == 'visual' else cmd_check_post)(f)}")
            except Exception as e:
                print(f"  {f.name}  FAILED: {e}")
    elif args.cmd == "check":
        if not (args.record and args.image):
            sys.exit("check needs a post folder, or --record and --image")
        cmd_check_record(args.record, args.image, args.out)
    elif args.cmd == "contrast":
        print(json.dumps(text_contrast(Image.open(args.image), args.box, args.fill), indent=2))
    elif args.cmd == "compare":
        cmd_compare(args.a, args.b, args.max)


if __name__ == "__main__":
    main()
