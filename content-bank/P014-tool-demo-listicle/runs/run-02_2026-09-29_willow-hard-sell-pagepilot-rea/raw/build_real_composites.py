"""Composite real PagePilot screenshots (their own site, screenshotted with the browser pane and cropped to
clean, own-brand-only regions) onto the laptop screen in laptop_base.png. Owner, 2026-09-29: 'access their
website, take a screenshot of certain pages, then make it the screen of the laptop.'"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

R = Path("content-bank/P014-tool-demo-listicle/runs/run-02_2026-09-29_willow-hard-sell-pagepilot-rea")


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p2[0], p2[1], 1, 0, 0, 0, -p1[0] * p2[0], -p1[0] * p2[1]])
        matrix.append([0, 0, 0, p2[0], p2[1], 1, -p1[1] * p2[0], -p1[1] * p2[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(pa, dtype=np.float64).reshape(8)
    return np.linalg.solve(A, B).tolist()


def perspective_paste(base, card, quad):
    w, h = card.size
    coeffs = find_coeffs([(0, 0), (w, 0), (w, h), (0, h)], quad)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    warped = card.convert("RGBA").transform(base.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    layer.paste(warped, (0, 0), warped)
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


QUAD = [(578, 270), (1488, 238), (1488, 1032), (578, 1058)]
CARD_W, CARD_H = 1600, 1000  # aspect the quad roughly maps to


def fit_card(im):
    """Fill CARD_W x CARD_H with the real screenshot, cropping the overflow (never stretching)."""
    return ImageOps.fit(im.convert("RGB"), (CARD_W, CARD_H), Image.LANCZOS, centering=(0.5, 0.5))


SHOTS = {
    "slide2.png": "pagepilot_real/pp_hero_cta.png",
    "slide3.png": "pagepilot_real/pp_step1.png",
    "slide4.png": "pagepilot_real/pp_step2.png",
    "slide5.png": "pagepilot_real/pp_pricing.png",
}

base = Image.open(R / "raw" / "laptop_base.png")
for out_name, shot_rel in SHOTS.items():
    card = fit_card(Image.open(R / "raw" / shot_rel))
    composited = perspective_paste(base, card, QUAD)
    composited.save(R / "raw" / f"laptop_{out_name}")
    print(R / "raw" / f"laptop_{out_name}")
