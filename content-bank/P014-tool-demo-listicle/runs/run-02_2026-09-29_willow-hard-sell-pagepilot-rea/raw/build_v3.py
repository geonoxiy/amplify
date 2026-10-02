"""run-02, third pass: real screenshots captured at a landscape (1.6:1) browser viewport so they already match
the laptop screen's own proportions (no more squishing thin bands into a mismatched card size), and two
different laptop angles/positions across the feature slides (matching the source's varied camera setups)."""
import sys
sys.path.insert(0, "tools")
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageFont
import overlay as ov

R = Path("content-bank/P014-tool-demo-listicle/runs/run-02_2026-09-29_willow-hard-sell-pagepilot-rea")
FONT_BOLD = Path("assets/fonts/TikTokSans-700.ttf")
W, H = 1080, 1350


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


BASES = {
    "A": dict(file="laptop_base.png", quad=[(578, 270), (1488, 238), (1488, 1032), (578, 1058)]),
    "B": dict(file="laptop_angleB.png", quad=[(512, 222), (1128, 278), (1078, 795), (478, 715)]),
}

# each real crop is already ~1.6:1 landscape (captured at a 1600x1000 browser viewport), so ImageOps.fit only
# trims a little off one side rather than blowing up a thin sliver.
FEATURE_SLIDES = [
    ("slide2.png", "A", "pagepilot_real/land_hero.jpg", "pagepilot builds your page in 60 seconds ⏱️"),
    ("slide3.png", "B", "pagepilot_real/land_stats.jpg", "over $200m made on pagepilot pages \U0001F4B0"),
    ("slide4.png", "A", "pagepilot_real/pp_full_features.png", "every tool you need, one plan \U0001F6E0️"),
    ("slide5.png", "B", "pagepilot_real/land_steps.jpg", "paste a link, publish a page \U0001F517"),
]


def fit_frame(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def draw_block(img, text, y_pct, size_pct, align="center", x_margin_pct=6):
    img = img.convert("RGBA")
    font = ImageFont.truetype(str(FONT_BOLD), round(H * size_pct))
    lines = ov.wrap(ov.curly(text), font, W * (1 - 2 * x_margin_pct / 100))
    line_h = round(font.size * 1.22)
    top = round(H * y_pct)
    for i, line in enumerate(lines):
        w = ov.measure_mixed(line, font)
        x = W * x_margin_pct / 100 if align == "left" else (W - w) / 2
        y = top + i * line_h
        ov.draw_mixed(img, (x, y), line, font, (255, 255, 255, 255), stroke_width=round(font.size * 0.11), stroke_fill=(0, 0, 0, 255))
    return img.convert("RGB")


for out_name, base_key, real_rel, sub_text in FEATURE_SLIDES:
    b = BASES[base_key]
    base_img = Image.open(R / "raw" / b["file"])
    quad = b["quad"]
    qw = round(max(p[0] for p in quad) - min(p[0] for p in quad))
    qh = round(max(p[1] for p in quad) - min(p[1] for p in quad))
    real_card = ImageOps.fit(Image.open(R / "raw" / real_rel).convert("RGB"), (qw, qh), Image.LANCZOS, centering=(0.5, 0.25))
    composited = perspective_paste(base_img, real_card, quad)
    frame = fit_frame(composited)
    frame = draw_block(frame, sub_text, 0.80, 0.026)
    frame = ov.phone_look(frame, 0.5)
    frame.save(R / "output" / out_name, quality=95)
    print(R / "output" / out_name)

cover = fit_frame(Image.open(R / "raw" / "cover.png"))
cover = draw_block(cover, "how i build shopify pages fast", 0.06, 0.048, align="left")
cover = draw_block(cover, "using pagepilot \U0001F680", 0.235, 0.028, align="left")
cover = ov.phone_look(cover, 0.5)
cover.save(R / "output" / "slide1.png", quality=95)
print(R / "output" / "slide1.png")
