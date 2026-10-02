# P004 learnings

Feedback from runs, turned into general rules.

## From run-01 (2026-09-24, user feedback)
- **Personas are visual only (face + body frame).** Personality and lifestyle details pulled the output away from the source format. The pillar and its source post decide clothes, vibe, setting, pose and hook.
- **Slide 1 must carry the laid-back, quirky energy:** baggy clothes, a candid or goofy selfie angle (lying down, odd crop, playful face or prop), with the hook text overlay.
- **Slide 2 must hide the figure:** oversized, baggy clothes top and bottom.
- **Slide 3 must reveal the silhouette:** a fitted, sultry going-out look and a more confident pose. That contrast is the whole payoff; a "style upgrade" isn't enough.
- **Realism beats polish:** images must look like real phone photos: imperfect or mixed lighting, noise, slight blur, a lived-in or messy room, no styled-set look. Add phone-camera artifacts in code after generation.

## From run-02 (2026-09-24, user feedback)
- **Text overlay must match the source exactly.** TikTok Classic: white text with a thick black outline (no soft shadow), centred, tight leading, curly quotes, block centred at about 37.5% of the height, first line about 73% of the width, wrapping to 4 lines. The tool defaults in `tools/overlay.py` are calibrated to this. **Keep the source's hook wording as-is** (user: hooks are the trend already); originality comes from the images only, so the 30% hook-overlap rule doesn't apply to P004 runs.
- **Slide 1 pose should be its own, not a clone.** Keep the energy (lying down, odd angle, smug side-eye), change the prop, setting and pose. It must be a true front-camera selfie: no phone visible in shot. Put the face in the lower half so the hook text lands over the background, not the eyes.
- **Use the best image model** (Nano Banana Pro, 2K). Cost is not the constraint.
- **Busy, lived-in backgrounds in all three slides**: laundry piles, cables, glasses, unmade bed, mirror dust. Clean, empty rooms read as AI.
