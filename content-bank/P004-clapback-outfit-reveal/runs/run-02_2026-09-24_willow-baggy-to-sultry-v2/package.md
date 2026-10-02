# P004 · run 02 · Willow · baggy → going-out (v2)

Pillar = format (3 slides, hook on slide 1 only, identical mirror selfies for 2 and 3). Persona = Willow's face and body only (`personas/willow`). Everything else comes from the pillar and its source.

## Hook
`When someone says "why do you always wear baggy clothes" like my body was gonna disappoint`

Kept word for word from the source. TikTok hooks are the trend itself, so only the images change (new person, room, pose and outfits).

## Slides
| # | Role | Visual | Text |
|---|------|--------|------|
| 1 | Hook | True front-camera selfie, lying on her back on an unmade bed, head tilted, raised eyebrow + side-eye, arm bent behind her head, grey sweatshirt, claw clip. Face in the lower 45%, cluttered room above (lamp, chair of laundry, glass, charger, lip balm). Different pose from the source (lollipop, lying on a couch). | Source hook (unchanged), white with thick black outline, centred at 37.5% of the height |
| 2 | Before | Full-length mirror selfie, phone over face, oversized grey sweatshirt + baggy sweatpants + slides. Messy bedroom: unmade bed, chair of clothes, trainers, cables, dusty mirror. | none |
| 3 | After | Same mirror, framing and room (edited from slide 2). Fitted black satin mini dress, strappy heels, hair down, hip popped, hand on hip. | none |

## Caption and hashtags
Caption: `🤫🤫🤫` · `#fyp #outfitcheck #ootd #littleblackdress #getreadywithme` · AI-generated content label on.

## Production (what was actually run)
- Model: Nano Banana Pro (`nbp`, 2K, 18 credits per image), the most realistic one available on kie. Persona ref attached to every image where her face shows.
- Slide 2 generated from the persona ref → slide 3 is an edit of slide 2 (same scene, only outfit, hair and pose change) → slide 1 generated with the persona ref + slide 2 (same sweatshirt).
- Text drawn in code (`tools/overlay.py`, TikTok Classic style calibrated on the source), then grain, softness and JPEG artefacts added in code.
- Cost: 84 credits ($0.42) including v1 attempts and one rejected slide 1 (it showed the phone in shot).
- Output: `output/slide1-3.png`, `output/preview.jpg`. Raws in `raw/`; earlier attempts in `raw-v1-nb/` and `raw/slide1_attempt1_third-person.png`.

## Posting
Wednesday morning, same as the source's best slot; trending confident sound.
