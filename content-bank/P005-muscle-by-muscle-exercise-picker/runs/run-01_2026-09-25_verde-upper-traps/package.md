# P005 · run 01 · Verde · upper traps

**Mode: Trend rider.** The pillar (P005) controls the format; the persona (`personas/verde.md`, a light profile) controls the look. The source account's mascot is its own brand character, so it is not reused: Verde is a new original character in the same comic style, with our own card colors and fonts. Rendered slides: `output/slide1-6.png` (4:5, 1080×1350), contact sheet `output/preview.jpg`.

## How the pillar and the topic combine
P005 is "one slide per muscle, 2 to 3 options each". The topic is one muscle, so the per-muscle slides become **per-job slides**: the upper trapezius does four things, and each gets a slide with two exercise options. Everything else follows the pillar: problem hook over the mascot, anatomy overview, `#N` heading + underline + short paragraph + sets × reps + two illustrated options joined by an `OR` badge, no CTA (Trend mode has no product), 6 slides, second person, no emoji.

## Hook
`FLAT` / `TRAPS?` (formula `[BODY PART] [PROBLEM WORD]?`, 2 lines: navy, then accent). Options checked in code against every source hook (rule: under 30% shared words):

| Option | Shared with any source hook |
|---|---|
| **FLAT TRAPS?** (used) | 0% |
| NO TRAP SLOPE? | 0% |
| YOUR NECK LOOKS THIN / HERE'S HOW TO FILL OUT A HOODIE | 45% (your, here's, how, to, a): rejected, it copies the "problem, then here's how" frame word for word |

## Slides
| # | Role | Visual | Text on screen |
|---|------|--------|----------------|
| 1 | Hook | Verde from behind in a rear double-biceps pose, both arms fully in frame, cropped at the belt line and bleeding off the bottom edge. Only the upper-trapezius slope (neck to shoulder tips) is filled red. | `FLAT` / `TRAPS?` |
| 2 | Anatomy | Verde's back view, head to mid-thigh. Upper trapezius red, the rest of the trapezius (middle and lower) yellow. Elbow leader lines run from two pills to the regions. | `Trap Anatomy` · `The upper traps run from your neck out to your shoulders. They lift and rotate your shoulder blades.` · pills `UPPER TRAPS` (red), `MID + LOWER TRAPS` (yellow) |
| 3 | Pick 1: lifting | Two figures: dumbbell shrug and barbell shrug, shoulders shrugged high. | `#1 Shrugs` · `2-3 Sets x 8-15 Reps` · `Shrugs train the upper traps' main job: lifting your shoulders. Pause at the top, then lower slowly.` · `Pick either:` · captions `Dumbbell Shrug`, `Barbell Shrug` |
| 4 | Pick 2: pulling | Cable upright row (side view, elbows above hands) and dumbbell upright row (front view, symmetrical). | `#2 Upright Rows` · `2-3 Sets x 8-12 Reps` · `Pulls that end with your shoulders lifting also load the upper traps. Lead with your elbows and stop at chest height.` |
| 5 | Pick 3: holding | Farmer's carry (two dumbbells) and suitcase carry (one dumbbell, torso level). | `#3 Carries` · `2-3 Sets x 30-60 Seconds` · `Holding a heavy load keeps the upper traps working the whole time. Walk tall and don't let your shoulders sag.` |
| 6 | Pick 4: overhead | Seated dumbbell shoulder press at lockout and a landmine press. | `#4 Overhead Press` · `2-3 Sets x 6-10 Reps` · `Pressing overhead turns your shoulder blades upward, and the upper traps help. Press until your arms are fully overhead.` |

Body copy is 17 to 21 words per slide (pillar rule: up to 26). The anatomy claims are the standard ones: the upper trapezius lifts and upwardly rotates the scapula; carries load it isometrically. The exercise cues are general technique, not medical advice.

## Caption and hashtags
Caption: `Flat traps? Build a bigger upper-trap slope with these lifts!` (0% shared words with the four source captions) · `#uppertraps #trapworkout #trapday #shrugs #hypertrophy` · TikTok AI-generated content label on. Replace the placeholder wordmark `VERDE FIT` with the real handle first.

## Production (what was actually run)
- **Model:** Nano Banana Pro (`nbp`, 2K, 18 credits = $0.09 per image), the best image model available on kie.
- **Character:** one model sheet (front, side, back) generated first and attached as a reference to every later image, so Verde stays the same across all 10 slide images (cover, anatomy and the 8 exercises). The cover also carried the anatomy diagram as a second reference.
- **Images:** cover (3 tries), anatomy overview (1), 8 exercise illustrations (2 redone: one showed a biceps curl instead of an upright row, one added a rack and bench). All on a plain white background, no text.
- **What went wrong and how it was fixed:**
  - The model colors the whole trapezius kite red even when asked for the upper part only. The first two covers did this; the third, with a stricter prompt, a second reference and a "wide composition" instruction, came out right, so the cover needed no repair.
  - In the anatomy diagram it filled the lats purple as "lower trapezius". The purple was recolored to the body teal in code (`postprocess.py`, hue and saturation only, outlines and shading kept), and the yellow region is labelled "MID + LOWER TRAPS".
- **Text and layout:** drawn in code by `tools/cards.py` (DIN Condensed Bold and Avenir Next, installed system fonts) from `spec.json`, using the pillar's geometry. Art is normalised to a pure-white background and multiply-blended onto the card. The renderer writes a visual-model record per slide (`output/records/`).
- **Checks:** `tools/measure.py check` (0 box problems; text contrast in `output/boxcheck/`), `tools/originality.py` (`output/originality.json`).
- **Cost:** 14 paid images in this run = 252 credits ($1.26), plus the persona sheet 18 credits ($0.09). Total $1.35.
- **Not rendered:** the sound (a trending sound is picked at posting).

## Posting
Any time; the source account's posts cluster around 09:00 Manila time. Trending sound at posting. Add a caption line asking viewers to use a load they can control if you want a safety note (not part of the format).
