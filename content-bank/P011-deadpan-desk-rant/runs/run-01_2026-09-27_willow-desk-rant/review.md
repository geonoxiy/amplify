# Review · P011 run 01

## Format match (7 points)
| # | Point | Result |
|---|-------|--------|
| 1 | Structure | Match: 1 shot of about 5 s, no cuts, text on screen from 0 s. |
| 2 | Hook | Match on the shape (grievance, then a named coworker and an absurd understatement); every word is new. |
| 3 | Camera & motion | Match: locked-off selfie video (term 1), chest-up, typing hands at the bottom edge, deadpan eyes up. Kling pulled the framing back a little, so more of the office shows than in the source. |
| 4 | Pacing | Match: 5.03 s, 0 cuts, 32 words on screen (source 34). |
| 5 | Text overlay | Match: white, thin black outline (Classic), centred, 8 lines, 55% of the width, centre at 66.7% of the height (source about 64%). |
| 6 | Audio | Match in `final_with_sound.mp4` (the same sound, the source's 5 s clip); `final.mp4` is silent. |
| 7 | Arc | Match: a relatable grievance answered by a deadpan look. |

## Video check (`textclip.py check`)
**PASS** (3 of 3): one shot with 0 cuts (largest frame-to-frame jump 2.0) · 1080×1920 · the subject moves (mean frame change 0.86).

## Originality
- **Words:** 17% overlap of our unique words with the source text (5 shared function words), longest shared run 2 words (`output/word_overlap.json`).
- **Frames:** 3 frames of our video against the source's key frames with `measure.py compare`: closest 30 bits, near-duplicate at 10 or less. No pair flagged.
- **Person and setting:** fictional persona (Willow), different office, clothes, prop, mug side and wording. The source's woman, sunglasses-on-head, cream wall and paper cup are not reused.
- `originality.py` was not run (it only handles slide images).

## Caption check
- `caption.py check` (default `caption.json` / **no sell**, and `--in caption_none.json`, identical): style **none**, PASS (no brand, no disclosure).
- `caption.py check --in caption_soft.json` (**soft sell**, brand Bolt Pharmacy): style **soft**, PASS (bridge names the brand, disclosure appears once and last, no banned word from the brand's `never_say` list).
- **Bolt Pharmacy is a real, regulated brand** (GPhC-registered UK online pharmacy, prescription weight-loss medicine). The checker only catches word-level problems; it is not a legal or regulatory compliance check. See `brands/boltpharmacy.md`'s compliance note — get this caption reviewed by Bolt Pharmacy before it is posted, and never let a future edit add a medicine name or a weight-loss outcome claim.

## Known limits
- **AI human video:** a fictional person in a generated office. The AI-generated label must be on. Look for small artifacts: the pencil behind her ear drifts above her head near the end, and her fingers move but do not type real words.
- **Framing:** Kling did not keep my start frame exactly (wider room, smaller subject); still within the pillar's chest-up framing.
- **Resolution:** Kling std gives 716×1284, scaled up to 1080×1920, so the picture is slightly soft.
- **Topic and wording** (a real lunch break, "Greg") are my choices; the owner gave no topic.
- **Sound:** the source's sound is attached in `final_with_sound.mp4` and saved as a separate file; the silent `final.mp4` is kept for adding the sound in TikTok. Third-party music: see the licence note in `package.md` (not in TikTok's commercial library).
- Text style, position and length were measured from one source frame and one enlarged crop.
- Pillar P011 is Low confidence (1 post). The pilot scope in the Deliverables doc lists talking heads and multi-scene edits as out of scope; this one-shot, no-speech video is the simplest human case.
- The 7 points were checked by me; tester ratings are pending.

## Tester ratings (1–5)
Pending.

## Owner verdict
Pending.

## Feedback
