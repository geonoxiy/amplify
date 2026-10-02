#!/usr/bin/env python3
"""Put TikTok-style text on an image (text is always drawn in code, never by the AI model).

Usage:
  overlay.py <image> --text "line one / line two 🚀" --out slide.png [--y 0.38] [--size 0.031] [--weight 500]

- Crops/resizes to 1080×1920 (9:16) first.
- "/" in --text marks line breaks; without it, lines wrap at 78% of the width.
- --y is the vertical centre of the text block (0 = top, 1 = bottom); --size is font size as a share of height.
- TikTok "Classic" text: white TikTok Sans with a thick black outline (no soft shadow), centred, tight leading,
  straight quotes turned into curly ones. Defaults are calibrated on P004's source hook (size 0.029, y 0.375,
  wraps at ~76% of the width, first line ~73% wide). Use --style shadow for the old soft-shadow look.
- --phone adds real-phone-camera imperfections before the text: grain, slight softness, JPEG compression.
- Emoji (owner, 2026-09-29: "use emojis when applicable" in overlay text and captions): the project font has no
  emoji glyphs, so emoji in --text are rendered from a colour emoji font (Apple Color Emoji on macOS, the bundled
  Noto Color Emoji on Windows) and composited inline at the right size — no missing-glyph boxes. See
  draw_mixed()/split_runs() below; wrap() and main() use them automatically, so any caller passing emoji through
  --text already gets this for free.
"""
import argparse
import io
import re
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920

# --- emoji support -----------------------------------------------------------------------------
# Apple Color Emoji (macOS, sbix) and Noto Color Emoji (bundled for Windows, CBDT) are fixed bitmap strike fonts:
# only these exact pixel sizes can be loaded, so we always ask for the nearest one and scale the rendered glyph.
if Path("/System/Library/Fonts/Apple Color Emoji.ttc").exists():
    EMOJI_FONT_PATH, EMOJI_STRIKE_SIZES = "/System/Library/Fonts/Apple Color Emoji.ttc", [20, 32, 40, 48, 64, 96, 160]
else:
    EMOJI_FONT_PATH, EMOJI_STRIKE_SIZES = str(ROOT / "assets" / "fonts" / "NotoColorEmoji.ttf"), [109]
EMOJI_RE = re.compile(
    "(?:"
    "[\U0001F1E6-\U0001F1FF]{2}"          # regional-indicator flag pairs
    "|[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF\U00002190-\U000021FF"
    "\U00002300-\U000023FF\U0000FE0F](?:\U0000200D[\U0001F300-\U0001FAFF\U00002600-\U000027BF])*"
    ")"
)
_emoji_glyph_cache = {}
_emoji_font_cache = {}


def _emoji_font(px):
    best = min(EMOJI_STRIKE_SIZES, key=lambda s: abs(s - px))
    if best not in _emoji_font_cache:
        _emoji_font_cache[best] = ImageFont.truetype(EMOJI_FONT_PATH, best)
    return _emoji_font_cache[best]


def _emoji_glyph(chunk, target_h):
    """A colour glyph image for one emoji (possibly a multi-codepoint ZWJ sequence), scaled to target_h tall."""
    key = (chunk, target_h)
    if key in _emoji_glyph_cache:
        return _emoji_glyph_cache[key]
    font = _emoji_font(target_h)
    pad = font.size
    tmp = Image.new("RGBA", (font.size * 2 + pad, font.size * 2 + pad), (0, 0, 0, 0))
    glyph = None
    try:
        ImageDraw.Draw(tmp).text((pad // 2, pad // 2), chunk, font=font, embedded_color=True)
    except (ValueError, OSError):
        # a handful of emoji + variation-selector sequences fail Pillow's text shaper on this font;
        # retry with just the base codepoint (drop VS16 etc.) before giving up on this glyph entirely.
        base = "".join(ch for ch in chunk if unicodedata.category(ch) != "Mn" and ch not in "︎️")
        try:
            if base and base != chunk:
                ImageDraw.Draw(tmp).text((pad // 2, pad // 2), base, font=font, embedded_color=True)
        except (ValueError, OSError):
            pass
    bbox = tmp.getbbox()
    if bbox:
        cropped = tmp.crop(bbox)
        scale = target_h / cropped.height
        glyph = cropped.resize((max(1, round(cropped.width * scale)), max(1, round(cropped.height * scale))), Image.LANCZOS)
    _emoji_glyph_cache[key] = glyph
    return glyph


def split_runs(text):
    """Split text into (is_emoji, chunk) runs; each emoji run is one grapheme (glyph) to render as a unit."""
    runs, pos = [], 0
    for m in EMOJI_RE.finditer(text):
        if m.start() > pos:
            runs.append((False, text[pos:m.start()]))
        runs.append((True, m.group()))
        pos = m.end()
    if pos < len(text):
        runs.append((False, text[pos:]))
    return runs or [(False, text)]


def measure_mixed(text, font):
    """Text width including emoji, for wrap() decisions. Equals font.getlength(text) when there is no emoji."""
    total = 0.0
    for is_emoji, chunk in split_runs(text):
        if is_emoji:
            g = _emoji_glyph(chunk, font.size)
            total += (g.width if g else font.size) + font.size * 0.08
        else:
            total += font.getlength(chunk)
    return total


def draw_mixed(img, xy, text, font, fill, stroke_width=0, stroke_fill=None):
    """Draw `text` onto RGBA image `img` at (x, baseline-top) `xy`, with any emoji rendered as real colour glyphs
    inline. Returns the ending x. Stroke only applies to the text runs (colour emoji needs no outline)."""
    x, y = xy
    draw = ImageDraw.Draw(img)
    asc, _ = font.getmetrics()
    for is_emoji, chunk in split_runs(text):
        if is_emoji:
            g = _emoji_glyph(chunk, round(asc * 0.92))
            if g:
                img.paste(g, (round(x), round(y + (asc - g.height) / 2)), g)
                x += g.width + font.size * 0.08
            else:
                x += font.size  # glyph failed to render (e.g. not covered by this macOS version); leave a gap
        else:
            draw.text((x, y), chunk, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
            x += font.getlength(chunk)
    return x


def curly(text):
    out, opened = [], False
    for ch in text:
        if ch == '"':
            out.append("”" if opened else "“")
            opened = not opened
        else:
            out.append(ch)
    return "".join(out).replace("'", "’")


def wrap(text, font, max_w):
    if "/" in text:
        return [l.strip() for l in text.split("/")]
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if measure_mixed(trial, font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--text", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--y", type=float, default=0.375)
    ap.add_argument("--size", type=float, default=0.029)
    ap.add_argument("--weight", default="500", choices=["500", "700"])
    ap.add_argument("--style", default="classic", choices=["classic", "shadow"])
    ap.add_argument("--phone", type=float, nargs="?", const=1.0, default=0.0,
                    help="phone-camera imperfections, strength (default 1.0 when given)")
    args = ap.parse_args()

    img = fit(Image.open(args.image))
    if args.phone:
        img = phone_look(img, args.phone)
    if args.text:
        font = ImageFont.truetype(str(ROOT / "assets" / "fonts" / f"TikTokSans-{args.weight}.ttf"), round(H * args.size))
        text = curly(args.text)
        lines = wrap(text, font, W * 0.76)
        line_h = round(font.size * (1.3 if args.style == "classic" else 1.22))
        top = round(H * args.y - line_h * len(lines) / 2)
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        stroke = round(font.size * 0.11)
        for i, line in enumerate(lines):
            x = (W - measure_mixed(line, font)) / 2
            y = top + i * line_h
            if args.style == "classic":
                draw_mixed(text_layer, (x, y), line, font, (255, 255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            else:
                xs = x
                for is_emoji, chunk in split_runs(line):
                    if not is_emoji:
                        sd.text((xs, y + 2), chunk, font=font, fill=(0, 0, 0, 170))
                    xs += measure_mixed(chunk, font)
                draw_mixed(text_layer, (x, y), line, font, (255, 255, 255, 255))
        shadow = shadow.filter(ImageFilter.GaussianBlur(3))
        img = Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), shadow), text_layer).convert("RGB")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out, quality=95)
    print(args.out)


def fit(img):
    img = img.convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def phone_look(img, strength=1.0):
    """Make an AI image read like a real phone photo: sensor grain, a touch of softness, JPEG compression."""
    img = img.filter(ImageFilter.GaussianBlur(0.5 * strength))
    a = np.asarray(img, dtype=np.float32)
    rng = np.random.default_rng()
    luma = rng.normal(0, 5.5 * strength, a.shape[:2])[..., None]
    chroma = rng.normal(0, 2.0 * strength, a.shape)
    a = np.clip(a + luma + chroma, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(a).save(buf, "JPEG", quality=78)
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB")


if __name__ == "__main__":
    main()
