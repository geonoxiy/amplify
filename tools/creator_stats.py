#!/usr/bin/env python3
"""Posting cadence and performance numbers for one creator's downloaded posts.

Usage:
  creator_stats.py content-bank/_sources/<creator>

Writes content-bank/_sources/<creator>/stats.json and prints a short summary.
Only posts from the creator's last fetch are counted (last_run.json), or all posts if there is none.
"""
import json
import statistics as st
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


MIN_VIEWS = 5000


def brand_palette(folder, ids, k=6):
    """Account-wide palette: the per-slide and per-shot palettes (measures.json) merged and clustered, weighted by pixel share.
    Cluster centres are averages, so treat them as the account's dominant colours, not exact brand hex codes."""
    import numpy as np
    entries = []
    for f in folder.glob("*/analysis/measures.json"):
        if f.parent.parent.name not in ids:
            continue
        m = json.loads(f.read_text())
        groups = list((m.get("palettes") or {}).values()) + [s["palette"] for s in m.get("shots", []) if s.get("palette")]
        entries += [(c["hex"], c["share"]) for g in groups for c in g]
    if len(entries) < k:
        return []
    rgb = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h, _ in entries], float)
    w = np.array([s for _, s in entries], float)
    centres = rgb[np.argsort(-w)[:k]].copy()
    for _ in range(25):
        labels = np.argmin(((rgb[:, None] - centres[None]) ** 2).sum(-1), axis=1)
        centres = np.array([np.average(rgb[labels == i], axis=0, weights=w[labels == i]) if (labels == i).any() else centres[i]
                            for i in range(k)])
    share = np.array([w[labels == i].sum() for i in range(k)]) / w.sum()
    return [{"hex": "#%02x%02x%02x" % tuple(int(c) for c in centres[i]), "share": round(float(share[i]), 3)}
            for i in np.argsort(-share)]


def main():
    folder = Path(sys.argv[1])
    ids = None
    if (folder / "last_run.json").exists():
        ids = {p["id"] for p in json.loads((folder / "last_run.json").read_text())["posts"] if p["status"] != "failed"}
    posts = [json.loads(p.read_text()) for p in sorted(folder.glob("*/post.json"))]
    posts = [p for p in posts if ids is None or p["id"] in ids]
    if not posts:
        sys.exit("No posts found")
    posts.sort(key=lambda p: p["published"]["utc"])
    times = [datetime.fromisoformat(p["published"]["local"]) for p in posts]
    span_days = max((times[-1] - times[0]).total_seconds() / 86400, 1)
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:])]
    by_day = Counter(t.date().isoformat() for t in times)
    # A tiny post can top a rate ranking on a handful of likes, so rate rankings only use posts with enough views.
    eligible = [p for p in posts if p["stats"]["views"] >= MIN_VIEWS] or posts
    ranked = sorted(eligible, key=lambda p: p["rates"]["engagement"] or 0, reverse=True)
    by_views = sorted(posts, key=lambda p: p["stats"]["views"], reverse=True)
    brief = lambda p: {"id": p["id"], "type": p["type"], "views": p["stats"]["views"],
                       "engagement": p["rates"]["engagement"], "save": p["rates"]["save"],
                       "caption": p["caption"][:80]}
    mean = lambda k: round(st.mean(p["rates"][k] or 0 for p in posts), 4)
    stats = {
        "posts": len(posts),
        "types": dict(Counter(p["type"] for p in posts)),
        "first": times[0].isoformat(), "last": times[-1].isoformat(),
        "posts_per_week": round(len(posts) / span_days * 7, 1),
        "max_posts_in_a_day": max(by_day.values()),
        "median_gap_hours": round(st.median(gaps), 1) if gaps else None,
        "weekdays": dict(Counter(t.strftime("%A") for t in times).most_common()),
        "hours_local": dict(sorted(Counter(t.hour for t in times).items())),
        "timezone": posts[0]["published"]["timezone"],
        "median_views": st.median(p["stats"]["views"] for p in posts),
        "average_rates": {k: mean(k) for k in ("engagement", "save", "share", "comment")},
        "ranked_by": f"engagement rate among posts with at least {MIN_VIEWS:,} views ({len(eligible)} of {len(posts)} posts)",
        "top_5": [brief(p) for p in ranked[:5]],
        "bottom_5": [brief(p) for p in ranked[-5:][::-1]],
        "top_5_by_views": [brief(p) for p in by_views[:5]],
        "bottom_5_by_views": [brief(p) for p in by_views[-5:][::-1]],
        "brand_palette": brand_palette(folder, {p["id"] for p in posts}),
        "hashtags": dict(Counter(h.lower() for p in posts for h in p["hashtags"]).most_common(15)),
        "sounds": dict(Counter(f"{p['sound']['title']} – {p['sound']['author']}" for p in posts).most_common(5)),
    }
    (folder / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"{len(posts)} posts · {stats['posts_per_week']}/week · median gap {stats['median_gap_hours']}h · "
          f"median views {stats['median_views']:,} · avg engagement {stats['average_rates']['engagement']:.2%}")
    print("Top weekdays:", ", ".join(list(stats["weekdays"])[:3]), "· hours:", stats["hours_local"])


if __name__ == "__main__":
    main()
