"""The macOS and Windows differences, in one place, so every tool runs on both.

- exe(name): the conda environment in .venv keeps ffmpeg, ffprobe, yt-dlp and gallery-dl in bin/ on macOS, and on
  Windows as .exe files in Library/bin/ (ffmpeg, ffprobe) or Scripts/ (tools installed with pip).
- font(mac, bundled): a macOS system font when it is installed, else its free look-alike in assets/fonts/ (Windows).
  Apple's fonts can't be redistributed, so output on Windows uses the look-alikes: DIN Condensed → Barlow Condensed,
  Avenir Next → Nunito Sans, SF Pro → Inter, Apple Color Emoji → Noto Color Emoji (all SIL Open Font License).
- weighted(path, size, weight): a variable font at a numeric weight (400 regular, 500 medium, 600 semibold).
"""
import shutil
import sys
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"


def exe(name):
    for env in (ROOT / ".venv", Path(sys.prefix)):
        for sub in ("bin", "Library/bin", "Scripts"):
            for p in (env / sub / name, env / sub / f"{name}.exe"):
                if p.is_file():
                    return str(p)
    found = shutil.which(name)
    if not found:
        sys.exit(f"{name} not found in .venv or on PATH (see Setup in README.md)")
    return found


def font(mac_path, bundled):
    return mac_path if Path(mac_path).exists() else str(FONTS / bundled)


def weighted(path, size, weight):
    f = ImageFont.truetype(str(path), size)
    try:
        axes = f.get_variation_axes()
    except OSError:  # a static font: it has one weight
        return f
    f.set_variation_by_axes([weight if a["name"] in (b"Weight", "Weight") else a["default"] for a in axes])
    return f
