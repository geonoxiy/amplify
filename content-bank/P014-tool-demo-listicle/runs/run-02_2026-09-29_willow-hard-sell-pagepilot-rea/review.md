# review · P014 run 02

## format match (7 points)
| # | point | result |
|---|---|---|
| 1 | structure | cover + 4 feature slides, same shape as run-01 and the source (cover + N tip slides). |
| 2 | hook | match on shape (a payoff title, own words). |
| 3 | camera & motion | match: humans (cover) + ui screenshots (feature slides), a laptop-and-desk scene. this time the screens show pagepilot's own real site, not a drawn recreation. |
| 4 | pacing | match: one short subheading per slide. |
| 5 | text overlay | match on position and classic style (white, thick black outline); now lowercase per the new style rule, with an emoji on every slide. |
| 6 | audio | not applicable (slideshow). |
| 7 | arc | adapted for hard sell: ends on a call to action, as run-01 did. |

## originality
- **frames:** `measure.py compare` against all 7 of the source's slides: closest pair 30 bits (limit: 10 or less). pass.
- **content:** the real pagepilot screenshots used are pagepilot's own genuine site content, not the source creator's tools. willow's cover photo is the same fictional persona as run-01.

## caption check
`caption.py check`: style **hard**, brand **pagepilot**, PASS. only a warning for "Shopify" being capitalised (a real product name, expected and left as is).

## what changed from run-01, and why
- **real screenshots instead of a drawn mockup**, per the owner's standing rule set after run-01 ("access their website, take a screenshot of certain pages, then make it the screen of the laptop").
- **lowercase, no em dash, en dash, semicolon or colon**, per the owner's standing style rule, checked in code this time.
- **emoji used on every slide**, per the owner's standing rule, using the emoji-rendering fix built into `overlay.py` this session.

## known limits
- **the real screenshot does not fill 100% of the visible laptop screen** on slides 2-5, leaving a strip of the original plain lavender screen colour visible around each pasted screenshot. cosmetic, not a factual problem, but worth a tighter quad calibration in a future run.
- **not every pagepilot feature has a safe real screenshot.** their own marketing page mixes genuine own-brand ui with example demo stores that show other real companies' products or real people's photos (a different real drink brand in one, a real face wearing a third-party-branded cap in another, real customer photos in a template preview and a promotional popup). those were identified and excluded; the 4 slides used instead (hero, copy & paste link, choose a template, pricing) are all genuinely pagepilot's own content.
- **no new photography this run** — willow's cover and the laptop base are reused from run-01 unchanged. if the owner wants a fresh look, a future run should regenerate them.
- this run cost $0.00 (no new ai image generation, only real screenshots and code).
- the 7 points were checked by me. tester ratings are pending.

## tester ratings (1-5)
pending.

## owner verdict
pending.

## feedback

## revision 2 (owner feedback: floating screenshot, full-page capture, varied angles)
- **full-page capture:** resized the browser viewport to 900x4500 and captured in one screenshot (not narrow viewport crops), covering the hero, stats, feature grid and ai-creatives sections in one pass.
- **relaxed collateral rule:** owner confirmed full permission to use pagepilot's whole site for a brand we work with, so the ai-creatives section (which shows a different real drink brand, "breez dream", as pagepilot's own example) is now used; a real child's face elsewhere on the site is still avoided as a separate privacy matter, not a brand-permission one.
- **fixed the floating look:** rebuilt the perspective composite; the screenshot now fills nearly the whole visible screen (a thin gap remains on some slides, cosmetic only).
- **varied angles: attempted, not fully delivered.** generated a second, differently-angled laptop photo (over-the-shoulder, different desk). its perspective composite had a real bug (a black void instead of the screenshot) that i did not have budget left to debug this session, so all 4 feature slides use the one laptop angle. the content on screen still varies (4 different real sections of the site), but the camera angle does not. flagged as an open item rather than silently dropped.

## revision 3 (owner feedback: still floating, aspect ratio, angle variance)
- **root cause found: the screen quad coordinates were wrong all along.** i had been estimating the laptop screen's corner pixels by eye instead of measuring them, and was off by 200-300px on the left and right edges (using roughly x=578-1488 when the real screen spans x=698-1788 in `laptop_base.png`). that's why every prior attempt still looked like the screenshot was floating above the display instead of sitting in it, however much the compositing logic itself was fixed.
- **fixed by pixel-grid calibration:** zoomed into each corner of the laptop screen with labelled coordinate-grid overlays, read the exact white-bezel edge pixels, then drew the candidate quad back onto the photo as a red-outline/green-dot overlay (`boxcheck_A.jpg`-style check, same method as `measure.py check` uses for text boxes) and visually confirmed it traced the screen edges before using it. corrected quad: `[(698, 300), (1788, 278), (1788, 1253), (698, 1225)]`.
- **aspect ratio fixed at the fit step:** the real screenshot crop is now resized to the exact bounding-box size of the (possibly rotated) quad it's being pasted into, not a fixed arbitrary card size, so it's never stretched or squeezed out of proportion.
- **angle variance: fixed, correctly scoped this time.** owner clarified the source's angle change is subtle (a hand holding the phone slightly differently), not a full different camera setup. replaced the abandoned second-angle photo with a small in-code rotate/zoom/shift (roughly ±0.5-1° rotation, 1.0-1.04x zoom) of the *same* pixel-verified base photo per slide, carrying the screen quad through the identical transform mathematically — so every slide still uses the one calibrated photo and there's no risk of a fresh mis-calibration.
- **re-checked after this fix:** `caption.py check` still PASS (hard, brand pagepilot, only the expected "Shopify" capitalisation warning); `measure.py compare` against all 7 source slides found 0 pairs at or under the near-duplicate threshold.
