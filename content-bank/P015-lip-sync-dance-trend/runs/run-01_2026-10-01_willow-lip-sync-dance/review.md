# P015 run-01 · review

**Deliverable:** `output/final.mp4` (13.3 s, 1080×1920, 30 fps, silent). Caption: `caption.txt` (style none, PASS).

## Owner feedback on the first finished version (2026-10-01)
"why are there floating figures in the foreground? the replica looks too much like ai … the camera should not be moving so much. it did not copy the original well." Then: layers (background, character, foreground); background different but realistic; character more real; nothing added to an empty foreground; follow the original's angle and placements. That version (`raw/motion_trim/final_v3_REJECTED-…mp4`) is kept for reference.

## What changed for the final, by layer (numbers from code)
| Layer | Original | Rejected version | Final |
|---|---|---|---|
| Foreground | empty | invented heads, hands and a band (from my prompts) | empty: one person in 100% of frames (kie's minimal prompt) |
| Character | real person | Willow from the old cheap-model ref, sharpness 167 | Willow from the new 4K unretouched ref with specific traits, sharpness 633 |
| Background | sunlit brick alley, saturation 33% | clean mews, flat even light, saturation 22% | lived-in London back passage, low sun on one wall, saturation 28% |
| Camera | locked after the opening (0.00 to 0.03% shift) | digital pull-back + model drift (zoom 4.4%/s) | locked (0.00 to 0.01% shift) |
| Placement: nose height | 48.8% | 32% | 51.2% |
| Placement: body centre | 46.7% | 50% | 47.7% |
| Placement: torso size | 23.4% of the height | 30% | 26.1% |
| Brightness / contrast | 48.6 / 18.8 | 57 / 23 | 50.0 / 20.4 |
| Noise | 1.7 | 1.0 | 2.1 |

**Movement (`motion.py check`):** pass, mean limb angle error 7.4° (arms 9.4, legs 9.8, torso 2.4, head 5.1), lag 0.07 s, no frame within phash 10 of the source or the driver (closest 18 and 22).

## 7-point format check
1. Structure: one take, no cuts ✓ (13.3 s; the source's 1.2 s opening pull-back is cut, see limits)
2. Hook: the dance starts on frame 0 ✓; the face-first close-up open is not reproduced
3. Camera & motion: locked camera, same placement and angle, same moves ✓
4. Pacing: same beats (driver is the source's own timing) ✓
5. Text overlay: none, as the source ✓
6. Audio: silent; pick the trending sound in TikTok and start it about 1.6 s in
7. Arc: confident, playful performance ✓

## Originality
New person (fictional Willow), new place, new outfit, no source frames. The choreography is the creator's and is credited in the caption (`dc @aishahdv`).

## Known limits
- Willow is about 11% larger than the original dancer (torso 26.1% vs 23.4%): Kling enlarges the still's subject slightly. Next time crop the still about 10% wider.
- The opening pull-back (source 0.4 to 1.6 s) is left out; adding it back as a digital zoom is what made the camera feel restless.
- Saturation 28% vs 33%: the new place has more cream render than orange brick, so a full match would push colours unnaturally.
- Sound sync depends on starting the sound about 1.6 s in when posting.

## Cost
1,491 credits ($7.46) in this run: 3 stills ($0.30), 5 motion clips ($7.16, the last at 1080p). Plus Willow's new face ref ($0.12). The 720p price is measured (280 credits per 14.6 s); 1080p came in at 351 credits per 13.4 s.

## Tester ratings
Pending.

## Round 3 (owner, 2026-10-01): "the teeth looks distorted sometimes as well as the face … still looks too polished and unrealistic"
Owner shared a realism checklist (character sheet with several angles, human imperfections, realism-tuned image models, feed the base image back, texture enhancement after generation, natural movement).

**Changed:** Willow character sheet `personas/willow/refs/sheet_real.png` (front, three-quarter, profile, laughing close-up with her own uneven teeth); starting still edited with **Seedream 5.0 Pro** (`kie.py --model sd5`, 14.5 credits) from the round-2 still + the sheet: open laugh with her real teeth, more skin texture (Nano Banana Pro's version gave even, veneer-like teeth); two 1080p takes; new tools `motion.py faces` (face close-ups every 3 frames, distortion flags) and `motion.py splice` (best-of takes); the camera lock now aims at the middle of the model's drift.

| | Round-2 final | Round-3 final (take B) |
|---|---|---|
| Faces flagged by `motion.py faces` | 13% of samples | 7.5% (10 of 134) |
| Movement error | 7.4° | 7.4° |
| Camera | locked | locked (0.03 to 0.23% shift), 3.5% crop |
| Sharpness / noise (source 727 / 1.7) | 633 / 2.1 | 653 / 2.0 |
| Saturation (source 33) | 28 | 28 |
| Placement: nose / centre / torso (source 48.8 / 46.7 / 23.4) | 51.2 / 47.7 / 26.1 | 49.8 / 50.1 / 27.1 |

**Take A** had 8 flagged faces but Kling gave it a made-up camera move (pans of about 6% and a 9% pull-back); locking it needed a 15% zoom that enlarged and softened Willow, so it is unused (`raw/motion_trim/final_v6a_UNUSED-…`). Takes differ in camera behaviour: measure each before choosing.

**Still there:** short face smears (about 0.2 to 0.3 s each) at 1.6, 4.8, 5.4 to 5.7, 6.3, 7.4 and 11.1 s: the source's spins, hair flips and head throws. Both takes fail at the same moments, so they come from the source's speed at this face size (about 150 px tall), not from chance. Willow is a little larger (torso 27.1%) and to the right (50.1%) than the source: Seedream drew her slightly bigger. Topaz video upscale failed twice on kie's side (500, 0 credits).

**Round-3 cost:** 762 credits ($3.81): sheet and still $0.19 (+ $0.12 face ref earlier), two 1080p takes $3.51. Run total 2,231.5 credits ($11.16) + $0.24 persona refs.
