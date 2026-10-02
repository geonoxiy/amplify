# P013 · run 01 · Willow · unhinged advice request (soft sell, PagePilot)

**Mode:** Trend rider · **Caption style:** soft, brand PagePilot (`brands/pagepilot.md`). Pillar = format (1 slide, tight exaggerated selfie, a direct crowdsourcing question as the whole text block). Persona = Willow's face only (`personas/willow`); the confession, category and expression are the run's own.

## Text on screen (revised 2026-09-28: less niche, closer to the source's register)
First draft leaned too specific/quirky ("two Klarna payments behind," "only admit to at 2am" — owner feedback: this style shows up across several runs and reads as try-hard rather than as the trend). Rewritten to stay in common, recognisable "broke" phrasing instead:
```
I'm on my last twenty,
send me your wildest
income ideas. Not the
whole selling old clothes
thing - I want the plan
you'd only post in a
private group chat
```
Shape unchanged: a confession → a request for wild answers → a ruled-out obvious example → an escalation line. Word overlap with the source text: **24.1%** of unique words, longest shared run 2 words ("me your"). Neither draft reuses the source's specific confession, category or example.

## Slide (1 slide, exaggerated comedic selfie)
Selfie, term 1 (front camera, no phone in shot), tight crop from the nose up. Willow's brows raised high, eyes wide, mouth slightly open in a comedic (not sincere) distressed expression, plain warm-grey wall behind, same framing and text style as the source (TikTok Classic, thick black outline, centred, over the upper half of the frame).

## Caption (`caption.txt`, style soft, brand PagePilot)
> Unhinged money advice is my favourite genre. Everyone has one scrappy plan they have never admitted to out loud.
>
> Here is mine: I stopped building my Shopify product pages by hand. PagePilot turns a product link into a finished page in under 60 seconds, so I actually ship the idea instead of just planning it.
>
> #fyp #advice #unhinged #pagepilot
>
> This is an advertisement.

Bridge stays on speed/effort (never a money-made or income claim, per `brands/pagepilot.md`'s Never claim list) and lands naturally on the source's own theme (money-making hacks → a tool that ships e-commerce pages), not a stretch.

## Production (what was actually run)
- **Still:** Nano Banana Pro, 2K, 9:16, Willow's reference attached ($0.09).
- **Text:** drawn in code (`tools/overlay.py --style classic --weight 700 --phone 0.8`), TikTok Classic (white, thick black outline), plus phone-camera grain and softness (`phone_look()`, owner feedback: the first pass looked too clean/AI-polished).
- **Cost:** 18 credits = **$0.09**.
- **Output:** `output/slide1.png` (1080×1920).

## Originality
`measure.py compare` against the source's key frame: closest 36 bits (limit: near-duplicate at 10 or less). Pass. Different face (Willow, fictional), different wall colour, entirely rewritten text.

## Posting
No sound needed (slideshow). Caption and hashtags as above; TikTok's AI-generated content label ON (Willow is fictional, the image is AI-generated) and its own commercial-content disclosure toggle also ON (separate from the "This is an advertisement." line in the caption).
