"""Build a PagePilot-branded editor mockup (real logo wordmark, real brand colours, real functional
UI labels observed on pagepilot.ai) and perspective-warp it onto the laptop screen in laptop_base_v2.png.
No third-party brand content or real people's photos are used (checked and excluded from the downloaded
reference assets)."""
import sys
sys.path.insert(0, "tools")
from pathlib import Path
import numpy as np
import overlay as ov
from PIL import Image, ImageDraw, ImageFont

R = Path("content-bank/P014-tool-demo-listicle/runs/run-01_2026-09-28_willow-hard-sell-pagepilot")
FONT_BOLD = Path("assets/fonts/TikTokSans-700.ttf")
FONT_MED = Path("assets/fonts/TikTokSans-500.ttf")

PURPLE = "#4922FF"   # PagePilot's real CTA/brand colour, sampled from pagepilot.ai
NAVY = "#1F1555"     # PagePilot's real dark hero colour
LILAC_BG = "#F9F7FF"  # PagePilot's real light background colour
CARD_W, CARD_H = 1600, 1000


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mockup(feature_label):
    img = Image.new("RGB", (CARD_W, CARD_H), hexrgb(LILAC_BG))
    d = ImageDraw.Draw(img)
    # browser chrome
    d.rectangle((0, 0, CARD_W, 70), fill=(255, 255, 255))
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        d.ellipse((30 + i * 34, 26, 30 + i * 34 + 18, 44), fill=hexrgb(c))
    d.rounded_rectangle((160, 18, 700, 52), radius=16, fill=(240, 240, 245))
    urlf = ImageFont.truetype(str(FONT_MED), 22)
    d.text((180, 27), "pagepilot.ai/editor", font=urlf, fill=(90, 90, 100))
    d.line((0, 70, CARD_W, 70), fill=(225, 222, 235), width=2)
    # top bar: real wordmark + real button label
    wf = ImageFont.truetype(str(FONT_BOLD), 40)
    d.text((36, 92), "PagePilot", font=wf, fill=hexrgb(PURPLE))
    btnf = ImageFont.truetype(str(FONT_MED), 26)
    d.rounded_rectangle((CARD_W - 320, 84, CARD_W - 36, 152), radius=34, fill=hexrgb(PURPLE))
    d.text((CARD_W - 296, 102), "Publish to Shopify", font=btnf, fill=(255, 255, 255))
    # left sidebar: real tab + section labels seen on pagepilot.ai
    tabf = ImageFont.truetype(str(FONT_MED), 26)
    d.rounded_rectangle((36, 180, 220, 226), radius=20, fill=hexrgb(PURPLE))
    d.text((60, 190), "Elements", font=tabf, fill=(255, 255, 255))
    d.text((246, 190), "Gallery", font=tabf, fill=(110, 105, 130))
    labels = ["Social Proof Logos", "Video Testimonials", "Benefits & Features", "Review Bar"]
    itemf = ImageFont.truetype(str(FONT_MED), 24)
    for i, lab in enumerate(labels):
        y = 270 + i * 58
        d.rounded_rectangle((36, y, 300, y + 44), radius=10, fill=(255, 255, 255), outline=(226, 222, 240))
        d.text((54, y + 10), lab, font=itemf, fill=(70, 65, 90))
    # main canvas: feature heading + generic placeholder blocks (no third-party content)
    d.rounded_rectangle((340, 180, CARD_W - 36, CARD_H - 36), radius=18, fill=(255, 255, 255), outline=(226, 222, 240))
    hf = ImageFont.truetype(str(FONT_BOLD), 34)
    d.text((376, 216), feature_label, font=hf, fill=hexrgb(NAVY))
    for i, (bw, bh) in enumerate([(720, 190), (330, 260), (330, 260)]):
        bx = 376 + (0 if i == 0 else (i - 1) * 350)
        by = 280 if i == 0 else 500
        d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=14, fill=hexrgb(LILAC_BG))
    return img


def find_coeffs(pa, pb):
    """Canonical PIL perspective-coefficient recipe. pa = plain rectangle corners of the source
    image (the card); pb = the quad in the destination (base) image those corners should land on."""
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p2[0], p2[1], 1, 0, 0, 0, -p1[0] * p2[0], -p1[0] * p2[1]])
        matrix.append([0, 0, 0, p2[0], p2[1], 1, -p1[1] * p2[0], -p1[1] * p2[1]])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(pa, dtype=np.float64).reshape(8)
    res = np.linalg.solve(A, B)
    return res.tolist()


def perspective_paste(base, card, quad):
    """Warp `card` onto `base` at the 4 (x,y) corners in quad = [TL, TR, BR, BL]."""
    w, h = card.size
    coeffs = find_coeffs([(0, 0), (w, 0), (w, h), (0, h)], quad)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    warped = card.convert("RGBA").transform(base.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    layer.paste(warped, (0, 0), warped)
    out = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    return out


# eyeballed screen quad in laptop_base_v2.png (1792x2400), top-left/top-right/bottom-right/bottom-left
QUAD = [(578, 270), (1488, 238), (1488, 1032), (578, 1058)]

FEATURES = {
    "slide2.png": "Paste A Product Link",
    "slide3.png": "AI Product Photos",
    "slide4.png": "Ad Copy Written For You",
    "slide5.png": "Cart + Upsells Built In",
}

base_img = Image.open(R / "raw" / "laptop_base_v2.png")
for fname, label in FEATURES.items():
    card = mockup(label)
    composited = perspective_paste(base_img, card, QUAD)
    composited.save(R / "raw" / f"laptop_{fname}")
    print(R / "raw" / f"laptop_{fname}")
