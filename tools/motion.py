#!/usr/bin/env python3
"""Motion transfer: read how a person moves in a video, cut a clean driver clip for a motion-control model
(`kie.py motion`), and check that the generated clip copies the movement without copying the source footage.

Usage:
  motion.py scan <video or post folder> [--fps 15]
      Pose-track the people in the video → <post>/analysis/pose.json + pose_sheet.jpg + pose_track.npz
      (a loose video writes <stem>_pose.json etc. next to it): framing and people count per shot, limb energy,
      tempo, a movement label, and the usable driver segments (one continuous shot, one person, head to waist in
      frame, 3 to 30 s), best first.
  motion.py driver <video or post folder> --out <dir> [--segment 1 | --start S --end E] [--size 720|1080] [--no-crop]
      Cut a segment into <dir>/driver.mp4 (silent, 9:16, h264) + driver.json (source, credit, framing, checks)
      + driver_pose0.png: a stick figure of the first frame, to pose the persona still. It has no source pixels in
      it, so it can go to the image model without showing it the real person.
  motion.py preflight <character image> <driver.mp4> [--orientation video|image]
      Checks before paying: the character is one of our fictional personas, the still shows every body part the
      driver moves, model input limits. `kie.py motion` runs it on its own and stops on a fail.
  motion.py check <driver.mp4> <clip.mp4> [--source <original video>]
      Compares the generated clip with the driver → <clip>_motion_check.json + <clip>_compare.jpg: limb angle
      error per body part and per second, timing, extra or missing people, stretching limbs, and near-duplicate
      frames against the source video (the source person and scene must not come through).
  motion.py faces <clip.mp4> [--every 6] [--z 4]
      Face close-ups every few frames (the pose model finds the head, the face model reads the enlarged crop) →
      <clip>_faces.jpg + .json: face size in pixels, frames where no face is found, and frames whose face proportions
      (nose, jaw, mouth width against the eye spacing) jump from the clip's median, boxed in red. Look at the sheet:
      teeth are not measured, only seen.
  motion.py splice <take_a.mp4> <take_b.mp4> [...] --out best.mp4 [--window 1] [--plan "0-3:a,6-8:b"]
      Best-of takes made from the same driver (frame k is the same pose in each): per window the take with fewer
      flagged faces, cut where the takes look most alike, 4-frame crossfade → best.mp4 + best.json (the plan).
  motion.py finish <clip.mp4> --out final.mp4 [--camera generated|static|<driver.mp4>] [--exposure 1] [--saturation 1]
                   [--sharpen 0] [--grain 3] [--pullback 0 --zoom 1.8]
      1080×1920, 30 fps, silent. --camera undoes the camera movement the model made up (tracked on the background,
      people masked out) and either locks it or replays the driver's real handheld path, with the smallest zoom that
      hides the edges. Then a grade, sharpening and sensor grain (noise only, no blur), and an optional digital
      pull-back for sources that open on a face close-up (cut the real pull-back out of the driver: a close-up start
      makes the model invent a body in the foreground).

Pose model: MediaPipe Pose Landmarker (33 body points), run on the CPU. The model file is downloaded once from
Google's model storage into .cache/models/. Angles are measured in the image plane (0° = the limb points straight
down), so they compare across different bodies and framings but not across a mirrored video.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
import warnings
from pathlib import Path

os.environ.setdefault("GLOG_minloglevel", "2")  # MediaPipe logs every graph start at INFO
warnings.filterwarnings("ignore", "Mean of empty slice")  # a body part unseen for a whole stretch is normal
import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import portable  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / ".cache" / "models" / "pose_landmarker_full.task"
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/"
             "pose_landmarker_full.task")
VIS = 0.5  # a landmark counts as seen at this visibility, and only inside the frame
LEVELS = ["face", "chest up", "waist up", "knees up", "full body"]
MIN_LEVEL = 2  # Kling motion control needs head, shoulders and torso in the driver: waist up or wider
LIMITS = {"min_s": 3, "max_s": {"video": 30, "image": 10}, "max_mb": 100, "min_px": 300, "aspect": (0.4, 2.5)}

# body parts as image-plane angles: limbs from joint to joint, torso from hips to shoulders, head from shoulders to nose
SEGMENTS = {"l_upper_arm": (11, 13), "l_forearm": (13, 15), "r_upper_arm": (12, 14), "r_forearm": (14, 16),
            "l_thigh": (23, 25), "l_shin": (25, 27), "r_thigh": (24, 26), "r_shin": (26, 28)}
GROUPS = {"arms": ["l_upper_arm", "l_forearm", "r_upper_arm", "r_forearm"],
          "legs": ["l_thigh", "l_shin", "r_thigh", "r_shin"], "torso": ["torso"], "head": ["head"]}
PARTS = list(SEGMENTS) + ["torso", "head"]
BONES = [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12), (11, 23), (12, 24), (23, 24),
         (23, 25), (25, 27), (24, 26), (26, 28), (27, 31), (28, 32)]
LEFT = {11, 13, 15, 23, 25, 27, 31}
RIGHT = {12, 14, 16, 24, 26, 28, 32}

# Thresholds set on our own clips (2026-10-01). A body group whose smoothed angle moves less than ACTIVE deg/s on
# average counts as still: tracker jitter on a still person read 5 to 12 deg/s, exercise movement 38 to 155.
ACTIVE = 25.0
TRAVEL = 0.6      # the hip centre covering more than this many torso lengths over the segment = travelling
GOOD_ERR, BAD_ERR = 20.0, 35.0  # mean limb angle error between driver and clip, degrees


# ---------------------------------------------------------------- tracking

def ffmpeg(name="ffmpeg"):
    return portable.exe(name)


def duration_of(video):
    out = subprocess.run([ffmpeg("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(video)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def landmarker(video_mode=True, num_poses=3):
    from mediapipe.tasks.python import BaseOptions, vision
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading the pose model once → {MODEL.relative_to(ROOT)}", flush=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    # CPU on purpose: the Metal path of MediaPipe 1.0.x aborts on this Mac, and the CPU runs ~25 frames a second
    opts = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL), delegate=BaseOptions.Delegate.CPU),
        running_mode=vision.RunningMode.VIDEO if video_mode else vision.RunningMode.IMAGE, num_poses=num_poses)
    return vision.PoseLandmarker.create_from_options(opts)


def main_person(people, w, h):
    """(count, landmarks of the biggest person as (33, 3) pixel x, y, visibility). Points outside the frame get 0
    visibility. A detection whose box sits mostly inside another one is the same body found twice (it happens on
    fast arm crossings), so it is not counted as an extra person."""
    best, area, boxes = None, -1, []
    for p in people:
        a = np.array([[q.x * w, q.y * h, q.visibility] for q in p], dtype=np.float32)
        out = (a[:, 0] < 0) | (a[:, 0] > w) | (a[:, 1] < 0) | (a[:, 1] > h)
        a[out, 2] = 0
        seen = a[a[:, 2] >= VIS]
        if len(seen) >= 2:
            boxes.append((seen[:, 0].min(), seen[:, 1].min(), seen[:, 0].max(), seen[:, 1].max()))
        box = np.ptp(seen[:, 0]) * np.ptp(seen[:, 1]) if len(seen) >= 2 else 0
        if box > area:
            best, area = a, box
    distinct = []
    for b in sorted(boxes, key=lambda b: -(b[2] - b[0]) * (b[3] - b[1])):
        size = max((b[2] - b[0]) * (b[3] - b[1]), 1e-6)
        inside = [max(0, min(b[2], d[2]) - max(b[0], d[0])) * max(0, min(b[3], d[3]) - max(b[1], d[1])) / size
                  for d in distinct]
        if not inside or max(inside) < 0.5:
            distinct.append(b)
    return (len(distinct) if boxes else len(people)), best


def track(video, fps=15.0, start=0.0, end=None):
    """Sample the video at `fps` and pose-track each sample. Returns t (s), n (people), lm (N, 33, 3), size."""
    import mediapipe as mp
    cap = cv2.VideoCapture(str(video))
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ts, ns, lms = [], [], []
    nxt, i = start, 0
    with landmarker() as lm:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            t = i / src_fps
            i += 1
            if t + 1e-6 < nxt:
                continue
            if end is not None and t > end:
                break
            nxt += 1 / fps
            res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,
                                               data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), int(t * 1000))
            n, a = main_person(res.pose_landmarks, w, h)
            ts.append(t)
            ns.append(n)
            lms.append(a if a is not None else np.full((33, 3), np.nan, np.float32))
    cap.release()
    if not ts:
        sys.exit(f"could not read frames from {video}")
    return {"t": np.array(ts), "n": np.array(ns), "lm": np.stack(lms), "size": (w, h), "fps": fps}


def pose_still(image):
    """(people count, landmarks) for one image."""
    import mediapipe as mp
    im = Image.open(image).convert("RGB")
    with landmarker(video_mode=False) as lm:
        res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(im)))
    return main_person(res.pose_landmarks, *im.size)


# ---------------------------------------------------------------- measures

def seen(lm, idx):
    return lm[..., idx, 2] >= VIS


def level_of(lm):
    """How far down the body the frame reaches, as an index into LEVELS (-1 = nobody). Says nothing about the head:
    see head_in()."""
    lvl = np.full(lm.shape[:-2], -1)
    for k, pts in enumerate([[0], [11, 12], [23, 24], [25, 26], [27, 28]]):
        lvl = np.where(np.any(lm[..., pts, 2] >= VIS, axis=-1), k, lvl)
    return lvl


def head_in(lm):
    return seen(lm, 0)


def framing(lm):
    """The most common framing over samples, e.g. 'full body' or 'knees up (head cut off)'."""
    lvl = level_of(lm)
    if not np.any(lvl >= 0):
        return None
    label = LEVELS[int(np.bincount(lvl[lvl >= 0]).argmax())]
    return label + (" (head cut off)" if np.mean(head_in(lm)[lvl >= 0]) < 0.5 else "")


def angles(lm):
    """Image-plane angle of each body part, degrees, NaN when unseen. Limbs: 0 = pointing down, 90 = pointing to the
    image right. Torso and head: 180 = upright."""
    def ang(v, ok):
        return np.where(ok, np.degrees(np.arctan2(v[..., 0], v[..., 1])), np.nan)
    out = {name: ang(lm[..., b, :2] - lm[..., a, :2], seen(lm, a) & seen(lm, b)) for name, (a, b) in SEGMENTS.items()}
    sh = (lm[..., 11, :2] + lm[..., 12, :2]) / 2
    hp = (lm[..., 23, :2] + lm[..., 24, :2]) / 2
    sh_ok = seen(lm, 11) & seen(lm, 12)
    out["torso"] = ang(sh - hp, sh_ok & seen(lm, 23) & seen(lm, 24))
    out["head"] = ang(lm[..., 0, :2] - sh, sh_ok & seen(lm, 0))
    return out


def circ(d):
    return np.abs((d + 180) % 360 - 180)


def smooth(x, k=3):
    """NaN-aware moving average over unwrapped angles."""
    u = np.where(np.isnan(x), np.nan, np.degrees(np.unwrap(np.radians(np.nan_to_num(x)))))
    out = np.full_like(u, np.nan)
    for i in range(len(u)):
        win = u[max(0, i - k // 2): i + k // 2 + 1]
        if not np.isnan(u[i]) and np.sum(~np.isnan(win)):
            out[i] = np.nanmean(win)
    return out


def speeds(ang, dt):
    """deg/s per part between consecutive seen samples."""
    return {p: np.abs(np.diff(smooth(a))) / dt for p, a in ang.items()}


def torso_len(lm):
    sh = (lm[..., 11, :2] + lm[..., 12, :2]) / 2
    hp = (lm[..., 23, :2] + lm[..., 24, :2]) / 2
    ok = seen(lm, 11) & seen(lm, 12) & seen(lm, 23) & seen(lm, 24)
    return np.where(ok, np.linalg.norm(sh - hp, axis=-1), np.nan), np.where(ok[..., None], hp, np.nan)


def movement(trk, a=None, b=None):
    """Energy per body group, travel (how far the hips move, in torso lengths), hits per second and a label for a:b."""
    lm, dt = trk["lm"][a:b], 1 / trk["fps"]
    sp = speeds(angles(lm), dt)
    energy = {}
    for g, parts in GROUPS.items():
        vals = np.concatenate([sp[p][~np.isnan(sp[p])] for p in parts])
        energy[g] = round(float(np.mean(vals)), 1) if len(vals) >= 3 else None
    tl, hip = torso_len(lm)
    travel = None
    ok = ~np.isnan(tl)
    if ok.sum() >= 3:  # spread of the hip centre, not summed steps: summed steps add up tracker jitter
        span = np.percentile(hip[ok], 95, axis=0) - np.percentile(hip[ok], 5, axis=0)
        travel = round(float(np.hypot(*span) / np.median(tl[ok])), 2)
    limb = np.stack([sp[p] for p in GROUPS["arms"] + GROUPS["legs"]])
    hits = None
    if np.sum(np.any(~np.isnan(limb), axis=0)) >= 10:
        from scipy.signal import find_peaks
        with np.errstate(all="ignore"):
            s = np.nan_to_num(np.nanmean(limb, axis=0))
        peaks, _ = find_peaks(s, distance=max(1, round(0.2 / dt)), prominence=max(ACTIVE, np.percentile(s, 75) * 0.5))
        hits = round(len(peaks) / (len(s) * dt), 2)
    active = [g for g in ("arms", "legs", "torso", "head") if (energy[g] or 0) >= ACTIVE]
    if "arms" in active and "legs" in active:
        label = "full body"
    elif active:
        label = " + ".join(active) + " only"
    else:
        label = "still"
    if travel and travel >= TRAVEL:
        label += ", travelling"
    if label.startswith("full body") and (hits or 0) >= 1.5:
        label = "complex " + label
    return {"label": label, "energy_deg_per_s": energy, "travel_torso_lengths": travel, "hits_per_s": hits}


# ---------------------------------------------------------------- scan

def resolve(target):
    """(video, analysis folder, post.json or None) for a post folder or a loose video."""
    target = Path(target)
    if target.is_dir():
        post = json.loads((target / "post.json").read_text())
        if post["type"] != "video":
            sys.exit(f"{target} is a {post['type']}, not a video")
        return target / post["files"]["video"], target / "analysis", post
    pj = target.parent / "post.json"
    post = json.loads(pj.read_text()) if pj.exists() else None
    return target, (target.parent / "analysis" if post else target.parent), post


def out_name(video, folder, post, name):
    return folder / (name if post else f"{Path(video).stem}_{name}")


def rel(p):
    p = Path(p).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def find_segments(trk, shots):
    t, n, lm, fps = trk["t"], trk["n"], trk["lm"], trk["fps"]
    lvl = level_of(lm)
    ok = (n == 1) & (lvl >= MIN_LEVEL) & head_in(lm)
    gap = round(0.3 * fps)
    segs, rejected = [], []
    for si, (s0, s1) in enumerate(shots, 1):
        idx = np.where((t >= s0) & (t < s1))[0]
        if len(idx) == 0:
            continue
        runs, cur, miss = [], None, 0  # runs of good samples; short drop-outs (a blink of two people, a lost hand) are kept
        for j, g in enumerate(ok[idx]):
            if g:
                cur = [j, j] if cur is None else [cur[0], j]
                miss = 0
            elif cur is not None:
                miss += 1
                if miss > gap:
                    runs.append(cur)
                    cur, miss = None, 0
        if cur is not None:
            runs.append(cur)
        best_len = 0
        for r0, r1 in runs:
            a, b = idx[r0], idx[r1] + 1
            length = (b - a) / fps
            best_len = max(best_len, length)
            if length < LIMITS["min_s"]:
                continue
            if length > 30:  # keep the most active 30 s
                win, hop = int(30 * fps), int(fps)
                tot = [np.nansum(np.concatenate(list(speeds(angles(lm[k:k + win]), 1 / fps).values())))
                       for k in range(a, b - win + 1, hop)]
                a = a + int(np.argmax(tot)) * hop
                b = a + win
            m = movement(trk, a, b)
            hands = seen(lm[a:b], 15) | seen(lm[a:b], 16)
            segs.append({"shot": si, "start": round(float(t[a]), 2), "end": round(float(t[b - 1] + 1 / fps), 2),
                         "length": round((b - a) / fps, 2), "framing": framing(lm[a:b]),
                         "max_people": int(n[a:b].max()),
                         "hands_out_of_frame_pct": round(float(1 - hands.mean()) * 100, 1), **m})
        if best_len < LIMITS["min_s"]:
            why = []
            if s1 - s0 < LIMITS["min_s"]:
                why.append(f"shot is {s1 - s0:.1f}s (motion control needs one continuous shot of 3s or more)")
            if np.mean(n[idx] == 0) > 0.5:
                why.append("no person found in most frames")
            if np.mean(n[idx] > 1) > 0.2:
                why.append("more than one person")
            if np.mean((lvl[idx] < MIN_LEVEL) & (lvl[idx] >= 0)) > 0.5:
                why.append("framing tighter than waist up (Kling needs head, shoulders and torso)")
            if np.mean(~head_in(lm[idx]) & (lvl[idx] >= 0)) > 0.5:
                why.append("head out of frame (Kling needs head, shoulders and torso)")
            rejected.append({"shot": si, "start": round(s0, 2), "end": round(s1, 2),
                             "why": why or [f"longest clean run is {best_len:.1f}s"]})

    def rank(s):  # more movement first, and a 10 s segment beats a 3 s one
        return sum(v or 0 for v in s["energy_deg_per_s"].values()) * min(s["length"], 10) / 10
    segs.sort(key=rank, reverse=True)
    for i, s in enumerate(segs, 1):
        s["segment"] = i
    return segs, rejected


def grab(video, t, width=None):
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t) * 1000)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return None
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if width:
        img = img.resize((width, round(img.height * width / img.width)))
    return img


def draw_skeleton(img, lm, scale=1.0, width=None):
    """Bones on top of an image: the person's left side orange, right side blue."""
    d = ImageDraw.Draw(img)
    width = width or max(3, round(img.width / 120))
    for a, b in BONES:
        if lm[a, 2] >= VIS and lm[b, 2] >= VIS:
            col = "#ff8c00" if a in LEFT and b in LEFT else "#1e90ff" if a in RIGHT and b in RIGHT else "#9a9a9a"
            d.line([tuple(lm[a, :2] * scale), tuple(lm[b, :2] * scale)], fill=col, width=width)
    if lm[7, 2] >= VIS and lm[8, 2] >= VIS:  # head outline from the ears, so a pose reference reads as a person
        cx, cy = (lm[7, :2] + lm[8, :2]) / 2 * scale
        r = np.linalg.norm(lm[7, :2] - lm[8, :2]) * scale * 0.65
        d.ellipse([cx - r, cy - r * 1.25, cx + r, cy + r * 1.05], outline="#222222", width=max(2, width // 2))
    for k in [0] + sorted(LEFT | RIGHT):
        if lm[k, 2] >= VIS:
            x, y = lm[k, :2] * scale
            r = width * (1.6 if k == 0 else 0.9)
            d.ellipse([x - r, y - r, x + r, y + r], fill="#ff8c00" if k in LEFT else "#1e90ff" if k in RIGHT else "#222222")
    return img


def sheet(images, labels, dest, cols=4):
    from prepare import contact_sheet
    contact_sheet(images, labels, dest, cols=cols)


def nearest(trk, t):
    return int(np.argmin(np.abs(trk["t"] - t)))


def cmd_scan(args):
    from measure import camera_motion
    from prepare import find_shots
    video, folder, post = resolve(args.target)
    folder.mkdir(parents=True, exist_ok=True)
    length = duration_of(video)
    shots, detector = find_shots(video, length)
    trk = track(video, args.fps)
    segs, rejected = find_segments(trk, shots)
    lvl = level_of(trk["lm"])
    per_shot = []
    for si, (s0, s1) in enumerate(shots, 1):
        idx = np.where((trk["t"] >= s0) & (trk["t"] < s1))[0]
        if not len(idx):
            continue
        per_shot.append({"shot": si, "start": round(s0, 2), "end": round(s1, 2), "people_max": int(trk["n"][idx].max()),
                         "person_found_pct": round(float(np.mean(trk["n"][idx] > 0)) * 100, 1),
                         "framing": framing(trk["lm"][idx]),
                         **(movement(trk, idx[0], idx[-1] + 1) if len(idx) >= 4 else {})})
    for s in segs[:5]:
        s["camera"] = (camera_motion(video, s["start"], s["end"]) or {}).get("label")
    overall = movement(trk)
    if len(shots) > 1:  # hips jump at every cut, so travel only means something inside one shot
        overall["travel_torso_lengths"] = None
        overall["label"] = overall["label"].replace(", travelling", "")
    result = {"video": rel(video), "length": round(length, 2), "size": list(trk["size"]), "sampled_fps": args.fps,
              "shot_detector": detector, "shots": per_shot, "overall": overall,
              "driver_segments": segs, "no_segment_shots": rejected,
              "note": ("Angles are image-plane; limb energy is the mean smoothed angular speed (a still person reads "
                       f"5-12 deg/s from tracker jitter, {ACTIVE:g}+ counts as moving). Labels are rough. Pick a "
                       "segment for `motion.py driver --segment N`.")}
    out = out_name(video, folder, post, "pose.json")
    out.write_text(json.dumps(result, indent=2))
    np.savez_compressed(out_name(video, folder, post, "pose_track.npz"), t=trk["t"], n=trk["n"], lm=trk["lm"],
                        size=np.array(trk["size"]), fps=trk["fps"])
    a, b = (segs[0]["start"], segs[0]["end"]) if segs else (0, length)
    imgs, labels = [], []
    for t in np.linspace(a, b - 0.05, 8):
        img = grab(video, t)
        if img is None:
            continue
        k = nearest(trk, t)
        if not np.isnan(trk["lm"][k, 0, 0]):
            draw_skeleton(img, trk["lm"][k])
        imgs.append(img)
        labels.append(f"{t:.1f}s  {LEVELS[lvl[k]] if lvl[k] >= 0 else 'nobody'}")
    sheet(imgs, labels, out_name(video, folder, post, "pose_sheet.jpg"))
    print(f"{rel(out)}: {len(shots)} shots, overall {result['overall']['label']}")
    for s in segs[:5]:
        print(f"  segment {s['segment']}: {s['start']}-{s['end']}s ({s['length']}s) {s['framing']}, {s['label']}, "
              f"camera {s.get('camera')}, hands out {s['hands_out_of_frame_pct']}%")
    if not segs:
        print("  no usable driver segment:")
        for r in rejected[:6]:
            print(f"    shot {r['shot']} {r['start']}-{r['end']}s: {'; '.join(r['why'])}")


# ---------------------------------------------------------------- driver

def crop_box(trk, size):
    """A fixed 9:16 window around everything the person covers (a moving crop would add camera motion)."""
    w, h = size
    pts = trk["lm"]
    m = pts[..., 2] >= VIS
    xs, ys = pts[..., 0][m], pts[..., 1][m]
    if len(xs) < 10:
        return None
    x0, x1, y0, y1 = np.percentile(xs, 1), np.percentile(xs, 99), np.percentile(ys, 1), np.percentile(ys, 99)
    head = np.nanmedian(np.linalg.norm(pts[:, 0, :2] - (pts[:, 11, :2] + pts[:, 12, :2]) / 2, axis=-1))
    y0 -= (head if np.isfinite(head) else 0.08 * h) * 0.9  # landmarks stop at the eyes: leave room for the hair
    padx, pady = 0.10 * (x1 - x0) + 0.03 * w, 0.05 * (y1 - y0)
    x0, x1, y0, y1 = x0 - padx, x1 + padx, y0 - pady, y1 + pady
    cw = max(x1 - x0, (y1 - y0) * 9 / 16)
    ch = cw * 16 / 9
    if ch > h:  # the person fills the height: take the full height (any extra width is padded later)
        ch, cw = h, max(h * 9 / 16, min(x1 - x0, w))
    cw, ch = min(cw, w), min(ch, h)
    left = float(np.clip((x0 + x1) / 2 - cw / 2, 0, w - cw))
    top = float(np.clip((y0 + y1) / 2 - ch / 2, 0, h - ch))
    return [round(left), round(top), int(cw) // 2 * 2, int(ch) // 2 * 2]


def stick_figure(lm, size, dest):
    """The first frame's pose as a stick figure on white, with a key for the image prompt."""
    w, h = size
    img = Image.new("RGB", (w, h), "white")
    draw_skeleton(img, lm, width=max(6, round(w / 60)))
    font = ImageFont.load_default(size=max(18, w // 30))
    ImageDraw.Draw(img).text((w * 0.04, h * 0.02), "pose only. orange = the person's left, blue = their right",
                             fill="#555555", font=font)
    img.save(dest)


def cmd_driver(args):
    video, folder, post = resolve(args.target)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.start is None:
        scan = out_name(video, folder, post, "pose.json")
        if not scan.exists():
            sys.exit(f"no scan yet: run `motion.py scan {args.target}` first, or give --start and --end")
        segs = json.loads(scan.read_text())["driver_segments"]
        if not segs:
            sys.exit(f"the scan found no usable segment (see no_segment_shots in {rel(scan)}); give --start and --end to force one")
        seg = next((s for s in segs if s["segment"] == args.segment), None)
        if seg is None:
            sys.exit(f"no segment {args.segment}; the scan has 1 to {len(segs)}")
        start, end = seg["start"], seg["end"]
    else:
        start, end = args.start, args.end
    if not LIMITS["min_s"] <= end - start <= LIMITS["max_s"]["video"]:
        sys.exit(f"a driver must be 3 to 30 s long; {start}-{end} is {end - start:.1f}s")
    vw, vh = video_size(video)
    vertical = abs(vw / vh - 9 / 16) < 0.03  # already 9:16: keep the whole frame, a crop would only cut hands off
    box = None if args.no_crop or vertical else crop_box(track(video, 15, start, end), (vw, vh))
    W, H = (720, 1280) if args.size == 720 else (1080, 1920)
    vf = (f"crop={box[2]}:{box[3]}:{box[0]}:{box[1]}," if box else "") + \
         f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
    dst = out / "driver.mp4"
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(video),
                    "-vf", vf, "-an", "-r", "30", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)], check=True)
    dtrk = track(dst, 15)
    m = movement(dtrk)
    lvl = level_of(dtrk["lm"])
    first = next((k for k in range(len(dtrk["t"])) if dtrk["n"][k] >= 1), None)
    if first is not None:
        stick_figure(dtrk["lm"][first], dtrk["size"], out / "driver_pose0.png")
    length = duration_of(dst)
    mb = dst.stat().st_size / 1e6
    checks = {"length_3_to_30s": LIMITS["min_s"] <= length <= 30, "under_100mb": mb < LIMITS["max_mb"],
              "one_person_pct": round(float(np.mean(dtrk["n"] == 1)) * 100, 1),
              "head_to_waist_in_frame_pct": round(float(np.mean((lvl >= MIN_LEVEL) & head_in(dtrk["lm"]))) * 100, 1),
              "image_orientation_allowed": length <= LIMITS["max_s"]["image"]}
    warnings = []
    if checks["one_person_pct"] < 90:
        warnings.append("someone else is in frame for over 10% of the driver, or the person is lost: the model may follow the wrong body")
    if checks["head_to_waist_in_frame_pct"] < 90:
        warnings.append("head, shoulders and torso are not all in frame for over 10% of the driver")
    if box and box[2] / box[3] > 9 / 16 + 0.02:
        warnings.append("the person is wider than a 9:16 window, so the driver has black bars; prefer another segment")
    credit = None
    if post:
        credit = {"creator": "@" + post["creator"], "url": post.get("url"), "post_id": post.get("id"),
                  "caption_credit": f"dc @{post['creator']}",
                  "note": "the moves are theirs: credit the creator in the caption (TikTok's 'dc' convention), never present the choreography as ours"}
    info = {"source": rel(video), "segment": [round(start, 2), round(end, 2)], "crop": box, "size": [W, H],
            "length": round(length, 2), "mb": round(mb, 2),
            "framing": framing(dtrk["lm"]),
            **m, "checks": checks, "warnings": warnings, "credit": credit,
            "pose_reference": "driver_pose0.png" if first is not None else None,
            "next": ("render the persona still in the same framing and starting pose (attach driver_pose0.png as a pose "
                     "reference, never a frame of the source person), in the setting you want: Kling keeps the still's "
                     "background. Then kie.py motion.")}
    (out / "driver.json").write_text(json.dumps(info, indent=2))
    print(f"{rel(dst)}: {length:.1f}s, {mb:.1f} MB, {info['framing']}, {m['label']}")
    for w_ in warnings:
        print(f"  warning: {w_}")


def video_size(video):
    cap = cv2.VideoCapture(str(video))
    size = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return size


# ---------------------------------------------------------------- preflight

def preflight(character, driver, orientation="video"):
    fails, warnings = [], []
    r = rel(character)
    if not (r.startswith("personas/") or (r.startswith("content-bank/") and "/runs/" in r)):
        fails.append("the character must be one of our fictional personas: a file in personas/ or a still rendered in a "
                     "run folder (owner rule: never move a real person's likeness)")
    im = Image.open(character)
    if min(im.size) <= LIMITS["min_px"]:
        fails.append(f"character image is {im.size[0]}x{im.size[1]}; both sides must be over 300px")
    ar = im.size[0] / im.size[1]
    if not LIMITS["aspect"][0] <= ar <= LIMITS["aspect"][1]:
        fails.append(f"character aspect {ar:.2f} is outside 2:5 to 5:2")
    d = Path(driver)
    if d.suffix.lower() not in (".mp4", ".mov"):
        fails.append("the driver must be an .mp4 or .mov")
    length = duration_of(d)
    cap = LIMITS["max_s"][orientation]
    if not LIMITS["min_s"] <= length <= cap:
        fails.append(f"driver is {length:.1f}s; with orientation '{orientation}' it must be 3 to {cap}s")
    if d.stat().st_size / 1e6 >= LIMITS["max_mb"]:
        fails.append("driver is 100 MB or more")
    n, lm = pose_still(character)
    info_file = d.parent / "driver.json"
    if info_file.exists() and json.loads(info_file.read_text()).get("framing"):
        drv_level = LEVELS.index(json.loads(info_file.read_text())["framing"].split(" (")[0])
    else:
        lv = level_of(track(d, 5)["lm"])
        drv_level = int(np.bincount(lv[lv >= 0]).argmax()) if np.any(lv >= 0) else -1
    img_level = int(level_of(lm)) if lm is not None else -1
    if n == 0:
        warnings.append("no human pose found in the still (expected for a stylised mascot; the model may still manage)")
    elif n > 1:
        warnings.append(f"{n} people found in the still: use a still with only the persona")
    if n and drv_level >= 0 and img_level >= 0 and drv_level > img_level:
        msg = (f"the driver is {LEVELS[drv_level]} but the still is {LEVELS[img_level]}: the model has to invent the "
               "missing body. Render the persona in the driver's framing first")
        (fails if drv_level - img_level >= 2 else warnings).append(msg)
    return {"ok": not fails, "fails": fails, "warnings": warnings, "driver_seconds": round(length, 2),
            "driver_framing": LEVELS[drv_level] if drv_level >= 0 else None,
            "still_framing": LEVELS[img_level] if img_level >= 0 else None}


def cmd_preflight(args):
    r = preflight(args.character, args.driver, args.orientation)
    print(json.dumps(r, indent=2))
    sys.exit(0 if r["ok"] else 1)


# ---------------------------------------------------------------- check

def grid(trk, fps, length):
    """Angles on a fixed time grid from 0, NaN where no sample landed."""
    n = int(round(length * fps)) + 1
    ang = angles(trk["lm"])
    out = np.full((n, len(PARTS)), np.nan)
    people = np.full(n, -1)
    for i, t in enumerate(trk["t"] - trk["t"][0]):
        k = int(round(t * fps))
        if 0 <= k < n:
            out[k] = [ang[p][i] for p in PARTS]
            people[k] = trk["n"][i]
    return out, people


def limb_stretch(trk):
    """Per limb: how much its length varies over the clip relative to the torso (morphing shows up as a large spread)."""
    tl, _ = torso_len(trk["lm"])
    out = {}
    for name, (a, b) in SEGMENTS.items():
        ok = seen(trk["lm"], a) & seen(trk["lm"], b) & ~np.isnan(tl)
        if ok.sum() < 8:
            continue
        ln = np.linalg.norm(trk["lm"][ok, b, :2] - trk["lm"][ok, a, :2], axis=-1) / tl[ok]
        out[name] = round(float(np.std(ln) / np.mean(ln)), 3)
    return out


def frame_hashes(video, every=0.5):
    import imagehash
    out, t, length = [], 0.0, duration_of(video)
    while t < length:
        img = grab(video, t, width=256)
        if img is not None:
            out.append(imagehash.phash(img))
        t += every
    return out


def cmd_check(args):
    fps = 15
    drv, clip = Path(args.driver), Path(args.clip)
    dl, cl = duration_of(drv), duration_of(clip)
    dtrk, ctrk = track(drv, fps), track(clip, fps)
    D, _ = grid(dtrk, fps, dl)
    C, cn = grid(ctrk, fps, cl)
    best = None
    for lag in range(-fps, fps + 1):  # the model may start a few frames early or late
        a0, b0 = max(0, -lag), max(0, lag)
        k = min(len(D) - a0, len(C) - b0)
        if k < len(D) * 0.5:
            continue
        err = circ(D[a0:a0 + k] - C[b0:b0 + k])
        if np.sum(~np.isnan(err)) < 10:
            continue
        m = float(np.nanmean(err))
        if best is None or m < best[0]:
            best = (m, lag, a0, b0, k, err)
    if best is None:
        sys.exit("not enough body seen in both videos to compare (is there a person in the clip?)")
    mean_err, lag, a0, b0, k, err = best
    by_group = {}
    for g, parts in GROUPS.items():
        e = err[:, [PARTS.index(p) for p in parts]]
        by_group[g] = round(float(np.nanmean(e)), 1) if np.any(~np.isnan(e)) else None
    with np.errstate(all="ignore"):
        per_frame = np.nanmean(err, axis=1)
    seconds = []
    for s in range(int(np.ceil(k / fps))):
        chunk = per_frame[s * fps:(s + 1) * fps]
        seconds.append(round(float(np.nanmean(chunk)), 1) if np.any(~np.isnan(chunk)) else None)
    with np.errstate(all="ignore"):  # timing: does the clip move when the driver moves
        ds = np.nanmean(circ(np.diff(D[a0:a0 + k], axis=0)), axis=1)
        cs = np.nanmean(circ(np.diff(C[b0:b0 + k], axis=0)), axis=1)
    ok = ~np.isnan(ds) & ~np.isnan(cs)
    timing_r = (round(float(np.corrcoef(ds[ok], cs[ok])[0, 1]), 2)
                if ok.sum() >= 10 and np.std(ds[ok]) > 0 and np.std(cs[ok]) > 0 else None)
    drv_move = movement(dtrk)
    clip_people = cn[b0:b0 + k]
    clip_people = clip_people[clip_people >= 0]
    stretch_d, stretch_c = limb_stretch(dtrk), limb_stretch(ctrk)
    stretched = [p for p in stretch_c if p in stretch_d and stretch_c[p] > stretch_d[p] + 0.12]
    src = Path(args.source) if args.source else None  # originality: the clip must not reuse source or driver frames
    if src is None and (drv.parent / "driver.json").exists():
        s = json.loads((drv.parent / "driver.json").read_text()).get("source")
        src = ROOT / s if s and (ROOT / s).exists() else None
    ch = frame_hashes(clip)
    dup = {}
    for name, path in (("driver", drv), ("source", src)):
        if path is None or Path(path).resolve() == clip.resolve():
            continue
        ref = frame_hashes(path)
        dists = [min(c - r for r in ref) for c in ch]
        dup[name] = {"min_phash_distance": int(min(dists)), "near_duplicate_frames": int(sum(x <= 10 for x in dists))}
    fails, warns = [], []
    if mean_err > BAD_ERR:
        fails.append(f"mean limb angle error {mean_err:.0f}° (over {BAD_ERR:g}°): the clip does not follow the driver")
    elif mean_err > GOOD_ERR:
        warns.append(f"mean limb angle error {mean_err:.0f}°: watch the worst seconds")
    if np.mean(clip_people == 0) > 0.1:
        warns.append(f"no body found in {np.mean(clip_people == 0) * 100:.0f}% of the clip (melted or off-frame body?)")
    if np.mean(clip_people > 1) > 0.05:
        fails.append(f"extra people in {np.mean(clip_people > 1) * 100:.0f}% of the clip")
    if stretched:
        warns.append("limbs change length much more than in the driver (stretching or morphing): " + ", ".join(stretched))
    if abs(cl - dl) > 0.6:
        warns.append(f"clip is {cl:.1f}s, driver {dl:.1f}s")
    for name, v in dup.items():
        if v["near_duplicate_frames"]:
            fails.append(f"{v['near_duplicate_frames']} frames are near-duplicates of the {name} (source footage came through)")
    if drv_move["label"] == "still":
        warns.append("the driver barely moves, so this comparison says little")
    worst = sorted([(v, i) for i, v in enumerate(seconds) if v is not None], reverse=True)[:3]
    result = {"driver": rel(drv), "clip": rel(clip), "verdict": "fail" if fails else "check" if warns else "pass",
              "mean_angle_error_deg": round(mean_err, 1), "by_group_deg": by_group, "per_second_deg": seconds,
              "worst_seconds": [{"second": i, "error_deg": v} for v, i in worst],
              "lag_s": round(lag / fps, 2), "timing_r": timing_r, "driver_movement": drv_move["label"],
              "clip_movement": movement(ctrk)["label"],
              "clip_one_person_pct": round(float(np.mean(clip_people == 1)) * 100, 1),
              "limb_length_spread": {"driver": stretch_d, "clip": stretch_c}, "duplicates": dup,
              "fails": fails, "warnings": warns,
              "thresholds": {"good_deg": GOOD_ERR, "fail_deg": BAD_ERR, "near_duplicate_phash": 10}}
    dest = clip.with_name(clip.stem + "_motion_check.json")
    dest.write_text(json.dumps(result, indent=2))
    imgs, labels = [], []
    for t in np.linspace(0.2, max(0.3, min(dl, cl) - 0.2), 6):
        for name, video, trk, off in (("driver", drv, dtrk, 0), ("clip", clip, ctrk, lag / fps)):
            img = grab(video, t + off, width=360)
            if img is None:
                continue
            kk = nearest(trk, t + off)
            if not np.isnan(trk["lm"][kk, 0, 0]):
                draw_skeleton(img, trk["lm"][kk], scale=360 / trk["size"][0])
            imgs.append(img)
            i = min(int(t), len(seconds) - 1)
            labels.append(f"{name} {t:.1f}s" + (f"  err {seconds[i]}°" if name == "clip" and seconds[i] is not None else ""))
    sheet(imgs, labels, clip.with_name(clip.stem + "_compare.jpg"), cols=4)
    print(f"{result['verdict']}: mean error {mean_err:.1f}° (arms {by_group['arms']}, legs {by_group['legs']}), "
          f"timing r {timing_r}, lag {lag / fps:+.2f}s → {rel(dest)}")
    for f in fails + warns:
        print(f"  {f}")


# ---------------------------------------------------------------- faces

FACE_MODEL = ROOT / ".cache" / "models" / "face_landmarker.task"
FACE_URL = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/"
            "face_landmarker.task")
# face mesh points: eye outer corners, nose tip, nose bridge, mouth corners, upper and lower lip, chin, cheeks
FP = {"eye_l": 33, "eye_r": 263, "nose": 1, "bridge": 168, "mouth_l": 61, "mouth_r": 291, "lip_up": 13, "lip_lo": 14,
      "chin": 152, "cheek_l": 234, "cheek_r": 454}


def face_shape(pts):
    """Proportions that stay put on a real face whatever the expression or turn: all relative to the eye spacing."""
    eye = np.linalg.norm(pts[FP["eye_l"]] - pts[FP["eye_r"]])
    d = lambda a, b: np.linalg.norm(pts[FP[a]] - pts[FP[b]]) / eye
    return {"nose_len": d("bridge", "nose"), "nose_chin": d("nose", "chin"), "face_w": d("cheek_l", "cheek_r"),
            "mouth_w": d("mouth_l", "mouth_r"), "eye_mid_nose": np.linalg.norm((pts[FP["eye_l"]] + pts[FP["eye_r"]]) / 2
                                                                                 - pts[FP["nose"]]) / eye}


def cmd_faces(args):
    """Face close-ups every few frames (pose finds the head, the face model reads the enlarged crop), with frames
    whose face proportions jump flagged: a melting face or a warped jaw shows up as a proportion outlier."""
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
    if not FACE_MODEL.exists():
        print(f"downloading the face model once → {FACE_MODEL.relative_to(ROOT)}", flush=True)
        urllib.request.urlretrieve(FACE_URL, FACE_MODEL)
    video = Path(args.video)
    trk = track(video, 30)
    fopts = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(FACE_MODEL), delegate=BaseOptions.Delegate.CPU),
        running_mode=vision.RunningMode.IMAGE, num_faces=1, output_face_blendshapes=True)
    rows, tiles = [], []
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    with vision.FaceLandmarker.create_from_options(fopts) as fl:
        for k in range(0, len(trk["t"]), args.every):
            t = float(trk["t"][k])
            lm = trk["lm"][k]
            cap.set(cv2.CAP_PROP_POS_FRAMES, round(t * fps))
            ok, frame = cap.read()
            if not ok or np.isnan(lm[0, 0]):
                continue
            ears = np.linalg.norm(lm[7, :2] - lm[8, :2])
            sw = np.linalg.norm(lm[11, :2] - lm[12, :2])
            half = max(ears * 1.5, sw * 0.45, 40)
            cx, cy = lm[0, 0], lm[0, 1] - 0.15 * half
            x0, y0 = int(max(0, cx - half)), int(max(0, cy - half))
            crop = frame[y0:int(cy + half), x0:int(cx + half)]
            if crop.size == 0:
                continue
            big = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LANCZOS4)
            res = fl.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(big, cv2.COLOR_BGR2RGB)))
            row = {"t": round(t, 2), "face_px": round(2 * half), "found": bool(res.face_landmarks)}
            if res.face_landmarks:
                pts = np.array([(q.x * 512, q.y * 512) for q in res.face_landmarks[0]])
                row.update({k_: round(float(v), 3) for k_, v in face_shape(pts).items()})
                bs = {c.category_name: c.score for c in res.face_blendshapes[0]}
                row["jaw_open"] = round(bs.get("jawOpen", 0), 2)
            rows.append(row)
            tiles.append((t, Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB)).resize((220, 220), Image.LANCZOS)))
    cap.release()
    keys = ["nose_len", "nose_chin", "face_w", "mouth_w", "eye_mid_nose"]
    found = [r for r in rows if r["found"]]
    stats = {}
    for k_ in keys:
        v = np.array([r[k_] for r in found])
        med, mad = float(np.median(v)), float(np.median(np.abs(v - np.median(v))) * 1.4826 + 1e-6)
        stats[k_] = {"median": round(med, 3), "mad": round(mad, 3)}
    for r in rows:
        why = []
        if not r["found"]:
            why.append("no face found in the head crop")
        else:
            for k_ in keys:
                z = abs(r[k_] - stats[k_]["median"]) / stats[k_]["mad"]
                if z > args.z:
                    why.append(f"{k_} {r[k_]} vs median {stats[k_]['median']} ({z:.1f} MAD)")
        r["flags"] = why
    flagged = [r for r in rows if r["flags"]]
    sheet_img = Image.new("RGB", (220 * 10, 220 * ((len(tiles) + 9) // 10)), "white")
    d = ImageDraw.Draw(sheet_img)
    for i, ((t, im), r) in enumerate(zip(tiles, rows)):
        x, y = (i % 10) * 220, (i // 10) * 220
        sheet_img.paste(im, (x, y))
        d.text((x + 5, y + 4), f"{t:.1f}s" + (f" open {r.get('jaw_open')}" if r["found"] else ""), fill="yellow")
        if r["flags"]:
            d.rectangle([x + 1, y + 1, x + 218, y + 218], outline="red", width=4)
    stem = video.with_name(video.stem + "_faces")
    sheet_img.save(stem.with_suffix(".jpg"), quality=88)
    stem.with_suffix(".json").write_text(json.dumps({"video": rel(video), "every_frames": args.every,
                                                     "face_px_median": int(np.median([r["face_px"] for r in rows])),
                                                     "found_pct": round(100 * len(found) / max(1, len(rows)), 1),
                                                     "flagged": len(flagged), "stats": stats, "rows": rows}, indent=1))
    print(f"{rel(stem.with_suffix('.jpg'))}: {len(rows)} faces, head crop about {int(np.median([r['face_px'] for r in rows]))} px, "
          f"face found {100 * len(found) / max(1, len(rows)):.0f}%, {len(flagged)} flagged")
    for r in flagged[:12]:
        print(f"  {r['t']}s: {'; '.join(r['flags'])}")


# ---------------------------------------------------------------- splice

def read_frames(video):
    cap = cv2.VideoCapture(str(video))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()
    return frames


def cmd_splice(args):
    """Best-of takes: every take follows the same driver, so frame k shows the same pose in each; per window keep the
    take whose face holds up, and cut where the takes look most alike, with a short crossfade."""
    takes = [Path(t) for t in args.takes]
    names = [chr(ord("a") + i) for i in range(len(takes))]
    sheets = []
    for t in takes:  # face checks (reuse a fresh one if it is there)
        js = t.with_name(t.stem + "_faces.json")
        if not js.exists() or js.stat().st_mtime < t.stat().st_mtime:
            cmd_faces(argparse.Namespace(video=str(t), every=3, z=args.z))
        sheets.append(json.loads(js.read_text())["rows"])
    clips = [read_frames(t) for t in takes]
    n = min(len(c) for c in clips)
    h, w = clips[0][0].shape[:2]
    for i, c in enumerate(clips):
        if c[0].shape[:2] != (h, w):
            clips[i] = [cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA) for f in c]
    fps = cv2.VideoCapture(str(takes[0])).get(cv2.CAP_PROP_FPS) or 30
    win = int(round(args.window * fps))
    nwin = int(np.ceil(n / win))
    bad = np.zeros((len(takes), nwin))
    for ti, rows in enumerate(sheets):
        for r in rows:
            wi = min(int(r["t"] * fps) // win, nwin - 1)
            bad[ti, wi] += len(r["flags"]) > 0
    plan = []
    manual = {}
    for part in (args.plan or "").split(","):  # e.g. "0-3:a,3-5:b" in seconds
        if part.strip():
            span, take = part.split(":")
            a_, b_ = (float(x) for x in span.split("-"))
            for wi in range(int(a_ * fps) // win, int(np.ceil(b_ * fps / win))):
                manual[wi] = names.index(take.strip())
    for wi in range(nwin):
        if wi in manual:
            plan.append(manual[wi])
            continue
        best = int(np.argmin(bad[:, wi]))
        if plan and bad[plan[-1], wi] == bad[best, wi]:
            best = plan[-1]  # no gain: stay on the same take, fewer cuts
        plan.append(best)
    cuts = []  # (frame, from, to)
    for wi in range(1, nwin):
        if plan[wi] != plan[wi - 1]:
            c0, c1 = clips[plan[wi - 1]], clips[plan[wi]]
            lo, hi = max(2, wi * win - win // 2), min(n - 3, wi * win + win // 2)
            diffs = [np.mean(np.abs(cv2.resize(c0[k], (180, 320)).astype(np.int16) - cv2.resize(c1[k], (180, 320))))
                     for k in range(lo, hi)]
            cuts.append((lo + int(np.argmin(diffs)), plan[wi - 1], plan[wi]))
    xf = args.crossfade
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                            "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "medium",
                            "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    cur, ci = plan[0], 0
    for k in range(n):
        while ci < len(cuts) and k >= cuts[ci][0] + xf // 2:
            cur = cuts[ci][2]
            ci += 1
        frame = clips[cur][k]
        for c, a_, b_ in cuts:  # inside a crossfade: blend the two takes
            if c - xf // 2 <= k < c + xf - xf // 2:
                al = (k - (c - xf // 2) + 0.5) / xf
                frame = cv2.addWeighted(clips[a_][k], 1 - al, clips[b_][k], al, 0)
        enc.stdin.write(np.ascontiguousarray(frame).tobytes())
    enc.stdin.close()
    if enc.wait():
        sys.exit("ffmpeg failed while encoding")
    info = {"takes": {names[i]: rel(t) for i, t in enumerate(takes)}, "window_s": args.window,
            "flagged_faces_per_window": {names[i]: bad[i].astype(int).tolist() for i in range(len(takes))},
            "plan": [names[p_] for p_ in plan], "cuts": [{"t": round(c / fps, 2), "from": names[a_], "to": names[b_]}
                                                         for c, a_, b_ in cuts],
            "flagged_kept": int(sum(bad[p_, wi] for wi, p_ in enumerate(plan))),
            "flagged_per_take": {names[i]: int(bad[i].sum()) for i in range(len(takes))}}
    out.with_suffix(".json").write_text(json.dumps(info, indent=1))
    print(f"{rel(out)}: plan {''.join(info['plan'])} ({args.window:g}s windows), cuts at "
          f"{[c['t'] for c in info['cuts']]}; flagged faces per take {info['flagged_per_take']} → kept {info['flagged_kept']}")


# ---------------------------------------------------------------- finish

def person_masks(video, grow=0.03):
    """Per frame: a mask (uint8, 0 = a person, 255 = background) from the pose model's body outline, grown by a few
    percent of the width so hair and motion blur stay out of background tracking."""
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision
    landmarker()  # makes sure the model file is there
    opts = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL), delegate=BaseOptions.Delegate.CPU),
        running_mode=vision.RunningMode.VIDEO, num_poses=3, output_segmentation_masks=True)
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    masks, i = [], 0
    with vision.PoseLandmarker.create_from_options(opts) as lmk:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            h, w = frame.shape[:2]
            res = lmk.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,
                                                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), int(i / fps * 1000))
            i += 1
            people = np.zeros((h, w), np.uint8)
            for sm in res.segmentation_masks or []:
                people |= (sm.numpy_view().squeeze() > 0.3).astype(np.uint8)
            k = max(3, int(grow * w)) | 1
            people = cv2.dilate(people, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
            masks.append(np.where(people > 0, 0, 255).astype(np.uint8))
    cap.release()
    return masks


def camera_path(video):
    """How the scene moves on screen, per frame: 3x3 matrices mapping frame-0 positions to frame-i positions,
    from background points tracked frame to frame (people masked out), one similarity transform per step."""
    masks = person_masks(video)
    cap = cv2.VideoCapture(str(video))
    path, prev, prev_pts = [np.eye(3)], None, None
    k = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            M = None
            if prev_pts is not None and len(prev_pts) >= 12:
                cur, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, prev_pts, None, winSize=(31, 31), maxLevel=4)
                good = st.ravel() == 1
                if good.sum() >= 12:
                    M, _ = cv2.estimateAffinePartial2D(prev_pts[good], cur[good], method=cv2.RANSAC,
                                                       ransacReprojThreshold=2.0)
            step = np.vstack([M, [0, 0, 1]]) if M is not None else np.eye(3)
            path.append(step @ path[-1])
        prev = g
        prev_pts = cv2.goodFeaturesToTrack(g, 500, 0.005, 10, mask=masks[k] if k < len(masks) else None)
        k += 1
    cap.release()
    return path


def overscan(warps, w, h, anchor, limit=1.2):
    """Smallest zoom about `anchor` that keeps every warped frame covering the whole output (no empty edges)."""
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], float).T
    for z in np.arange(1.0, limit + 1e-9, 0.005):
        Z = np.array([[z, 0, anchor[0] * (1 - z)], [0, z, anchor[1] * (1 - z)], [0, 0, 1]])
        ok = True
        for W_ in warps:
            src = np.linalg.inv(Z @ W_) @ corners  # where each output corner samples the clip
            if src[0].min() < 0 or src[0].max() > w or src[1].min() < 0 or src[1].max() > h:
                ok = False
                break
        if ok:
            return float(z)
    return limit


def cmd_finish(args):
    """1080×1920 finish: lock or replace the generated camera, optional pull-back, grade, sensor grain."""
    clip, W, H, fps = Path(args.clip), 1080, 1920, 30
    cap = cv2.VideoCapture(str(clip))
    src_fps = cap.get(cv2.CAP_PROP_FPS) or fps
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    warps = [np.eye(3)] * n
    if args.camera != "generated":
        gen = camera_path(clip)  # the camera the model made up: undone frame by frame
        # lock to the middle of the made-up drift, not to frame 0: that halves the zoom needed to hide the edges
        tx = [m_[0, 2] for m_ in gen]
        ty = [m_[1, 2] for m_ in gen]
        sc = [np.hypot(m_[0, 0], m_[1, 0]) for m_ in gen]
        smid = float(np.sqrt(min(sc) * max(sc)))
        ref = np.array([[smid, 0, (min(tx) + max(tx)) / 2], [0, smid, (min(ty) + max(ty)) / 2], [0, 0, 1]])
        warps = [ref @ np.linalg.inv(m_) for m_ in gen]
        if args.camera != "static":  # replay a real camera: the original's handheld path, in this clip's pixels
            src = camera_path(args.camera)
            sw = video_size(args.camera)[0]
            S = np.diag([w / sw, w / sw, 1.0])
            src = [S @ m_ @ np.linalg.inv(S) for m_ in src]
            warps = [src[min(i, len(src) - 1)] @ warps[i] for i in range(len(warps))]
        n = min(n, len(warps))
    anchor = (w / 2, h / 2)
    z0 = overscan(warps[:n], w, h, anchor) if args.camera != "generated" else 1.0
    nose = None
    if args.pullback > 0:
        trk = track(clip, 15, 0, max(args.pullback, 0.5))
        pts = trk["lm"][:, 0, :2][trk["lm"][:, 0, 2] >= VIS]
        nose = (np.median(pts, axis=0) + [0, 0.04 * h]) if len(pts) else np.array([w / 2, h / 3])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    rng = np.random.default_rng()
    i = 0
    while i < n:
        ok, frame = cap.read()
        if not ok:
            break
        t = i / src_fps
        z, ax = z0, anchor
        if nose is not None and t < args.pullback:  # ease-out from a face close-up, like a real step back
            z = z0 * (1 + (args.zoom - 1) * (1 - t / args.pullback) ** 3)
            ax = tuple(nose)
        Z = np.array([[z, 0, ax[0] * (1 - z)], [0, z, ax[1] * (1 - z)], [0, 0, 1]])
        M = (np.diag([W / w, H / h, 1.0]) @ Z @ warps[i])[:2]
        img = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
        if args.exposure != 1.0:
            img *= args.exposure
        if args.saturation != 1.0:
            luma = img @ np.array([0.299, 0.587, 0.114], np.float32)
            img = luma[..., None] + (img - luma[..., None]) * args.saturation
        if args.sharpen > 0:
            img = img + args.sharpen * (img - cv2.GaussianBlur(img, (0, 0), 1.2))
        if args.grain > 0:  # sensor noise: mostly luminance, a little colour, no blur
            img += rng.normal(0, args.grain, img.shape[:2])[..., None] + rng.normal(0, args.grain * 0.35, img.shape)
        enc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
        i += 1
    cap.release()
    enc.stdin.close()
    if enc.wait():
        sys.exit("ffmpeg failed while encoding")
    print(f"{rel(out)}: {i / src_fps:.1f}s, {W}x{H}, camera {args.camera if args.camera in ('static', 'generated') else 'from ' + rel(args.camera)}, "
          f"overscan {z0:.3f}x, pull-back {args.pullback:g}s, exposure {args.exposure:g}, saturation {args.saturation:g}, "
          f"sharpen {args.sharpen:g}, grain sigma {args.grain:g}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("target")
    s.add_argument("--fps", type=float, default=15)
    d = sub.add_parser("driver")
    d.add_argument("target")
    d.add_argument("--out", required=True)
    d.add_argument("--segment", type=int, default=1)
    d.add_argument("--start", type=float)
    d.add_argument("--end", type=float)
    d.add_argument("--size", type=int, choices=[720, 1080], default=720)
    d.add_argument("--no-crop", action="store_true")
    p = sub.add_parser("preflight")
    p.add_argument("character")
    p.add_argument("driver")
    p.add_argument("--orientation", choices=["video", "image"], default="video")
    c = sub.add_parser("check")
    c.add_argument("driver")
    c.add_argument("clip")
    c.add_argument("--source")
    fc = sub.add_parser("faces")
    fc.add_argument("video")
    fc.add_argument("--every", type=int, default=6, help="every Nth frame (at 30 fps)")
    fc.add_argument("--z", type=float, default=4.0, help="flag a proportion this many MADs from the clip's median")
    sp = sub.add_parser("splice")
    sp.add_argument("takes", nargs="+")
    sp.add_argument("--out", required=True)
    sp.add_argument("--window", type=float, default=1.0, help="seconds per choice")
    sp.add_argument("--crossfade", type=int, default=4, help="frames")
    sp.add_argument("--plan", help="manual choices in seconds, e.g. '0-3:a,3-5:b' (the rest is automatic)")
    sp.add_argument("--z", type=float, default=4.0)
    f = sub.add_parser("finish")
    f.add_argument("clip")
    f.add_argument("--out", required=True)
    f.add_argument("--camera", default="generated",
                   help="'generated' keeps the model's camera; 'static' locks it; a video path (the driver) replays that "
                        "video's real camera movement")
    f.add_argument("--pullback", type=float, default=0.0, help="seconds of digital pull-back at the start (0 = none)")
    f.add_argument("--zoom", type=float, default=1.8, help="zoom at the first frame of the pull-back")
    f.add_argument("--exposure", type=float, default=1.0, help="brightness gain")
    f.add_argument("--saturation", type=float, default=1.0, help="colour gain around grey")
    f.add_argument("--sharpen", type=float, default=0.0, help="unsharp-mask amount")
    f.add_argument("--grain", type=float, default=3.0, help="sensor noise sigma in 8-bit levels (0 = none)")
    args = ap.parse_args()
    if args.cmd == "driver" and (args.start is None) != (args.end is None):
        sys.exit("give both --start and --end, or neither")
    {"scan": cmd_scan, "driver": cmd_driver, "preflight": cmd_preflight, "check": cmd_check,
     "finish": cmd_finish, "faces": cmd_faces,
     "splice": cmd_splice}[args.cmd](args)


if __name__ == "__main__":
    main()
