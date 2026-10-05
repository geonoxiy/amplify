# P006 run-01 · Pip × PagePilot · product page tips (pt. 1)

Request (2026-10-06): copy @bluebro.fit's account for @pagepilot.ai. Owner choices: one static carousel of 5 images, a new original mascot, PagePilot colours, a Blue Bro style sell mix (value tips + one product slot).

## How the account was translated
| Blue Bro (@bluebro.fit) | PagePilot version |
|---|---|
| Faceless blue muscular mascot acts each tip out | **Pip**, an original faceless purple pilot (PagePilot's rocket logo → pilot theme), `personas/pip.md` |
| Beige card, navy and blue, BLUE BRO mark top-left | Lavender-white card, PagePilot dark `#1f1555` and purple `#4922ff`, Pip head + PagePilot mark top-left |
| Gym tips by muscle for beginner lifters | Product page tips for new Shopify sellers and dropshippers |
| Sells its own eBook, plugs an app as the bonus tip | PagePilot itself sits in the bonus tip slot, on a phone showing the real site |

Format: P006 numbered tip cards. Pillar range is 6 to 9 slides; this run is 5 (owner asked for 5): hook → 3 tips → bonus tip.

## Hook options (mechanic: regret + series counter, the pillar's formula)
1. **used** `i wish i knew these / product page tips / sooner (pt. 1)`. Formula phrase "i wish i knew these … tips sooner" kept as trend wording (amplify-plus rule 2); "product page" is new. Measured overlap 75% because of the formula words.
2. alt (how-to + speed mechanic) `how to fix your product page / as fast as possible`. Different formula, use for part 2 or an A/B test.

## Slides
| # | Role | Text (lowercase, no colons, dashes or semicolons) | Art |
|---|---|---|---|
| 1 | hook | i wish i knew these / product page tips / sooner (pt. 1) | Pip waist up, shopping bag + thumbs up, bleeds off the bottom |
| 2 | tip | #1 say what it does first · title says what it is, first line says what it does for them, specs lower down | Pip with a megaphone |
| 3 | tip | #2 show it in use · 5 to 7 photos, a clean shot, in hands, in use, next to something for scale | Pip photographing a mug |
| 4 | tip | #3 answer the doubts early · shipping, returns and sizing under add to cart | Pip holding out a parcel |
| 5 | bonus tip (product slot) | stop building pages by hand, paste a product link into PagePilot, full Shopify page in under 60 seconds, drag and drop | phone drawn in code with the real pagepilot.ai mobile hero (captured 2026-10-06), Pip pointing at it |

All three tips are general, true advice; no statistics invented. The only product claims are from `brands/pagepilot.md` (under 60 seconds, drag and drop, Shopify).

## Caption (hard, `caption.txt`)
Built by `caption.py`: a save prompt, the bonus tip restated with the brand, the CTA, the pillar's part-1 question, 4 hashtags, "this is an advertisement." last.

## Posting
- 4:5 slideshow, 5 images in order. A soft background track (the pillar uses third-party music only); pick it in TikTok.
- Blue Bro's best window is around midday NZ; for PagePilot's audience, post when its own analytics show activity (unknown here).
- Switch on TikTok's AI-generated label and the commercial content toggle.

## Production
Model sheet (1) → 5 art images on white, GPT Image 2.5 Sunburst 2K with the sheet as reference (4 square requests failed first: GPT renders 1:1 only at 1K, re-run at 4:3, no charge) → `tools/tipcards.py spec.json` (new renderer, text in code) → `measure.py check` → `originality.py` → `caption.py check`. Cost 60 credits ($0.30) incl. the sheet.
