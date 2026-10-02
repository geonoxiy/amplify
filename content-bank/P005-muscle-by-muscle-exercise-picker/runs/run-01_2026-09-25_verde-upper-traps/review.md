# Review

## Format match (7 points)
1. **Structure:** 6 slides: hook → anatomy overview → 4 muscle-pick slides. The pillar allows 6 to 8 slides and an optional CTA (omitted: Trend mode has no product). ✔
2. **Hook:** `[BODY PART] [PROBLEM WORD]?` = "FLAT TRAPS?", two lines over the mascot, whose pose (rear double biceps) shows the body part. ✔
3. **Camera and visual:** designed cards with a 2D mascot as the illustration layer, 4:5, colored anatomy diagram with callouts, `OR` badge between two exercise options (P005 variant b). The mascot, colors and fonts are our own (Trend rider substitution). ✔
4. **Pacing:** 6 slides, 17 to 21 words of body copy per pick slide (pillar: up to 26). ✔
5. **Text overlay:** numbered heading `#N` + title, short accent underline, gray body, sets × reps line, captions under the figures, brand mark top-left; boxes follow the pillar's geometry. Fonts are the closest installed match, not the source's. ✔
6. **Audio:** not rendered; a trending sound is chosen at posting. ⏳
7. **Arc:** problem → what the muscle does → four ways to train it, no sell. ✔

6 of 7 verified, 1 pending (audio); the pillar's pass line is 6.

## Originality check (`tools/originality.py`, `output/originality.json`): PASS
- **Text vs the 4 source posts** (the pillar's own `2-3 Sets x N-N Reps` line is excluded: it is a format element): shared words are only function words and format tokens (`the`, `your`, `or`, `#1`, `anatomy`). Raw overlap 0 to 20% per slide, content words 0 to 8%, longest shared run 2 words (`your arms`). Rule: under 30%. ✔
- **Hook:** 0% of its words appear in any source hook. The other two options were also checked; one was rejected at 45%. ✔
- **Caption:** 0% shared words with the four source captions. ✔
- **Images:** the closest of our slides to any source slide is 15 bits apart on a 64-bit perceptual hash (near-duplicate is 10 or less). ✔
- **Character:** the source mascot's blue covers 9.0% of the pixels in the source slides and 0.00% of ours. Verde has a different color, head, visor and outfit. ✔
- **Person and setting:** no real person (an illustrated fictional character); the poses, props and exercise choices are new (a trapezius topic, not the sources' muscles). ✔
- Not done: a check by eye of the source slides next to ours by someone on the Amplify team.

## Known limits (check before posting)
- **Anatomy is simplified.** The diagram shows the upper trapezius (red) and the rest of the trapezius (yellow, labelled "MID + LOWER TRAPS"). The generated image filled the lats purple as "lower trapezius", so the purple was recolored to teal in code (`postprocess.py`).
- **Exercise drawings are stylized.** Two were redone (a biceps curl instead of an upright row; a cluttered background). The dumbbell shrug shows only moderate elevation, the farmer's-carry dumbbells look plate-loaded, and the landmine-press geometry is approximate. Someone who trains should look before it goes out.
- **Cues are general technique, not medical advice.** The upright-row cue ("stop at chest height") is deliberately conservative.
- **Contrast:** the teal numbers and last cover line are 3.8:1 on the card (fine for large text, below 4.5). White on the teal `OR` badge is about 4.2:1 by hand (the tool measures against the card behind and reports 1.1). White on the red pill reads 4.4:1.
- **Placeholder brand mark** `VERDE FIT`: replace with the real handle.
- **TikTok AI-generated content label** on when posted.

## Owner verdict
**Success** (Love, 2026-09-25). This is an overall verdict: no per-question scores were given and no changes were requested. It is recorded separately from the tester ratings below, because the Deliverables (section 6) count the testers' scores toward the 4.0 average.

## Tester ratings (1–5)
Pending: (1) follows the pillar's format · (2) sounds like our style · (3) usable with light edits.

## Feedback
- Owner (2026-09-25): rated the run a success; no changes requested. The reusable lessons are in the pillar's `learnings.md` (`content-bank/P005-muscle-by-muscle-exercise-picker/learnings.md`).
- Still open from the known limits above: someone who trains should check the exercise drawings, the placeholder handle `VERDE FIT` needs replacing, and the sound is not chosen.
