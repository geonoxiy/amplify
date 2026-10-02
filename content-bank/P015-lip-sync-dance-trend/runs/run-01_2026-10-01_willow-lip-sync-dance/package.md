# P015 run-01 · Willow lip-sync dance

**Request (2026-10-01):** "https://vt.tiktok.com/ZSbUWSYhp/ replicate this video with wellness willow". Mode trend (the sound and the moves are the trend), caption style none, no brand.

## How pillar and persona combine
- **Pillar P015 (format):** one 15 s take, face-first open with a pull-back, knees-up dance with arm and hand choreography, exaggerated lip-sync faces, eye contact, no on-screen text, a trending song.
- **Persona Willow (look only):** her face, hair, freckles and gold hoops from `personas/willow/refs/front.png`. She is fictional; the AI label goes on when posting.
- **Moves:** transferred from the source dancer (@aishahdv) by motion control, credited in the caption. Nothing else of the source is reused: new person, new place, new outfit, no source frames.

## Shot plan
| # | Time | What happens | Source of it |
|---|------|--------------|--------------|
| 1 | 0 to 14.6 s | Willow dances and lip-syncs in a sunny cobbled London mews (cream and pastel house fronts, potted plants, a bicycle), filmed handheld at chest height | Moves: `raw/motion/driver.mp4` (source 0.4 to 15.0 s). Look, outfit and place: `raw/stills/willow_start_v1.png` |

- **Outfit:** oversized sage-green fleece zip jacket, cream wide-leg joggers, white trainers, gold hoops (source: pale plaid track jacket, grey joggers, headphones; same oversized, comfy register, different items).
- **Place:** a mews lane instead of a brick alley; it keeps the narrow-lane framing with a vanishing point behind her head.
- **Text on screen:** none (as the source).
- **Sound:** silent export. Pick the source's trending sound in TikTok (sound ID `7684719903756045069`); that is the licensed way.

## Production
1. `motion.py scan` on the source: one 14.6 s usable segment (one person, head to waist in frame, no cuts), measured full body, travelling, about 1.1 hits per second.
2. `motion.py driver --segment 1` → `raw/motion/driver.mp4` (720×1280, 30 fps, silent), no warnings.
3. Still: Nano Banana Pro with the Willow ref, neutral standing pose, both hands visible, knees-up-or-wider framing (`raw/stills/willow_start_v1.png`). The driver opens on a face close-up and pulls back, so the start frame's pose (a close-up) and the first knees-up frame (mid-wave, one arm out of frame) were both poor still poses; a neutral full view gives the model the whole body.
4. `kie.py motion` (Kling 3.0 motion control, 720p, orientation video) → `raw/motion/clip_v1.mp4`.
5. `motion.py check` → `raw/motion/clip_v1_motion_check.json` and `_compare.jpg`; then scale to 1080×1920 → `output/final.mp4`.

## Caption
`the confidence was sent from above 🙏✨ dc @aishahdv` (style none, `caption.py check` PASS). Riffs on the source caption's theme without its words; `dc @aishahdv` credits the dance. No hashtags, as the source.

## Posting
- TikTok AI-generated label **on** (Willow is AI).
- Add the trending sound in the editor.
- The source posted Friday 16:30 Manila; this format is like-driven, so any evening slot works.
