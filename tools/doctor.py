#!/usr/bin/env python3
"""Setup check: is this copy of Amplify set up like the owner's? Run it after cloning, and again after every pull.

Usage:
  doctor.py                 every check, then a test render compared with the owner's machine
  doctor.py --offline       skip the checks that need the internet (kie.ai balance, GitHub)
  doctor.py --write-golden  owner only: store this machine's test render as the reference (assets/doctor/expected.json)

Checks: the Python environment (.venv, 3.12), the packages, ffmpeg, the Chromium browser that webshot.py and mockup.py
use, the fonts, the kie.ai key (asks kie for the credit balance, which costs nothing), the instruction files Claude
reads (CLAUDE.md, the skills, .claude/settings.json), the Drive files, and whether this copy is behind GitHub.
Then it renders the P006 test carousel (assets/doctor/spec.json, art from the 2026-10-06 PagePilot run) with
tools/tipcards.py and compares each slide with the owner's render by perceptual hash (256 bits):
  same   0 to 8 bits apart    the slides come out the same as on the owner's Mac
  close  9 to 40 bits apart   same layout, small drawing differences (expected on Windows: look-alike fonts)
  FAIL   more than 40 bits    something renders differently: look at the slides in .cache/doctor/
Exit code 1 if any check fails. Warnings don't fail the run.
"""
import argparse
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
FIX = ROOT / "assets" / "doctor"
sys.path.insert(0, str(TOOLS))

results = []  # (status, name, detail)


def report(status, name, detail=""):
    results.append((status, name, detail))
    mark = {"ok": "OK  ", "warn": "WARN", "fail": "FAIL"}[status]
    print(f"[{mark}] {name}" + (f"  ·  {detail}" if detail else ""))


def check_python():
    venv = ROOT / ".venv"
    inside = Path(sys.prefix).resolve() == venv.resolve()
    v = sys.version_info
    if not inside:
        report("fail", "python environment", f"running {sys.executable}; use ./.venv/bin/python (Windows: ./.venv/python.exe) tools/doctor.py")
    elif (v.major, v.minor) != (3, 12):
        report("fail", "python environment", f"Python {v.major}.{v.minor}; the owner's is 3.12 (README step 2)")
    else:
        report("ok", "python environment", f".venv, Python {v.major}.{v.minor}.{v.micro}, {platform.system()} {platform.machine()}")


def check_packages():
    mods = {"yt_dlp": "yt-dlp", "gallery_dl": "gallery-dl", "PIL": "pillow", "numpy": "numpy", "yaml": "pyyaml",
            "imagehash": "imagehash", "scenedetect": "scenedetect", "cv2": "opencv-python-headless",
            "playwright": "playwright", "scipy": "scipy", "requests": "requests", "matplotlib": "matplotlib"}
    if sys.platform == "darwin" and platform.machine() == "arm64":
        mods["mlx_whisper"] = "mlx-whisper"
    else:
        mods["faster_whisper"] = "faster-whisper"
    missing = []
    for m, pkg in mods.items():
        try:
            importlib.import_module(m)
        except Exception:
            missing.append(pkg)
    if missing:
        report("fail", "packages", "missing " + ", ".join(missing) + " (README step 3)")
    else:
        report("ok", "packages", f"{len(mods)} core packages import")
    try:
        importlib.import_module("mediapipe")
        report("ok", "mediapipe (motion tool)")
    except Exception:
        report("warn", "mediapipe (motion tool)", "not installed; only motion.py needs it (README step 3b)")
    try:
        importlib.import_module("claude_agent_sdk")
        report("ok", "web app packages")
    except Exception:
        report("warn", "web app packages", "claude-agent-sdk missing; only the web app needs it")


def check_ffmpeg():
    import portable
    found = []
    for name in ("ffmpeg", "ffprobe"):
        try:
            found.append(portable.exe(name))
        except SystemExit:
            report("fail", name, "not found in .venv (README step 2 installs it with conda)")
            return
    out = subprocess.run([found[0], "-version"], capture_output=True, text=True).stdout.split("\n")[0]
    report("ok", "ffmpeg + ffprobe", out[:60])


def check_chromium():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            ver = b.version
            b.close()
        report("ok", "chromium for website screenshots", ver)
    except Exception as e:
        report("fail", "chromium for website screenshots", f"{str(e).splitlines()[0][:80]} (README step 4)")


def check_fonts():
    import cards
    t = cards.DEFAULT_THEME
    fonts = [t["heading_font"], t["body_font"]]
    missing = [f for f in fonts if not Path(f).exists()]
    if missing:
        report("fail", "fonts", "missing " + ", ".join(missing))
    elif all(f.startswith("/System/Library") for f in fonts):
        report("ok", "fonts", "Apple fonts (DIN Condensed, Avenir Next), same as the owner")
    else:
        report("warn", "fonts", "look-alike fonts from assets/fonts (Barlow Condensed, Nunito Sans): slides look very close, not identical")


def check_key(offline):
    env = ROOT / ".env"
    key = ""
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("KIE_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key or key.startswith("paste-"):
        report("fail", "kie.ai key", "no key in .env (README step 5)")
        return
    if offline:
        report("ok", "kie.ai key", "present (not tested, --offline)")
        return
    r = subprocess.run([sys.executable, str(TOOLS / "kie.py"), "balance"], capture_output=True, text=True, cwd=ROOT)
    msg = (r.stdout if r.returncode == 0 else (r.stderr or r.stdout)).strip().splitlines()
    if r.returncode == 0:
        report("ok", "kie.ai key", f"works, balance {msg[-1] if msg else '?'}")
    else:
        report("fail", "kie.ai key", msg[-1][:100] if msg else "kie.py balance failed")


def check_instructions():
    need = ["CLAUDE.md", ".claude/skills/amplify/SKILL.md", ".claude/skills/amplify-plus/SKILL.md",
            ".claude/skills/amplify-account-copy/SKILL.md", "doc/Owner Rules.md", "doc/Project Deliverables.md"]
    missing = [n for n in need if not (ROOT / n).exists()]
    if missing:
        report("fail", "instruction files Claude reads", "missing " + ", ".join(missing) + " (pull from GitHub)")
    else:
        report("ok", "instruction files Claude reads", f"{len(need)} files")
    s = ROOT / ".claude" / "settings.json"
    try:
        ok = json.loads(s.read_text()).get("env", {}).get("PYTHONUTF8") == "1"
    except Exception:
        ok = False
    report("ok" if ok else "fail", ".claude/settings.json", "PYTHONUTF8=1" if ok else "missing or changed: keep the repo's version")


def check_drive():
    cache = ROOT / ".cache"
    n = sum(1 for p in cache.rglob("*") if p.is_file()) if cache.exists() else 0
    if n:
        report("ok", "Drive files", f".cache has {n} files (past paid generations are reused)")
    else:
        report("warn", "Drive files", "no .cache: past AI generations will be paid for again (README step 6)")


def check_git(offline):
    if not (ROOT / ".git").exists():
        report("warn", "git", "not a git clone: you can't pull updates")
        return
    if offline:
        return
    git = shutil.which("git")
    if not git:
        report("warn", "git", "git not on PATH")
        return
    subprocess.run([git, "fetch", "--quiet"], cwd=ROOT, capture_output=True, timeout=60)
    r = subprocess.run([git, "rev-list", "--count", "HEAD..@{u}"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        report("warn", "git", "no upstream branch to compare with")
    elif r.stdout.strip() != "0":
        report("fail", "git", f"{r.stdout.strip()} new commit(s) on GitHub: run git pull")
    else:
        report("ok", "git", "up to date with GitHub")


def render_test(write_golden):
    import imagehash
    from PIL import Image
    out = ROOT / ".cache" / "doctor"
    if out.exists():
        shutil.rmtree(out)
    r = subprocess.run([sys.executable, str(TOOLS / "tipcards.py"), str(FIX / "spec.json"), "--out", str(out)],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        report("fail", "test render", (r.stderr.strip().splitlines() or ["tipcards.py failed"])[-1][:120])
        return
    hashes = {p.name: str(imagehash.phash(Image.open(p), hash_size=16)) for p in sorted(out.glob("slide*.png"))}
    exp_file = FIX / "expected.json"
    if write_golden:
        exp_file.write_text(json.dumps({"machine": f"{platform.system()} {platform.machine()}", "hash_size": 16, "slides": hashes}, indent=1))
        report("ok", "test render", f"reference written to {exp_file.relative_to(ROOT)}")
        return
    if not exp_file.exists():
        report("fail", "test render", "assets/doctor/expected.json missing (pull from GitHub)")
        return
    exp = json.loads(exp_file.read_text())["slides"]
    worst, parts = 0, []
    for name, h in exp.items():
        if name not in hashes:
            report("fail", "test render", f"{name} was not drawn")
            return
        d = imagehash.hex_to_hash(h) - imagehash.hex_to_hash(hashes[name])
        worst = max(worst, d)
        parts.append(f"{name.replace('.png', '')} {d}")
    detail = "bits apart: " + ", ".join(parts) + f"  (slides in {out.relative_to(ROOT)})"
    if worst <= 8:
        report("ok", "test render: same as the owner's", detail)
    elif worst <= 40:
        report("warn", "test render: close to the owner's", detail)
    else:
        report("fail", "test render: differs from the owner's", detail)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--write-golden", action="store_true")
    args = ap.parse_args()
    os.chdir(ROOT)
    check_python()
    check_packages()
    check_ffmpeg()
    check_chromium()
    check_fonts()
    check_key(args.offline)
    check_instructions()
    check_drive()
    check_git(args.offline)
    render_test(args.write_golden)
    fails = [r for r in results if r[0] == "fail"]
    warns = [r for r in results if r[0] == "warn"]
    print(f"\n{len(results) - len(fails) - len(warns)} ok, {len(warns)} warnings, {len(fails)} failed")
    print("Setup matches the owner's." if not fails else "Fix the FAIL lines (README setup steps), then run this again.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
