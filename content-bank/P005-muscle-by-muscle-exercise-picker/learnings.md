# P005 learnings

Feedback from runs, turned into general rules.

## From run-01 (2026-09-25, Verde · upper traps): the owner rated the run a success
The owner's verdict is an overall "success" (no per-question scores, no changes requested). What that accepts, so repeat it:
- **A Trend rider run keeps the source's format and replaces its character and look.** The source mascot is the source account's own brand character, so the run used a new original mascot (`personas/verde.md`) with its own colors and fonts. Structure, hook formula and layout geometry carry over unchanged.
- **A single-muscle topic becomes per-job slides.** P005 gives one slide per muscle. For one muscle (the upper traps), each slide covers one job of the muscle (lifting, pulling, holding, overhead) with two exercise options. The fixed parts stay: problem hook → anatomy overview → picks, `#N` heading + sets × reps + `OR` badge, and no CTA when there is no product.
- **Short body copy:** 17 to 21 words per pick slide, second person, no emoji. The hook follows `[BODY PART] [PROBLEM WORD]?` and is checked in code against every source hook (under 30%).
- **The production loop that worked:** a model sheet first, attached to every image; art on a plain white background with no text; text and layout drawn in code (`tools/cards.py`); every figure looked at by eye; originality checked in code (`tools/originality.py`).

Production rules learned during the run (from the run itself, not separately reviewed by the owner):
- **Ask for exactly one highlighted region and check it.** The model colors a whole muscle group even when asked for one part (the first two covers did). A stricter prompt, a second reference showing the exact area, and "nothing lower" fixed it. If it still fills the wrong area, recolor in code (hue and saturation only) or merge the regions and label them honestly (the anatomy slide says "MID + LOWER TRAPS" because the model filled the lats as "lower trapezius").
- **Ask for a wide composition** ("both arms fully inside the frame, nothing touching an edge") when arms or props risk being cut by the image edge; a cut limb shows as a hard vertical line on the card.
- **Check every exercise figure.** A prompt for one exercise can produce another (an upright row came out as a biceps curl). Say "exactly symmetrical front view" and what each arm does; say "nothing else in the scene" to stop it adding racks and benches.
- **Generate on plain white and multiply-blend onto the card,** after snapping the near-white noise to pure white; otherwise a faint speckle band shows.
- **Contrast:** the accent teal on the chalk card is 3.8:1, which is fine for large text only. Keep small text in the gray or navy.

Still to check in later runs: the exercise drawings by someone who trains (the landmine press and the dumbbell shrug are approximate), the placeholder brand handle, and the sound (not chosen).
