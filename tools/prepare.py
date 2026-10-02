#!/usr/bin/env python3
"""Turn downloaded posts into analysis-ready files, so Claude reads small, labeled images
instead of full-resolution media.

Usage:
  prepare.py <post folder or creator folder> [--no-transcript] [--refresh]

Writes <post folder>/analysis/:
  sheet.jpg        one overview image: all slides, or the video's key frames with timestamps
  slides/NN.jpg    slideshows: each slide, downsized to 1024px
  frames/*.jpg     videos: one key frame per shot, plus frames at 0s, 1s and 2s (the hook)
  measures.json    numbers measured in code: counts, timing, pacing, palettes, transcript, and (from measure.py) per-frame
                   visual measures and per-shot camera motion
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import portable
from measure import camera_motion, visual_measures

ROOT = Path(__file__).resolve().parent.parent
FFMPEG, FFPROBE = portable.exe("ffmpeg"), portable.exe("ffprobe")
os.environ["PATH"] = f"{Path(FFMPEG).parent}{os.pathsep}{os.environ.get('PATH', '')}"  # mlx-whisper calls ffmpeg by name
READ_SIZE = 1024       # long edge for images Claude reads one by one
TILE = 360             # long edge for contact-sheet tiles
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"  # Apple Silicon (mlx-whisper)
FASTER_WHISPER_MODEL = "large-v3-turbo"                # the same model elsewhere, e.g. Windows (faster-whisper)


def palette(img, k=5):
    """Top-k dominant colors as hex, largest share first (k-means on a small copy)."""
    px = np.asarray(img.convert("RGB").resize((96, 96)), dtype=np.float32).reshape(-1, 3)
    rng = np.random.default_rng(0)
    centers = px[rng.choice(len(px), k, replace=False)]
    for _ in range(12):
        labels = np.argmin(((px[:, None] - centers[None]) ** 2).sum(-1), axis=1)
        centers = np.array([px[labels == i].mean(0) if (labels == i).any() else centers[i] for i in range(k)])
    shares = np.bincount(labels, minlength=k) / len(px)
    order = np.argsort(-shares)
    return [{"hex": "#%02x%02x%02x" % tuple(int(c) for c in centers[i]), "share": round(float(shares[i]), 3)}
            for i in order]


def shrink(img, size):
    img = img.convert("RGB")
    img.thumbnail((size, size))
    return img


def contact_sheet(images, labels, dest, cols=4):
    tiles = [shrink(im, TILE) for im in images]
    w = max(t.width for t in tiles)
    h = max(t.height for t in tiles) + 26
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (w * min(cols, len(tiles)), h * rows), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)
    for i, (t, label) in enumerate(zip(tiles, labels)):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(t, (x, y + 26))
        draw.text((x + 6, y + 3), label, fill="black", font=font)
    sheet.save(dest, quality=85)


def frame_at(video, t, dest):
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
                    "-frames:v", "1", "-vf", f"scale='min({READ_SIZE},iw)':-2", str(dest)], check=True)
    return Image.open(dest)


def duration_of(video):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def whisper(media):
    """Whisper large-v3-turbo segments and the detected language. Apple Silicon Macs run it on the GPU with mlx-whisper;
    Windows (and Intel Macs) run the same model on the CPU with faster-whisper: slower, same segment fields."""
    if sys.platform == "darwin" and platform.machine() == "arm64":
        import mlx_whisper
        r = mlx_whisper.transcribe(str(media), path_or_hf_repo=WHISPER_MODEL, verbose=None)
        return r.get("segments", []), r.get("language")
    from faster_whisper import WhisperModel
    segments, info = WhisperModel(FASTER_WHISPER_MODEL, device="cpu", compute_type="int8").transcribe(str(media))
    return [{"start": s.start, "end": s.end, "text": s.text, "no_speech_prob": s.no_speech_prob,
             "avg_logprob": s.avg_logprob, "compression_ratio": s.compression_ratio} for s in segments], info.language


def transcribe(media):
    raw, language = whisper(media)
    segs = [{"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip(),
             "no_speech": round(s.get("no_speech_prob", 0), 2), "avg_logprob": round(s.get("avg_logprob", 0), 2),
             "compression_ratio": round(s.get("compression_ratio", 0), 2)} for s in raw]
    for s in segs:  # music makes Whisper invent words ("Thank you.", "so", "and and and") even when no_speech is 0.0
        why = []
        if s["no_speech"] >= 0.5:
            why.append("no_speech >= 0.5")
        if not 0.8 <= s["compression_ratio"] <= 2.4:
            why.append(f"compression ratio {s['compression_ratio']} is outside 0.8-2.4 (typical of a hallucination on music)")
        if s["end"] - s["start"] >= 6 and len(s["text"].split()) <= 3:
            why.append("1-3 words spread over 6s or more")
        s["suspect"] = why
    speech = [s for s in segs if s["text"] and not s["suspect"]]
    return {"language": language, "has_speech": bool(speech), "segments": segs,
            "note": "A segment with a non-empty 'suspect' list is probably music or noise, not words. has_speech is true only if at least one segment passes."}


def prepare_slideshow(folder, post, out):
    slides = [folder / s for s in post["files"]["slides"]]
    images = [Image.open(s) for s in slides]
    (out / "slides").mkdir(parents=True, exist_ok=True)
    for i, im in enumerate(images, 1):
        shrink(im, READ_SIZE).save(out / "slides" / f"{i:02}.jpg", quality=88)
    contact_sheet(images, [f"slide {i}" for i in range(1, len(images) + 1)], out / "sheet.jpg")
    return {
        "type": "slideshow",
        "slide_count": len(images),
        "size": {"width": images[0].width, "height": images[0].height},
        "aspect": f"{images[0].width}:{images[0].height}",
        "palettes": {f"slide {i}": palette(im) for i, im in enumerate(images, 1)},
        "visual": {f"slide {i}": visual_measures(im) for i, im in enumerate(images, 1)},
    }


def find_shots(video, length):
    """Shot list as [(start, end)] plus the detector used. Animated or hard-cut edits on a constant background (e.g. a
    mascot on white) barely move the default threshold, so if it finds under 4 cuts in a video of 8s or more, retry finer."""
    from scenedetect import ContentDetector, detect
    cuts, method = detect(str(video), ContentDetector()), "content-27"
    if len(cuts) < 4 and length >= 8:
        finer = detect(str(video), ContentDetector(threshold=12))
        if len(finer) > len(cuts):
            cuts, method = finer, "content-12 (fallback: the default found few cuts)"
    shots = [(a.seconds, min(b.seconds, length)) for a, b in cuts] or [(0.0, length)]  # scenedetect can report an end past the file
    merged = []
    for a, b in shots:  # a shot under 0.15s is a detector artifact: fold it into the one before
        if merged and b - a < 0.15:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged, method


def prepare_video(folder, post, out, with_transcript):
    video = folder / post["files"]["video"]
    length = duration_of(video)
    shots, shot_detector = find_shots(video, length)
    (out / "frames").mkdir(parents=True, exist_ok=True)
    images, labels, shot_rows = [], [], []
    for t in [0.0, 1.0, 2.0]:  # the hook: what the viewer sees before deciding to stay
        if t < length:
            images.append(frame_at(video, t, out / "frames" / f"hook_{t:.0f}s.jpg"))
            labels.append(f"hook {t:.0f}s")
    for i, (a, b) in enumerate(shots, 1):
        mid = min((a + b) / 2, max(length - 0.1, 0))  # a frame past the end can't be extracted
        img = frame_at(video, mid, out / "frames" / f"shot_{i:02}_{mid:.1f}s.jpg")
        images.append(img)
        labels.append(f"shot {i}  {a:.1f}-{b:.1f}s")
        shot_rows.append({"shot": i, "start": round(a, 2), "end": round(b, 2), "length": round(b - a, 2),
                          "key_frame": f"frames/shot_{i:02}_{mid:.1f}s.jpg", "palette": palette(img),
                          "visual": visual_measures(img), "motion": camera_motion(video, a, b)})
    contact_sheet(images, labels, out / "sheet.jpg")
    measures = {
        "type": "video",
        "length": round(length, 2),
        "size": {"width": images[0].width, "height": images[0].height},
        "shot_detector": shot_detector,
        "shot_count": len(shots),
        "cuts_per_second": round((len(shots) - 1) / length, 3) if length else None,
        "average_shot_length": round(length / len(shots), 2),
        "shots": shot_rows,
    }
    if with_transcript:
        measures["transcript"] = transcribe(video)
    return measures


def prepare(folder, with_transcript=True, refresh=False):
    post = json.loads((folder / "post.json").read_text())
    out = folder / "analysis"
    if (out / "measures.json").exists() and not refresh:
        return "cached"
    out.mkdir(exist_ok=True)
    if refresh:  # a refresh can change how many frames there are; don't leave the old ones behind (fingerprint.json is kept)
        for sub in ("frames", "slides"):
            shutil.rmtree(out / sub, ignore_errors=True)
    if post["type"] == "slideshow":
        measures = prepare_slideshow(folder, post, out)
    else:
        measures = prepare_video(folder, post, out, with_transcript)
    (out / "measures.json").write_text(json.dumps(measures, ensure_ascii=False, indent=2))
    return "prepared"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--no-transcript", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    folders = [args.folder] if (args.folder / "post.json").exists() else sorted(
        p.parent for p in args.folder.glob("*/post.json"))
    if not folders:
        sys.exit(f"No downloaded posts in {args.folder}")
    for f in folders:
        try:
            print(f"  {f.name}  {prepare(f, not args.no_transcript, args.refresh)}")
        except Exception as e:
            print(f"  {f.name}  FAILED: {e}")


if __name__ == "__main__":
    main()
