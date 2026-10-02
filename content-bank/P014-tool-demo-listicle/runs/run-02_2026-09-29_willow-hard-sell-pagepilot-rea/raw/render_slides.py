import sys
sys.path.insert(0, "tools")
from pathlib import Path
import overlay as ov
from PIL import Image, ImageFont

R = "content-bank/P014-tool-demo-listicle/runs/run-02_2026-09-29_willow-hard-sell-pagepilot-rea"
W, H = 1080, 1350
FONT_BOLD = Path("assets/fonts/TikTokSans-700.ttf")


def fit(img):
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


slides = [
    dict(bg="cover.png", out="slide1.png",
         heading=("how i build shopify pages fast", 0.06, 0.048, "left"),
         sub=("using pagepilot \U0001F680", 0.235, 0.028)),
    dict(bg="laptop_slide2.png", out="slide2.png",
         heading=(None, None, None, "center"),
         sub=("pagepilot builds your page in 60 seconds ⏱️", 0.76, 0.026)),
    dict(bg="laptop_slide3.png", out="slide3.png",
         heading=(None, None, None, "center"),
         sub=("just paste a product link \U0001F517", 0.76, 0.026)),
    dict(bg="laptop_slide4.png", out="slide4.png",
         heading=(None, None, None, "center"),
         sub=("pick a template you like \U0001F3A8", 0.76, 0.026)),
    dict(bg="laptop_slide5.png", out="slide5.png",
         heading=(None, None, None, "center"),
         sub=("plans start at $39 a month \U0001F4B8", 0.76, 0.026)),
]

for s in slides:
    img = fit(Image.open(f"{R}/raw/{s['bg']}"))
    h_text, h_y, h_size, align = s["heading"]
    if h_text:
        img = draw_block(img, h_text, h_y, h_size, align)
    s_text, s_y, s_size = s["sub"]
    img = draw_block(img, s_text, s_y, s_size, align)
    img = ov.phone_look(img, 0.6)
    img.save(f"{R}/output/{s['out']}", quality=95)
    print(f"{R}/output/{s['out']}")
