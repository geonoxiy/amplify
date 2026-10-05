#!/usr/bin/env python3
"""Numbered tip cards (P006 layouts) on top of cards.py: cover, numbered tip, bonus tip with a phone showing a real screenshot.
A new file so cards.py stays as it is on GitHub; it reuses cards.py's Card (text in code, art multiply-blended on the card).

Usage:
  tipcards.py <spec.json> [--out DIR]

Spec (paths relative to the spec file):
  {"canvas": [1080, 1350], "theme": {...},
   "brand": {"name": "PagePilot", "icon": "<art with the mascot head>", "icon_crop": [x0, y0, x1, y1] (fractions)},
   "slides": [
     {"type": "cover", "lines": [{"text", "color", "cap_pct"}], "tag": "(pt. 1)", "art", "art_box"},
     {"type": "tip", "number": "#1", "title", "body", "art", "art_box"},
     {"type": "bonus", "title", "body", "screen": "<screenshot>", "screen_crop": [0, 0, 1, 0.7], "art", "art_box"}]}
Body text: "\\n\\n" starts a new paragraph. Writes DIR/slideN.png and DIR/records/slideN.json (visual data model).
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from cards import S, Card, accent_line, hex_rgb, wrap


class TipCard(Card):
    def __init__(self, spec_dir, canvas, theme, brand):
        super().__init__(spec_dir, canvas, theme)
        self.brand = brand

    def logo(self):
        b = self.brand
        h = self.hpx(4.2) * S
        x, y = self.wpx(2.7) * S, self.hpx(2.1) * S
        im = cv2.imread(str(self.dir / b["icon"]))
        H, W = im.shape[:2]
        c = b.get("icon_crop", [0, 0, 1, 1])
        tmp = self.dir / ".icon_tmp.png"
        cv2.imwrite(str(tmp), im[int(c[1] * H):int(c[3] * H), int(c[0] * W):int(c[2] * W)])
        art, _ = self.load_art(tmp.name)
        tmp.unlink()
        ibox, _ = self.place_art(art, [2.7, 2.1, 4.2 * self.H / self.W, 4.2])
        f = self.body(2.75, "demibold")
        asc = f.getbbox("H")[3] - f.getbbox("H")[1]
        bb = self.text((ibox[2] + 10 * S, y + h / 2 + asc / 2), b["name"], f, self.t["ink"])
        self.note_layer("mark", self.to_pct((x, y, bb[2], y + h)), "brand mark top-left on every slide: mascot head icon + wordmark")
        self.note_text(b["name"], bb, "watermark", "corner-mark", "left", "Avenir Next Demi Bold", 2.75, "brand name", self.t["ink"], "solid card background", origin="mark")


def paragraphs(card, text, x_pct, top_pct, width_pct, size_pct, align="left"):
    pf = card.body(size_pct)
    asc, desc = pf.getmetrics()
    y, bbs = card.hpx(top_pct) * S, []
    for para in text.split("\n\n"):
        for ln in wrap(card, para, pf, card.wpx(width_pct) * S):
            bbs.append(card.text((card.wpx(x_pct) * S, y + asc), ln, pf, card.t["body"]))
            y += (asc + desc) * 1.32
        y += (asc + desc) * 0.6
    box = (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs), max(b[3] for b in bbs))
    card.note_text(text.replace("\n\n", " / "), box, "body", "numbered-heading", align, "Avenir Next Regular", size_pct, "lowercase", card.t["body"], "solid card background")
    return box


def place(card, s, note):
    art, _ = card.load_art(s["art"], crop_top=s.get("crop_top"))
    box_px, _ = card.place_art(art, s["art_box"], align="bottom-center", bottom_bleed=s.get("bleed", False))
    pct = card.to_pct(box_px)
    card.note_layer("mascot", pct, note)
    return pct


def heading_row(card, number, title):
    nf, tf = card.heading(5.4), card.heading(4.4)
    base = card.hpx(22.6) * S
    x = card.wpx(10) * S
    if number:
        bb1 = card.text((x, base), number, nf, card.t["accent"])
        card.note_text(number, bb1, "number", "numbered-heading", "left", "DIN Condensed Bold", 5.4 / 0.71, "n/a", card.t["accent"], "solid card background")
        x = bb1[2] + card.wpx(3) * S
    bb2 = card.text((x, base), title, tf, card.t["ink"])
    card.note_text(title, bb2, "headline", "numbered-heading", "left", "DIN Condensed Bold", 4.4 / 0.71, "lowercase", card.t["ink"], "solid card background")
    accent_line(card, 10, 26.4)


def slide_cover(card, s):
    card.logo()
    y = card.hpx(s.get("top_pct", 12)) * S
    last = None
    for ln in s["lines"]:
        f = card.heading(ln["cap_pct"])
        cap = f.getbbox("H")[3] - f.getbbox("H")[1]
        last = card.text((card.W * S / 2, y + cap), ln["text"], f, card.t[ln["color"]], anchor="ms")
        card.note_text(ln["text"], last, "hook", "top-headline", "center", "DIN Condensed Bold", ln["cap_pct"] / 0.71, "lowercase", card.t[ln["color"]], "solid card background")
        y += cap + card.hpx(s.get("gap_pct", 2.6)) * S
    if s.get("tag"):  # series counter set after the last line, smaller, accent
        f = card.heading(s.get("tag_cap", 4.0))
        bb = card.text((last[2] + 14 * S, last[3]), s["tag"], f, card.t["accent"], anchor="ls")
        card.note_text(s["tag"], bb, "series", "top-headline", "left", "DIN Condensed Bold", s.get("tag_cap", 4.0) / 0.71, "lowercase", card.t["accent"], "solid card background")
    pct = place(card, {**s, "bleed": True}, s.get("art_note", "mascot, waist up, bleeds off the bottom edge"))
    return {"summary": "cover: regret hook with a series counter over the mascot", "subject_box": pct}


def slide_tip(card, s):
    card.logo()
    heading_row(card, s["number"], s["title"])
    paragraphs(card, s["body"], 10, 30.6, s.get("body_w", 72), 2.65)
    pct = place(card, s, s.get("art_note", "mascot acting the tip out with one prop"))
    return {"summary": f"tip {s['number']}: heading, underline, short paragraph, mascot with a prop", "subject_box": pct}


def slide_bonus(card, s):
    card.logo()
    heading_row(card, "", s["title"])
    paragraphs(card, s["body"], 10, 30.6, s.get("body_w", 76), 2.65)
    # phone drawn in code: dark bezel, rounded screen, the real screenshot inside (never generated)
    sx, sy, sw = s.get("phone_box", [9, 47, 37])
    shot = Image.open(card.dir / s["screen"]).convert("RGB")
    c = s.get("screen_crop", [0, 0, 1, 0.7])
    shot = shot.crop((int(c[0] * shot.width), int(c[1] * shot.height), int(c[2] * shot.width), int(c[3] * shot.height)))
    bez = card.wpx(sw) * 0.045 * S
    scr_w = card.wpx(sw) * S - 2 * bez
    scr_h = scr_w * shot.height / shot.width
    x0, y0 = card.wpx(sx) * S, card.hpx(sy) * S
    x1, y1 = x0 + scr_w + 2 * bez, y0 + scr_h + 2 * bez
    shadow = Image.new("L", card.img.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 10 * S, y0 + 14 * S, x1 + 10 * S, y1 + 14 * S), radius=bez * 3.2, fill=70)
    shadow = Image.fromarray(cv2.GaussianBlur(np.asarray(shadow), (0, 0), 14 * S))
    card.img = Image.composite(Image.new("RGB", card.img.size, (0, 0, 0)), card.img, shadow)
    card.d = ImageDraw.Draw(card.img)
    card.d.rounded_rectangle((x0, y0, x1, y1), radius=bez * 3.2, fill=hex_rgb(s.get("bezel", "#151618")))
    shot = shot.resize((int(scr_w), int(scr_h)), Image.LANCZOS)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width - 1, shot.height - 1), radius=bez * 2.3, fill=255)
    card.img.paste(shot, (int(x0 + bez), int(y0 + bez)), mask)
    card.d = ImageDraw.Draw(card.img)
    ix = (x0 + x1) / 2  # dynamic-island pill
    card.d.rounded_rectangle((ix - scr_w * .14, y0 + bez * 2.2, ix + scr_w * .14, y0 + bez * 2.2 + scr_w * .085), radius=scr_w * .05, fill=hex_rgb("#151618"))
    card.note_layer("phone-mockup", card.to_pct((x0, y0, x1, y1)), f"phone drawn in code showing a real screenshot of the brand's site ({s['screen']})")
    pct = place(card, s, s.get("art_note", "mascot pointing at the phone"))
    return {"summary": "bonus tip: product plug with a phone showing the brand's real site, mascot pointing at it", "subject_box": pct}


SLIDES = {"cover": slide_cover, "tip": slide_tip, "bonus": slide_bonus}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text())
    out = args.out or args.spec.parent / "output"
    (out / "records").mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(spec["slides"], 1):
        card = TipCard(args.spec.parent, spec.get("canvas", [1080, 1350]), spec.get("theme", {}), spec["brand"])
        info = SLIDES[s["type"]](card, s)
        card.finish(out / f"slide{i}.png")
        rec = {"n": i, "role": s.get("role", s["type"]), "class": s.get("class", "other:designed-card"), "confidence": "high", "summary": info["summary"],
               "frame": {"canvas": f"4:5 portrait, {card.W}x{card.H}",
                         "layers": [{"type": "background", "box": [0, 0, 100, 100], "note": f"flat card colour {card.t['bg']}"}] + card.layers,
                         "composition": {"subject_box": info["subject_box"]}},
               "text_blocks": card.texts}
        (out / "records" / f"slide{i}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2))
        print(f"slide{i}.png  ({len(card.texts)} text blocks)")


if __name__ == "__main__":
    main()
