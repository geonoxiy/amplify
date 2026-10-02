#!/usr/bin/env python3
"""kie.ai image generation with spending guards. Amplify pays per credit (1 credit = $0.005).

Usage:
  kie.py balance
  kie.py image --model nb|nb-edit|nb2 --prompt "…" [--ref img …] [--aspect 9:16] --out file.png
               [--run <run folder>] [--run-cap 100] [--resolution 1K]
  kie.py video --model kling3 --prompt "…" --first-frame still.png --duration 3 [--mode std|pro] --out clip.mp4
               [--run <run folder>] [--run-cap 100]      image-to-video, whole seconds 3 to 15, silent
  kie.py motion --model kling3-mc --character still.png --driver driver.mp4 [--prompt "…"] [--orientation video|image]
               [--mode 720p|1080p] --out clip.mp4 [--run <run folder>] [--run-cap 100]
  kie.py upscale-video clip.mp4 --factor 1|2|4 --out up.mp4 [--run …]   Topaz video upscale (factor 1 = enhance only)
                                                 motion control: the persona copies the driver's movement (motion.py
                                                 driver makes the driver; motion.py preflight runs first and blocks a
                                                 fail; billed by the driver's length)
  kie.py spend                                   total spent so far, by run

Guards:
  - Every call is priced before it's sent; a run can't exceed --run-cap credits (default 100 = $0.50).
  - Identical requests (same model, prompt, references, aspect) are served from .cache/kie for free.
  - Local reference images and driver videos are uploaded once and the URL reused for 20 hours (kie deletes uploads after ~24h).
  - Every paid call is logged to content-bank/spend.csv and the run's costs.json.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "kie"
LEDGER = ROOT / "content-bank" / "spend.csv"
API = "https://api.kie.ai/api/v1"
UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
USD_PER_CREDIT = 0.005

MODELS = {  # alias: (model id, credits per image, how references are passed)
    "nb": ("google/nano-banana", 4, None),
    "nb-edit": ("google/nano-banana-edit", 4, "image_urls"),
    "nb2": ("nano-banana-2", 8, "image_input"),  # 1K; 2K = 12, 4K = 18
    "nbp": ("nano-banana-pro", 18, "image_input"),  # best realism + identity hold; up to 8 refs; 1K/2K = 18, 4K = 24
    "sd5": ("seedream/5-pro-image-to-image", 12, "image_urls"),  # Seedream 5.0 Pro: up to 10 refs; 1K = basic, 2K+ = high (2K); price unverified
}


VIDEO_MODELS = {  # alias: (model id, estimated credits per second by mode). The estimate only guards the cap;
    # the real cost (creditsConsumed) is what gets logged. Estimates come from a third-party price list, unverified.
    "kling3": ("kling-3.0/video", {"std": 14, "pro": 18}),
}

MOTION_MODELS = {  # alias: (model id, input style, estimated credits per second of driver by output resolution).
    # Kling 3.0 is measured (P015 run-01, 2026-10-01): 720p 280 credits for a 14.6 s driver (about 19.2/s), 1080p 351
    # for 13.4 s (about 26.2/s); the figures keep a small margin. kling26-mc and wan-move are unverified guesses. The
    # real cost (creditsConsumed) is what gets logged.
    "kling3-mc": ("kling-3.0/motion-control", "kling", {"720p": 20, "1080p": 27}),  # best identity hold, up to 30 s
    "kling26-mc": ("kling-2.6/motion-control", "kling", {"720p": 30, "1080p": 40}),
    "wan-move": ("wan/2-2-animate-move", "wan", {"480p": 12, "580p": 18, "720p": 25}),  # cheapest, no prompt
}
VIDEO_EXT = {".mp4", ".mov"}


def key():
    k = os.environ.get("KIE_API_KEY")
    if not k and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("KIE_API_KEY="):
                k = line.split("=", 1)[1].strip()
    if not k:
        sys.exit("No KIE_API_KEY in environment or .env")
    return k


def headers():
    return {"Authorization": f"Bearer {key()}"}


def api(method, path, **kw):
    r = requests.request(method, f"{API}{path}", headers=headers(), timeout=60, **kw)
    body = r.json()
    if body.get("code") != 200:
        sys.exit(f"kie.ai error {body.get('code')}: {body.get('msg')}")
    return body["data"]


def balance():
    return float(api("GET", "/chat/credit"))


def sha(path_or_text):
    p = Path(path_or_text)
    data = p.read_bytes() if p.exists() else str(path_or_text).encode()
    return hashlib.sha256(data).hexdigest()


def upload(path, max_edge=1280):
    """Upload a local image or video once; reuse its URL for 20 hours."""
    CACHE.mkdir(parents=True, exist_ok=True)
    index_file = CACHE / "uploads.json"
    index = json.loads(index_file.read_text()) if index_file.exists() else {}
    h = sha(path)
    is_video = Path(path).suffix.lower() in VIDEO_EXT
    slot = h if is_video or max_edge == 1280 else f"{h}_{max_edge}"
    hit = index.get(slot)
    if hit and time.time() - hit["time"] < 20 * 3600:
        return hit["url"]
    if is_video:  # drivers go up as they are: motion.py driver already made them small
        send, mime = Path(path), "video/mp4"
    else:  # references only need to be readable, not full size: a 1280px JPEG uploads in seconds (an 8 MB PNG stalls)
        from PIL import Image
        send, mime = CACHE / (f"ref_{h[:16]}.jpg" if max_edge == 1280 else f"ref_{h[:16]}_{max_edge}.jpg"), "image/jpeg"
        im = Image.open(path).convert("RGB")
        im.thumbnail((max_edge, max_edge))
        im.save(send, quality=90)
    for attempt in range(4):
        try:
            with open(send, "rb") as f:
                r = requests.post(UPLOAD, headers=headers(), timeout=300,
                                  files={"file": (send.name, f, mime)}, data={"uploadPath": "amplify"})
            body = r.json()
            break
        except requests.RequestException as e:
            print(f"  upload attempt {attempt + 1} failed ({type(e).__name__}), retrying", flush=True)
            time.sleep(3)
    else:
        sys.exit("upload failed after 4 attempts")
    if not body.get("success", body.get("code") == 200):
        sys.exit(f"upload failed: {body}")
    url = body["data"].get("fileUrl") or body["data"].get("downloadUrl")
    index[slot] = {"url": url, "time": time.time(), "file": str(path)}
    index_file.write_text(json.dumps(index, indent=1))
    return url


def download(url, dest, tries=12):
    """kie's temp file host is slow and drops connections; stream with resume and short timeouts."""
    dest = Path(dest)
    part = dest.with_suffix(".part")
    part.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(tries):
        have = part.stat().st_size if part.exists() else 0
        try:
            r = requests.get(url, stream=True, timeout=(10, 30), headers={"Range": f"bytes={have}-"} if have else {})
            if r.status_code == 416:  # already complete
                break
            r.raise_for_status()
            if have and r.status_code != 206:
                have = 0
            with open(part, "ab" if have else "wb") as f:
                for chunk in r.iter_content(65536):
                    f.write(chunk)
            break
        except requests.RequestException as e:
            print(f"  download attempt {attempt + 1} interrupted ({type(e).__name__}); resuming at {have} bytes", flush=True)
            time.sleep(2)
    else:
        sys.exit(f"download failed after {tries} attempts; partial file kept at {part}, url: {url}")
    part.replace(dest)


def download_via_kie(url, dest):
    """Fallback when the temp file host won't resolve or drops the connection: kie signs a link on its own storage host."""
    signed = requests.post(f"{API}/common/download-url", headers={**headers(), "Content-Type": "application/json"},
                           json={"url": url}, timeout=30).json().get("data")
    if not signed:
        sys.exit(f"kie gave no download link for {url}")
    r = requests.get(signed, timeout=(10, 120))
    r.raise_for_status()
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    Path(dest).write_bytes(r.content)


def run_spent(run):
    f = Path(run) / "costs.json"
    return sum(c["credits"] for c in json.loads(f.read_text())) if f.exists() else 0


def log(run, model, task, credits, out, prompt):
    LEDGER.parent.mkdir(exist_ok=True)
    new = not LEDGER.exists()
    with open(LEDGER, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "run", "model", "task_id", "credits", "usd", "output"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), run or "", model, task,
                    credits, round(credits * USD_PER_CREDIT, 4), out])
    if run:
        f = Path(run) / "costs.json"
        rows = json.loads(f.read_text()) if f.exists() else []
        rows.append({"model": model, "task_id": task, "credits": credits, "output": str(out),
                     "prompt": prompt[:300]})
        f.write_text(json.dumps(rows, indent=1))


def from_cache(cached, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    if cached.exists():
        shutil.copy(cached, out)
        print(f"cache hit, 0 credits → {out}")
        return True
    return False


def check_cap(run, price, cap):
    if run:
        spent = run_spent(run)
        if spent + price > cap:
            sys.exit(f"Run cap reached: spent {spent} + ~{price:g} > cap {cap:g} credits. Raise --run-cap on purpose.")


def submit(model, inp, price, cached, out, run, prompt, label, polls):
    """Create the task, wait for it (3 s per poll), log the real cost, then download into the cache and copy to out."""
    task = api("POST", "/jobs/createTask", json={"model": model, "input": inp})["taskId"]
    print(f"task {task} ({label}, ~{price:g} credits) …", flush=True)
    for _ in range(polls):
        time.sleep(3)
        d = api("GET", "/jobs/recordInfo", params={"taskId": task})
        if d["state"] == "success":
            url = json.loads(d["resultJson"])["resultUrls"][0]
            CACHE.mkdir(parents=True, exist_ok=True)
            credits = float(d.get("creditsConsumed") or price)
            log(run, model, task, credits, out, prompt)  # paid already: record before the slow download
            try:
                download(url, cached, tries=3)
            except SystemExit:
                print("  direct download failed; asking kie for a signed link", flush=True)
                download_via_kie(url, cached)
            shutil.copy(cached, out)
            print(f"done: {credits:g} credits (${credits * USD_PER_CREDIT:.3f}) → {out}")
            return
        if d["state"] == "fail":
            log(run, model, task, float(d.get("creditsConsumed") or 0), "FAILED", prompt)
            sys.exit(f"task failed: {d.get('failCode')} {d.get('failMsg')}")
    sys.exit(f"timed out waiting for task {task}; check https://kie.ai/logs")


def image(args):
    model, price, ref_field = MODELS[args.model]
    if args.model == "nb2":
        price = {"1K": 8, "2K": 12, "4K": 18}[args.resolution]
    if args.model == "nbp":
        price = {"1K": 18, "2K": 18, "4K": 24}[args.resolution]
    refs = args.ref or []
    if refs and not ref_field:
        sys.exit(f"{args.model} takes no reference images; use nb-edit or nb2")
    cache_key = hashlib.sha256(json.dumps(
        [model, args.prompt, [sha(r) for r in refs], args.aspect, args.resolution]).encode()).hexdigest()[:24]
    cached, out = CACHE / f"{cache_key}.png", Path(args.out)
    if from_cache(cached, out):
        return
    check_cap(args.run, price, args.run_cap)
    inp = {"prompt": args.prompt, "aspect_ratio": args.aspect, "output_format": "png"}
    if refs:
        inp[ref_field] = [r if r.startswith("http") else upload(r) for r in refs]
    if args.model in ("nb2", "nbp"):
        inp["resolution"] = args.resolution
    if args.model == "sd5":
        inp["quality"] = "basic" if args.resolution == "1K" else "high"
    submit(model, inp, price, cached, out, args.run, args.prompt, model, polls=120)  # up to ~6 minutes


def video(args):
    """Image-to-video: the first frame goes in, a silent clip comes out (whole seconds, 3 to 15)."""
    model, per_sec = VIDEO_MODELS[args.model]
    if not 3 <= args.duration <= 15:
        sys.exit("duration must be a whole number of seconds from 3 to 15")
    price = per_sec[args.mode] * args.duration
    frame = args.first_frame
    cache_key = hashlib.sha256(json.dumps(
        [model, args.prompt, sha(frame), args.duration, args.mode, args.aspect]).encode()).hexdigest()[:24]
    cached, out = CACHE / f"{cache_key}.mp4", Path(args.out)
    if from_cache(cached, out):
        return
    check_cap(args.run, price, args.run_cap)
    inp = {"prompt": args.prompt, "image_urls": [frame if frame.startswith("http") else upload(frame)],
           "duration": str(args.duration), "mode": args.mode, "aspect_ratio": args.aspect,
           "sound": False, "multi_shots": False}
    submit(model, inp, price, cached, out, args.run, args.prompt,
           f"{model} {args.mode}, {args.duration}s", polls=300)  # up to ~15 minutes


def motion(args):
    """Motion control: the persona still takes the movement of the driver video. Output length = driver length."""
    model, style, per_sec = MOTION_MODELS[args.model]
    mode = args.mode or "720p"
    if mode not in per_sec:
        sys.exit(f"{args.model} takes --mode {' or '.join(per_sec)}")
    if style == "wan" and args.prompt:
        sys.exit(f"{args.model} takes no prompt")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from motion import preflight  # pose model + rules: fictional persona, framing, input limits
    pf = preflight(args.character, args.driver, args.orientation)
    for w in pf["warnings"]:
        print(f"  preflight warning: {w}")
    if not pf["ok"]:
        sys.exit("preflight failed, nothing sent:\n  " + "\n  ".join(pf["fails"]))
    price = per_sec[mode] * math.ceil(pf["driver_seconds"])
    cache_key = hashlib.sha256(json.dumps([model, args.prompt, sha(args.character), sha(args.driver),
                                           args.orientation, mode]).encode()).hexdigest()[:24]
    cached, out = CACHE / f"{cache_key}.mp4", Path(args.out)
    if from_cache(cached, out):
        return
    check_cap(args.run, price, args.run_cap)
    img = upload(args.character, max_edge=1280 if mode != "1080p" else 2048)
    vid = upload(args.driver)
    if style == "kling":  # kie's docs list mode as 720p/1080p in the options and the example (std/pro in one line of prose)
        inp = {"input_urls": [img], "video_urls": [vid], "character_orientation": args.orientation, "mode": mode}
        if model.startswith("kling-3.0"):  # kie's documented default is the driver's background: never let the source scene in
            inp["background_source"] = "input_image"
        if args.prompt:
            inp["prompt"] = args.prompt
    else:
        inp = {"image_url": img, "video_url": vid, "resolution": mode}
    submit(model, inp, price, cached, out, args.run, args.prompt or "",
           f"{model} {mode}, {pf['driver_seconds']}s driver", polls=700)  # up to ~35 minutes


def upscale_video(args):
    """Topaz video upscale (no model or face options exposed by kie): factor 1 enhances in place, 2 or 4 enlarge."""
    model = "topaz/video-upscale"
    src = Path(args.video)
    if src.stat().st_size > 50e6:
        sys.exit("Topaz takes videos up to 50 MB")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from motion import duration_of
    seconds = duration_of(src)
    price = math.ceil(seconds) * 8 * int(args.factor)  # unverified guess, set high; the real cost is logged
    cache_key = hashlib.sha256(json.dumps([model, sha(src), args.factor]).encode()).hexdigest()[:24]
    cached, out = CACHE / f"{cache_key}.mp4", Path(args.out)
    if from_cache(cached, out):
        return
    check_cap(args.run, price, args.run_cap)
    inp = {"video_url": upload(src), "upscale_factor": str(args.factor)}
    submit(model, inp, price, cached, out, args.run, f"topaz x{args.factor} {src.name}",
           f"{model} x{args.factor}, {seconds:.1f}s", polls=700)


def spend():
    if not LEDGER.exists():
        print("Nothing spent yet.")
        return
    rows = list(csv.DictReader(open(LEDGER)))
    total = sum(float(r["credits"]) for r in rows)
    by_run = {}
    for r in rows:
        by_run[r["run"] or "(no run)"] = by_run.get(r["run"] or "(no run)", 0) + float(r["credits"])
    print(f"{len(rows)} paid calls · {total:g} credits · ${total * USD_PER_CREDIT:.2f}")
    for run, c in by_run.items():
        print(f"  {c:>6g} credits  ${c * USD_PER_CREDIT:.2f}  {run}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("balance")
    sub.add_parser("spend")
    p = sub.add_parser("image")
    p.add_argument("--model", choices=MODELS, default="nb")
    p.add_argument("--prompt", required=True)
    p.add_argument("--ref", nargs="*", help="reference images: local files or URLs")
    p.add_argument("--aspect", default="9:16")
    p.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    p.add_argument("--out", required=True)
    p.add_argument("--run", help="run folder, for per-run cost tracking and the cap")
    p.add_argument("--run-cap", type=float, default=100, help="max credits per run (default 100 = $0.50)")
    v = sub.add_parser("video")
    v.add_argument("--model", choices=VIDEO_MODELS, default="kling3")
    v.add_argument("--prompt", required=True)
    v.add_argument("--first-frame", required=True, help="local image or URL: the first frame of the clip")
    v.add_argument("--duration", type=int, default=3)
    v.add_argument("--mode", choices=["std", "pro"], default="std")
    v.add_argument("--aspect", default="9:16")
    v.add_argument("--out", required=True)
    v.add_argument("--run")
    v.add_argument("--run-cap", type=float, default=100)
    m = sub.add_parser("motion")
    m.add_argument("--model", choices=MOTION_MODELS, default="kling3-mc")
    m.add_argument("--character", required=True, help="the persona still: a file in personas/ or a run folder")
    m.add_argument("--driver", required=True, help="driver.mp4 from motion.py driver")
    m.add_argument("--prompt", help="optional: scene and style (the still's look and background are kept)")
    m.add_argument("--orientation", choices=["video", "image"], default="video",
                   help="face the way the driver faces (up to 30 s) or the way the still faces (up to 10 s)")
    m.add_argument("--mode", help="output resolution: 720p or 1080p (wan-move: 480p, 580p or 720p); default 720p")
    m.add_argument("--out", required=True)
    m.add_argument("--run")
    m.add_argument("--run-cap", type=float, default=100)
    u = sub.add_parser("upscale-video")
    u.add_argument("video")
    u.add_argument("--factor", choices=["1", "2", "4"], default="2")
    u.add_argument("--out", required=True)
    u.add_argument("--run")
    u.add_argument("--run-cap", type=float, default=100)
    args = ap.parse_args()
    if args.cmd == "balance":
        b = balance()
        print(f"{b:,.2f} credits (${b * USD_PER_CREDIT:,.2f})")
    elif args.cmd == "spend":
        spend()
    elif args.cmd == "video":
        video(args)
    elif args.cmd == "motion":
        motion(args)
    elif args.cmd == "upscale-video":
        upscale_video(args)
    else:
        image(args)


if __name__ == "__main__":
    main()
