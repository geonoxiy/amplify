#!/usr/bin/env python3
"""Device screen mockups (MacBooks, iPhones): a client's real website, composited flush into a photo of the device.

Pipeline, one subcommand per step:
  template   inspiration photo → our own look-alike photo (background changed so it can't be traced to the post) whose
             screen shows flat chroma-key green (Nano Banana Pro)
  calibrate  measure the screen in a template: sub-pixel corners, edge bow, screen brightness falloff, glass
             reflections, camera blur and grain → calib.json + check.jpg (corner zooms on a pixel grid)
  render     warp a webshot.py screenshot into the screen, then re-light it with what calibrate measured
  make       url → screenshot(s) at each template's screen size → a mockup per template, in one go

Usage:
  mockup.py template <inspo image> --id <name> [--device air13|iphone15|…] [--extra "…"] [--resolution 4K] [--as-is]
                     [--source <original post>]
  mockup.py calibrate <id> [--device air13] [--corners x,y x,y x,y x,y] [--brightness 1] [--tint 1,1,1] [--glare 1]
  mockup.py render <id|all> <screenshot.png> --out <file.png | dir> [--glare 1] [--bloom auto] [--fit 1080x1350]
  mockup.py make <url> [--templates all | laptops | phones | id …] [--out-dir mockups/out/<site>] [--frame fullscreen|flush]
                 [--fit 1080x1350]
  mockup.py list

How the site sits on the screen:
  MacBook with a notch  fullscreen (default): macOS full-screen, a black strip around the notch and the whole page below
                        it, exactly as a Mac shows it. flush: the page fills the panel and the notch covers its top.
  MacBook, no notch     the page fills the panel.
  iPhone                Safari as it looks mid-scroll: iOS status bar (9:41, signal, wi-fi, battery) in the page's own
                        top colour, the mobile site below, Safari's collapsed address bar with the domain, home indicator.

Templates live in mockups/templates/<id>/: template.png, meta.json (inspo, device, prompt), calib.json, check.jpg.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates

import portable

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "mockups" / "templates"
PY = sys.executable

DEVICES = {  # display aspect = native panel pixels; css = the "looks like" size a site lays out at; dpr = capture scale
    "air13": {"name": "MacBook Air 13-inch, M2 and later (notch)", "kind": "laptop", "native": (2560, 1664), "css": (1470, 956), "dpr": 2, "notch": True, "menubar": 37},
    "air15": {"name": "MacBook Air 15-inch (notch)", "kind": "laptop", "native": (2880, 1864), "css": (1710, 1112), "dpr": 2, "notch": True, "menubar": 37},
    "air13-classic": {"name": "MacBook Air 13-inch, M1 and older (no notch)", "kind": "laptop", "native": (2560, 1600), "css": (1440, 900), "dpr": 2, "notch": False, "menubar": 24},
    "pro14": {"name": "MacBook Pro 14-inch (notch)", "kind": "laptop", "native": (3024, 1964), "css": (1512, 982), "dpr": 2, "notch": True, "menubar": 37},
    "pro16": {"name": "MacBook Pro 16-inch (notch)", "kind": "laptop", "native": (3456, 2234), "css": (1728, 1117), "dpr": 2, "notch": True, "menubar": 37},
    # status_bar: iOS top inset (pt) the page sits below; safari_bar: Safari's collapsed address bar + home indicator zone
    "iphone15": {"name": "iPhone 15 / 16 (Dynamic Island)", "kind": "phone", "native": (1179, 2556), "css": (393, 852), "dpr": 3, "status_bar": 54, "safari_bar": 56},
    "iphone15pm": {"name": "iPhone 15 / 16 Pro Max (Dynamic Island)", "kind": "phone", "native": (1290, 2796), "css": (430, 932), "dpr": 3, "status_bar": 54, "safari_bar": 56},
}

# owner rule (2026-10-01): a template must not be traceable to the post it was inspired by
BACKGROUND_RULE = (
    "Change the background slightly so this photo cannot be traced back to the reference post: keep the overall mood, "
    "colour palette, light direction and time of day, but use a different room and surface, swap the props and decor "
    "for different ones in different places, and copy nothing distinctive from the reference's background. No readable "
    "text, brand names, logos or personal photos anywhere in the scene, and no people's faces."
)
REALISM = (
    "Shot on an iPhone, high resolution: natural phone-camera look, crisp focus on the device, slight grain, "
    "real-world imperfections, not polished CGI, no smoothing or posterised areas."
)
LAPTOP_PROMPT = (
    "Recreate this reference photo as a new, original photo to use as a product mockup template. Keep the same kind of "
    "laptop (same model, colour and size), the same camera angle, height, tilt and distance, the same framing and crop, "
    "and the same lighting mood and time of day.\n\n"
    "The laptop is switched on and its display is filled edge to edge with one flat, uniform, pure chroma-key green "
    "(#00FF00), exactly like a green screen used for compositing. Nothing else is on the display: no wallpaper, no menu "
    "bar, no dock, no icons, no widgets, no windows, no text, no cursor. The display's thin black border stays black and "
    "the camera notch (if this laptop has one) stays black. Keep nothing of the reference's screen: not one part of its "
    "wallpaper, stickers, pictures, widgets or windows survives. Only subtle, soft glass reflections from the room lights "
    "on the display, never a reflected square, rectangle or patch. The green does not tint the keyboard, the bezel or the room; everything else is lit only by the room's "
    "own light, as in the reference. The whole display is visible and nothing covers any part of it.\n\n"
    + BACKGROUND_RULE + "\n\n" + REALISM
)
PHONE_PROMPT = (
    "Recreate this reference photo as a new, original photo to use as a phone mockup template. Keep the same kind of "
    "phone (same model and size, same case style and colour), the same camera angle, tilt, distance and framing, and the "
    "same lighting mood. Keep how the phone is shown: if it lies on a surface in the reference, it lies on a surface here "
    "too, seen from the same angle, and no hand appears; if a hand holds it, keep a similar natural hand pose, holding the "
    "phone by its edges.\n\n"
    "The phone is switched on and its screen is filled edge to edge with one flat, uniform, pure chroma-key green "
    "(#00FF00), exactly like a green screen used for compositing. Nothing else is on the screen: no lock screen clock, no "
    "date, no status bar, no icons, no widgets, no notifications, no text. The Dynamic Island (the black pill at the top "
    "of the screen) stays black and the screen's thin black border stays black. Keep nothing of the reference's screen: "
    "not one part of its wallpaper, clock, pictures or widgets survives. Only subtle, soft glass reflections on the "
    "screen, never a reflected square, rectangle or patch. No finger or object covers any part of the screen. The green does not tint the hand, the case or the "
    "surroundings.\n\n"
    + BACKGROUND_RULE + "\n\n" + REALISM
)

ASPECTS = {"1:1": 1, "4:5": 4 / 5, "3:4": 3 / 4, "2:3": 2 / 3, "9:16": 9 / 16, "5:4": 5 / 4, "4:3": 4 / 3, "3:2": 3 / 2, "16:9": 16 / 9}


def tdir(tid):
    return TEMPLATES / tid


def load_meta(tid):
    f = tdir(tid) / "meta.json"
    if not f.exists():
        sys.exit(f"no template {tid!r} (expected {f})")
    return json.loads(f.read_text())


def template(a):
    if a.device not in DEVICES:
        sys.exit(f"unknown device {a.device}; one of {', '.join(DEVICES)}")
    d = tdir(a.id)
    d.mkdir(parents=True, exist_ok=True)
    w, h = Image.open(a.inspo).size
    aspect = min(ASPECTS, key=lambda k: abs(ASPECTS[k] - w / h))
    out = d / "template.png"
    if a.as_is:  # your own photo: ideally the laptop showing a full-screen #00FF00 image, or any photo + --corners later
        Image.open(a.inspo).convert("RGB").save(out)
        meta = {"id": a.id, "inspo": str(Path(a.inspo).resolve()), "device": a.device, "aspect": None, "prompt": None,
                "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        (d / "meta.json").write_text(json.dumps(meta, indent=1))
        print(f"template (photo as is) → {out}\nnext: mockup.py calibrate {a.id}  (add --corners if the screen is not green)")
        return
    base = PHONE_PROMPT if DEVICES[a.device]["kind"] == "phone" else LAPTOP_PROMPT
    prompt = base + (f"\n\n{a.extra}" if a.extra else "")
    subprocess.run([PY, str(ROOT / "tools" / "kie.py"), "image", "--model", "nbp", "--prompt", prompt, "--ref", str(a.inspo),
                    "--aspect", aspect, "--resolution", a.resolution, "--out", str(out), "--run", str(d),
                    "--run-cap", str(a.run_cap)], check=True)
    rel = lambda f: str(Path(f).resolve().relative_to(ROOT))  # noqa: E731
    meta = {"id": a.id, "inspo": rel(a.source or a.inspo), "reference": rel(a.inspo), "device": a.device,
            "aspect": aspect, "prompt": prompt, "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"template → {out}\nnext: mockup.py calibrate {a.id}")


# ---------------------------------------------------------------- colour

def to_lin(s):
    """sRGB 0..1 → linear light. Blur, resampling and reflections are only physically right in linear light."""
    return np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4).astype(np.float32)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def load_lin(path):
    return to_lin(np.asarray(Image.open(path).convert("RGB"), np.float32) / 255)


def key(L):
    """Green-screen key: green minus the larger of red and blue. A glass reflection adds about the same light to all
    three channels, so it cancels out here and a glare patch still keys as screen."""
    return L[..., 1] - np.maximum(L[..., 0], L[..., 2])


# ---------------------------------------------------------------- geometry
# The display is the unit square (u, v): u left → right, v top → bottom. corners are TL, TR, BR, BL in image pixels.
# A pure homography maps the square onto the photo; a small per-edge bow (lens barrel/pincushion, or a slightly curved
# edge in a generated photo) is added on top as a Coons-patch displacement that is zero at the corners.

EDGES = ("top", "right", "bottom", "left")


def homography(corners):
    src = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
    return cv2.getPerspectiveTransform(src, np.float32(corners)).astype(np.float64)


def apply_h(m, x, y):
    d = m[2, 0] * x + m[2, 1] * y + m[2, 2]
    return (m[0, 0] * x + m[0, 1] * y + m[0, 2]) / d, (m[1, 0] * x + m[1, 1] * y + m[1, 2]) / d


def bow_disp(cal, u, v):
    u, v = np.clip(u, 0, 1), np.clip(v, 0, 1)
    dx, dy = np.zeros_like(u), np.zeros_like(u)
    for name, t, w in (("top", u, 1 - v), ("bottom", u, v), ("left", v, 1 - u), ("right", v, u)):
        b = cal["bow"][name]
        if b:
            m = 4 * b * t * (1 - t) * w
            dx += m * cal["normal"][name][0]
            dy += m * cal["normal"][name][1]
    return dx, dy


def uv_to_image(cal, u, v):
    x, y = apply_h(np.array(cal["H"]), u, v)
    dx, dy = bow_disp(cal, u, v)
    return x + dx, y + dy


def image_to_uv(cal, x, y):
    hi = np.linalg.inv(np.array(cal["H"]))
    u, v = apply_h(hi, x, y)
    if any(cal["bow"].values()):
        for _ in range(4):  # fixed point: the bow is a few px at most, so this converges in 2-3 steps
            dx, dy = bow_disp(cal, u, v)
            u, v = apply_h(hi, x - dx, y - dy)
    return u, v


def outline(cal, n=400):
    t = np.linspace(0, 1, n)
    o, z = np.ones_like(t), np.zeros_like(t)
    u = np.concatenate([t, o, t[::-1], z])
    v = np.concatenate([z, t, o, t[::-1]])
    return np.stack(uv_to_image(cal, u, v), -1)


def screen_box(cal, size, pad):
    pts = outline(cal, 100)
    w, h = size
    x0, y0 = np.floor(pts.min(0) - pad).astype(int)
    x1, y1 = np.ceil(pts.max(0) + pad).astype(int)
    return max(x0, 0), max(y0, 0), min(x1, w), min(y1, h)


def grid(box, ss=1):
    x0, y0, x1, y1 = box
    xs = x0 + (np.arange((x1 - x0) * ss) + 0.5) / ss - 0.5
    ys = y0 + (np.arange((y1 - y0) * ss) + 0.5) / ss - 0.5
    return np.meshgrid(xs, ys)


def estimate_aspect(c, w, h):
    """Width/height of the real rectangle behind a photographed quad, assuming the lens centre is the image centre
    (Zhang & He, whiteboard scanning). A check on the template, not used for the warp."""
    u0, v0 = w / 2, h / 2
    m1, m2, m3, m4 = [np.array([x, y, 1.0]) for x, y in (c[0], c[1], c[3], c[2])]  # TL, TR, BL, BR
    k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
    k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)
    n2, n3 = k2 * m2 - m1, k3 * m3 - m1
    if abs(n2[2] * n3[2]) < 1e-12:
        return float(np.hypot(n2[0], n2[1]) / np.hypot(n3[0], n3[1])), None
    f2 = -((n2[0] * n3[0] - (n2[0] * n3[2] + n2[2] * n3[0]) * u0 + n2[2] * n3[2] * u0 ** 2)
           + (n2[1] * n3[1] - (n2[1] * n3[2] + n2[2] * n3[1]) * v0 + n2[2] * n3[2] * v0 ** 2)) / (n2[2] * n3[2])
    if f2 <= 0:
        return None, None
    f = np.sqrt(f2)
    ai = np.linalg.inv(np.array([[f, 0, u0], [0, f, v0], [0, 0, 1]]))
    q = ai.T @ ai
    return float(np.sqrt((n2 @ q @ n2) / (n3 @ q @ n3))), float(f)


class Edge:
    """One display edge, measured on a visible stretch a → b: offset e(s) along the outward normal n, s ∈ [0, 1].
    Outside [0, 1] it continues straight along its end tangent, so corners off the photo extrapolate sanely."""

    def __init__(self, a, b, n, coef):
        self.a, self.b, self.n, self.coef = a, b, n, coef
        self.dc = np.polyder(coef) if len(coef) > 1 else np.zeros(1)

    def point(self, s):
        sc = np.clip(s, 0, 1)
        return self.a + s * (self.b - self.a) + (np.polyval(self.coef, sc) + np.polyval(self.dc, sc) * (s - sc)) * self.n

    def tangent(self, s):
        return (self.b - self.a) + np.polyval(self.dc, np.clip(s, 0, 1)) * self.n

    def param(self, p):
        d = self.b - self.a
        return float(np.dot(p - self.a, d) / np.dot(d, d))


def line_x(p1, d1, p2, d2):
    m = np.array([d1, -d2]).T
    t = np.linalg.solve(m, p2 - p1)
    return p1 + t[0] * d1


def corner(e1, e2):
    p = line_x(e1.point(0.5), e1.tangent(0.5), e2.point(0.5), e2.tangent(0.5))
    for _ in range(8):  # Newton on the two curves' tangents
        s1, s2 = e1.param(p), e2.param(p)
        p = line_x(e1.point(s1), e1.tangent(s1), e2.point(s2), e2.tangent(s2))
    return p


def rough_edges(k, kmax, kind="laptop"):
    """The 4 straight sides of the green region's convex hull (the hull bridges the notch). Sides that run along the
    photo's border are dropped: a display can run off the frame, and then its corner is rebuilt from the two edge lines."""
    h, w = k.shape
    # threshold at the histogram valley between bezel (≈0) and panel: a panel can fade to 40% of its peak toward one
    # side (viewing angle), so a fixed fraction of the peak can cut the dim side off and fake an edge there
    hist, bins = np.histogram(k / kmax, bins=50, range=(0, 1))
    lo, hi = 3, 23  # search 0.06 .. 0.46
    thr = bins[lo + int(np.argmin(hist[lo:hi]))] + 0.01
    mask = cv2.morphologyEx((k > thr * kmax).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n < 2:
        sys.exit("no green display found; generate the template again or pass --corners")
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    if stats[big, cv2.CC_STAT_AREA] < 0.01 * h * w:
        sys.exit("the green area is tiny; is the display really chroma green? pass --corners for a non-green screen")
    comp = (lab == big).astype(np.uint8)
    cnt = max(cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
    hull = cv2.convexHull(cnt)
    poly = cv2.approxPolyDP(hull, 0.003 * cv2.arcLength(hull, True), True)[:, 0, :].astype(float)
    centre = poly.mean(0)

    def along_border(p, q):
        return any((abs(p[i] - lim) < 3 and abs(q[i] - lim) < 3) for i, lim in ((0, 0), (0, w - 1), (1, 0), (1, h - 1)))

    def angle(d1, d2):
        c = abs(np.dot(d1, d2)) / (np.linalg.norm(d1) * np.linalg.norm(d2))
        return np.degrees(np.arccos(np.clip(c, -1, 1)))

    segs = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        if along_border(p, q) or np.hypot(*(q - p)) < 0.04 * min(h, w):
            continue  # off-frame side, or a rounded-corner chamfer
        if segs and angle(segs[-1][1] - segs[-1][0], q - p) < 6:
            segs[-1][1] = q
        else:
            segs.append([p, q])
    if len(segs) > 4 and angle(segs[-1][1] - segs[-1][0], segs[0][1] - segs[0][0]) < 6:
        segs[0][0] = segs.pop()[0]
    if len(segs) > 4:  # a phone's big rounded corners leave chord pieces between the sides: keep the 4 longest, in order
        keep = sorted(np.argsort([-np.hypot(*(q - p)) for p, q in segs])[:4])
        segs = [segs[i] for i in keep]
    if len(segs) != 4:
        sys.exit(f"found {len(segs)} straight display edges, expected 4; pass --corners")
    best, names = -9, None
    import itertools
    normals = []
    for p, q in segs:
        d = (q - p) / np.linalg.norm(q - p)
        nv = np.array([d[1], -d[0]])
        normals.append(nv if np.dot(nv, (p + q) / 2 - centre) > 0 else -nv)
    up = np.array([0.0, -1.0])
    if kind == "phone":  # portrait screen, possibly tilted or upside down: "up" is the short side with the Dynamic Island
        lens = [np.hypot(*(q - p)) for p, q in segs]
        pair = (0, 2) if lens[0] + lens[2] < lens[1] + lens[3] else (1, 3)
        long_len = max(lens)

        def island(i):
            p, q = segs[i]
            m, d = (p + q) / 2, (q - p) / np.linalg.norm(q - p)
            pts = [m - normals[i] * t * long_len + d * o * lens[i] for t in np.linspace(0.01, 0.06, 12)
                   for o in np.linspace(-0.25, 0.25, 15)]
            vals = [k[int(np.clip(y, 0, h - 1)), int(np.clip(x, 0, w - 1))] for x, y in pts]
            return float(np.mean(np.array(vals) < 0.3 * kmax))
        up = normals[max(pair, key=island)]
    right = np.array([-up[1], up[0]])
    outward = {"top": up, "right": right, "bottom": -up, "left": -right}
    for perm in itertools.permutations(EDGES):
        score = sum(np.dot(normals[i], outward[nm]) for i, nm in enumerate(perm))
        if score > best:
            best, names = score, perm
    return {nm: (np.array(segs[i][0]), np.array(segs[i][1]), normals[i]) for i, nm in enumerate(names)}, comp


def robust_fit(s, e, deg):
    keep = np.ones(len(s), bool)
    for it in range(7):
        d = deg if it >= 3 else 1
        c = np.polyfit(s[keep], e[keep], d)
        r = e - np.polyval(c, s)
        mad = 1.4826 * np.median(np.abs(r[keep])) + 1e-6
        keep = np.abs(r) < max(3 * mad, 0.6 if it >= 3 else 2.0)
        if keep.sum() < 8:
            sys.exit("too few clean samples along a display edge; pass --corners")
    return c, keep


def refine_edge(kl, a, b, n, kmax, reach, span=(0.06, 0.94)):
    """Sub-pixel edge: sample the key across the edge (0.25 px steps) at ~every 5 px along it, take the 50% crossing.
    Samples where the inside is not bright green (the notch, a sticker) are rejected, then outliers are dropped by a
    robust line → quadratic fit. Also returns the 10-90% edge widths, which measure the camera's blur."""
    h, w = kl.shape
    length = np.hypot(*(b - a))
    s = np.linspace(span[0], span[1], max(40, int(length / 5)))
    t = np.arange(-reach, reach + 1e-6, 0.25)
    p = a[None, :] + s[:, None] * (b - a)[None, :]
    q = p[:, None, :] + t[None, :, None] * n[None, None, :]
    ok = (q[..., 0].min(1) >= 0) & (q[..., 0].max(1) <= w - 1) & (q[..., 1].min(1) >= 0) & (q[..., 1].max(1) <= h - 1)
    prof = map_coordinates(kl, [q[..., 1].ravel(), q[..., 0].ravel()], order=1, mode="nearest").reshape(q.shape[:2])
    quarter = len(t) // 4
    gin, gout = np.median(prof[:, :quarter], 1), np.median(prof[:, -quarter:], 1)
    con = gin - gout
    ok &= con > 0.3 * kmax
    f = (prof - gout[:, None]) / np.maximum(con[:, None], 1e-6)
    ss, es, widths = [], [], []
    for i in np.where(ok)[0]:
        fi = f[i]
        cross = np.where((fi[:-1] >= 0.5) & (fi[1:] < 0.5))[0]
        if not len(cross):
            continue
        j = cross[np.argmin(np.abs(t[cross]))]
        ss.append(s[i])
        es.append(t[j] + (fi[j] - 0.5) / (fi[j] - fi[j + 1]) * 0.25)
        j9, j1 = j, j + 1
        while j9 > 0 and fi[j9] < 0.9:
            j9 -= 1
        while j1 < len(t) - 1 and fi[j1] > 0.1:
            j1 += 1
        widths.append(t[j1] - t[j9])
    ss, es, widths = np.array(ss), np.array(es), np.array(widths)
    if len(ss) < 8:
        sys.exit("could not measure a display edge; pass --corners")
    coef, keep = robust_fit(ss, es, 2)
    return coef, ss, es, keep, widths[keep]


# ---------------------------------------------------------------- photometry
# Linear model of every display pixel in the template: L = a·E·(kr, 1, kb) + a·ρ + (1 − a)·bezel
#   a   coverage (1 inside the panel, 0 on the bezel/notch, fractional on the anti-aliased edge)
#   E   how bright the panel shows green there: exposure × the panel's own falloff, smooth, fitted as a cubic in (u, v)
#   kr, kb  the green's small red/blue leak
#   ρ   the glass reflection (room lights, a window), added on top of whatever the panel shows

def basis(u, v):
    u, v = np.clip(u, -0.05, 1.05), np.clip(v, -0.05, 1.05)
    return np.stack([np.ones_like(u), u, v, u * u, u * v, v * v, u ** 3, u * u * v, u * v * v, v ** 3], -1)


def unmix(ls, kr, kb):
    """Split a (smoothed) screen pixel into green emission E and reflection ρ per channel."""
    rg = (ls[..., 0] + ls[..., 2] - (kr + kb) * ls[..., 1]) / (2 - kr - kb)
    e = ls[..., 1] - rg
    rho = np.stack([ls[..., 0] - kr * e, rg, ls[..., 2] - kb * e], -1)
    return e, np.clip(rho, 0, None)


def screen_model(L, cal, box):
    """Per-pixel maps over the box: u, v, coverage a, emission E, reflection ρ (filled in from the clean interior
    under the anti-aliased edge, where the bezel would pollute it)."""
    x0, y0, x1, y1 = box
    gx, gy = grid(box)
    u, v = image_to_uv(cal, gx, gy)
    e_fit = (basis(u, v) @ np.array(cal["E_poly"])).astype(np.float32)
    e_fit = np.maximum(e_fit, 1e-3)
    sub = L[y0:y1, x0:x1]
    if cal["mode"] == "plain":  # a non-green screen with hand-placed corners: geometry only
        a = poly_mask(cal, box)
        return dict(u=u, v=v, a=a, E=np.ones_like(a), rho=np.zeros_like(sub))
    kr, kb = cal["kr"], cal["kb"]
    a = np.clip(key(sub) / (e_fit * (1 - max(kr, kb))), 0, 1)
    a = np.clip((a - 0.06) / 0.88, 0, 1)
    inside = (u > -0.01) & (u < 1.01) & (v > -0.01) & (v < 1.01)
    pad = 2 + 3 * cal["psf_sigma"]
    near = cv2.dilate(inside.astype(np.uint8), np.ones((2 * int(pad) + 1,) * 2, np.uint8)) > 0
    a *= near  # green elsewhere in the room is not screen
    core = (u > 0.01) & (u < 0.99) & (v > 0.01) & (v < 0.99)
    holes = ((a < 0.5) & core).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(holes, connectivity=8)
    area = core.sum()
    for i in range(1, n):  # dust specks in the generated green: fill. Anything touching the edge (a notch, a phone's
        x, y, bw, bh, ar = stats[i]  # rounded corner) or as big as a Dynamic Island is real and stays
        touches = not core[max(y - 2, 0):y + bh + 2, max(x - 2, 0):x + bw + 2].all()
        if not touches and ar < 0.003 * area:
            a[lab == i] = 1
    # a lit panel is there or it is not: inside the display, a patch where the generated green is just a bit darker
    # is still screen, not a see-through hole. Partial coverage is kept only on the outer edge (anti-aliasing) and
    # around real cut-outs (the notch: key near zero)
    m = int(np.ceil(pad)) + 1
    k5 = np.ones((2 * m + 1,) * 2, np.uint8)
    deep = cv2.erode(inside.astype(np.uint8), k5) > 0
    cutout = cv2.dilate(((a < 0.3) & deep).astype(np.uint8), k5) > 0
    a = np.where(deep & ~cutout, 1, a)
    # reflections are out of focus anyway: a blur scaled to the photo keeps the green's grain and any fine texture a
    # generated photo drew into its "reflection" out of the glare layer
    ls = cv2.GaussianBlur(sub, (0, 0), max(2.0, 0.0015 * max(L.shape[:2])))
    _, rho = unmix(ls, kr, kb)
    # measure reflections a few px inside the edge only: generated photos often draw a bright sharpening halo along
    # the panel border, which is not glass glare; the edge band takes the reflection from just inside it instead
    k9 = np.ones((2 * (m + 3) + 1,) * 2, np.uint8)
    solid = ((a > 0.97) & (cv2.erode(inside.astype(np.uint8), k9) > 0) & ~cutout).astype(np.float32)
    num = cv2.GaussianBlur(rho * solid[..., None], (0, 0), m + 3)
    den = cv2.GaussianBlur(solid, (0, 0), m + 3)[..., None]
    rho = np.where(solid[..., None] > 0, rho, num / np.maximum(den, 1e-4))
    rho *= (a > 0)[..., None]
    return dict(u=u, v=v, a=a.astype(np.float32), E=e_fit, rho=rho.astype(np.float32))


def poly_mask(cal, box, ss=4):
    x0, y0, x1, y1 = box
    m = Image.new("L", ((x1 - x0) * ss, (y1 - y0) * ss), 0)
    pts = [((x - x0 + 0.5) * ss, (y - y0 + 0.5) * ss) for x, y in outline(cal)]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.asarray(m.resize((x1 - x0, y1 - y0), Image.BOX), np.float32) / 255


def top_cutout(model):
    """Where the photo's notch or Dynamic Island really is, as [u0, u1, v0, v1] on the panel, or None. Generated
    photos often draw it lower or bigger than the real device, so the status bar / menu-bar strip is laid out around
    this measurement rather than the spec."""
    u, v, a = model["u"], model["v"], model["a"]
    cut = ((a < 0.5) & (u > 0.2) & (u < 0.8) & (v > 0.004) & (v < 0.15)).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cut, connectivity=8)
    if n < 2:
        return None
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    if stats[i, cv2.CC_STAT_AREA] < 50:
        return None
    m = lab == i
    return [float(u[m].min()), float(u[m].max()), float(min(v[m].min(), 0.0) if v[m].min() < 0.01 else v[m].min()),
            float(v[m].max())]


def noise_sigma(gray):
    """Immerkær's estimator, median form: grain std of an image, in the same units as the input."""
    r = cv2.filter2D(gray.astype(np.float32), -1, np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], np.float32))
    return float(1.4826 * np.median(np.abs(r[2:-2, 2:-2])) / 6)


# ---------------------------------------------------------------- calibrate

def calibrate(a):
    meta = load_meta(a.id)
    d = tdir(a.id)
    device = a.device or meta["device"]
    if device not in DEVICES:
        sys.exit(f"unknown device {device}")
    if device != meta["device"]:  # the generated photo can show a different model than the inspiration did
        meta["device"] = device
        (d / "meta.json").write_text(json.dumps(meta, indent=1))
    dev = DEVICES[device]
    srgb = np.asarray(Image.open(d / "template.png").convert("RGB"), np.float32) / 255
    L = to_lin(srgb)
    h, w = L.shape[:2]
    kl = key(L)
    kmax = float(np.percentile(kl, 99.5))
    cal = {"device": device, "size": [w, h], "display_aspect": dev["native"][0] / dev["native"][1],
           "bow": {e: 0.0 for e in EDGES}, "normal": {}, "brightness": a.brightness, "tint": a.tint, "glare": a.glare}
    old = d / "calib.json"
    if old.exists():  # keep hand-tuned looks across re-calibration, unless set again now
        prev = json.loads(old.read_text())
        cal.update({k: prev[k] for k in ("brightness", "tint", "glare") if k in prev and cal[k] is None})
    cal["brightness"] = cal["brightness"] if cal["brightness"] is not None else 1.0
    cal["tint"] = cal["tint"] if cal["tint"] is not None else [1.0, 1.0, 1.0]
    cal["glare"] = cal["glare"] if cal["glare"] is not None else 1.0
    samples = {}
    if a.corners:
        corners = [tuple(map(float, c.split(","))) for c in a.corners]
        cal["corners"] = [list(c) for c in corners]
        cal["H"] = homography(corners).tolist()
        for i, nm in enumerate(EDGES):
            p, q = np.array(corners[i]), np.array(corners[(i + 1) % 4])
            dd = (q - p) / np.linalg.norm(q - p)
            cal["normal"][nm] = [dd[1], -dd[0]]
        cal["psf_sigma"] = 0.8
    else:
        rough, _ = rough_edges(kl, kmax, dev["kind"])
        span = (0.1, 0.9) if dev["kind"] == "phone" else (0.06, 0.94)  # keep clear of a phone's rounded corners
        reach = float(np.clip(0.008 * min(h, w), 6, 24))
        edges, widths = {}, []
        for nm in EDGES:
            p, q, n = rough[nm]
            coef, s, e, keep, wd = refine_edge(kl, p, q, n, kmax, reach, span)
            edges[nm] = Edge(p, q, n, coef)
            samples[nm] = (edges[nm], s, e, keep)
            widths.extend(wd)
        tl, tr = corner(edges["left"], edges["top"]), corner(edges["top"], edges["right"])
        br, bl = corner(edges["right"], edges["bottom"]), corner(edges["bottom"], edges["left"])
        corners = [tl, tr, br, bl]
        cal["corners"] = [[float(x), float(y)] for x, y in corners]
        cal["H"] = homography(corners).tolist()
        for i, nm in enumerate(EDGES):
            c0, c1 = corners[i], corners[(i + 1) % 4]
            chord = c1 - c0
            nc = np.array([chord[1], -chord[0]]) / np.linalg.norm(chord)
            cal["normal"][nm] = nc.tolist()
            e = edges[nm]
            mid = (c0 + c1) / 2
            sm = e.param(mid)
            vis = np.linalg.norm(e.b - e.a) / np.linalg.norm(chord)
            if len(e.coef) == 3 and 0.1 < sm < 0.9 and vis > 0.4:
                bow = float(np.dot(e.point(sm) - mid, nc))
                bow = float(np.clip(bow, -0.015 * np.linalg.norm(chord), 0.015 * np.linalg.norm(chord)))
                cal["bow"][nm] = round(bow, 2) if abs(bow) >= 0.3 else 0.0
        cal["psf_sigma"] = float(np.clip(np.median(widths) / 2.563, 0.4, 3.0))
    cal["visible"] = [bool(0 <= x < w and 0 <= y < h) for x, y in cal["corners"]]
    asp, foc = estimate_aspect(np.array(cal["corners"]), w, h)
    if foc and not 0.25 <= foc / np.hypot(w, h) <= 2.0:
        asp = None  # nearly parallel edges: the lens can't be solved for, so neither can the shape (a phone is ~0.3-1.2)
    cal["measured_aspect"], cal["focal_px"] = asp, foc

    # photometry: fit E over the clean interior, then measure grain and scene darkness
    box = screen_box(cal, (w, h), 4)
    x0, y0, x1, y1 = box
    gx, gy = grid(box)
    u, v = image_to_uv(cal, gx, gy)
    sub = L[y0:y1, x0:x1]
    ksub = key(sub)
    core = (u > 0.03) & (u < 0.97) & (v > 0.03) & (v < 0.97)
    green = float(np.median(ksub[core])) > 0.08 if core.any() else False
    cal["mode"] = "green" if green else "plain"
    if green:
        strong = core & (ksub > 0.5 * np.percentile(ksub[core], 95))
        ls = cv2.GaussianBlur(sub, (0, 0), 1.2)
        ratio_r = ls[..., 0][strong] / np.maximum(ls[..., 1][strong], 1e-4)
        ratio_b = ls[..., 2][strong] / np.maximum(ls[..., 1][strong], 1e-4)
        kr, kb = float(np.percentile(ratio_r, 5)), float(np.percentile(ratio_b, 5))
        e, _ = unmix(ls, kr, kb)
        idx = np.flatnonzero(strong.ravel())
        idx = idx[:: max(1, len(idx) // 150000)]
        bu, bv, be = u.ravel()[idx], v.ravel()[idx], e.ravel()[idx]
        keep = np.ones(len(idx), bool)
        for _ in range(4):
            coef = np.linalg.lstsq(basis(bu[keep], bv[keep]), be[keep], rcond=None)[0]
            r = be - basis(bu, bv) @ coef
            sd = 1.4826 * np.median(np.abs(r[keep])) + 1e-6
            keep = np.abs(r) < 2.5 * sd
        cal.update(kr=kr, kb=kb, E_poly=coef.tolist(), green_level=float(np.median(be)))
        gch = srgb[y0:y1, x0:x1, 1]
        clipped = float(np.median(gch[core])) > 0.97
        scene = noise_sigma(srgb.mean(-1))
        panel = scene if clipped else noise_sigma(np.where(core, gch, np.median(gch[core])))
        cal["noise"] = max(panel, 0.8 * scene)  # a flat generated green can read as noiseless; the camera's grain is not
    else:
        cal.update(kr=0.0, kb=0.0, E_poly=[1.0] + [0.0] * 9, green_level=1.0, noise=noise_sigma(srgb.mean(-1)))
    model = screen_model(L, cal, box)
    if dev["kind"] == "laptop" and not a.device and cal["mode"] == "green":
        # the generated photo may show a newer or older MacBook than the inspiration did: a notch decides the panel shape
        mid = (model["u"] > 0.47) & (model["u"] < 0.53) & (model["v"] > 0.004) & (model["v"] < 0.018)
        notch = bool(mid.any() and float((model["a"][mid] < 0.5).mean()) > 0.6)
        if notch != dev["notch"]:
            device = "air13" if notch else "air13-classic"
            dev = DEVICES[device]
            print(f"  {'a notch' if notch else 'no notch'} in the photo: device set to {device}")
            cal["device"], cal["display_aspect"] = device, dev["native"][0] / dev["native"][1]
            meta["device"] = device
            (d / "meta.json").write_text(json.dumps(meta, indent=1))
    a_full = np.zeros((h, w), np.float32)
    a_full[y0:y1, x0:x1] = model["a"]
    lum = L @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    cal["scene_luma"] = float(np.median(lum[a_full < 0.01]))
    cal["coverage"] = float(model["a"][core].mean()) if core.any() else 0.0
    cal["cutout"] = top_cutout(model)
    cal["calibrated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (d / "calib.json").write_text(json.dumps(cal, indent=1))
    Image.fromarray((a_full * 255).astype(np.uint8)).save(d / "matte.png")
    check_image(d, srgb, cal, samples, a_full)
    da = cal["display_aspect"]
    vis = ", ".join(f"{nm} {'in frame' if v else 'OFF FRAME (rebuilt from edges)'}" for nm, v in zip(("TL", "TR", "BR", "BL"), cal["visible"]))
    print(f"{a.id}: {cal['mode']} screen, {device}")
    print("  corners " + "  ".join(f"({x:.1f}, {y:.1f})" for x, y in cal["corners"]) + f"   [{vis}]")
    print(f"  edge bow px {cal['bow']}   camera blur sigma {cal['psf_sigma']:.2f}px   grain {cal['noise'] * 255:.2f}/255")
    if not asp:
        print("  display aspect from the photo: not measurable (perspective too flat); the device preset is used as is")
    else:
        flag = "ok" if abs(asp - da) / da < 0.08 else "CHECK: the photo's display looks a different shape from this device"
        print(f"  display aspect from the photo {asp:.3f} vs {device} {da:.3f}: {flag}")
    if green:
        print(f"  green level {cal['green_level']:.2f} (1 = full brightness), leak r {cal['kr']:.3f} b {cal['kb']:.3f}, "
              f"scene luma {cal['scene_luma']:.3f}, panel coverage {cal['coverage']:.1%}")
    print(f"  → {d / 'calib.json'}, {d / 'check.jpg'}")


def check_image(d, srgb, cal, samples, a_full):
    """Overview with the fitted outline + corner coordinates, and an 8x zoom of each corner on a pixel grid."""
    h, w = srgb.shape[:2]
    img = Image.fromarray((srgb * 255).astype(np.uint8))
    scale = 1100 / h
    pad = 160
    ov = Image.new("RGB", (round(w * scale) + 2 * pad, 1100 + 2 * pad), (40, 40, 40))
    ov.paste(img.resize((round(w * scale), 1100), Image.LANCZOS), (pad, pad))
    dr = ImageDraw.Draw(ov)
    font = ImageFont.load_default(size=18)
    pts = [(x * scale + pad, y * scale + pad) for x, y in outline(cal)]
    dr.line(pts + [pts[0]], fill=(0, 230, 255), width=2)
    for nm, (e, s, off, keep) in samples.items():
        for si, oi, k in zip(s, off, keep):
            x, y = e.a + si * (e.b - e.a) + oi * e.n
            dr.point((x * scale + pad, y * scale + pad), fill=(255, 220, 0) if k else (255, 0, 160))
    for (x, y), nm, vis in zip(cal["corners"], ("TL", "TR", "BR", "BL"), cal["visible"]):
        cx, cy = x * scale + pad, y * scale + pad
        cx, cy = np.clip(cx, 6, ov.width - 6), np.clip(cy, 6, ov.height - 6)
        dr.line([(cx - 10, cy), (cx + 10, cy)], fill=(255, 40, 40), width=2)
        dr.line([(cx, cy - 10), (cx, cy + 10)], fill=(255, 40, 40), width=2)
        dr.text((cx + 8, cy + 6), f"{nm} {x:.1f},{y:.1f}" + ("" if vis else " (off frame)"), fill=(255, 80, 80), font=font)
    half = zoom_half(cal, (w, h))
    zoom = max(2, 480 // (2 * half))
    insets = []
    for (x, y), nm in zip(cal["corners"], ("TL", "TR", "BR", "BL")):
        fx, fy = np.clip(x, half, w - half - 1), np.clip(y, half, h - half - 1)  # off-frame: nearest point in frame
        bx, by = int(round(fx)) - half, int(round(fy)) - half
        crop = img.crop((bx, by, bx + 2 * half, by + 2 * half)).resize((2 * half * zoom,) * 2, Image.NEAREST)
        cd = ImageDraw.Draw(crop)
        for i in range(0, 2 * half * zoom, zoom if zoom >= 6 else 10 ** 9):  # a pixel grid only when cells are visible
            cd.line([(i, 0), (i, crop.height)], fill=(90, 90, 90))
            cd.line([(0, i), (crop.width, i)], fill=(90, 90, 90))
        ol = outline(cal, 4000)
        sel = (ol[:, 0] > bx - 2) & (ol[:, 0] < bx + 2 * half + 2) & (ol[:, 1] > by - 2) & (ol[:, 1] < by + 2 * half + 2)
        for run in np.split(np.flatnonzero(sel), np.flatnonzero(np.diff(np.flatnonzero(sel)) > 1) + 1):
            if len(run) > 1:  # each edge separately: the outline array starts and ends at TL
                cd.line([((px - bx + 0.5) * zoom, (py - by + 0.5) * zoom) for px, py in ol[run]], fill=(0, 230, 255), width=2)
        if 0 <= x - bx < 2 * half and 0 <= y - by < 2 * half:
            px, py = (x - bx + 0.5) * zoom, (y - by + 0.5) * zoom
            cd.ellipse([px - 6, py - 6, px + 6, py + 6], outline=(255, 40, 40), width=3)
        cd.rectangle([0, 0, 240, 26], fill=(0, 0, 0))
        cd.text((6, 4), f"{nm}  x{zoom}" + ("  1 cell = 1 px" if zoom >= 6 else ""), fill=(255, 255, 255), font=font)
        insets.append(crop)
    side = 2 * half * zoom
    sheet = Image.new("RGB", (ov.width + 2 * side + 30, max(ov.height, 2 * side + 280)), (25, 25, 25))
    sheet.paste(ov, (0, 0))
    for i, im in enumerate(insets):
        sheet.paste(im, (ov.width + 10 + (i % 2) * (side + 10), 10 + (i // 2) * (side + 10)))
    sd = ImageDraw.Draw(sheet)
    asp = f"{cal['measured_aspect']:.3f}" if cal["measured_aspect"] else "n/a"
    lines = [f"device {cal['device']}  aspect {cal['display_aspect']:.3f}  measured {asp}",
             f"bow px {cal['bow']}", f"blur sigma {cal['psf_sigma']:.2f}px  grain {cal['noise'] * 255:.2f}/255  mode {cal['mode']}",
             "cyan = fitted display edge, yellow = edge samples kept, pink = rejected (notch, glare)"]
    for i, t in enumerate(lines):
        sd.text((ov.width + 10, 2 * side + 40 + i * 26), t, fill=(230, 230, 230), font=font)
    matte = Image.fromarray((a_full * 255).astype(np.uint8)).resize((round(w * 150 / h), 150))
    sheet.paste(matte.convert("RGB"), (ov.width + 10, 2 * side + 150))
    sheet.save(d / "check.jpg", quality=90)


# ---------------------------------------------------------------- render

SF = Path("/System/Library/Fonts/SFNS.ttf")  # SF Pro, the iPhone system font (macOS only)
INTER = portable.FONTS / "Inter-VF.ttf"  # its free look-alike, used where SF Pro is not installed (Windows)


def sf(size, weight):
    if not SF.exists():
        return portable.weighted(INTER, size, {"Medium": 500, "Semibold": 600}[weight])
    f = ImageFont.truetype(str(SF), size)
    f.set_variation_by_name(weight)
    return f


def ios_frame(shot, dev, url=None, cutout=None):
    """What Safari on an iPhone shows mid-scroll, drawn around the real mobile capture: the status bar (9:41, signal,
    wi-fi, battery) filled with the page's own top colour, the page below it, and Safari's collapsed address bar
    (frosted, the domain only) over the bottom of the page, with the home indicator."""
    from urllib.parse import urlparse
    from PIL import ImageFilter
    k = shot.width / dev["css"][0]  # the capture's own pixel density (3 on a real iPhone; up to 4 for a 4K template)
    W, H = shot.width, round(dev["css"][1] * k)
    cw_pt, ch_pt = dev["css"]
    # spec: a 126x37 pt Dynamic Island at y 11, time centred in the left ear, icons in the right one. A measured island
    # moves all of that, and pushes the page down if it reaches below the spec status bar
    i0, i1, j0, j1 = cutout or (0.5 - 63 / cw_pt, 0.5 + 63 / cw_pt, 11 / ch_pt, 48 / ch_pt)
    sb_pt = max(dev["status_bar"], j1 * ch_pt + 6)
    sb, bar = round(sb_pt * k), round(dev["safari_bar"] * k)
    canvas = Image.new("RGB", (W, H), tuple(int(c) for c in np.asarray(shot)[-1].mean(0)))
    canvas.paste(shot.crop((0, 0, W, min(shot.height, H - sb))), (0, sb))
    top = tuple(int(c) for c in np.median(np.asarray(shot)[:4].reshape(-1, 3), 0))
    ImageDraw.Draw(canvas).rectangle([0, 0, W, sb], fill=top)

    # status bar, drawn 4x and scaled down for clean edges. Layout in pt around a 126x37 pt Dynamic Island at y 11
    ss = 4
    lay = Image.new("RGBA", (W * ss, sb * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fg = (0, 0, 0) if 0.299 * top[0] + 0.587 * top[1] + 0.114 * top[2] > 150 else (255, 255, 255)
    u = k * ss  # pt → px on the 4x layer
    cy = (j0 + j1) / 2 * ch_pt * u
    d.text((i0 * cw_pt / 2 * u, cy), "9:41", font=sf(round(17 * u), "Semibold"), fill=fg + (255,), anchor="mm")
    dx = ((i1 * cw_pt + cw_pt) / 2 - 327.3) * u  # the icon group (291..363.6 pt in spec) centred in the right ear
    x = 291 * u + dx
    for i, bh in enumerate((4.0, 6.2, 8.6, 11.0)):  # cellular bars
        x0 = x + i * 4.6 * u
        d.rounded_rectangle([x0, cy + 5.5 * u - bh * u, x0 + 3 * u, cy + 5.5 * u], radius=0.9 * u, fill=fg + (255,))
    wx, wy = 318.5 * u + dx, cy + 5.2 * u  # wi-fi: three arcs as stacked wedges
    for r, on in ((8.8, 1), (7.0, 0), (5.8, 1), (4.1, 0), (2.9, 1)):
        d.pieslice([wx - r * u, wy - r * u, wx + r * u, wy + r * u], 222, 318, fill=fg + (255,) if on else (0, 0, 0, 0))
    bx = 336 * u + dx  # battery
    d.rounded_rectangle([bx, cy - 6.2 * u, bx + 25 * u, cy + 6.2 * u], radius=3.9 * u, outline=fg + (100,), width=round(1.1 * u))
    d.rounded_rectangle([bx + 2.1 * u, cy - 4.1 * u, bx + 22.9 * u, cy + 4.1 * u], radius=2.2 * u, fill=fg + (255,))
    d.rounded_rectangle([bx + 26.2 * u, cy - 2.1 * u, bx + 27.6 * u, cy + 2.1 * u], radius=0.7 * u, fill=fg + (100,))
    lay = lay.resize((W, sb), Image.LANCZOS)
    canvas.paste(lay, (0, 0), lay)

    # Safari's collapsed address bar: frosted glass over the page bottom, domain, home indicator
    region = canvas.crop((0, H - bar, W, H)).filter(ImageFilter.GaussianBlur(10 * k))  # frosted glass
    lum = float(np.asarray(region.convert("L")).mean())
    light = lum > 100
    frost = Image.blend(region, Image.new("RGB", region.size, (250, 250, 250) if light else (28, 28, 30)), 0.72)
    canvas.paste(frost, (0, H - bar))
    d = ImageDraw.Draw(canvas)
    ink = (20, 20, 20) if light else (240, 240, 240)
    d.line([(0, H - bar), (W, H - bar)], fill=(205, 205, 205) if light else (60, 60, 62), width=1)
    domain = urlparse(url).netloc.removeprefix("www.") if url else ""
    if domain:
        d.text((W / 2, H - 34 * k - (bar - 34 * k) / 2), domain, font=sf(round(13 * k), "Medium"), fill=ink, anchor="mm")
    d.rounded_rectangle([W / 2 - 67 * k, H - 13 * k, W / 2 + 67 * k, H - 8 * k], radius=2.5 * k, fill=ink)
    return canvas


def display_canvas(shot, cal, url=None):
    """The screenshot at exactly the display's aspect ratio, never stretched: a shorter capture (macOS full-screen
    on a notch MacBook) gets a black menu-bar strip on top; a taller one keeps the top of the page. A phone capture
    gets the iOS status bar and Safari's bottom bar around it."""
    dev = DEVICES[cal["device"]]
    if dev["kind"] == "phone":
        return ios_frame(shot, dev, url, cal.get("cutout"))
    ar = cal["display_aspect"]
    w, h = shot.size
    if abs(w / h - ar) / ar < 0.01:
        return shot
    if w / h > ar:
        full_h = round(w / ar)
        strip = full_h - h
        if cal.get("cutout"):  # a notch drawn taller than the real menu bar: the strip grows, the page bottom is cut
            strip = max(strip, round(cal["cutout"][3] * full_h) + round(0.004 * full_h))
        canvas = Image.new("RGB", (w, full_h), (0, 0, 0))
        canvas.paste(shot, (0, strip))
        return canvas
    return shot.crop((0, 0, w, round(w / ar)))


def render_one(tid, shot_path, out_path, glare=None, bloom="auto", fit=None, debug=False, quiet=False):
    d = tdir(tid)
    if not (d / "calib.json").exists():
        sys.exit(f"{tid} is not calibrated yet: mockup.py calibrate {tid}")
    cal = json.loads((d / "calib.json").read_text())
    side = Path(shot_path).with_suffix(".json")
    url = None
    if side.exists():
        url = json.loads(side.read_text()).get("url")
        sdev = json.loads(side.read_text()).get("device")
        if sdev and sdev != cal["device"] and DEVICES[sdev]["native"] != DEVICES[cal["device"]]["native"]:
            print(f"  note: screenshot was taken for {sdev}, template is {cal['device']}; fitted without stretching")
    shot = display_canvas(Image.open(shot_path).convert("RGB"), cal, url)
    L = load_lin(d / "template.png")
    h, w = L.shape[:2]
    box = screen_box(cal, (w, h), 4)
    x0, y0, x1, y1 = box
    m = screen_model(L, cal, box)
    a = m["a"]

    # warp in linear light (2x supersampled and area-averaged when the page shrinks), then the camera's own blur
    sides = [np.linalg.norm(np.subtract(cal["corners"][i], cal["corners"][j])) for i, j in ((0, 1), (3, 2), (0, 3), (1, 2))]
    src = to_lin(np.asarray(shot, np.float32) / 255)
    panel_w = max(sides[0], sides[1])
    ss = 2 if shot.width > 1.2 * panel_w else 1  # supersample only when the page is shrunk onto the panel
    target_w = ss * panel_w
    if target_w < shot.width:
        src = cv2.resize(src, (round(target_w), round(target_w * shot.height / shot.width)), interpolation=cv2.INTER_AREA)
    gx, gy = grid(box, ss)
    u, v = image_to_uv(cal, gx, gy)
    sh, sw = src.shape[:2]
    site = cv2.remap(src, (u * sw - 0.5).astype(np.float32), (v * sh - 0.5).astype(np.float32),
                     cv2.INTER_LINEAR if ss == 2 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    site = np.clip(site, 0, None)
    site = cv2.resize(site, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    sig = float(np.sqrt(max(cal["psf_sigma"] ** 2 - 0.3 ** 2, 0)))
    if sig > 0.05:
        site = cv2.GaussianBlur(site, (0, 0), sig)
    lit = site * m["E"][..., None] * cal["brightness"] * np.array(cal["tint"], np.float32)

    # composite: panel light × falloff, plus the template's own glass reflection, over the cleaned bezel
    g = cal["glare"] if glare is None else glare
    sub = L[y0:y1, x0:x1]
    # an edge pixel is part panel, part bezel. Its bezel share takes the colour of the real bezel right next to it
    # (pixels with no panel at all), not what is left after subtracting the green: generated photos draw halos and
    # fringes on that boundary which would otherwise survive as a thin teal or magenta line
    clear = (a < 0.02).astype(np.float32)
    rs = 1.5 + cal["psf_sigma"]
    ref = cv2.GaussianBlur(sub * clear[..., None], (0, 0), rs) / np.maximum(cv2.GaussianBlur(clear, (0, 0), rs), 1e-4)[..., None]
    bezel = np.where(clear[..., None] > 0, sub, (1 - a)[..., None] * ref)
    comp = L.copy()
    comp[y0:y1, x0:x1] = a[..., None] * (lit + g * m["rho"]) + bezel
    a_full = np.zeros((h, w), np.float32)
    a_full[y0:y1, x0:x1] = a

    # light the screen throws on the room. The green panel lit the laptop body and desk in front of it; that green is
    # taken out and the same amount of light put back in the site's own average colour, so a dark site leaves a dim
    # keyboard and a white one a bright, neutral one. Only in front of the screen and on a band around it (the whole
    # room only when the screen is its sole light), so a plant or a window behind the laptop keeps its green.
    dark = float(np.clip((0.06 - cal["scene_luma"]) / 0.05, 0, 1))
    screen_h = (sides[2] + sides[3]) / 2
    dist = cv2.distanceTransform((a_full < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    # the panel's own glow on the black glass right around it counts too (weight 1 up to the edge). Spill is read
    # from the photo's share of each pixel only, so an edge pixel's bezel part is cleaned exactly once and the site's
    # own green (a green button at the edge) is never touched
    reach = front_weight(cal, (w, h), dist, screen_h)
    pitch_dark = float(np.clip((0.02 - cal["scene_luma"]) / 0.01, 0, 1))
    if pitch_dark:  # a room lit by nothing but the screen: any green cast on the walls is the screen's too
        reach = np.maximum(reach, 0.85 * pitch_dark)
    back = L.copy()
    back[y0:y1, x0:x1] = bezel  # the photo's share of each pixel; the panel's own pixels have none
    # spill = green above what the surface would show without it. Laptop: the keyboard and bezel are grey, so above the
    # larger of red and blue. Phone: the band is a hand and a (clear) case, skin keeps green between red and blue
    ref_rb = np.maximum(back[..., 0], back[..., 2]) if DEVICES[cal["device"]]["kind"] == "laptop" \
        else (back[..., 0] + back[..., 2]) / 2
    spill = np.clip(back[..., 1] - ref_rb, 0, None) / (1 - max(cal["kr"], cal["kb"]))
    site_mean = cv2.resize(src, (64, 40), interpolation=cv2.INTER_AREA).reshape(-1, 3).mean(0)
    site_light = site_mean * cal["brightness"] * np.array(cal["tint"], np.float32)
    kvec = np.array([cal["kr"], 1, cal["kb"]], np.float32)
    if cal["mode"] == "green":  # a hand-cornered photo of a real screen threw no green light to take out
        relit = (reach * spill)[..., None] * (site_light - kvec)
        comp = np.clip(comp + relit, 0, None)
        back = np.clip(back + relit, 0, None)
    bl = (0.06 * dark) if bloom == "auto" else float(bloom)
    if bl > 0:
        glow = np.zeros_like(comp)
        glow[y0:y1, x0:x1] = a[..., None] * lit
        comp += bl * cv2.GaussianBlur(glow, (0, 0), 0.012 * screen_h)

    res = to_srgb(comp)
    rng = np.random.default_rng(7)
    n = cal["noise"]
    if n > 0:
        grain = rng.normal(0, n, (h, w, 1)) + rng.normal(0, 0.35 * n, (h, w, 3))
        res = res + a_full[..., None] * grain.astype(np.float32)
    img = Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8))

    # leak check: green left in the photo's own share of the 3 px just outside the panel edge. Read from the bezel
    # layer, not the finished image, so a green button on the site itself at the edge doesn't count
    ring = (dist > 0) & (dist <= 3)
    b8 = (to_srgb(back) * 255).astype(np.int16)
    leak = int(((b8[..., 1] - np.maximum(b8[..., 0], b8[..., 2]) > 12) & ring).sum())
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if debug:
        corner_zooms(img, cal, out.with_name(out.stem + "_corners.jpg"))
    if fit:
        img = fit_frame(img, fit, cal)
    img.save(out)
    if not quiet:
        check = "" if cal["mode"] != "green" else f"  green leak on the bezel: {leak} px" + (
            "" if leak < 20 else "  ← check the edge (zoom the corners)")
        print(f"{out}  {img.size[0]}x{img.size[1]}{check}")
    return out, leak


def front_weight(cal, size, dist, screen_h):
    """0..1: where the panel's own light lands. The laptop body and desk below the screen (between its side edges,
    extended), plus a band all around the panel. The caller masks the panel itself out. A phone has no keyboard in
    front of it: only the band (the hand and case right around the screen)."""
    w, h = size
    if DEVICES[cal["device"]]["kind"] == "phone":
        near = np.clip(1 - dist / (0.08 * screen_h), 0, 1)
        return cv2.GaussianBlur(near.astype(np.float32), (0, 0), 0.005 * screen_h)
    tl, tr, br, bl = (np.array(c) for c in cal["corners"])
    s = 4
    gx, gy = np.meshgrid(np.arange(0, w, s) + s / 2, np.arange(0, h, s) + s / 2)

    def signed(p0, p1, inside):  # distance from the line p0→p1, positive on the side away from `inside`
        d = (p1 - p0) / np.linalg.norm(p1 - p0)
        n = np.array([d[1], -d[0]])
        if np.dot(inside - p0, n) > 0:
            n = -n
        return (gx - p0[0]) * n[0] + (gy - p0[1]) * n[1]

    centre = (tl + tr + br + bl) / 4
    sw = (np.linalg.norm(tr - tl) + np.linalg.norm(br - bl)) / 2
    below = signed(bl, br, centre)
    left, right = signed(tl, bl, centre), signed(tr, br, centre)
    front = (np.clip(below / (0.04 * screen_h), 0, 1) * np.clip((2.6 * screen_h - below) / (0.9 * screen_h), 0, 1)
             * np.clip((0.3 * sw - left) / (0.12 * sw), 0, 1) * np.clip((0.3 * sw - right) / (0.12 * sw), 0, 1))
    front = cv2.resize(front.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    near = np.clip(1 - dist / (0.15 * screen_h), 0, 1)  # 1 on the panel too, so the blur keeps the edge at full weight
    return cv2.GaussianBlur(np.maximum(front, near), (0, 0), 0.01 * screen_h)


def fit_frame(img, fit, cal):
    fw, fh = map(int, fit.lower().split("x"))
    w, h = img.size
    s = max(fw / w, fh / h)
    cw, ch = fw / s, fh / s
    cx, cy = np.array(cal["corners"]).mean(0)
    left = float(np.clip(cx - cw / 2, 0, w - cw))
    top = float(np.clip(cy - ch / 2, 0, h - ch))
    return img.resize((fw, fh), Image.LANCZOS, box=(left, top, left + cw, top + ch))


def zoom_half(cal, size):
    """Half-width of a corner zoom window: wider on big photos, and on phones, whose rounded corners put the fitted
    (square) corner well outside the glass."""
    c = np.array(cal["corners"])
    short = min(np.linalg.norm(c[0] - c[1]), np.linalg.norm(c[0] - c[3]))
    half = max(30, round(0.008 * max(size)))
    if DEVICES[cal["device"]]["kind"] == "phone":
        half = max(half, round(0.09 * short))
    return half


def corner_zooms(img, cal, path):
    w, h = img.size
    half = zoom_half(cal, (w, h))
    zoom = max(2, 480 // (2 * half))
    tiles = []
    for x, y in cal["corners"]:
        fx, fy = np.clip(x, half, w - half - 1), np.clip(y, half, h - half - 1)
        bx, by = int(round(fx)) - half, int(round(fy)) - half
        tiles.append(img.crop((bx, by, bx + 2 * half, by + 2 * half)).resize((2 * half * zoom,) * 2, Image.NEAREST))
    s = 2 * half * zoom
    sheet = Image.new("RGB", (2 * s + 10, 2 * s + 10), (20, 20, 20))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * (s + 10), (i // 2) * (s + 10)))
    sheet.save(path, quality=90)


def all_ids():
    return sorted(p.parent.name for p in TEMPLATES.glob("*/calib.json"))


def render(a):
    ids = all_ids() if a.id == "all" else [a.id]
    many = len(ids) > 1 or Path(a.out).suffix == ""
    for tid in ids:
        out = Path(a.out) / f"{tid}.png" if many else Path(a.out)
        render_one(tid, a.shot, out, a.glare, a.bloom, a.fit, a.debug)


def make(a):
    from urllib.parse import urlparse
    import webshot
    kinds = {"laptops": "laptop", "phones": "phone"}
    if a.templates in (["all"], ["laptops"], ["phones"]):
        ids = [t for t in all_ids() if a.templates == ["all"]
               or DEVICES[json.loads((tdir(t) / "calib.json").read_text())["device"]]["kind"] == kinds[a.templates[0]]]
    else:
        ids = a.templates
    slug = urlparse(a.url).netloc.replace("www.", "") or "site"
    out_dir = Path(a.out_dir or ROOT / "mockups" / "out" / slug)
    shots = {}
    for tid in ids:
        cal = json.loads((tdir(tid) / "calib.json").read_text())
        dev = cal["device"]
        fs = a.frame == "fullscreen" and DEVICES[dev]["kind"] == "laptop" and DEVICES[dev]["notch"]
        c = np.array(cal["corners"])
        panel_w = max(np.linalg.norm(c[1] - c[0]), np.linalg.norm(c[2] - c[3]))
        # at least as many page pixels as the photo has panel pixels (a 4K template), same layout, capped at 4x
        dpr = int(min(4, max(DEVICES[dev]["dpr"], np.ceil(panel_w / DEVICES[dev]["css"][0]))))
        key_ = (dev, fs, dpr)
        if key_ not in shots:
            name = f"{dev}{'_fullscreen' if fs else ''}_{dpr}x.png"
            shots[key_] = webshot.shoot(a.url, out_dir / "shots" / name, dev, fs, a.scroll, a.at, None, a.hide, a.wait,
                                        scale=dpr)
        render_one(tid, shots[key_], out_dir / f"{tid}.png", fit=a.fit, debug=a.debug)


def list_templates(_):
    for d in sorted(TEMPLATES.glob("*/meta.json")):
        meta = json.loads(d.read_text())
        c = d.parent / "calib.json"
        state = "calibrated" if c.exists() else "not calibrated"
        print(f"{meta['id']:<14} {meta['device']:<14} {state:<15} {meta['inspo']}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template")
    t.add_argument("inspo")
    t.add_argument("--id", required=True)
    t.add_argument("--device", default="air13")
    t.add_argument("--extra", help="extra prompt lines for this one scene")
    t.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    t.add_argument("--run-cap", type=float, default=100)
    t.add_argument("--as-is", action="store_true", help="use the photo itself (your own shot), no image generation")
    t.add_argument("--source", help="the original post, when the reference given is our own earlier green-screen "
                   "version of it (for a post whose screen content the model keeps copying)")
    c = sub.add_parser("calibrate")
    c.add_argument("id")
    c.add_argument("--device")
    c.add_argument("--corners", nargs=4, metavar="X,Y", help="TL TR BR BL by hand, for a photo without a green screen")
    c.add_argument("--brightness", type=float, help="panel brightness multiplier (default 1, kept across re-calibrations)")
    c.add_argument("--tint", type=lambda s: [float(x) for x in s.split(",")], help="r,g,b multipliers for the panel")
    c.add_argument("--glare", type=float, help="glass reflection strength kept from the photo (default 1; 0 drops an "
                   "odd reflection the generated photo drew, kept across re-calibrations)")
    r = sub.add_parser("render")
    r.add_argument("id", help="template id, or all")
    r.add_argument("shot")
    r.add_argument("--out", required=True)
    r.add_argument("--glare", type=float, help="glass reflection strength (default 1 = as photographed)")
    r.add_argument("--bloom", default="auto")
    r.add_argument("--fit", help="crop/resize the result, e.g. 1080x1350")
    r.add_argument("--debug", action="store_true", help="also save a 6x zoom of the four corners")
    m = sub.add_parser("make")
    m.add_argument("url")
    m.add_argument("--templates", nargs="+", default=["all"])
    m.add_argument("--out-dir")
    m.add_argument("--frame", choices=["fullscreen", "flush"], default="fullscreen",
                   help="notch MacBooks: fullscreen (owner's pick, 2026-10-01) or flush; no effect on other devices")
    m.add_argument("--scroll", type=int, default=0)
    m.add_argument("--at")
    m.add_argument("--hide", nargs="*", default=[])
    m.add_argument("--wait", type=float, default=1.5)
    m.add_argument("--fit")
    m.add_argument("--debug", action="store_true")
    sub.add_parser("list")
    a = p.parse_args()
    {"template": template, "calibrate": calibrate, "render": render, "make": make, "list": list_templates}[a.cmd](a)


if __name__ == "__main__":
    main()
