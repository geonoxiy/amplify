#!/usr/bin/env python3
"""Designed-card renderer: text drawn in code, generated art placed as layers (guideline 2.16, 3.3).
The image model never draws text. Built for the P005 layouts (cover, anatomy overview, muscle pick); the helpers are general.

Usage:
  cards.py <spec.json> [--out DIR]

Spec (paths are relative to the spec file):
  {"canvas": [1080, 1350], "theme": {...}, "slides": [{"type": "cover|overview|pick", ...}]}
Writes DIR/slideN.png and DIR/records/slideN.json: one frame record per slide in the visual data model
(boxes measured from the pixels actually drawn, in % of the frame), ready for `measure.py check --record`.

Art is generated on a plain white background. It is normalised to pure white, cropped to its content, and multiply-blended onto
the card, so the white disappears into the card colour and the outlines and fills stay as drawn.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import portable

S = 2  # supersampling factor for drawing; the result is downsampled to the canvas size

DEFAULT_THEME = {
    "bg": "#f2f3ee", "ink": "#16202b", "accent": "#0b8a77", "body": "#4a5561",
    "red": "#e5322d", "yellow": "#ffd23f", "white": "#ffffff",
    # DIN Condensed and Avenir Next are macOS fonts; on Windows their look-alikes in assets/fonts stand in. body_index
    # is the face index inside a .ttc, or the numeric weight of a variable font (Nunito Sans)
    "heading_font": portable.font("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf", "BarlowCondensed-SemiBold.ttf"),
    "body_font": portable.font("/System/Library/Fonts/Avenir Next.ttc", "NunitoSans-VF.ttf"),
    "body_index": ({"regular": 7, "medium": 5, "demibold": 2} if Path("/System/Library/Fonts/Avenir Next.ttc").exists()
                   else {"regular": 400, "medium": 500, "demibold": 600}),
    "brand": {"name": "VERDE FIT", "icon_fill": "#16b7a1", "visor": "#ffb020"},
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Card:
    def __init__(self, spec_dir, canvas, theme):
        self.dir, self.W, self.H, self.t = spec_dir, canvas[0], canvas[1], {**DEFAULT_THEME, **theme}
        self.img = Image.new("RGB", (self.W * S, self.H * S), hex_rgb(self.t["bg"]))
        self.d = ImageDraw.Draw(self.img)
        self.texts, self.layers = [], []

    # ---- units and fonts
    def px(self, v):
        return int(round(v * S))

    def wpx(self, pct):
        return pct / 100 * self.W

    def hpx(self, pct):
        return pct / 100 * self.H

    def heading(self, cap_pct):
        """DIN Condensed sized so a capital letter is cap_pct of the frame height."""
        path = self.t["heading_font"]
        target = self.hpx(cap_pct) * S
        size = target / 0.71
        f = ImageFont.truetype(path, int(size))
        for _ in range(3):  # correct with the real cap height
            h = f.getbbox("H")[3] - f.getbbox("H")[1]
            size *= target / h
            f = ImageFont.truetype(path, int(round(size)))
        return f

    def body(self, size_pct, weight="regular"):
        path, w, size = self.t["body_font"], self.t["body_index"][weight], int(round(self.hpx(size_pct) * S))
        if path.endswith(".ttc"):
            return ImageFont.truetype(path, size, index=w)
        return portable.weighted(path, size, w)

    # ---- records
    def zone(self, box):
        cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
        return ("top" if cy < 33.3 else "middle" if cy < 66.6 else "bottom") + "-" + ("left" if cx < 33.3 else "center" if cx < 66.6 else "right")

    def to_pct(self, bbox):
        x0, y0, x1, y1 = [v / S for v in bbox]
        return [round(x0 / self.W * 100, 1), round(y0 / self.H * 100, 1), round((x1 - x0) / self.W * 100, 1), round((y1 - y0) / self.H * 100, 1)]

    def note_text(self, text, bbox, role, pattern, align, font, size_pct, case, fill, under, origin="designed"):
        box = self.to_pct(bbox)
        self.texts.append({"text": text, "origin": origin, "role": role, "pattern": pattern, "box": box, "zone": self.zone(box), "align": align,
                           "font": font, "size_pct": round(size_pct, 1), "case": case, "fill": fill, "stroke": "none", "under": under})

    def note_layer(self, typ, box, note):
        self.layers.append({"type": typ, "box": [round(v, 1) for v in box], "note": note})

    # ---- drawing
    def text(self, xy, s, font, fill, anchor="ls"):
        self.d.text(xy, s, font=font, fill=hex_rgb(fill), anchor=anchor)
        return self.d.textbbox(xy, s, font=font, anchor=anchor)

    def rrect(self, box_px, radius, fill):
        self.d.rounded_rectangle(box_px, radius=radius, fill=hex_rgb(fill))

    def logo(self):
        b = self.t["brand"]
        h = self.hpx(4.2) * S
        x, y = self.wpx(2.7) * S, self.hpx(2.1) * S
        self.d.ellipse((x, y, x + h, y + h), fill=hex_rgb(b["icon_fill"]))
        self.rrect((x + h * .22, y + h * .40, x + h * .78, y + h * .58), h * .09, b["visor"])
        f = self.heading(2.5)
        bb = self.text((x + h + 12 * S, y + h * .5 + (f.getbbox("H")[3] - f.getbbox("H")[1]) / 2), b["name"], f, self.t["ink"])
        box = self.to_pct((x, y, bb[2], y + h))
        self.note_layer("mark", box, "placeholder brand mark: teal circle with an amber visor slit + wordmark, top-left on every slide (swap for the real handle)")
        self.note_text(b["name"], bb, "watermark", "corner-mark", "left", "DIN Condensed Bold", 3.5, "ALL CAPS", self.t["ink"], "solid card background", origin="mark")

    # ---- art
    def load_art(self, rel, crop_top=None):
        """Normalise the background to white and crop to the content. Returns (RGB array, bbox in the cropped image)."""
        im = cv2.imread(str(self.dir / rel))
        if crop_top:
            im = im[: int(im.shape[0] * crop_top)]
        ring = np.concatenate([im[:12].reshape(-1, 3), im[-12:].reshape(-1, 3), im[:, :12].reshape(-1, 3), im[:, -12:].reshape(-1, 3)])
        gain = np.clip(255.0 / np.maximum(np.median(ring, axis=0), 1), 1.0, 1.15)
        im = np.clip(im.astype(np.float32) * gain, 0, 255)
        # snap the generator's faint near-white background noise to pure white (soft ramp, so real colours and outlines are untouched)
        snap = np.clip((im.min(axis=2) - 226) / 16, 0, 1)[..., None]
        im = (im * (1 - snap) + 255 * snap).astype(np.uint8)
        nonwhite = (im.min(axis=2) < 232)
        ys, xs = np.where(nonwhite)
        pad = 6
        x0, x1, y0, y1 = max(xs.min() - pad, 0), min(xs.max() + pad, im.shape[1] - 1), max(ys.min() - pad, 0), min(ys.max() + pad, im.shape[0] - 1)
        return im[y0:y1 + 1, x0:x1 + 1], (x0, y0)

    def place_art(self, art, box_pct, align="center", bottom_bleed=False):
        """Fit the art inside box_pct ([x, y, w, h] in %), keep the aspect ratio, multiply-blend it onto the card. Returns the placed box in canvas px (at S)."""
        bx, by, bw, bh = self.wpx(box_pct[0]) * S, self.hpx(box_pct[1]) * S, self.wpx(box_pct[2]) * S, self.hpx(box_pct[3]) * S
        h, w = art.shape[:2]
        k = min(bw / w, bh / h)
        nw, nh = int(round(w * k)), int(round(h * k))
        small = cv2.resize(art, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
        x = int(round(bx + (bw - nw) / 2)) if align != "left" else int(round(bx))
        y = int(round(by + bh - nh)) if align in ("bottom-center", "center-bottom") or bottom_bleed else int(round(by + (bh - nh) / 2))
        region = np.asarray(self.img)[y:y + nh, x:x + nw].astype(np.float32)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        out = np.asarray(self.img).copy()
        out[y:y + nh, x:x + nw] = np.clip(region * rgb, 0, 255).astype(np.uint8)
        self.img = Image.fromarray(out)
        self.d = ImageDraw.Draw(self.img)
        return (x, y, x + nw, y + nh), k

    def finish(self, path):
        out = self.img.resize((self.W, self.H), Image.LANCZOS)
        out.save(path)
        return out


def centered_lines(card, lines, top_pct, gap_pct, role):
    y = card.hpx(top_pct) * S
    for ln in lines:
        f = card.heading(ln["cap_pct"])
        cap = f.getbbox("H")[3] - f.getbbox("H")[1]
        bb = card.text((card.W * S / 2, y + cap), ln["text"], f, card.t[ln["color"]], anchor="ms")
        card.note_text(ln["text"], bb, role, "top-headline", "center", "DIN Condensed Bold", ln["cap_pct"] / 0.71, "ALL CAPS", card.t[ln["color"]], "solid card background")
        y += cap + card.hpx(gap_pct) * S


def wrap(card, text, font, max_px):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if card.d.textlength(trial, font=font) <= max_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def accent_line(card, x_pct, y_pct, w_pct=12.6, h_pct=0.45):
    box = (card.wpx(x_pct) * S, card.hpx(y_pct) * S, card.wpx(x_pct + w_pct) * S, card.hpx(y_pct + h_pct) * S)
    card.d.rectangle(box, fill=hex_rgb(card.t["accent"]))
    card.note_layer("accent-line", [x_pct, y_pct, w_pct, h_pct], "short accent underline under the heading")


def slide_cover(card, s):
    card.logo()
    centered_lines(card, s["lines"], s.get("top_pct", 11), s.get("gap_pct", 3), "hook")
    art, _ = card.load_art(s["art"], crop_top=s.get("crop_top"))
    box_px, _ = card.place_art(art, s["art_box"], align="bottom-center", bottom_bleed=True)
    pct = card.to_pct(box_px)
    card.note_layer("mascot", pct, "original mascot Verde, rear double-biceps pose; only the upper trapezius slope is highlighted (red); bleeds off the bottom edge")
    return {"summary": "cover: 2-line problem hook over the mascot's back, upper traps highlighted", "subject_box": pct}


def slide_overview(card, s):
    card.logo()
    f = card.heading(s.get("title_cap", 5.2))
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    top = card.hpx(s.get("title_top", 12.5)) * S
    bb = card.text((card.W * S / 2, top + cap), s["title"], f, card.t["ink"], anchor="ms")
    card.note_text(s["title"], bb, "headline", "numbered-heading", "center", "DIN Condensed Bold", s.get("title_cap", 5.2) / 0.71, "Title Case", card.t["ink"], "solid card background")
    accent_line(card, 50 - 6.3, s.get("line_y", 20.6))
    bf = card.body(2.5)
    lines = wrap(card, s["body"], bf, card.wpx(76) * S)
    asc, desc = bf.getmetrics()
    y = card.hpx(s.get("body_top", 23.5)) * S
    boxes = []
    for ln in lines:
        boxes.append(card.text((card.W * S / 2, y + asc), ln, bf, card.t["body"], anchor="ms"))
        y += (asc + desc) * 1.35
    card.note_text(" ".join(lines), (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)), "body", "top-headline", "center",
                   "Avenir Next Regular", 2.5, "Sentence case", card.t["body"], "solid card background")
    art, _ = card.load_art(s["art"], crop_top=s.get("crop_top"))
    box_px, k = card.place_art(art, s["art_box"])
    pct = card.to_pct(box_px)
    card.note_layer("mascot", pct, "anatomy diagram: mascot back view with the upper trapezius in red and the middle and lower trapezius in yellow")
    # colour targets for the leader lines: centroid of each coloured region, mapped from art pixels to the canvas
    hsv = cv2.cvtColor(art, cv2.COLOR_BGR2HSV)
    masks = {"red": ((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 110) & (hsv[..., 2] > 80),
             "yellow": (hsv[..., 0] > 18) & (hsv[..., 0] < 36) & (hsv[..., 1] > 120) & (hsv[..., 2] > 150)}
    for lab in s["labels"]:
        ys, xs = np.where(masks[lab["target"]])
        tx, ty = box_px[0] + np.median(xs) * k, box_px[1] + np.percentile(ys, lab.get("target_q", 50)) * k
        fill, txt = card.t[lab["color"]], card.t[lab["text_color"]]
        lf = card.heading(2.7)
        capl = lf.getbbox("H")[3] - lf.getbbox("H")[1]
        tw = card.d.textlength(lab["text"], font=lf)
        ph, pw = card.hpx(5.4) * S, tw + 64 * S
        py = card.hpx(lab["y_pct"]) * S
        px0 = card.wpx(3.5) * S if lab["side"] == "left" else card.W * S - card.wpx(3.5) * S - pw
        card.rrect((px0, py, px0 + pw, py + ph), ph / 2, fill)
        bbt = card.text((px0 + pw / 2, py + ph / 2 + capl / 2), lab["text"], lf, card.t[lab["text_color"]], anchor="ms")
        ax, ay = px0 + pw / 2, py + ph
        card.d.line([(ax, ay), (ax, ty), (tx, ty)], fill=hex_rgb(card.t["ink"]), width=4 * S, joint="curve")  # elbow leader: down, then across
        card.d.ellipse((tx - 9 * S, ty - 9 * S, tx + 9 * S, ty + 9 * S), fill=hex_rgb(card.t["ink"]))
        card.note_text(lab["text"], bbt, "label", "callout", "center", "DIN Condensed Bold", 2.7 / 0.71, "ALL CAPS", card.t[lab["text_color"]], f"{lab['color']} pill")
        card.note_layer("callout", card.to_pct((px0, py, px0 + pw, py + ph)), f"{lab['text']} pill with a leader line to the {lab['target']} region")
    return {"summary": "anatomy overview: colour-coded trapezius regions with callouts", "subject_box": pct}


def slide_pick(card, s):
    card.logo()
    nf, tf = card.heading(5.4), card.heading(4.2)
    base = card.hpx(22.6) * S
    bb1 = card.text((card.wpx(10) * S, base), s["number"], nf, card.t["accent"])
    card.note_text(s["number"], bb1, "number", "numbered-heading", "left", "DIN Condensed Bold", 5.4 / 0.71, "n/a", card.t["accent"], "solid card background")
    bb2 = card.text((card.wpx(24.4) * S, base), s["title"], tf, card.t["ink"])
    card.note_text(s["title"], bb2, "headline", "numbered-heading", "left", "DIN Condensed Bold", 4.2 / 0.71, "Title Case", card.t["ink"], "solid card background")
    sf = card.body(2.15, "medium")
    bb3 = card.text((card.wpx(24.4) * S, card.hpx(23.6) * S + sf.getmetrics()[0]), s["sets"], sf, card.t["body"])
    card.note_text(s["sets"], bb3, "label", "numbered-heading", "left", "Avenir Next Medium", 2.15, "Title Case", card.t["body"], "solid card background")
    accent_line(card, 10, 26.9)
    pf = card.body(2.65)
    asc, desc = pf.getmetrics()
    lines = wrap(card, s["body"], pf, card.wpx(64) * S)
    y = card.hpx(31.3) * S
    bbs = []
    for ln in lines:
        bbs.append(card.text((card.wpx(10) * S, y + asc), ln, pf, card.t["body"]))
        y += (asc + desc) * 1.32
    card.note_text(" ".join(lines), (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs), max(b[3] for b in bbs)), "body", "top-headline", "left",
                   "Avenir Next Regular", 2.65, "Sentence case", card.t["body"], "solid card background")
    lf = card.body(2.2, "demibold")
    bb4 = card.text((card.wpx(10) * S, card.hpx(s.get("pick_y", 46.2)) * S + lf.getmetrics()[0]), s["pick_label"], lf, card.t["ink"])
    card.note_text(s["pick_label"], bb4, "label", "callout", "left", "Avenir Next Demi Bold", 2.2, "Sentence case", card.t["ink"], "solid card background")
    boxes = [[3, 50.5, 43, 39], [54, 50.5, 43, 39]]
    cf = card.body(2.4, "medium")
    figs = []
    for art_spec, box in zip(s["options"], boxes):
        art, _ = card.load_art(art_spec["art"])
        box_px, _ = card.place_art(art, box, align="bottom-center")
        pct = card.to_pct(box_px)
        card.note_layer("mascot", pct, f"exercise illustration: {art_spec['caption']}")
        figs.append(pct)
        cx = card.wpx(box[0] + box[2] / 2) * S
        bbc = card.text((cx, card.hpx(93.4) * S), art_spec["caption"], cf, card.t["ink"], anchor="ms")
        card.note_text(art_spec["caption"], bbc, "caption", "callout", "center", "Avenir Next Medium", 2.4, "Title Case", card.t["ink"], "solid card background")
    r = 31 * S
    cx, cy = card.W * S / 2, card.hpx(70) * S
    card.d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hex_rgb(card.t["accent"]))
    of = card.heading(2.7)
    capo = of.getbbox("H")[3] - of.getbbox("H")[1]
    bbo = card.text((cx, cy + capo / 2), "OR", of, card.t["white"], anchor="ms")
    card.note_layer("badge", card.to_pct((cx - r, cy - r, cx + r, cy + r)), "round accent 'OR' badge between the two options")
    card.note_text("OR", bbo, "label", "callout", "center", "DIN Condensed Bold", 2.7 / 0.71, "ALL CAPS", card.t["white"], "accent circle")
    return {"summary": s.get("summary", "muscle pick: explainer + two exercise illustrations"), "subject_box": [3, 50.5, 94, 39]}


SLIDES = {"cover": slide_cover, "overview": slide_overview, "pick": slide_pick}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text())
    out = args.out or args.spec.parent / "output"
    (out / "records").mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(spec["slides"], 1):
        card = Card(args.spec.parent, spec.get("canvas", [1080, 1350]), spec.get("theme", {}))
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
