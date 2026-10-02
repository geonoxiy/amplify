#!/usr/bin/env python3
"""Originality check for a run (Project Deliverables section 12): our output must follow the format without being a copy.

Usage:
  originality.py <run folder> [--source-blue "#0270f9"]

Reads <run>/output/records/slide*.json (the text we drew) and <run>/output/slide*.png, and compares them with every source post of the pillar
(<pillar>/originals/<post id>/: post.json, analysis/fingerprint.json, slide images). Writes <run>/output/originality.json.

Text (numbers from code):
  raw overlap      share of our slide's distinct words that appear in ONE source post (rule: under 30%)
  content overlap  the same without common function words (a fairer read: "the", "your", "and" are shared by any English text)
  longest run      the longest stretch of consecutive words shared with any single source line (a copied line shows up here)
  hook overlap     the hook against every source hook
Images:
  phash distance   perceptual-hash distance (0 to 64 bits) between each of our slides and each source slide; 10 or less is a near-duplicate
  source blue      share of pixels close to the source mascot's colour, in our slides and in the sources (evidence the character changed)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import imagehash
import numpy as np
from PIL import Image

STOP = set("""a an the and or but of to in on at for with from by as is are was were be been it its this that these those you your yours i me my we our they their them he she
his her not no do does did don't doesn't can will just so if then than too very also up out into over about how what when where which who why more most some any all each""".split())


def tokens(s):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", s.lower().replace("’", "'"))


FORMAT_LINE = re.compile(r"^\s*\d+(?:-\d+)?\s*sets?\s*x\s", re.I)  # the pillar's own sets x reps formula (P005 section 10): a format element, not content
QUOTE = re.compile(r"(?<!\w)'(.+?)'(?!\w)")  # slide text quoted inside a fingerprint field; an apostrophe inside a word does not close the quote


def lcs_run(a, b):
    """Longest common contiguous run of tokens: (length, the tokens)."""
    best, end, prev = 0, 0, [0] * (len(b) + 1)
    for i, x in enumerate(a, 1):
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, end = cur[j], i
        prev = cur
    return best, a[end - best:end]


def source_texts(post_dir):
    """The actual text of a source post: its caption, on-slide text blocks, and anything quoted in its fingerprint fields (slide text and hooks).
    Descriptive prose (poses, colours, muscle names in a summary) is left out on purpose: it would read as overlap without being copied."""
    strings, hooks = [], []
    pj = post_dir / "post.json"
    if pj.exists():
        strings.append(json.loads(pj.read_text()).get("caption", ""))
    fp = post_dir / "analysis" / "fingerprint.json"
    if fp.exists():
        d = json.loads(fp.read_text())
        hooks += QUOTE.findall(d.get("fingerprint", {}).get("hook", "") or "")
        for u in d.get("units", []):
            if isinstance(u.get("text"), str):  # older fingerprints keep the exact slide text here
                strings.append(u["text"])
            if isinstance(u.get("summary"), str):
                strings += QUOTE.findall(u["summary"])
                if u.get("n") == 1:
                    hooks += QUOTE.findall(u["summary"])
            for tb in u.get("text_blocks") or []:
                strings.append(tb.get("text", ""))
                if u.get("n") == 1 and tb.get("role") in ("hook", "headline"):
                    hooks.append(tb.get("text", ""))
    return [s for s in strings if s], [h for h in hooks if h]


def source_images(post_dir):
    pj = post_dir / "post.json"
    if not pj.exists():
        return []
    post = json.loads(pj.read_text())
    files = [post_dir / f for f in (post.get("files", {}).get("slides") or [])]
    files = [f for f in files if f.exists()] or sorted((post_dir / "analysis" / "slides").glob("*.jpg"))
    return files


def blue_share(path, rgb):
    im = np.asarray(Image.open(path).convert("RGB").resize((256, 256))).astype(int)
    return float((np.abs(im - np.array(rgb)).sum(axis=2) < 90).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", type=Path)
    ap.add_argument("--source-blue", default="#0270f9")
    args = ap.parse_args()
    run = args.run
    pillar = run.parent.parent
    sources = sorted(p for p in (pillar / "originals").iterdir() if p.is_dir())
    if not sources:
        sys.exit(f"No originals in {pillar / 'originals'}")
    blue = tuple(int(args.source_blue.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))

    src = {p.name: source_texts(p) for p in sources}
    src_words = {n: set(tokens(" ".join(t))) for n, (t, _) in src.items()}
    records = sorted((run / "output" / "records").glob("slide*.json"), key=lambda p: int(re.findall(r"\d+", p.stem)[0]))
    result = {"slides": [], "hook": {}, "images": {}, "verdict": {}}

    for rp in records:
        rec = json.loads(rp.read_text())
        blocks = [b["text"] for b in rec["text_blocks"] if b.get("origin") != "mark" and not FORMAT_LINE.match(b["text"])]
        words = set(tokens(" ".join(blocks)))
        content = {w for w in words if w not in STOP and not w.isdigit()}
        raw = {n: len(words & sw) / max(len(words), 1) for n, sw in src_words.items()}
        cont = {n: len(content & sw) / max(len(content), 1) for n, sw in src_words.items()}
        run_len, run_words, run_src = 0, [], ""
        for b in blocks:
            tb = tokens(b)
            for n, (texts, _) in src.items():
                for t in texts:
                    k, shared_run = lcs_run(tb, tokens(t))
                    if k > run_len:
                        run_len, run_words, run_src = k, shared_run, f"{n}: {t[:60]}"
        worst = max(raw, key=raw.get)
        result["slides"].append({"slide": rec["n"], "words": len(words), "raw_overlap_max": round(raw[worst], 2), "raw_overlap_post": worst,
                                 "shared_words_with_that_post": sorted(words & src_words[worst]),
                                 "content_overlap_max": round(max(cont.values()), 2), "longest_shared_run_words": run_len,
                                 "longest_shared_run": " ".join(run_words), "longest_run_source": run_src,
                                 "status": "pass" if raw[worst] < 0.30 and run_len <= 3 else "review" if max(cont.values()) < 0.30 and run_len <= 3 else "FAIL"})

    # hook (slide 1) against every source hook
    if records:
        first = json.loads(records[0].read_text())
        hook_words = set(tokens(" ".join(b["text"] for b in first["text_blocks"] if b.get("origin") != "mark" and b.get("role") in ("hook", "headline", None))))
        per = {}
        for n, (_, hooks) in src.items():
            hw = set(tokens(" ".join(hooks)))
            per[n] = round(len(hook_words & hw) / max(len(hook_words), 1), 2)
        result["hook"] = {"words": sorted(hook_words), "overlap_by_source": per, "max": max(per.values()), "status": "pass" if max(per.values()) < 0.30 else "FAIL"}

    # images: perceptual hashes against every source slide
    ours = sorted((run / "output").glob("slide*.png"), key=lambda p: int(re.findall(r"\d+", p.stem)[0]))
    ours_h = {p.name: (imagehash.phash(Image.open(p)), imagehash.dhash(Image.open(p))) for p in ours}
    best = (99, "", "")
    src_share = []
    for s in sources:
        for f in source_images(s):
            ph, dh = imagehash.phash(Image.open(f)), imagehash.dhash(Image.open(f))
            src_share.append(blue_share(f, blue))
            for name, (oh, od) in ours_h.items():
                d = int(min(oh - ph, od - dh))
                if d < best[0]:
                    best = (d, name, f"{s.name}/{f.name}")
    result["images"] = {"min_hash_distance": best[0], "closest_pair": f"{best[1]} ~ {best[2]}", "near_duplicate_threshold": 10,
                        "status": ("not checked (no source images stored)" if not src_share
                                   else "pass" if best[0] > 10 else "FAIL"),
                        "source_blue_share_in_sources_mean": round(float(np.mean(src_share)), 3) if src_share else None,
                        "source_blue_share_in_ours_mean": round(float(np.mean([blue_share(p, blue) for p in ours])), 4) if ours else None}
    statuses = [s["status"] for s in result["slides"]] + [result["hook"].get("status", "pass"), result["images"]["status"]]
    result["verdict"] = ("FAIL" if "FAIL" in statuses else "review" if "review" in statuses
                         else "incomplete" if any(x.startswith("not checked") for x in statuses) else "pass")
    (run / "output" / "originality.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"originality vs {len(sources)} source posts: {result['verdict'].upper()}")
    for s in result["slides"]:
        shared = ", ".join(s["shared_words_with_that_post"][:8]) or "none"
        print(f"  slide {s['slide']}: raw overlap {s['raw_overlap_max']:.0%} (max, post …{s['raw_overlap_post'][-6:]}; shared: {shared}) · content words {s['content_overlap_max']:.0%} · longest shared run {s['longest_shared_run_words']} words"
              f"{' (“' + s['longest_shared_run'] + '”)' if s['longest_shared_run_words'] else ''} · {s['status']}")
    if result["hook"]:
        print(f"  hook {result['hook']['words']}: max overlap {result['hook']['max']:.0%} · {result['hook']['status']}")
    im = result["images"]
    if im["status"].startswith("not checked"):
        print(f"  images: {im['status']}")
    else:
        print(f"  images: closest to a source slide = {im['min_hash_distance']} bits ({im['closest_pair']}), near-duplicate at {im['near_duplicate_threshold']} or less · {im['status']}")
    if im["source_blue_share_in_sources_mean"] is not None:
        print(f"  source-mascot blue: {im['source_blue_share_in_sources_mean']:.1%} of pixels in the source slides vs {im['source_blue_share_in_ours_mean']:.2%} in ours")


if __name__ == "__main__":
    main()
