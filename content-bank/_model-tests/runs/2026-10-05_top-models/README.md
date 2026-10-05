# Top-model test, 2026-10-05

Same brief on every model, to learn how each one behaves on our content before writing the model guide (doc/Model Guide and Prompt Templates.md).

1. Stills: `prompt_still.txt` + refs (real_face, sheet_real, rooms/kitchen) on nbp 4K, gpt25s 4K, gpt25f 4K, gpt2 4K, nb2 4K, sd5 2K; 2 takes each.
2. Image-to-video: the best still as first frame, 6 s, same prompt, on seedance25, wan3, h3, omni11, kling3.
3. Motion transfer: P015 driver, first 10 s, Willow P015 still; kling3-mc vs seedance25, h3, wan3, omni11 reference mode.

## Status when paused (2026-10-05)
- Stills done ($0.90): `stills_sheet.jpg`, `faces_sheet.jpg`, `stills_measures.json`. GPT Image 2.5 Sunburst best on brief adherence (waist-up, gesture, hard warm sun, leaf shadows), 2/2 usable, most phone-like noise (1.5 vs 0.72 for Nano Banana), cheapest at 4K (16 vs NBP 24). NBP t2 and Seedream t1 drew the phone because the prompt named the iPhone on the sill: describe the viewpoint, never the device. Face proportions of frontal takes all within the refs' own spread (GPT 2.5 Flare closest). Nobody pushed the sleeves up.
- Motion test: Seedance 2.5 done, billed 1900 credits = (10 s reference + 10 s output) x 95 (kie.py guard fixed). Kling MC, Wan 3, H3, Omni were still rendering; logs in `motion/`.
- Next: score motion clips (`motion.py check inputs/driver10.mp4 <clip>`, `faces`, scratch evalvid.py for camera/wobble), run `run_i2v.sh` (not started, ~$7), then write doc/Model Guide and Prompt Templates.md.

## Owner verdict (2026-10-05)
- Motion transfer: **Seedance 2.5 is the most accurate**, so it is the main video model. Costs: Seedance 1900 credits, Wan 3.0 640, Kling MC 270, MiniMax H3 260, Gemini Omni 168 (Wan and H3 also bill the reference seconds).
