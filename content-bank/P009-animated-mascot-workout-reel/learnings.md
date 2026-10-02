# P009 learnings

Feedback from runs, turned into general rules.

## From run-01 (2026-09-26, my own notes, not owner feedback)
- **Image-to-video models embellish exercises.** With a plain "do a shrug" prompt Kling curled the dumbbells to the shoulders; an upright row became an overhead press. What worked: say exactly which body parts move and which never move ("only the shoulders move, the elbows never bend"), name the wrong movements ("NOT a curl, NOT a lateral raise"), cap the range ("the bar never goes above chest height"), and when the first frame already shows the top of the rep, describe the rep starting from there. Always watch every clip.
- **Trim, don't stretch.** Kling makes whole seconds only (3 to 15); ask for 3 s and cut to the pillar's 2.7 s.
- **Kling's first frame jumps to its second.** Harmless on a hard cut; the checker merges cut detections within 0.25 s.
- **Start frames from the still library.** Reusing already-approved stills (P005 run-01) composed onto the card background gave a consistent character and cost $0 for images.
- **Cost:** about $0.21 per 3 s clip on Kling 3.0 std (42 credits); a 6-shot reel is about $1.26 if every take works, $1.68 here with 2 retakes.
- **The finished-file host may not resolve** (`tempfile.aiquickdraw.com`); `kie.py video` now falls back to kie's signed download link.
