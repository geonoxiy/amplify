# Review · P014 run 01

## Format match (7 points)
| # | Point | Result |
|---|-------|--------|
| 1 | Structure | Partial match: cover + 4 feature slides (source: cover + 6). Reduced count, noted in `package.md`; the cover-then-tip-slides shape and the heading/subheading pattern match. |
| 2 | Hook | Match on shape (a payoff title + a credibility/use line); reworded for PagePilot. |
| 3 | Camera & motion | Match: humans (cover) + ui-screenshots (feature slides), the same reused laptop-and-desk scene across slides, low angle from the keyboard. |
| 4 | Pacing | Match: one heading + one subheading per slide, both short. |
| 5 | Text overlay | Match on position and Classic style (white, thick black outline); emoji dropped (font has no glyphs for them — see Known limits). |
| 6 | Audio | Not applicable (slideshow; the source's sped-up song is not carried over). |
| 7 | Arc | Adapted: the source is a generous "free tools" round-up ending soft; this is a hard sell, so it ends on a CTA instead, which is the deliberate difference a hard-sell caption style requires. |

## Originality
- **Frames:** `measure.py compare` against all 7 of the source's slides (re-checked after the 2026-09-28 revision): closest pair 30 bits (limit: 10 or less). Pass.
- **Content:** none of the source's featured tools (HubSpot, Canva, Semrush, AnswerThePublic, Google, BuzzSumo) or their real screenshots are reused. The laptop screen is a generated abstract mockup, not any real product's UI.
- **Person:** fictional persona (Willow); the source's cover also has no visible face, so no likeness question there either.

## Caption check
`caption.py check`: style **hard**, brand **PagePilot**, PASS. Body names the brand and the product, collateral is filled in, ends with the brand's exact call to action, disclosure appears once and last, no `never_say` word (checked against the earnings-claim ban list).

## Known limits
- **Slide count reduced** from the source's 7 to 5 (cover + 4), to keep the run's image spend proportionate to a single-pillar test. If the owner wants the full 6-feature count, 2 more feature slides reuse the same `laptop_base.png` at no extra image cost — only more heading/subheading text.
- **Real artifacts, partially.** 2026-09-28 revision: the laptop screen now shows PagePilot's real wordmark, real brand colours and real interface labels (drawn in code, perspective-warped on), not the earlier abstract placeholder. It is still not a literal screenshot of their actual editor: I checked PagePilot's own marketing screenshots and excluded the ones that would have worked as literal screenshots, because they show a different real company's product ("Breez Dream") or real, identifiable people's faces wearing a third-party-branded cap — reusing those in an unrelated ad wasn't appropriate. Flag to PagePilot whether they can supply a clean screenshot of their own empty editor (no customer's real store, no other person's photo) for a fully literal version next time; `brands/pagepilot.md`'s `product_images` field is ready for that.
- **Emoji dropped from every heading.** The project's TikTok Sans font has no emoji glyphs; a tofu box looked worse than omitting them. If emoji matter for this format, a separate emoji-font compositing step would need building.
- **Realism pass (2026-09-28):** both base photos regenerated with explicit phone-camera-imperfection prompts (grain, uneven light, a coffee stain, faint glare) and `phone_look()` applied again on the finished slides, after owner feedback that the first pass looked too smooth/AI-polished. The first cover attempt also showed more of the persona than appropriate and was rejected and redone (kept in `raw/` for the record, not used).
- **PagePilot is a real SaaS business** whose core audience (dropshippers, new merchants) is a category regulators watch for earnings claims. No income or results claim is made anywhere in the caption or slides (checked against the brand's own ban list), but get this reviewed by PagePilot before posting — especially the $200M figure, which this run did **not** use, but a future run might.
- Pillar P014 is Low confidence (1 post).
- The 7 points were checked by me; tester ratings are pending.

## Tester ratings (1–5)
Pending.

## Owner verdict
Pending.

## Feedback
