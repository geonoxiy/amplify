#!/usr/bin/env python3
"""Build and check a caption for one of the three caption styles.

Usage:
  caption.py check <run folder> [--in caption_soft.json] [--brand brands/<id>.md] [--max 2200]

Reads <run>/caption.json (or <run>/<--in>, for a second caption variant on the same run — e.g. `--in caption_soft.json`
alongside the run's default `caption.json`) and writes the matching `<stem>.txt` and `<stem>_check.json` next to it.

caption.json:
  {"style": "none" | "soft" | "hard",
   "brand": "brands/<id>.md",            # required for soft and hard; optional for none (used to scan for leaks)
   "trend": "…",                         # soft, part 1: the callback to the source post/trend, no brand words
   "source_credit": "…",                 # soft, optional part 2: e.g. "Source: r/AskReddit 🔗" (screenshot-sourced pillars)
   "bridge": "…",                        # soft, part 3: connects the trend to the brand (names the brand)
   "body": "…",                          # hard and none (none may be empty, for pillars whose source has no caption)
   "collateral": "…",                    # hard: where the product shows on the image or video; none: leave empty
   "hashtags": ["…"]}                    # without the #

Styles (Project Deliverables §4.1):
  none  no brand mention anywhere, no disclosure.
  soft  trend callback → optional source credit → bridge that names the brand → disclosure.
  hard  a body that names the brand and the product (the product is also on the collateral) → disclosure.

Disclosure position: "this is an advertisement." is appended LAST by default (after the hashtags), matching how the
owner's soft-sell technique reads on screen — the content plays first, the ad line is the formality at the end. Set
disclosure_position: start in the brand profile for a run that needs it up front instead (e.g. to show before TikTok's
"…more" cutoff). Whichever position is chosen, the line must appear exactly once, at that position.

Style rule (owner, 2026-09-29), applies to every overlay/caption text this tool builds: lowercase throughout, and
never an em dash, en dash, semicolon or colon. Checked in code: banned punctuation is a hard FAIL; a capitalised word
is a warning, not a fail (a real brand or product name — read from the brand profile's brand_terms/product — is
exempted automatically; anything else capitalised is a style slip to fix by hand, most often a needlessly
capitalised sentence start).

Exit code 1 if any check fails. The character limit defaults to 2200 (a conservative figure; confirm TikTok's current limit).
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
AD_WORDS = ["advertisement", "#ad", "sponsored", "paid partnership"]
BANNED_PUNCT = {"—": "em dash", "–": "en dash", ";": "semicolon", ":": "colon"}


def load_brand(path):
    text = Path(path).read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def has(text, term):
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, re.I) is not None


def found(text, terms):
    return [t for t in dict.fromkeys(t.lstrip('#') for t in terms) if has(text, t)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check"])
    ap.add_argument("run")
    ap.add_argument("--in", dest="infile", default="caption.json", help="filename inside the run folder (default caption.json)")
    ap.add_argument("--brand")
    ap.add_argument("--max", type=int, default=2200)
    args = ap.parse_args()

    run = Path(args.run)
    infile = run / args.infile
    stem = infile.stem  # e.g. caption_soft.json -> caption_soft.txt, caption_soft_check.json
    cap = json.loads(infile.read_text())
    style = cap.get("style")
    fails, warns = [], []
    if style not in ("none", "soft", "hard"):
        sys.exit(f"style must be none, soft or hard (got {style!r})")

    brand_path = args.brand or cap.get("brand")
    brand = load_brand(ROOT / brand_path) if brand_path else {}
    if style != "none" and not brand:
        sys.exit(f"{style} needs a brand profile (caption.json 'brand' or --brand)")
    terms = list(dict.fromkeys(brand.get("brand_terms") or []))
    tags_brand = [h.lstrip("#") for h in brand.get("brand_hashtags") or []]
    disclosure = brand.get("disclosure") or "This is an advertisement."
    disclosure_at = brand.get("disclosure_position") or "end"
    if disclosure_at not in ("start", "end"):
        sys.exit(f"brand profile disclosure_position must be start or end (got {disclosure_at!r})")
    hashtags = [h.lstrip("#") for h in cap.get("hashtags") or []]
    tag_line = " ".join(f"#{h}" for h in hashtags)

    if style == "soft":
        trend = (cap.get("trend") or "").strip()
        credit = (cap.get("source_credit") or "").strip()
        bridge = (cap.get("bridge") or "").strip()
        if not trend or not bridge:
            fails.append("soft needs both a 'trend' part and a 'bridge' part")
        body_parts = [trend, credit, bridge]
        if found(trend, terms + tags_brand):
            fails.append(f"trend part mentions the brand: {found(trend, terms + tags_brand)}")
        if credit and found(credit, terms + tags_brand):
            fails.append(f"source_credit mentions the brand: {found(credit, terms + tags_brand)}")
        if bridge and not found(bridge, terms):
            fails.append("bridge part never names the brand")
        if len(re.findall(r"[.!?](?:\s|$)", bridge)) > 2:
            warns.append("bridge is longer than 2 sentences; soft sell reads better short")
    else:
        body = (cap.get("body") or "").strip()
        if not body and style == "hard":
            fails.append("hard needs a 'body'")
        if not body and style == "none" and not hashtags:
            warns.append("empty caption (no text, no hashtags): matches a pillar whose source has none")
        body_parts = [body]
        if style == "hard":
            if terms and not has(body, terms[0]):
                fails.append(f"body never names the brand ({terms[0]})")
            product = brand.get("product")
            if product and not has(body, product):
                fails.append(f"body never names the product ({product})")
            if brand.get("cta") and not has(body, brand["cta"]):
                warns.append(f"no call to action ({brand['cta']!r}) in the body")
            if not (cap.get("collateral") or "").strip():
                fails.append("hard sell needs 'collateral': where the product shows on the image or video")
        else:
            if (cap.get("collateral") or "").strip():
                fails.append("style none: the collateral must not carry the product")

    body_parts = [p for p in body_parts if p]
    tail = [tag_line] if tag_line else []
    if style == "none":
        parts = body_parts + tail
    elif disclosure_at == "start":
        parts = [disclosure] + body_parts + tail
    else:
        parts = body_parts + tail + [disclosure]
    text = "\n\n".join(parts)

    if style == "none":
        leaked = found(text, terms + tags_brand)
        if leaked:
            fails.append(f"brand mention in a none caption: {leaked}")
        ad = found(text, AD_WORDS)
        if ad:
            fails.append(f"disclosure wording in a none caption: {ad}")
    else:
        if text.lower().count(disclosure.lower()) != 1:
            fails.append(f"the disclosure must appear exactly once (found {text.lower().count(disclosure.lower())})")
        elif disclosure_at == "start" and not text.startswith(disclosure):
            fails.append("disclosure_position is start, but the caption does not start with the disclosure")
        elif disclosure_at == "end" and not text.rstrip().endswith(disclosure):
            fails.append("disclosure_position is end, but the caption does not end with the disclosure")
    bad = found(text, brand.get("never_say") or [])
    if bad:
        fails.append(f"never_say words present: {bad}")
    if len(text) > args.max:
        fails.append(f"caption is {len(text)} characters, over {args.max}")
    punct_hit = sorted({name for ch, name in BANNED_PUNCT.items() if ch in text})
    if punct_hit:
        fails.append(f"banned punctuation present: {', '.join(punct_hit)} (never use these in overlay/caption text)")
    # style rule: lowercase throughout, except an all-caps acronym (2-5 letters, e.g. AI, SEO) or a brand/product name
    # that is itself capitalised (checked against the brand profile so a real name like PagePilot isn't flagged).
    allowed_caps = set()
    for t in (brand.get("brand_terms") or []) + ([brand.get("product")] if brand.get("product") else []):
        allowed_caps.update(re.findall(r"[A-Za-z]+", t or ""))
    stripped = text
    for name in allowed_caps:
        stripped = re.sub(rf"(?<!\w){re.escape(name)}(?!\w)", "", stripped, flags=re.I)
    capitalised_words = re.findall(r"\b[A-Z][a-zA-Z]*\b", stripped)
    not_acronym = [w for w in capitalised_words if not (w.isupper() and 2 <= len(w) <= 5) and w not in ("I",)]
    if not_acronym:
        warns.append(f"style rule is lowercase for overlay/caption text; found capitalised word(s): {sorted(set(not_acronym))[:8]}")

    result = {"style": style, "brand": brand_path, "disclosure_position": disclosure_at if style != "none" else None,
              "characters": len(text), "hashtags": len(hashtags), "first_100_characters": text[:100],
              "fails": fails, "warnings": warns, "verdict": "FAIL" if fails else "pass"}
    (run / f"{stem}.txt").write_text(text + "\n")
    (run / f"{stem}_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"caption ({style}): {result['verdict'].upper()} · {len(text)} characters · {len(hashtags)} hashtags")
    print(f"  shows before 'more' (about 100 characters): {text[:100]!r}")
    for f in fails:
        print(f"  FAIL: {f}")
    for w in warns:
        print(f"  warn: {w}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
