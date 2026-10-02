# Review · P009 run 01

## Format match (7 points)
| # | Point | Result |
|---|-------|--------|
| 1 | Structure | Match: 6 shots, one exercise each, ticks 1 to 6, no outro or CTA. |
| 2 | Hook | Match: exercise already moving at 0 s, title and tracker fade in within 1 s, formula `The Perfect [Muscle] Workout`. |
| 3 | Camera & motion | Match: locked camera, only the character moves, plain background, AI image-to-video. |
| 4 | Pacing | Match: 5 cuts in 16.2 s (0.31 cuts/s), shots 2.67 to 2.73 s. |
| 5 | Text overlay | Match on layout (title, tracker card, name and sets × reps, bottom fifth empty). Differs on purpose: Verde fonts and colours, teal ticks, no logo. |
| 6 | Audio | Not matched: the source uses music; this file is silent. |
| 7 | Arc | Match: a checklist the viewer watches complete. |

## Video check (`reel.py check`, measured from the finished MP4's pixels)
**PASS** (6 of 6): length 16.2 s · 5 hard cuts at 2.7, 5.4, 8.13, 10.8, 13.53 s · shot lengths 2.67 to 2.73 s · every clip moves · bottom 20% empty (0.0% differs from the background) · closest source frame 14 bits away (limit: above 10).
The 14 bits is close on purpose: the layout (title, tracker, name, art zone) is the format. The characters, colours and exercises are different.

## Originality
- **Frames:** perceptual-hash check above, against the 4 P009 source videos' key frames. Not a substitute for a human look.
- **Character:** Verde is original (teal, amber visor, faceless); not @bluebro.fit's blue mascot.
- **Words:** title overlap with the source titles is 60% because the pillar's formula is the trend (Trend rider keeps it). No exercise name matches a source's.
- `originality.py` was not run: it only handles slide images and has no video mode.

## Caption check
`caption.py check`: style **none**, PASS (118 characters, 5 hashtags, no brand, no disclosure).

## Known limits
- **Exercise form is AI-animated and unverified.** Someone who trains should watch every shot. Seen: the barbell shrug bends the arms a little at the top; the cable upright row turns Verde toward the camera during the rep; the carries drift slightly. Two shots needed a second attempt.
- **Resolution:** Kling std gives 720×1280; the reel is scaled up to 1080×1920, so the art is a little soft. Pro mode was not tried.
- **Tracker icons are identical** (one muscle).
- **Rep scheme for the carries** is `2-3 x 30 sec`, not the pillar's `2-3 x N-N` reps pattern.
- **Silent.** No sound chosen.
- Only Kling 3.0 standard was tried; no other video model was compared.
- The 7 points were checked by me; tester ratings are pending.

## Tester ratings (1–5)
Pending.

## Owner verdict
Pending.

## Feedback
