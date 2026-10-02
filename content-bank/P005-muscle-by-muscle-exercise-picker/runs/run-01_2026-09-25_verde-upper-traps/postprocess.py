"""Post-processing of the generated art (run-01).
  overview: recolour the purple (it filled the lats, not the lower trapezius) to the body teal.
Shading and outlines are kept: only hue and saturation of the selected pixels change."""
import sys
from pathlib import Path
import cv2
import numpy as np

RUN = Path(sys.argv[1])

def recolor(img, sel, target_h, target_s, v_gain):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0][sel] = target_h
    hsv[..., 1][sel] = target_s
    hsv[..., 2][sel] = np.clip(hsv[..., 2][sel] * v_gain, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def teal_stats(img, box):
    x0, y0, x1, y1 = box
    hsv = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2HSV).reshape(-1, 3)
    teal = hsv[(hsv[:, 0] > 70) & (hsv[:, 0] < 95) & (hsv[:, 1] > 90) & (hsv[:, 2] > 80)]
    return np.median(teal, axis=0)

# ---- overview: purple -> teal
ov = cv2.imread(str(RUN / "raw" / "overview.png"))
h, w = ov.shape[:2]
th, ts, tv = teal_stats(ov, (int(w * .22), int(h * .30), int(w * .30), int(h * .45)))  # upper arm
hsv = cv2.cvtColor(ov, cv2.COLOR_BGR2HSV)
purple = (hsv[..., 0] > 120) & (hsv[..., 0] < 160) & (hsv[..., 1] > 70) & (hsv[..., 2] > 70)
purple = cv2.dilate(purple.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (hsv[..., 0] > 105) & (hsv[..., 1] > 40)
pv = np.median(hsv[..., 2][purple])
ov2 = recolor(ov, purple, th, ts, tv / pv)
cv2.imwrite(str(RUN / "raw" / "overview_fixed.png"), ov2)
print("overview: recoloured", int(purple.sum()), "purple pixels; teal target HSV", th, ts, tv)

# ---- cover: not needed. cover v3 (third generation, two references, "wide composition") came out with red only on the upper-trapezius slope.
#      Earlier versions (raw/cover_v1_*, raw/cover_v2_*) coloured the whole trapezius red and were recoloured below the seam; they are kept for the record.
