# Worked example: one unit written with the visual data model

Slide 2 of @smartshopper858's post 7684431864446127380 (glycolic acid explainer), a designed card that fits none of the six classes. Copy this shape (guideline Part 3): every slide gets the frame record and text blocks, the class module goes in `image` (empty here, because there is no class module), and the open describer goes in `other`.

Boxes are `[x, y, w, h]` in % of the frame from the top-left, estimated by eye on the 1024px slide and then confirmed with `measure.py check` (the drawn boxes line up with every element). The palette, brightness, contrast, saturation, sharpness, noise and clutter come from `measures.json` (code). Text fills are the darkest pixels sampled inside each box. The font sizes are estimated. Use "estimated" only for the † fields in the guideline.

```json
{
  "n": 2, "role": "definition", "confidence": "high",
  "class": "other:designed-card",
  "frame": {
    "canvas": "1:1, 1024x1024 analysis copy, no bars, no border",
    "layers": [
      {"type": "background", "box": [0, 0, 100, 100], "note": "pale blue gradient (#dbedfb, 71% of pixels, code) with two soft blurred blobs: top-right darker blue-grey, bottom-left grey-green (mesh-gradient look)"},
      {"type": "icon", "box": [10, 39.5, 22.5, 22.5], "note": "light circle (#ebf5fe) with a soft drop shadow; inside it an outline water-drop icon in navy, thin even stroke, about 25% of the circle width; the drop stands for the acid"},
      {"type": "text-block", "box": [36.8, 41.8, 19.8, 3.9], "note": "title"},
      {"type": "text-block", "box": [36.8, 48.1, 39, 2.6], "note": "description"},
      {"type": "text-block", "box": [36.8, 53.5, 19.8, 1.7], "note": "label"},
      {"type": "pills", "box": [36.8, 56.5, 34.2, 3.8], "note": "3 pill chips, fully rounded, #edf6fc fill, small gaps, text inside"},
      {"type": "mark", "box": [43, 93.6, 15.8, 2.3], "note": "search icon + 'smartshopper' watermark, low contrast grey-green"}
    ],
    "composition": {
      "focal": [22, 50.5],
      "subject_box": [10, 39.5, 66, 22.4],
      "zone": "middle-center",
      "negative_space": [[0, 0, 100, 38], [0, 64, 100, 28]],
      "balance": "one lockup, slightly left of center, floating in the middle third; empty above and below",
      "grouping": "icon left, text stack right with vertical centers aligned, chips as a row under the stack"
    },
    "safe_zones": "not applicable (1:1 card)",
    "color_light": "palette from code: #dbedfb .71, #d3e6f2 .12, #c8dce9 .10, #edf6fc .06, #8fa6b9 .01. Brightness 90.6%, contrast 6.0%, saturation 12.6% (code). Cool, low-contrast background, dark navy text. Flat soft light, no photographic light source.",
    "quality": "clean vector-like render. Sharpness 123.6, noise sigma 0.24, clutter 0.74% (code); no grain",
    "origin_realism": "rendered graphic (designed in a card tool or HTML), stylized"
  },
  "text_blocks": [
    {"text": "what is it?", "origin": "designed", "role": "headline", "pattern": "icon-lockup", "box": [36.8, 41.8, 19.8, 3.9], "zone": "middle-center", "align": "left", "font": "Helvetica Bold or Arial Bold (closest)", "size_pct": 4.6, "case": "lowercase", "fill": "#0d253a", "stroke": "none", "under": "solid gradient background (negative space)"},
    {"text": "the acid that melts away dead skin cells", "origin": "designed", "role": "body", "pattern": "icon-lockup", "box": [36.8, 48.1, 39, 2.6], "zone": "middle-center", "align": "left", "font": "Helvetica or Arial Regular (closest)", "size_pct": 3.1, "case": "lowercase", "fill": "#254156", "stroke": "none", "under": "solid gradient background"},
    {"text": "COMMONLY FOUND IN", "origin": "designed", "role": "label", "pattern": "icon-lockup", "box": [36.8, 53.5, 19.8, 1.7], "zone": "middle-center", "align": "left", "font": "Helvetica or Arial Bold, letter-spaced", "size_pct": 2.2, "case": "ALL CAPS", "fill": "#284157", "stroke": "none", "under": "solid gradient background"},
    {"text": "toners / serums / peel pads", "origin": "designed", "role": "list item", "pattern": "icon-lockup", "box": [36.8, 56.5, 34.2, 3.8], "zone": "middle-center", "align": "left", "font": "Helvetica or Arial Bold", "size_pct": 2.3, "case": "lowercase", "fill": "#11212e", "stroke": "none", "under": "pill chips: #edf6fc fill, fully rounded, about 1.5% side padding"},
    {"text": "smartshopper", "origin": "mark", "role": "watermark", "pattern": "corner-mark", "box": [43, 93.6, 15.8, 2.3], "zone": "bottom-center", "align": "center", "font": "Helvetica or Arial Bold", "size_pct": 2.3, "case": "lowercase", "fill": "#a9bcc0", "stroke": "none", "under": "solid gradient background"}
  ],
  "image": {},
  "other": {
    "what": "A pale blue card: a water-drop icon in a round badge on the left, and beside it the title 'what is it?', a one-line answer, a small caps label and three pill tags.",
    "made": "rendered graphic; no photo",
    "job": "definition slide: answers the hook's question and opens the fact sequence",
    "nearest_class": "none. It shares rounded chips and cards with UI screenshots, but it is not a screen.",
    "traits": {
      "essential": ["one pastel hue per slide, with the title in a darker shade of it", "icon in a round badge on the left", "lowercase bold sans title", "small caps label followed by pill tags"],
      "incidental": ["which icon", "where the background blobs sit"]
    },
    "recreate": "HTML render to PNG; needs a simple outline icon set and a Helvetica-like font; low difficulty; no likeness or brand risk; swap the watermark for our own handle",
    "name": "designed-card",
    "definition": "a card built from text and simple graphics on a built background, with no photo",
    "unsure": "exact font (Helvetica Bold vs Arial Bold); box values are estimates from the 1024px slide"
  }
}
```
