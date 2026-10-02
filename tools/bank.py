#!/usr/bin/env python3
"""Manage the content bank: pillar folders, originals, runs and the index.

Usage:
  bank.py new "<name>" --type slideshow|video   create P###-slug/ with pillar.md, originals/, runs/, learnings.md
  bank.py add <P###> <post folder> [...]        copy downloaded posts into the pillar's originals/
  bank.py run <P###> "<topic>"                  create the next runs/run-NN_<date>_<topic>/ folder
  bank.py index                                 rebuild content-bank/index.md from every pillar.md
  bank.py list                                  print the index
  bank.py show <P### or name>                   print a pillar
"""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "content-bank"
TEMPLATE = ROOT / "templates" / "pillar.md"


def slug(text, n=40):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n].strip("-")


def pillar_dirs():
    return sorted(p for p in BANK.glob("P[0-9][0-9][0-9]-*") if (p / "pillar.md").exists())


def find(key):
    key_l = key.lower()
    for p in pillar_dirs():
        if p.name.lower().startswith(key_l + "-") or p.name.lower() == key_l:
            return p
    matches = [p for p in pillar_dirs() if key_l in p.name.lower()
               or key_l in (read(p)[0].get("name") or "").lower()]
    if len(matches) == 1:
        return matches[0]
    sys.exit(f"No single pillar matches '{key}'" + (f": {[m.name for m in matches]}" if matches else ""))


def read(folder):
    text = (folder / "pillar.md").read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}, text[m.end():]) if m else ({}, text)


def write(folder, meta, body):
    head = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000).strip()
    (folder / "pillar.md").write_text(f"---\n{head}\n---\n{body}")


def confidence(n):
    return "High" if n >= 3 else "Medium" if n == 2 else "Low"


def cmd_new(args):
    ids = [int(p.name[1:4]) for p in pillar_dirs()]
    pid = f"P{(max(ids) + 1) if ids else 1:03}"
    folder = BANK / f"{pid}-{slug(args.name)}"
    for sub in ("originals", "runs"):
        (folder / sub).mkdir(parents=True, exist_ok=True)
    text = TEMPLATE.read_text().replace("P000", pid).replace("Short format name", args.name)
    (folder / "pillar.md").write_text(text)
    meta, body = read(folder)
    today = date.today().isoformat()
    meta.update(type=args.type, created=today, updated=today)
    write(folder, meta, body)
    (folder / "learnings.md").write_text(f"# {pid} learnings\n\nFeedback from runs, turned into general rules.\n")
    cmd_index(None)
    print(folder)


def cmd_add(args):
    folder = find(args.pillar)
    meta, body = read(folder)
    sources, creators = list(meta.get("sources") or []), list(meta.get("creators") or [])
    for src in map(Path, args.posts):
        if not (src / "post.json").exists():
            sys.exit(f"Not a downloaded post: {src}")
        shutil.copytree(src, folder / "originals" / src.name, dirs_exist_ok=True)
        if src.name not in sources:
            sources.append(src.name)
        if src.parent.name not in creators:
            creators.append(src.parent.name)
    meta.update(sources=sources, creators=creators, confidence=confidence(len(sources)),
                updated=date.today().isoformat())
    write(folder, meta, body)
    cmd_index(None)
    print(f"{folder.name}: {len(sources)} source post(s), confidence {meta['confidence']}")


def cmd_run(args):
    folder = find(args.pillar)
    n = len(list((folder / "runs").glob("run-*"))) + 1
    run = folder / "runs" / f"run-{n:02}_{date.today().isoformat()}_{slug(args.topic, 30)}"
    (run / "output").mkdir(parents=True)
    (run / "package.md").write_text(f"# {folder.name[:4]} · run {n:02} · {args.topic}\n")
    (run / "review.md").write_text("# Review\n\n## Format match (7 points)\n\n## Originality check\n\n"
                                   "## Tester ratings (1–5)\n\n## Feedback\n")
    print(run)


def cmd_index(_):
    rows = []
    for p in pillar_dirs():
        m, _ = read(p)
        rows.append(f"| {m.get('id', p.name[:4])} | [{m.get('name', '')}]({p.name}/pillar.md) | {m.get('type', '')} "
                    f"| {m.get('visual_class', '')} | {m.get('confidence', '')} | {m.get('status', '')} "
                    f"| {len(m.get('sources') or [])} "
                    f"| {', '.join('@' + c for c in m.get('creators') or [])} | {m.get('summary', '')} |")
    BANK.mkdir(exist_ok=True)
    (BANK / "index.md").write_text(
        "# Content bank\n\n| ID | Name | Type | Visual class | Confidence | Status | Posts | Creators | Summary |\n"
        "|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")


def cmd_list(_):
    cmd_index(None)
    print((BANK / "index.md").read_text())


def cmd_show(args):
    print((find(args.pillar) / "pillar.md").read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("name"); p.add_argument("--type", choices=["slideshow", "video"], required=True)
    p = sub.add_parser("add"); p.add_argument("pillar"); p.add_argument("posts", nargs="+")
    p = sub.add_parser("run"); p.add_argument("pillar"); p.add_argument("topic")
    sub.add_parser("index"); sub.add_parser("list")
    p = sub.add_parser("show"); p.add_argument("pillar")
    args = ap.parse_args()
    {"new": cmd_new, "add": cmd_add, "run": cmd_run, "index": cmd_index, "list": cmd_list, "show": cmd_show}[args.cmd](args)


if __name__ == "__main__":
    main()
