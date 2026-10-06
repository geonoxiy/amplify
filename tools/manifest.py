#!/usr/bin/env python3
"""File list check: does this copy of Amplify have the same files as the owner's Mac?

Usage:
  manifest.py write      owner only: list every file on this machine into doc/setup/owner-manifest.tsv
  manifest.py compare    anyone: compare this copy with doc/setup/owner-manifest.tsv and print what is missing or different

Each row is: path, where it comes from, size, hash. "Where it comes from":
  github      in the repo; a clone or `git pull` brings it
  unpushed    on the owner's Mac, committed or changed but not on GitHub yet; the owner has to push it
  local       left out of git on purpose (downloaded media, finished renders, mockup photos, raw takes); the run
              text is in git, the media is on the owner's Drive folder (README step 6)
Text files are hashed with Windows line endings turned into Unix ones, so a Windows checkout still matches.
Never listed: .git, .venv, .cache, caches, .env (the key), .claude/settings.local.json, .claude/launch.json, web/data.
"""
import hashlib
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "doc" / "setup" / "owner-manifest.tsv"
SKIP_DIRS = {".git", ".venv", ".cache", "__pycache__", "_render_tmp"}
SKIP_FILES = {".DS_Store", ".env", ".claude/settings.local.json", ".claude/launch.json", "doc/setup/owner-manifest.tsv"}
TEXT = {".py", ".md", ".json", ".txt", ".tsv", ".csv", ".yaml", ".yml", ".html", ".js", ".css", ".sh", ".log",
        ".gitignore", ".example", ".toml", ".srt", ".vtt"}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()


def files():
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if not p.is_file() or set(p.relative_to(ROOT).parts) & SKIP_DIRS or rel in SKIP_FILES:
            continue
        if p.name == ".DS_Store" or rel.startswith("web/data/") or p.suffix == ".pyc":
            continue
        yield rel, p


def digest(p):
    data = p.read_bytes()
    if p.suffix.lower() in TEXT or p.name in TEXT:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:16]


def write():
    git("fetch", "-q")
    on_github = set(git("ls-tree", "-r", "--name-only", "origin/main"))
    changed = set(git("diff", "--name-only", "origin/main"))  # committed-not-pushed and uncommitted edits
    ignored = set(git("ls-files", "--others", "--ignored", "--exclude-standard"))
    rows = []
    for rel, p in files():
        if rel in on_github and rel not in changed:
            src = "github"
        elif rel in ignored:
            src = "local"
        else:
            src = "unpushed"
        rows.append(f"{rel}\t{src}\t{p.stat().st_size}\t{digest(p)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    head = git("rev-parse", "--short", "HEAD")[0]
    OUT.write_text(f"# owner manifest, commit {head}\npath\tsource\tbytes\tsha256_16\n" + "\n".join(rows) + "\n")
    counts = defaultdict(int)
    for r in rows:
        counts[r.split("\t")[1]] += 1
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} files ({', '.join(f'{k} {v}' for k, v in sorted(counts.items()))})")


def compare():
    if not OUT.exists():
        sys.exit(f"{OUT.relative_to(ROOT)} not found: git pull first")
    owner = {}
    for line in OUT.read_text().splitlines()[2:]:
        rel, src, size, h = line.split("\t")
        owner[rel] = (src, int(size), h)
    mine = {rel: p for rel, p in files()}
    git("fetch", "-q")
    on_github = set(git("ls-tree", "-r", "--name-only", "origin/main"))  # pushed since the manifest was written
    missing, different = defaultdict(list), defaultdict(list)
    for rel, (src, size, h) in owner.items():
        if src == "unpushed" and rel in on_github:
            src = "github"
        if rel not in mine:
            missing[src].append(rel)
        elif rel != "content-bank/spend.csv" and digest(mine[rel]) != h:
            different[src].append(rel)
    extra = sorted(set(mine) - set(owner))

    def show(title, groups, note):
        total = sum(len(v) for v in groups.values())
        print(f"\n== {title}: {total}")
        for src in ("github", "unpushed", "local"):
            items = groups.get(src, [])
            if not items:
                continue
            print(f"-- {src} ({len(items)}): {note[src]}")
            by_dir = defaultdict(list)
            for rel in items:
                by_dir[rel.rsplit("/", 1)[0] if "/" in rel else "."].append(rel)
            for d, rels in sorted(by_dir.items()):
                if src == "local" and len(rels) > 3:
                    print(f"   {d}/  ({len(rels)} files)")
                else:
                    for r in rels:
                        print(f"   {r}")

    show("MISSING here, present on the owner's Mac", missing, {
        "github": "run `git pull` (or re-clone); these are on GitHub",
        "unpushed": "the owner has not pushed these yet; ask the owner to push, then `git pull`",
        "local": "media kept out of git on purpose; only needed to look at past runs (owner's Drive folder)"})
    show("DIFFERENT from the owner's copy", different, {
        "github": "this copy was edited locally: `git diff <file>`; undo with `git checkout -- <file>` unless the change is wanted",
        "unpushed": "the owner changed these after the last push; ask the owner to push, then `git pull`",
        "local": "media differs; harmless"})
    tools_extra = [e for e in extra if e.startswith(("tools/", ".claude/", "CLAUDE.md", "doc/"))]
    print(f"\n== EXTRA here, not on the owner's Mac: {len(extra)} files"
          f" ({len(tools_extra)} in tools/, .claude/ or doc/, which change how Claude works)")
    for e in tools_extra:
        print(f"   {e}")
    bad = missing.get("github") or missing.get("unpushed") or different.get("github") or tools_extra
    print("\nRESULT:", "differs from the owner's setup (see above)" if bad else "same tools and instructions as the owner")
    return 1 if bad else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "write":
        write()
    elif cmd == "compare":
        sys.exit(compare())
    else:
        sys.exit(__doc__)
