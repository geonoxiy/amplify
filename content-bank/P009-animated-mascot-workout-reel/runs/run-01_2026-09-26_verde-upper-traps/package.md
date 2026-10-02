# P009 · run 01 · Verde · The Perfect Upper Traps Workout

**Mode:** Trend rider · **Caption style:** none (no brand anywhere, no disclosure). Pillar = format (16 s, 6 hard-cut shots of 2.7 s, a tracker that ticks once per exercise, title and exercise name in code). Persona = Verde (`personas/verde.md`), the original mascot, so the source's own character is never copied.

## Hook
On screen: `The Perfect Upper Traps Workout` (the pillar's formula `The Perfect [Muscle group] Workout`, kept as the trend; word overlap with the source title is 60% by design). Verde is already mid-rep at 0 s; the title and tracker fade in between 0.15 and 0.9 s.

## Shots (2.7 s each, hard cuts, locked camera)
| # | Exercise | Sets × reps on screen | Tick lands | Animation |
|---|----------|----------------------|-----------|-----------|
| 1 | Dumbbell Shrug | 2-3 x 8-12 | 1.2 s | shoulders rise and drop, arms stay down |
| 2 | Barbell Shrug | 2-3 x 8-12 | 3.9 s | same with a barbell |
| 3 | Cable Upright Row | 2-3 x 10-12 | 6.6 s | bar lowers to the thighs and returns to chest height |
| 4 | Dumbbell Shoulder Press | 2-3 x 8-10 | 9.3 s | seated press overhead and down |
| 5 | Farmer's Carry | 2-3 x 30 sec | 12.0 s | walking in place, two weights |
| 6 | Suitcase Carry | 2-3 x 30 sec | 14.7 s | walking in place, one weight |

Tracker: 6 identical Verde back-view icons with the upper traps in red (one muscle, so the icons repeat; the source varied them because each exercise hit a different muscle). Ticks are Verde teal.

## Caption and hashtags (`caption.txt`, style none)
`The perfect upper traps workout in 6 exercises!` + `#trapsworkout #upperbodyworkout #gymworkout #hypertrophy #shoulderday`
TikTok's AI-generated content label ON when posted.

## Production (what was actually run)
- **Start frames:** Verde stills from P005 run-01 (already generated, owner-approved run), multiply-blended onto the Verde card background with the top 42% and bottom 20% empty (`reel.py frames`). No new images bought.
- **Animation:** Kling 3.0 image-to-video via kie (`kie.py video --model kling3 --mode std --duration 3`), 720×1280, 24 fps, silent, trimmed to 2.7 s. 8 clips generated for 6 shots (2 rejected takes, below). 42 credits ($0.21) each.
- **Assembly:** `reel.py render`: hard cuts, 30 fps, scaled to 1080×1920, title, tracker and exercise text drawn in code (DIN Condensed Bold, Verde palette), H.264, no audio.
- **Cost:** 336 credits = **$1.68**. `costs.json` has every call.
- **Rejected takes:** shot 1 first try (curled the dumbbells to the shoulders), shot 3 first try (pushed the bar overhead behind the head). Both kept in `raw/` with the reason in the file name.
- **Output:** `output/reel.mp4` (16.2 s, 1080×1920, silent), `output/preview.jpg`, `output/reel_timing.json`, `output/video_check.json`.

## Posting
Add a trending sound in TikTok (the file is silent on purpose: third-party music can't be shipped). Caption as above. No brand, no logo, no link.
