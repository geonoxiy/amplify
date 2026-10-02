import sys
sys.path.insert(0, "tools")
from pathlib import Path
import overlay as ov
from PIL import Image, ImageDraw, ImageFont

R = "content-bank/P014-tool-demo-listicle/runs/run-01_2026-09-28_willow-hard-sell-pagepilot"
W, H = 1080, 1350

FONT_BOLD = Path("assets/fonts/TikTokSans-700.ttf")


def fit(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def draw_block(img, text, y_pct, size_pct, align="center", x_margin_pct=6):
    d = ImageDraw.Draw(img, "RGBA")
    font = ImageFont.truetype(str(FONT_BOLD), round(H * size_pct))
    text = ov.curly(text)
    max_w = W * (1 - 2 * x_margin_pct / 100)
    lines = ov.wrap(text, font, max_w)
    line_h = round(font.size * 1.22)
    top = round(H * y_pct)
    for i, line in enumerate(lines):
        w = font.getlength(line)
        x = W * x_margin_pct / 100 if align == "left" else (W - w) / 2
        y = top + i * line_h
        d.text((x, y), line, font=font, fill=(255, 255, 255, 255), stroke_width=round(font.size * 0.11), stroke_fill=(0, 0, 0, 255))
    return img


slides = [
    dict(bg="cover_v2.png", out="slide1.png",
         heading=("How I Build Shopify Pages Fast", 0.06, 0.048, "left"),
         sub=("Using PagePilot", 0.235, 0.028)),
    dict(bg="laptop_slide2.png", out="slide2.png",
         heading=(None, None, None, "center"),
         sub=("PagePilot Builds The Page In Under 60 Seconds", 0.76, 0.026)),
    dict(bg="laptop_slide3.png", out="slide3.png",
         heading=(None, None, None, "center"),
         sub=("No Camera, No Studio, Just PagePilot", 0.76, 0.026)),
    dict(bg="laptop_slide4.png", out="slide4.png",
         heading=(None, None, None, "center"),
         sub=("PagePilot Writes It While You Do Something Else", 0.76, 0.026)),
    dict(bg="laptop_slide5.png", out="slide5.png",
         heading=(None, None, None, "center"),
         sub=("Works With Any Shopify Theme", 0.76, 0.026)),
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
