#!/usr/bin/env python3
"""Pull the sound a source post used and add it to a replication.

Usage:
  sound.py extract <source post folder> --out <dir>      audio track of the source video (stream copy, no re-encode)
                                                          → <dir>/<title>_<author>_source-clip.m4a + <dir>/sound.json (metadata, provenance, caveats)
  sound.py attach <video.mp4> <audio.m4a> --out <mp4> [--fade 0.3]
                                                          mux: the video is copied, the audio is cut to the video's length with a short fade-out

Notes:
- The clip is only the part of the sound that the source video used (its audio track), not the full TikTok sound.
- Third-party music: the rights stay with its owner. The file is for the replication draft; the licensed way to use a sound
  is to pick it in TikTok by name or ID when posting. sound.json records TikTok's own flags (original, commercial library).
- Source posts are internal-analysis material (Project Deliverables §9): the extracted clip stays in the run folder.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import portable

ROOT = Path(__file__).resolve().parent.parent


def ffmpeg():
    return portable.exe("ffmpeg")


def ffprobe():
    return portable.exe("ffprobe")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "unknown").lower()).strip("-")[:40]


def seconds(path):
    out = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def extract(a):
    src = Path(a.post)
    post = json.loads((src / "post.json").read_text())
    raw = json.loads((src / "raw.json").read_text()) if (src / "raw.json").exists() else {}
    music = raw.get("music") or {}
    if not (src / "video.mp4").exists():
        sys.exit(f"{src}/video.mp4 not found (slideshows have no audio track here)")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    title, author = post["sound"].get("title"), post["sound"].get("author")
    clip = out / f"{slug(title)}_{slug(author)}_source-clip.m4a"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src / "video.mp4"), "-vn", "-c:a", "copy", str(clip)], check=True)
    vol = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(clip), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    mean = re.search(r"mean_volume: (-?[\d.]+) dB", vol)
    mx = re.search(r"max_volume: (-?[\d.]+) dB", vol)
    info = {
        "title": title, "author": author, "album": music.get("album"),
        "tiktok_sound_id": post["sound"].get("id"),
        "tiktok_sound_page": f"https://www.tiktok.com/music/{slug(title).title()}-{post['sound'].get('id')}" if post["sound"].get("id") else None,
        "sound_page_note": "standard TikTok sound-page pattern, not opened",
        "original_sound": post["sound"].get("original"),
        "full_sound_seconds": music.get("duration"),
        "tiktok_flags": {"isCopyrighted": music.get("isCopyrighted"), "is_commerce_music": music.get("is_commerce_music"),
                         "is_unlimited_music": music.get("is_unlimited_music")},
        "source_post": post["url"],
        "clip_file": clip.name, "clip_seconds": round(seconds(clip), 2),
        "clip_is": "the audio track of the source video (the part of the sound the source used), copied without re-encoding",
        "loudness_db": {"mean": float(mean.group(1)) if mean else None, "max": float(mx.group(1)) if mx else None},
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "caveats": [
            "Third-party music: rights stay with the owner. The licensed way to use it is to pick the sound in TikTok by name or ID when posting.",
            "TikTok's data does not list it as commercial-library music (is_commerce_music false): business or brand accounts may not be allowed to use it.",
            "This clip is the source video's mix, which may also carry that video's own audio.",
        ],
    }
    (out / "sound.json").write_text(json.dumps(info, indent=1, ensure_ascii=False))
    print(f"{clip}  ({info['clip_seconds']} s, mean {info['loudness_db']['mean']} dB)")
    print(f"{out / 'sound.json'}")


def attach(a):
    vlen = seconds(a.video)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fade_at = max(vlen - a.fade, 0)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", a.video, "-i", a.audio,
                    "-filter_complex", f"[1:a]atrim=0:{vlen:.3f},afade=t=out:st={fade_at:.3f}:d={a.fade}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print(f"{out}  (video {vlen:.2f} s, audio cut to match, {a.fade} s fade-out)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("post")
    e.add_argument("--out", required=True)
    t = sub.add_parser("attach")
    t.add_argument("video")
    t.add_argument("audio")
    t.add_argument("--out", required=True)
    t.add_argument("--fade", type=float, default=0.3)
    a = ap.parse_args()
    extract(a) if a.cmd == "extract" else attach(a)


if __name__ == "__main__":
    main()
