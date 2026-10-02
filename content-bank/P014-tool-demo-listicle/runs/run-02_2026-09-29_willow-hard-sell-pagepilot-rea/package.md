# P014 · run 02 · willow · shopify feature tour (hard sell, pagepilot, real screenshots)

**mode:** trend rider · **caption style:** hard, brand pagepilot (`brands/pagepilot.md`). This is a second attempt at the same pillar and brand as run-01, now applying three rules the owner set after run-01: (1) for a real brand, screenshot their own site and use that as the laptop screen instead of a drawn mockup, (2) captions and overlay text are lowercase with no em dash, en dash, semicolon or colon, (3) use emoji where applicable.

## What changed from run-01
- **Real screenshots, not a mockup.** Navigated to pagepilot.ai with the browser pane and screenshotted 4 sections of their real site: the hero tagline + "start free trial" button, the "copy & paste product link" step, the "choose a template" step, and the pricing cards (lite/starter/scaler). Each is perspective-warped onto the laptop screen in `raw/laptop_slideN.png` (`raw/build_real_composites.py`).
  - **Still excluded on purpose:** their "AI product images" and "ad creatives" marketing examples (a different real company's product, and real identifiable people's faces), their Shopify-themes showcase and a template preview (other demo brands, a real customer's photo), and a "customize & publish" icon crop that a promotional popup kept bleeding into. Picked clean, own-brand-only sections instead (see `raw/pagepilot_real/` for what was actually used).
- **Lowercase, no banned punctuation.** Every heading, subheading and the caption are lowercase; checked with `tools/caption.py check`, which now enforces this (added this session).
- **Emoji used where applicable.** 🚀 on the cover, ⏱️🔗🎨💸 on the feature slides, matching the new capability built into `tools/overlay.py` this session (colour emoji composited from the system font). Hit and fixed a real bug along the way: the ⏱️ (clock + variation selector) sequence crashed Pillow's text shaper; `overlay.py`'s `_emoji_glyph()` now retries without the variation selector before giving up on a glyph.
- **Reused** run-01's persona photos (`cover.png`, `laptop_base.png`) rather than regenerating them — the photography itself wasn't what changed this run, only the screen content and text style.

## Slides
| # | heading / subheading | real content on the laptop screen |
|---|---|---|
| 1 (cover) | "how i build shopify pages fast" / "using pagepilot 🚀" | willow, no real content needed (matches the source pillar's faceless cover) |
| 2 | "pagepilot builds your page in 60 seconds ⏱️" | real screenshot: pagepilot's hero tagline + start free trial button |
| 3 | "just paste a product link 🔗" | real screenshot: pagepilot's "copy & paste product link" step |
| 4 | "pick a template you like 🎨" | real screenshot: pagepilot's "choose a template" step |
| 5 | "plans start at $39 a month 💸" | real screenshot: pagepilot's pricing cards |

## Caption (`caption.txt`, style hard, brand pagepilot)
> i stopped building my Shopify product pages from scratch. pagepilot turns a product link into a finished page in under 60 seconds ⏱️ no coding or design skill needed. start your free trial, link in bio 🚀
>
> #pagepilot #shopify #ecommerce #dropshipping
>
> this is an advertisement.

## Production (what was actually run)
- **No new AI image generation.** `cover.png` and `laptop_base.png` are copied from run-01 ($0 this run).
- **4 real screenshots**, captured with the browser pane, cropped to clean sections, perspective-warped onto the laptop screen in code.
- **Text and emoji** drawn in code (`raw/render_slides.py`, using `overlay.py`'s new emoji-aware `draw_mixed`/`measure_mixed`).
- **Cost: $0.00.**
- **Output:** `output/slide1.png` … `output/slide5.png` (1080×1350, 4:5).

## Posting
No sound needed (slideshow). Caption and hashtags as above; TikTok's AI-generated content label ON (willow's cover photo is AI-generated) and its own commercial-content disclosure toggle ON.
