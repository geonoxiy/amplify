#!/usr/bin/env python3
"""Download Instagram posts (Reels, photo and carousel posts) with their data, without logging in.

The Instagram twin of fetch.py: it saves each post in the same folder layout and the same post.json fields, so
prepare.py, measure.py, motion.py, creator_stats.py and the rest of the extract steps work on it unchanged.

Usage:
  fetch_insta.py <reel, post or profile link> [--limit 12] [--refresh]
  fetch_insta.py --file <video.mp4 | slide1.jpg slide2.jpg …> --handle <account> [--url <post link>] [--caption "…"]
  fetch_insta.py --stats content-bank/_sources/ig_<account>     (use this instead of creator_stats.py for Instagram)

Each post is saved to content-bank/_sources/ig_<account>/<shortcode>/:
  post.json        normalized data (same fields as fetch.py, plus "platform": "instagram")
  raw.json         what Instagram returned, for fields post.json doesn't cover
  video.mp4        Reels and video posts (audio included)
  slides/01.jpg …  photo and carousel posts, every image in order
Profile links also write content-bank/_sources/ig_<account>/creator.json.

How, and what Instagram allows without an account (tested 2026-10-05):
  - Reels and video posts: yt-dlp, full resolution with sound. Gives caption, likes, comments, time; no view count.
  - Photo and carousel posts: Instagram's public embed page (the one websites use to show a post), stepped through
    in a headless browser to collect every image. yt-dlp gives the caption and likes.
  - Profiles: the public profile page shows about the latest 12 posts (pinned first); more needs a login, which this
    tool never does. Private accounts, search pages and hashtag pages need a login too: send post links instead.
  - Anything Instagram refuses: save the post yourself and import it with --file.
Missing numbers stay null (unknown), never 0. Views are usually missing, so --stats ranks Instagram posts by likes
(creator_stats.py expects TikTok view counts and stops on a missing one).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "content-bank" / "_sources"
LOCAL_TZ = ZoneInfo("Asia/Manila")  # same as fetch.py: all posting times are normalized to this timezone
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/151.0.0.0 Safari/537.36")

POST_RE = re.compile(r"instagram\.com/(?:([A-Za-z0-9_.]+)/)?(reels?|p|tv)/([A-Za-z0-9_-]+)")
PROFILE_RE = re.compile(r"instagram\.com/([A-Za-z0-9_.]+)/?(?:reels/|tagged/)?(?:[?#].*)?$")
NOT_PROFILES = {"explore", "accounts", "stories", "direct", "reels", "reel", "p", "tv", "about", "legal"}


def ffmpeg():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import portable
        return str(portable.exe("ffmpeg"))
    except Exception:
        return shutil.which("ffmpeg") or "ffmpeg"


def yt_dlp(*args):
    p = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", *map(str, args)],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {p.stderr.strip()[-500:]}")
    return p.stdout


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.instagram.com/"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    b = pw.chromium.launch()
    page = b.new_context(user_agent=UA, viewport={"width": 1200, "height": 1000}, locale="en-US").new_page()
    return pw, b, page


# ---------- what Instagram returns ----------

def post_meta(code):
    """yt-dlp's data for a post. Carousels come back as a playlist whose image items are empty."""
    # yt-dlp exits with an error on carousels ("No video formats found" for each image) but still prints the post
    p = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", "-J", "--ignore-errors",
                        f"https://www.instagram.com/p/{code}/"], capture_output=True, text=True)
    try:
        meta = json.loads(p.stdout)
    except ValueError:
        meta = None
    if not meta:
        raise RuntimeError(f"no post data (private, removed, or Instagram wants a login): {p.stderr.strip()[-300:]}")
    return meta


def carousel_images(code):
    """Every image of a photo or carousel post, from the public embed page, largest size offered."""
    pw, b, page = browser()
    try:
        page.goto(f"https://www.instagram.com/p/{code}/embed/captioned/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        seen, names = [], set()  # the same image can show at two sizes; its file name stays the same
        for _ in range(25):  # Instagram allows up to 20 items per post
            for src in page.evaluate("""() => [...document.querySelectorAll('img')].filter(i => i.naturalWidth >= 300)
                .map(i => { const c = (i.srcset || '').split(',').map(s => s.trim().split(' '))
                    .filter(x => x[0]).sort((a, b) => parseInt(b[1] || 0) - parseInt(a[1] || 0));
                  return c.length ? c[0][0] : (i.currentSrc || i.src); })"""):
                name = src.split("?")[0].rsplit("/", 1)[-1]
                if name not in names:
                    names.add(name)
                    seen.append(src)
            nxt = page.locator("[aria-label='Next'], .coreSpriteRightChevron")
            if not nxt.count():
                break
            try:
                nxt.first.click(timeout=3000)
            except Exception:
                break
            page.wait_for_timeout(800)
        info = page.evaluate("""() => ({caption: (document.querySelector('.Caption') || {}).innerText || null,
            user: (document.querySelector('.UsernameText') || {}).innerText || null,
            likes: (document.querySelector('.SocialProof') || {}).innerText || null})""")
        return seen, info
    finally:
        b.close()
        pw.stop()


def embed_meta(info):
    """The embed page's caption, account and likes, for photo posts yt-dlp can't read (it only handles video)."""
    cap = info.get("caption") or ""
    user = info.get("user")
    if user and cap.startswith(user):
        cap = cap[len(user):]
    cap = re.sub(r"\s*View all [\d,]+ comments?\s*$", "", cap).strip()
    likes = re.search(r"([\d,]+) likes?", info.get("likes") or "")
    return {"_source": "instagram embed page (yt-dlp has no data for photo-only posts)", "description": cap,
            "channel": user, "like_count": int(likes.group(1).replace(",", "")) if likes else None}


def profile_posts(handle, limit):
    """Shortcodes of the latest posts on the public profile page (pinned first), about 12 at most without a login."""
    pw, b, page = browser()
    try:
        page.goto(f"https://www.instagram.com/{handle}/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(5000)
        codes = []
        for _ in range(4):
            for href in page.evaluate("() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))"):
                m = re.search(r"/(?:reels?|p|tv)/([A-Za-z0-9_-]+)", href or "")
                if m and m.group(1) not in codes:
                    codes.append(m.group(1))
            if len(codes) >= limit:
                break
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)
        info = {"description": page.evaluate(
            "() => (document.querySelector('meta[name=description]') || {}).content || null")}
        return codes[:limit], info
    finally:
        b.close()
        pw.stop()


# ---------- post.json ----------

def hashtags_of(text):
    seen, out = set(), []
    for t in re.findall(r"#([\wÀ-￿]+)", text or ""):
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def normalize(meta, handle, code, kind, files, n_slides=None, size=None):
    views = meta.get("view_count")
    likes, comments = meta.get("like_count"), meta.get("comment_count")
    rate = lambda x: round(x / views, 4) if views and x is not None else None
    ts = meta.get("timestamp")
    published = datetime.fromtimestamp(ts, timezone.utc) if ts else None
    local = published.astimezone(LOCAL_TZ) if published else None
    desc = meta.get("description") or ""
    return {
        "id": code,
        "platform": "instagram",
        "url": f"https://www.instagram.com/{'reel' if kind == 'video' else 'p'}/{code}/",
        "creator": handle,
        "type": kind,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "published": {
            "utc": published.isoformat() if published else None,
            "local": local.isoformat() if local else None,
            "timezone": str(LOCAL_TZ),
            "weekday": local.strftime("%A") if local else None,
            "hour": local.hour if local else None,
        },
        "caption": desc,
        "hashtags": hashtags_of(desc),
        "mentions": list(dict.fromkeys(re.findall(r"@([\w.]+)", desc))),
        # Instagram doesn't show shares or saves to the public, and views only sometimes
        "stats": {"views": views, "likes": likes, "comments": comments, "shares": None, "saves": None},
        "rates": {"engagement": rate((likes or 0) + (comments or 0)) if likes is not None else None,
                  "save": None, "share": None, "comment": rate(comments)},
        "sound": {"title": meta.get("track"), "author": ", ".join(meta.get("artists") or []) or meta.get("artist"),
                  "original": None, "id": None},
        "slide_count": n_slides,
        "duration": meta.get("duration"),
        "size": size or {"width": meta.get("width"), "height": meta.get("height")},
        "labels": {"ad": None, "ai_generated": None, "location": meta.get("location")},
        "files": files,
    }


def probe_video(path):
    probe = str(Path(ffmpeg()).with_name("ffprobe")) if Path(ffmpeg()).exists() else "ffprobe"
    try:
        out = subprocess.run([probe, "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height:format=duration", "-of", "json", str(path)],
                             capture_output=True, text=True).stdout
        d = json.loads(out)
        s = d["streams"][0]
        return {"width": s["width"], "height": s["height"]}, round(float(d["format"]["duration"]), 2)
    except Exception:
        return None, None


def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return {"width": im.width, "height": im.height}
    except Exception:
        return None


def fetch_post(code, handle_hint=None, refresh=False):
    if handle_hint:
        cached = SOURCES / f"ig_{handle_hint}" / code / "post.json"
        if cached.exists() and not refresh:
            return json.loads(cached.read_text()), None, "cached"
    try:
        meta = post_meta(code)
    except RuntimeError as e:
        if "no video in this post" not in str(e).lower():
            raise
        meta = None  # a single photo: everything comes from the embed page below
    urls, info = ([], {}) if meta and meta.get("_type") != "playlist" and meta.get("formats") else carousel_images(code)
    if meta is None:
        meta = embed_meta(info)
    handle = meta.get("channel") or meta.get("uploader_id") or handle_hint or "unknown"
    folder = SOURCES / f"ig_{handle}" / code
    if (folder / "post.json").exists() and not refresh:
        return json.loads((folder / "post.json").read_text()), meta, "cached"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "raw.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    if meta.get("_type") != "playlist" and meta.get("formats"):
        yt_dlp("-q", "-f", "bv*+ba/b", "--merge-output-format", "mp4", "--ffmpeg-location", ffmpeg(),
               "-o", folder / "video.%(ext)s", f"https://www.instagram.com/p/{code}/")
        size, duration = probe_video(folder / "video.mp4")
        meta["duration"] = meta.get("duration") or duration
        post = normalize(meta, handle, code, "video", {"video": "video.mp4"}, size=size)
    else:
        if not urls:
            raise RuntimeError("the embed page showed no images (Instagram may want a login for this post); "
                               "save it yourself and use --file")
        slides = []
        for i, u in enumerate(urls, 1):
            name = f"slides/{i:02}.jpg"
            download(u, folder / name)
            slides.append(name)
        post = normalize(meta, handle, code, "slideshow", {"slides": slides}, len(slides), image_size(folder / slides[0]))
        expected = meta.get("playlist_count")
        if expected and expected != len(slides):
            post["warning"] = (f"Instagram lists {expected} items but {len(slides)} images were saved; a video item "
                               "inside a carousel isn't saved, check the post")
    (folder / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2))
    return post, meta, "downloaded"


def import_files(paths, handle, url=None, caption=""):
    """A post saved by hand: one video, or images in slide order."""
    paths = [Path(p) for p in paths]
    for p in paths:
        if not p.exists():
            sys.exit(f"No such file: {p}")
    m = POST_RE.search(url or "")
    code = m.group(3) if m else "manual-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = SOURCES / f"ig_{handle}" / code
    folder.mkdir(parents=True, exist_ok=True)
    meta = {"description": caption, "_source": "imported by hand with --file", "url": url}
    if len(paths) == 1 and paths[0].suffix.lower() in (".mp4", ".mov", ".m4v", ".webm"):
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", str(paths[0]), "-c:v", "copy", "-c:a", "aac",
                        str(folder / "video.mp4")], check=True)
        size, duration = probe_video(folder / "video.mp4")
        meta["duration"] = duration
        post = normalize(meta, handle, code, "video", {"video": "video.mp4"}, size=size)
    else:
        from PIL import Image
        slides = []
        (folder / "slides").mkdir(exist_ok=True)
        for i, p in enumerate(paths, 1):
            name = f"slides/{i:02}.jpg"
            Image.open(p).convert("RGB").save(folder / name, quality=95)
            slides.append(name)
        post = normalize(meta, handle, code, "slideshow", {"slides": slides}, len(slides), image_size(folder / slides[0]))
    if url:
        post["url"] = url
    (folder / "raw.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    (folder / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2))
    print(f"Imported {post['type']} → {folder}")


def creator_profile(handle, page_info, metas):
    desc = page_info.get("description") or ""
    m = re.match(r"([\d.,]+[KM]?) Followers, ([\d.,]+[KM]?) Following, ([\d.,]+[KM]?) Posts", desc)
    name = next((x.get("uploader") for x in metas if x and x.get("uploader")), None)
    return {"platform": "instagram", "handle": handle, "name": name,
            "followers": m.group(1) if m else None, "following": m.group(2) if m else None,
            "posts": m.group(3) if m else None, "page_description": desc or None,
            "bio_link": None,  # not in the logged-out page data: read the profile page with browse.py if needed
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def account_stats(folder):
    """creator_stats.py's numbers for an Instagram account: cadence, likes ranking, hashtags → stats.json."""
    import statistics as st
    from collections import Counter
    folder = Path(folder)
    posts = [json.loads(f.read_text()) for f in sorted(folder.glob("*/post.json"))]
    if not posts:
        sys.exit("No posts found")
    timed = sorted((p for p in posts if p["published"]["local"]), key=lambda p: p["published"]["utc"])
    times = [datetime.fromisoformat(p["published"]["local"]) for p in timed]
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:])]
    span_days = max((times[-1] - times[0]).total_seconds() / 86400, 1) if times else None
    likes = lambda p: p["stats"]["likes"] or 0
    ranked = sorted(posts, key=likes, reverse=True)
    brief = lambda p: {"id": p["id"], "type": p["type"], "likes": p["stats"]["likes"],
                       "comments": p["stats"]["comments"], "caption": p["caption"][:80]}
    stats = {
        "platform": "instagram", "posts": len(posts), "types": dict(Counter(p["type"] for p in posts)),
        "first": times[0].isoformat() if times else None, "last": times[-1].isoformat() if times else None,
        "posts_per_week": round(len(timed) / span_days * 7, 1) if span_days else None,
        "median_gap_hours": round(st.median(gaps), 1) if gaps else None,
        "weekdays": dict(Counter(t.strftime("%A") for t in times).most_common()),
        "hours_local": dict(sorted(Counter(t.hour for t in times).items())),
        "timezone": str(LOCAL_TZ),
        "median_likes": st.median(likes(p) for p in posts),
        "ranked_by": "likes (Instagram hides views, shares and saves from logged-out visitors)",
        "top_5": [brief(p) for p in ranked[:5]], "bottom_5": [brief(p) for p in ranked[-5:][::-1]],
        "hashtags": dict(Counter(h.lower() for p in posts for h in p["hashtags"]).most_common(15)),
    }
    (folder / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"{len(posts)} posts · {stats['posts_per_week']}/week · median likes {stats['median_likes']:,} → {folder / 'stats.json'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("link", nargs="?")
    ap.add_argument("--limit", type=int, default=12, help="profile links: latest N posts (about 12 at most)")
    ap.add_argument("--refresh", action="store_true", help="download again even if already saved")
    ap.add_argument("--file", nargs="+", help="import a post you saved yourself: one video, or images in order")
    ap.add_argument("--handle", help="--file: the account the post is from")
    ap.add_argument("--url", help="--file: the post's link, if you have it")
    ap.add_argument("--caption", default="", help="--file: the post's caption, if you have it")
    ap.add_argument("--stats", metavar="FOLDER", help="cadence and likes ranking for a downloaded account")
    a = ap.parse_args()

    if a.stats:
        return account_stats(a.stats)
    if a.file:
        if not a.handle:
            sys.exit("--file needs --handle <account>")
        return import_files(a.file, a.handle.lstrip("@"), a.url, a.caption)
    if not a.link:
        ap.error("give a link, or --file")

    link = a.link.strip()
    if re.search(r"instagram\.com/(accounts|explore)/", link):
        sys.exit("That's a login, search or explore page, which Instagram only shows to logged-in accounts. "
                 "Send the links of the posts or the account instead.")
    page_info, is_profile, handle = {}, False, None
    if m := POST_RE.search(link):
        handle, targets = m.group(1), [m.group(3)]
    elif (m := PROFILE_RE.search(link)) and m.group(1).lower() not in NOT_PROFILES:
        handle, is_profile = m.group(1), True
        targets, page_info = profile_posts(handle, a.limit)
        if not targets:
            sys.exit(f"No posts visible on @{handle}'s public page (private account, wrong name, or a login wall).")
    else:
        sys.exit(f"Not an Instagram post, reel or profile link: {link}")

    print(f"{'@' + handle if handle else 'Instagram'}: {len(targets)} post(s) to fetch")
    results, metas = [], []
    for i, code in enumerate(targets, 1):
        try:
            post, meta, status = fetch_post(code, handle, a.refresh)
        except Exception as e:  # keep going; one broken post shouldn't stop a profile run
            print(f"  [{i}/{len(targets)}] {code}  FAILED: {e}")
            results.append({"id": code, "status": "failed", "error": str(e)[:300]})
            continue
        metas.append(meta)
        handle = handle or post["creator"]
        count = post["slide_count"] and f"{post['slide_count']} slides" or f"{round(post['duration'] or 0)}s video"
        likes = post["stats"]["likes"]
        print(f"  [{i}/{len(targets)}] {code}  {post['type']:9} {count:>11}  "
              f"{likes if likes is not None else '?':>9} likes  {status}"
              + (f"  ({post['warning']})" if post.get("warning") else ""))
        results.append({"id": code, "status": status, "type": post["type"]})

    folder = SOURCES / f"ig_{handle}"
    if is_profile and handle and folder.exists():
        (folder / "creator.json").write_text(json.dumps(creator_profile(handle, page_info, metas), ensure_ascii=False, indent=2))
        (folder / "last_run.json").write_text(json.dumps(
            {"link": link, "limit": a.limit, "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "posts": results}, indent=2))
    failed = sum(r["status"] == "failed" for r in results)
    print(f"Done: {len(results) - failed} ok, {failed} failed" + (f" → {folder}" if handle else ""))


if __name__ == "__main__":
    main()
