# P015 learnings

Feedback from runs, turned into general rules.

## From run-01 (Willow, 2026-10-01): production rules for motion transfer

- **Cut a camera pull-back out of the driver.** When the source opens on a face close-up and pulls back, a driver that keeps the close-up makes Kling invent a body in front of the camera (v1: a head and arm in the foreground; v2: a blurry band across the bottom). Start the driver after the pull-back (here source 1.6 s, found from where the shoulder width stops shrinking) and rebuild the face-first open in post with `motion.py finish --pullback 1.2 --zoom 1.8`.
- **Kling keeps the still's framing, not the driver's.** A full-body still gave a small Willow in a big frame. Render or crop the still to the driver's framing (knees up here).
- **Nano Banana copies the composition of an attached reference.** Asked for "closer framing than image 2", it returned image 2's full-body framing. To change the framing of a still, crop it in code (keeps the face exact, free).
- **Never put the camera person in a prompt.** "Filmed by a friend" produced the friend. Describe only the subject and the place.
- **The motion score can't see a blurry extra person.** All three clips passed `motion.py check` (7 to 8 degrees) while a foreground head was visible; only looking at frames caught it. Always look at a strip of frames every 0.5 s, bottom edge included.
- **Sound sync after a trimmed driver.** The final video starts at source 1.6 s, so in TikTok start the trending sound about 1.6 s in for the moves to land on the same beats.

## From run-01 round 2 (owner feedback 2026-10-01: "floating figures", "too AI", "camera moves too much", "follow the angle and placements")

The owner's frame: **layers. background, character, foreground.** Change the background and the character, keep the foreground as empty as the source, and keep the source's camera angle and the person's placement.
- **Foreground: the floating figures came from the prompt.** v1 ("filmed by a friend") drew the friend; v2 and v3 ("no hands, heads or objects in the foreground") drew heads and hands. v4 with kie's minimal prompt only ("No distortion, the character's movements are consistent with the video.") had a clean foreground for all 13 s. Use the minimal prompt; put the scene in the still, not the prompt.
- **Character: the AI look came from the persona reference.** Willow's old `front.png` was made with the cheap model; every render inherited its smooth skin. New ref `personas/willow/refs/real_face.png` (Nano Banana Pro 4K, unretouched phone selfie wording, specific traits: moles, freckle cluster, pores, flyaways). Traits are in `personas/willow.md`.
- **Background: describe a specific, lived-in real place with directional light** (stains, moss, a drainpipe, a bin, low sun on one wall), and check it in numbers against the source (`measure.py` visual measures: sharpness, noise, saturation, clutter). The mews still read flat because it was evenly lit, clean and soft.
- **Placement: match the source's median placement, measured.** Source (after the pull-back): nose at 48.8% of the height, body centre 46.7% across, torso 23.4% of the height, vanishing point 49%, 49% (right behind the head, so the phone was held level at eye height). Render with a layout guide (grey silhouette from the pose model's segmentation + perspective lines, no source pixels) and crop the 4K still in code to the exact numbers.
- **Camera: the source camera is static after the pull-back** (ORB match between 0 s and 6.7 s: 0.02% shift, scale 1.000, 1431 inliers). `measure.py camera_motion` reported 2.5% w/s for it because a large dancing body reads as camera motion: don't trust that number when the person fills the frame. Lock the generated camera with `motion.py finish --camera static`; no digital pull-back.

## From run-01 round 3 (owner: "teeth and face distorted sometimes", "still too polished")
- **Teeth need a reference.** A closed-mouth still makes the video model invent teeth every frame. Start from a still with her own teeth showing (laughing close-up in the character sheet, then edit the still to an open laugh).
- **Seedream 5.0 Pro (`kie.py --model sd5`) looks less polished than Nano Banana Pro for skin and teeth** in the same edit (NBP gave even veneer-like teeth); cheaper too (14.5 credits at 2K).
- **Fast spins, hair flips and head throws smear the face** in every take (about 150 px face at knees-up framing). Pick sources with fewer of them when realism matters, or expect 0.2 to 0.3 s smears there. Adding motion blur does not hide it: our face is already blurrier than the source's at speed (measured).
- **Kling sometimes invents a camera move** (one take panned 6% and pulled back 9%). Measure each take's camera (`motion.camera_path`) before choosing: a locked camera on a moving take needs a big zoom.
- **Look at faces, don't trust the flags alone:** `motion.py faces` catches warped proportions, not smeared features.

## From run-02 (Willow car-park dance, @zaralarsson source, 2026-10-01)
- **A person walking towards or away from the camera:** match the still to where they stand when the driver starts (`motion.py layout --at start`), not their average placement.
- **Open scenes have no vanishing point:** the far ground edge shows the camera height (`layout` now detects it, draws it in the guide and states it in the prompt). Nano Banana Pro kept the camera at chest height or overdid a worm's-eye view; Seedream 5.0 Pro matched "phone at hip height, head and shoulders against the sky".
- **Kling pans to follow a person who comes close** (both takes, 10% and 22%), even when the source camera is still. Locking it costs a big zoom; filling the uncovered edge shows a seam when the scene has depth (parallax). Until there's a fix, offer the owner the follow-pan version and the zoomed lock side by side.
- **The face check is unreliable when the person is small or turned away:** run it on the driver too and compare (here both found a face in ~68% of samples), then judge by eye.

## Model test (2026-10-05, owner verdict)
- **Seedance 2.5 is the most accurate motion-transfer model** of the five tested on a 10 s cut of the run-01 driver (Kling 3.0 Motion Control, Seedance 2.5, Wan 3.0, MiniMax H3, Gemini Omni 1.1). It is now the main model (SKILL step 7.5); Kling Motion Control is the fallback. Log: `content-bank/_model-tests/runs/2026-10-05_top-models/`.
