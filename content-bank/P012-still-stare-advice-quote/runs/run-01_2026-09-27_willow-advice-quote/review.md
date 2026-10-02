# Review · P012 run 01

## Format match (7 points)
| # | Point | Result |
|---|-------|--------|
| 1 | Structure | Match: 1 shot of about 5 s, no cuts, text on screen from 0 s. |
| 2 | Hook | Match on the shape (credit line, a two-state contrast, the urge to quit, a one-word command); every sentence is new, and the credit is non-clinical on purpose. |
| 3 | Camera & motion | Match: locked selfie video (term 1), very tight close-up, still stare, one slow blink, dark room. |
| 4 | Pacing | Match: 5.03 s, 0 cuts, 52 words on screen (source about 62). |
| 5 | Text overlay | Match: pale yellow `#fcffb0`, no outline, centred, 11 lines with a blank line, centre at 59.5% of the height (source about 57%). Block is a little narrower (64% vs 68% of the width). |
| 6 | Audio | Match in `final_with_sound.mp4` (the same sound, the source's 5 s clip); `final.mp4` is silent. |
| 7 | Arc | Match: sincere advice, still face, a last-word payoff. |

## Video check (`textclip.py check`)
**PASS** (3 of 3): one shot with 0 cuts (largest frame-to-frame jump 1.3) · 1080×1920 · the subject moves (mean frame change 0.35; only a blink and breathing, as intended).

## Originality
- **Words:** 23.7% overlap of our unique words with the source text (9 shared function words), longest shared run 2 words (`output/word_overlap.json`).
- **Frames:** 3 frames of our video against the source's key frames with `measure.py compare`: closest 18 bits, near-duplicate at 10 or less. No pair flagged (both are dark close-ups of a face, so the distance is lower than for P011).
- **Person and setting:** fictional persona (Willow), a different room and top, a different credit line. The source's man, wall and quote are not reused.
- `originality.py` was not run (it only handles slide images).

## Caption check
`caption.py check`: style **none**, PASS with a warning: the caption is empty, as in the source.

## Known limits
- **AI human video:** a fictional person in a generated room; the AI-generated label must be on. In a very dark image the eyes and mouth are the things to check: I looked at frames from every second and found no artifact, but nobody has watched it in motion.
- **Framing fixed in code:** the model would not put her face high enough, so the still was shifted and the bottom extended. The mirrored cloth band shows as an oval shape only when the brightness is pushed up about 3.5 times.
- **Emotional content:** the still shows tears and a distressed look. It is a fictional persona and general friendship advice, not a therapy or medical claim; keep the credit non-clinical.
- **The credit line is an invented anecdote** (a grandmother's advice). AI label on.
- **Resolution:** Kling std gives 716×1284, scaled up to 1080×1920, so it is slightly soft. Brightness is lower than the source (about 7% vs 13%).
- **Sound:** commercially released and flagged copyrighted; see the licence note in `package.md`.
- **Topic and wording** (friendships, "my nan") are my choices.
- Pillar P012 is Low confidence (1 post). The pilot scope in the Deliverables doc lists human video as out of scope; this is the simplest case (one shot, no speech).
- The 7 points were checked by me; tester ratings are pending.

## Tester ratings (1–5)
Pending.

## Owner verdict
Pending.

## Feedback
