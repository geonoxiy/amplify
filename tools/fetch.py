#!/usr/bin/env python3
"""Download TikTok posts (slideshows and videos) with their data.

Usage:
  fetch.py <post or creator link> [--limit 20] [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--refresh]

Each post is saved to content-bank/_sources/<creator>/<post id>/:
  post.json        normalized data: caption, hashtags, stats, rates, sound, timing, labels
  raw.json         everything TikTok returned, for fields post.json doesn't cover yet
  slides/01.jpg …  slideshow images, full resolution
  video.mp4        video posts (audio included)
  sound.mp3        the slideshow's sound
Creator links also write content-bank/_sources/<creator>/creator.json.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import portable

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "content-bank" / "_sources"
LOCAL_TZ = ZoneInfo("Asia/Manila")  # all posting times are normalized to this timezone
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36"

POST_RE = re.compile(r"tiktok\.com/@([^/?#]+)/(?:video|photo)/(\d+)")
CREATOR_RE = re.compile(r"tiktok\.com/@([^/?#]+)/?(?:[?#].*)?$")


def run(cmd):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{Path(str(cmd[0])).name} failed: {p.stderr.strip()[-600:]}")
    return p.stdout


def resolve(link):
    """Expand short share links (vm.tiktok.com, vt.tiktok.com, tiktok.com/t/…)."""
    if re.search(r"//(vm|vt)\.tiktok\.com/|tiktok\.com/t/", link):
        req = urllib.request.Request(link, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.geturl()
    return link


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.tiktok.com/"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def id_time(post_id):
    # A TikTok ID carries a rough creation time (can be hours off for scheduled posts).
    return datetime.fromtimestamp(int(post_id) >> 32, timezone.utc)


def list_creator(handle, limit, since, until):
    """Return the creator's post IDs: the latest `limit`, or those published in [since, until]."""
    ranged = since or until
    # Pinned posts come first regardless of age, so read a few extra and sort by ID (newest first).
    end = 1000 if ranged else limit + 3
    data = json.loads(run([portable.exe("yt-dlp"), "--flat-playlist", "--playlist-end", end, "-J",
                           f"https://www.tiktok.com/@{handle}"]))
    ids = []
    for e in data.get("entries") or []:
        m = re.search(r"/(\d{15,})", e.get("url") or "") or re.fullmatch(r"(\d{15,})", str(e.get("id") or ""))
        if m:
            ids.append(m.group(1))
    ids = sorted(set(ids), key=int, reverse=True)
    if not ranged:
        return ids[:limit]
    # Shortlist by ID time with a 2-day margin; exact publish times are checked after fetching.
    lo = datetime.combine(since, datetime.min.time(), LOCAL_TZ) - timedelta(days=2) if since else None
    hi = datetime.combine(until, datetime.max.time(), LOCAL_TZ) + timedelta(days=2) if until else None
    return [i for i in ids if (not lo or id_time(i) >= lo) and (not hi or id_time(i) <= hi)]


def post_meta(handle, post_id):
    items = json.loads(run([portable.exe("gallery-dl"), "-j", f"https://www.tiktok.com/@{handle}/video/{post_id}"]))
    errors = [i for i in items if i and i[0] == -1]
    meta = next((i[1] for i in items if i and i[0] == 2), None)
    if meta is None:
        meta = meta_from_ytdlp(handle, post_id)  # gallery-dl returns nothing for some posts (seen on an artist's video)
        if meta is None:
            raise RuntimeError(f"no post data returned {errors[:1]}")
    files = [(i[1], i[2]) for i in items if i and i[0] == 3]
    return meta, files


def meta_from_ytdlp(handle, post_id):
    """Video posts only: yt-dlp's data mapped onto the TikTok fields normalize() reads. yt-dlp has no save count,
    so saves stay missing (None), not zero."""
    try:
        d = json.loads(run([portable.exe("yt-dlp"), "-J", "--no-warnings", "--impersonate", "chrome",
                            f"https://www.tiktok.com/@{handle}/video/{post_id}"]))
    except (RuntimeError, json.JSONDecodeError):
        return None
    artists = d.get("artists") or ([d["artist"]] if d.get("artist") else [])
    return {"_source": "yt-dlp (gallery-dl returned nothing)", "id": post_id, "desc": d.get("description") or "",
            "createTime": d.get("timestamp"),
            "stats": {"playCount": d.get("view_count"), "diggCount": d.get("like_count"),
                      "commentCount": d.get("comment_count"), "shareCount": d.get("repost_count"),
                      "collectCount": d.get("save_count")},
            "music": {"title": d.get("track"), "authorName": ", ".join(artists) or None, "original": None,
                      "id": None},
            "video": {"duration": d.get("duration"), "width": d.get("width"), "height": d.get("height")},
            "author": {"uniqueId": handle, "nickname": d.get("uploader") or d.get("channel")}}


def hashtags_of(meta):
    tags = [t.get("hashtagName") for t in meta.get("textExtra") or []]
    tags += [c.get("title") for c in meta.get("challenges") or []]
    tags += re.findall(r"#([\wÀ-￿]+)", meta.get("desc") or "")
    seen, out = set(), []
    for t in tags:
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def normalize(meta, handle, post_id, kind, files):
    stats = meta.get("statsV2") or meta.get("stats") or {}
    n = lambda k: int(stats.get(k) or 0)
    views, likes, comments, shares = n("playCount"), n("diggCount"), n("commentCount"), n("shareCount")
    saves = n("collectCount") if stats.get("collectCount") is not None else None  # yt-dlp fallback: unknown, not 0
    rate = lambda x: round(x / views, 4) if views and x is not None else None
    published = datetime.fromtimestamp(int(meta.get("createTime") or 0) or int(id_time(post_id).timestamp()),
                                       timezone.utc)
    local = published.astimezone(LOCAL_TZ)
    music = meta.get("music") or {}
    video = meta.get("video") or {}
    images = (meta.get("imagePost") or {}).get("images") or []
    desc = meta.get("desc") or ""
    mentions = [t.get("userUniqueId") for t in meta.get("textExtra") or [] if t.get("userUniqueId")]
    mentions += re.findall(r"@([\w.]+)", desc)
    return {
        "id": post_id,
        "url": f"https://www.tiktok.com/@{handle}/{'photo' if kind == 'slideshow' else 'video'}/{post_id}",
        "creator": handle,
        "type": kind,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "published": {
            "utc": published.isoformat(),
            "local": local.isoformat(),
            "timezone": str(LOCAL_TZ),
            "weekday": local.strftime("%A"),
            "hour": local.hour,
        },
        "caption": desc,
        "hashtags": hashtags_of(meta),
        "mentions": list(dict.fromkeys(mentions)),
        "stats": {"views": views, "likes": likes, "comments": comments, "shares": shares, "saves": saves},
        "rates": {
            "engagement": rate(likes + comments + shares + (saves or 0)),
            "save": rate(saves), "share": rate(shares), "comment": rate(comments),
        },
        "sound": {
            "title": music.get("title"),
            "author": music.get("authorName"),
            "original": music.get("original"),
            "id": music.get("id"),
        },
        "slide_count": len(images) or None,
        "duration": video.get("duration") or None,
        "size": ({"width": images[0].get("imageWidth"), "height": images[0].get("imageHeight")} if images
                 else {"width": video.get("width"), "height": video.get("height")}),
        "labels": {
            "ad": bool(meta.get("isAd")),
            "ai_generated": bool(meta.get("IsAigc")) or str(meta.get("aigcLabelType") or "0") != "0",
            "location": meta.get("locationCreated"),
        },
        "files": files,
    }


def creator_profile(meta, handle):
    a, s = meta.get("author") or {}, meta.get("authorStats") or {}
    return {
        "handle": a.get("uniqueId") or handle,
        "name": a.get("nickname"),
        "bio": a.get("signature"),
        "bio_link": (a.get("bioLink") or {}).get("link"),
        "verified": a.get("verified"),
        "private": a.get("privateAccount"),
        "avatar": a.get("avatarLarger"),
        "followers": s.get("followerCount"),
        "following": s.get("followingCount"),
        "likes": s.get("heartCount") or s.get("heart"),
        "posts": s.get("videoCount"),
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def fetch_post(handle, post_id, refresh=False):
    folder = SOURCES / handle / post_id
    if (folder / "post.json").exists() and not refresh:
        return json.loads((folder / "post.json").read_text()), None, "cached"
    meta, files = post_meta(handle, post_id)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "raw.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    saved = {}
    if meta.get("imagePost"):
        kind = "slideshow"
        slides = []
        for url, info in files:
            ext = (info.get("extension") or "jpg").replace("jpeg", "jpg")
            if ext in ("mp3", "m4a"):
                download(url, folder / f"sound.{ext}")
                saved["sound"] = f"sound.{ext}"
            else:
                name = f"slides/{int(info.get('num') or len(slides) + 1):02}.{ext}"
                download(url, folder / name)
                slides.append(name)
        saved["slides"] = sorted(slides)
    else:
        kind = "video"
        run([portable.exe("yt-dlp"), "-q", "--no-warnings", "--impersonate", "chrome", "-f", "bv*+ba/b",
             "--merge-output-format", "mp4", "--ffmpeg-location", portable.exe("ffmpeg"),
             "-o", folder / "video.%(ext)s", f"https://www.tiktok.com/@{handle}/video/{post_id}"])
        saved["video"] = "video.mp4"
    post = normalize(meta, handle, post_id, kind, saved)
    (folder / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2))
    return post, meta, "downloaded"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("link")
    ap.add_argument("--limit", type=int, default=20, help="latest N posts for a creator link (default 20)")
    ap.add_argument("--since", type=date.fromisoformat, help="creator link: first publish date, YYYY-MM-DD")
    ap.add_argument("--until", type=date.fromisoformat, help="creator link: last publish date, YYYY-MM-DD")
    ap.add_argument("--refresh", action="store_true", help="download again even if already saved")
    args = ap.parse_args()

    link = resolve(args.link.strip())
    if m := POST_RE.search(link):
        handle, targets, is_creator = m.group(1), [m.group(2)], False
    elif m := CREATOR_RE.search(link):
        handle, is_creator = m.group(1), True
        targets = list_creator(handle, args.limit, args.since, args.until)
    else:
        sys.exit(f"Not a TikTok post or creator link: {link}")

    print(f"@{handle}: {len(targets)} post(s) to fetch")
    results, last_meta = [], None
    for i, pid in enumerate(targets, 1):
        try:
            post, meta, status = fetch_post(handle, pid, args.refresh)
        except Exception as e:  # keep going; one broken post shouldn't stop a creator run
            print(f"  [{i}/{len(targets)}] {pid}  FAILED: {e}")
            results.append({"id": pid, "status": "failed", "error": str(e)[:300]})
            continue
        last_meta = meta or last_meta
        pub = datetime.fromisoformat(post["published"]["local"]).date()
        if (args.since and pub < args.since) or (args.until and pub > args.until):
            print(f"  [{i}/{len(targets)}] {pid}  outside date range ({pub}), kept but not counted")
            continue
        count = post["slide_count"] and f"{post['slide_count']} slides" or f"{post['duration']}s video"
        print(f"  [{i}/{len(targets)}] {pid}  {post['type']:9} {count:>11}  {post['stats']['views']:>9,} views  {status}")
        results.append({"id": pid, "status": status, "type": post["type"]})

    if is_creator:
        folder = SOURCES / handle
        if last_meta:
            (folder / "creator.json").write_text(json.dumps(creator_profile(last_meta, handle), ensure_ascii=False, indent=2))
        (folder / "last_run.json").write_text(json.dumps(
            {"link": link, "limit": args.limit, "since": str(args.since or ""), "until": str(args.until or ""),
             "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "posts": results}, indent=2))
    failed = sum(r["status"] == "failed" for r in results)
    print(f"Done: {len(results) - failed} ok, {failed} failed → {SOURCES / handle}")


if __name__ == "__main__":
    main()
