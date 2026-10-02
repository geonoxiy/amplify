# P012 learnings

Feedback from runs, turned into general rules.

## From run-01 (2026-09-27, my own notes, not owner feedback)
- **Nano Banana Pro ignores numeric framing for a face.** Two prompts asked for the eyes at about 22% of the frame height; the results had them at 40% and 52%, and "cut off the top of the head" made the face bigger and lower. Fix it in code instead: shift the still up, crop the empty top, extend the dark cloth at the bottom by mirroring a blurred band with matching noise. It only works when the lower part of the frame is near-black.
- **Very dark stills animate well.** Kling kept the face, the lamp and the darkness steady for 5 s with "almost perfectly still, one slow blink"; darkness hides small artifacts, but check the eyes and mouth.
- **Yellow text with no outline** needs a dark area under it: `textclip.py --fill "#fcffb0" --stroke 0` over the black top gives 19:1 contrast.
- **Words:** function words alone put a short rewrite near 28% overlap. Replace contractions (`you'll` to `you will`), drop shared verbs, and re-measure; text changes cost nothing because the video is not regenerated.
- **The credit line is a claim.** Credit a non-clinical source and claim no outcome (see the pillar's Do / Don't).
- **Sound:** "Younger Years" is a commercially released song flagged copyrighted and not commercial-library; keep the silent cut as the one to post.
