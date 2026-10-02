#!/usr/bin/env python3
"""Rank discovered Reddit threads or Letterboxd films into a numbered shortlist for the owner's approval.

Usage:
  shortlist.py rank <items.json> --site reddit|letterboxd [--top 10] [--max-per-sub 2] [--out captures/_shortlists/<date>_<site>.md]

The browser half (Claude in Chrome, see the capture command in the skill) gathers the items into a JSON list; this tool applies
the same eligibility rules and ranking every time and writes the shortlist. Nothing is captured until the owner approves numbers.

Reddit items:     {"title", "subreddit", "score", "num_comments", "upvote_ratio", "created_utc", "permalink", "over_18", "stickied", "locked"}
Letterboxd items: {"title", "year", "slug", "list_rank" (position on the popular list, 1 = top), "rated_reviews" (reviews with a star rating on the page),
                   "top_review_likes" (likes on the top reviews, a list of numbers)}

Reddit rules:     skip NSFW, stickied and removed posts; need at least 30 comments (8 usable replies) and a title of at least 15 characters;
                  rank by score per hour (age counted as at least 2 h), ties by comments; at most --max-per-sub per subreddit.
Letterboxd rules: need at least 8 reviews with a star rating and at least 1 like among the top reviews; rank by list position, ties by total likes.
The 3-word folder name (Reddit) and the hook idea are judgment calls: the columns are left for the agent to fill in before showing the list.
"""
import argparse
import json
import sys
import time
from pathlib import Path


def reddit(items, top, max_per_sub, now):
    rows, skipped = [], []
    for it in items:
        why = None
        if it.get("over_18"):
            why = "NSFW"
        elif it.get("stickied"):
            why = "stickied"
        elif (it.get("title") or "").strip() in ("", "[removed]", "[deleted]") or len((it.get("title") or "").strip()) < 15:
            why = "title too short or removed"
        elif (it.get("num_comments") or 0) < 30:
            why = f"only {it.get('num_comments') or 0} comments (need 30)"
        if why:
            skipped.append((it.get("title", "")[:60], why))
            continue
        age_h = max((now - float(it["created_utc"])) / 3600, 2.0)
        rows.append({**it, "age_h": round(age_h, 1), "velocity": round((it.get("score") or 0) / age_h, 1)})
    rows.sort(key=lambda r: (-r["velocity"], -(r.get("num_comments") or 0)))
    out, per = [], {}
    for r in rows:
        sub = (r.get("subreddit") or "").lower()
        if per.get(sub, 0) >= max_per_sub:
            skipped.append((r["title"][:60], f"already {max_per_sub} from r/{r.get('subreddit')}"))
            continue
        per[sub] = per.get(sub, 0) + 1
        out.append(r)
    return out[:top], skipped


def letterboxd(items, top):
    rows, skipped = [], []
    for it in items:
        likes = sum(it.get("top_review_likes") or [])
        if (it.get("rated_reviews") or 0) < 8:
            skipped.append((it.get("title", ""), f"only {it.get('rated_reviews') or 0} rated reviews (need 8)"))
        elif likes < 1:
            skipped.append((it.get("title", ""), "no likes on the top reviews"))
        else:
            rows.append({**it, "likes": likes})
    rows.sort(key=lambda r: (r.get("list_rank") or 10**6, -r["likes"]))
    return rows[:top], skipped


def write(site, rows, skipped, path):
    lines = [f"# {site.title()} shortlist for approval", "",
             "Reply with the numbers to make into content. Nothing is captured before you approve.", ""]
    if site == "reddit":
        lines += ["| # | Thread | Subreddit | Score | Comments | Age | Score/h | 3-word folder name | Hook idea |", "|---|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(rows, 1):
            lines.append(f"| {i} | [{r['title'][:80]}](https://www.reddit.com{r.get('permalink', '')}) | r/{r.get('subreddit')} | {r.get('score')} | "
                         f"{r.get('num_comments')} | {r['age_h']} h | {r['velocity']} | {r.get('folder_name', '')} | {r.get('hook', '')} |")
    else:
        lines += ["| # | Film | Year | Popular-list rank | Rated reviews | Likes on top reviews | Hook idea |", "|---|---|---|---|---|---|---|"]
        for i, r in enumerate(rows, 1):
            slug = r.get("slug", "")
            lines.append(f"| {i} | [{r['title']}](https://letterboxd.com/film/{slug}/) | {r.get('year', '')} | {r.get('list_rank', '')} | "
                         f"{r.get('rated_reviews')} | {r['likes']} | {r.get('hook', '')} |")
    if skipped:
        lines += ["", "Skipped:", *[f"- {t}: {w}" for t, w in skipped[:20]]]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["rank"])
    ap.add_argument("items")
    ap.add_argument("--site", choices=["reddit", "letterboxd"], required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--max-per-sub", type=int, default=2)
    ap.add_argument("--now", type=float, default=None, help="epoch seconds, for tests")
    ap.add_argument("--out")
    a = ap.parse_args()
    items = json.loads(Path(a.items).read_text())
    now = a.now or time.time()
    rows, skipped = reddit(items, a.top, a.max_per_sub, now) if a.site == "reddit" else letterboxd(items, a.top)
    out = a.out or f"captures/_shortlists/{time.strftime('%Y-%m-%d', time.localtime(now))}_{a.site}.md"
    write(a.site, rows, skipped, out)
    print(f"{len(rows)} shortlisted, {len(skipped)} skipped → {out}")
    if not rows:
        sys.exit(1)


if __name__ == "__main__":
    main()
