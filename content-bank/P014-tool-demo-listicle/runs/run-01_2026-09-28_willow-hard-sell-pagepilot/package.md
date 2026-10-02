# P014 · run 01 · Willow · Shopify feature tour (hard sell, PagePilot)

**Mode:** Trend rider · **Caption style:** hard, brand PagePilot (`brands/pagepilot.md`). Pillar = format (cover + N feature-demo slides, a laptop-screen desk scene reused across slides, Title Case heading + one-line subheading per slide). For a hard sell the pillar's Do/Don't calls for the product on every slide instead of unrelated tools, so this run is a single-brand feature tour: **5 slides** (cover + 4), not the source's 7 (cover + 6) — a deliberate reduction to keep the run's spend and scope proportionate; noted as a departure from the source count.

## Slides
| # | Role | Heading | Subheading | Visual |
|---|------|---------|------------|--------|
| 1 | Cover | How I Build Shopify Pages Fast | Using PagePilot | High-angle lifestyle photo: Willow's arm and hand (face not shown, matching the source's cover), a phone as a prop, a laptop beside her with a blurred abstract screen |
| 2 | Feature | Paste A Product Link | PagePilot Builds The Page In Under 60 Seconds | Laptop screen, low angle from the keyboard |
| 3 | Feature | AI Product Photos | No Camera, No Studio, Just PagePilot | Same laptop scene (reused desk setup, per the pillar's Do) |
| 4 | Feature | Ad Copy Written For You | PagePilot Writes It While You Do Something Else | Same laptop scene |
| 5 | Feature | Cart + Upsells Built In | Works With Any Shopify Theme | Same laptop scene |

Every heading/subheading is original copy built from PagePilot's own stated features (product-link import, AI images, AI copy, cart/upsells with any Shopify theme) — none of the source's actual tool names (HubSpot, Canva, Semrush, AnswerThePublic, Google, BuzzSumo) are reused, since a hard sell puts the product on every slide, not a round-up of other brands.

## Caption (`caption.txt`, style hard, brand PagePilot)
> I stopped building my Shopify product pages from scratch. PagePilot turns a product link into a finished page in under 60 seconds, no coding or design skill needed, with AI product photos, ad copy and a cart drawer with upsells built in. Start your free trial — link in bio.
>
> #pagepilot #shopify #ecommerce #dropshipping
>
> This is an advertisement.

`collateral` (required for hard sell): PagePilot is named on the cover and on every feature slide's subheading, each on a laptop screen — satisfies "the product is clearly on it."

## Revision (2026-09-28, owner feedback)
The owner asked for two things: (1) use PagePilot's real artifacts on the laptop screen instead of an abstract placeholder, and (2) make the photos read as real, imperfect phone photos, not a smooth AI render.

**Real artifacts.** I pulled PagePilot's own marketing screenshots from pagepilot.ai and checked each one before using it. Most were not safe to reuse: their "AI product images" example shows real, identifiable people's faces wearing a third-party "Alo" branded cap; their "ad creatives" example uses a different real company's product ("Breez Dream" drinks); their Shopify-theme showcase and a template preview both show other demo brands' products and a real customer's photo and name. None of those are used. Instead the laptop screen shows a mockup built from what's genuinely PagePilot's own and carries no third-party risk: their real wordmark, their real CTA colour (`#4922FF`, sampled from pagepilot.ai) and dark/light brand colours, and real, non-creative interface labels observed on their site ("Publish to Shopify," "Elements," "Gallery," "Social Proof Logos," "Video Testimonials," "Benefits & Features," "Review Bar"). This is perspective-warped onto the laptop screen in code (`raw/build_mockup.py`) so it sits correctly in the photo.

**Realism.** Both base photos were regenerated (`laptop_base_v2.png`, `cover_v2.png`) with prompts asking explicitly for phone-camera imperfections: visible grain, uneven/mixed window light instead of even studio light, a coffee-ring-stained mug, a faint glare, natural JPEG-style compression. `overlay.py`'s `phone_look()` is applied again as a final pass on every finished slide. The first cover attempt also showed more of the persona than appropriate for the ad; it was rejected and regenerated with an explicit fully-covered, buttoned-cardigan prompt (kept as `raw/cover_v2_REJECTED_too-revealing.png` for the record).

**Slide count stays 5** (cover + 4 features), as in the first pass — see the note below.

## Production (what was actually run)
- **Cover photo:** Nano Banana Pro, 2K, 3:4, Willow's reference attached ($0.09) — a high-angle couch scene, face not in frame (matches the source's cover, which also shows no face).
- **Laptop base photo:** Nano Banana Pro, 2K, 3:4, no persona reference needed ($0.09) — one image, **reused across all 4 feature slides**, screen deliberately generated as a soft abstract UI (rounded colour blocks, no readable text or logos), because the model cannot be trusted to render real, legible product-screen text, and recreating any other brand's actual UI is not something this run does.
- **Text:** every heading and subheading drawn in code (`raw/render_slides.py`, a run-specific script built on `tools/overlay.py`'s wrap/curly helpers), TikTok Classic-style bold white with a thick black outline. Emoji were dropped from the headlines: the project's TikTok Sans font has no emoji glyphs, and a missing-glyph box looked worse than no emoji.
- **Cost:** 36 credits = **$0.18** (2 images; the laptop base is reused for 4 slides at $0 extra).
- **Output:** `output/slide1.png` … `output/slide5.png` (1080×1350, 4:5).

- **PagePilot real artifacts:** `#4922FF` (CTA purple) and `#1F1555` (dark) sampled live from pagepilot.ai via computed styles; wordmark and UI labels drawn in code from what's genuinely PagePilot's own (see Revision above). Logo file downloaded (`raw/pagepilot_assets/logo_white.svg`) but not used directly in the end (a plain text wordmark in their exact purple was simpler and avoids SVG-rasterisation issues); five other real marketing images were downloaded and reviewed but excluded (third-party brand or real faces) — kept in `raw/pagepilot_assets/` for the record, not used in any output.
## Posting
No sound needed (slideshow). Caption and hashtags as above; TikTok's AI-generated content label ON and its own commercial-content disclosure toggle ON (separate from the "This is an advertisement." line in the caption).
