# Owner rules

Feedback the owner gave across runs (2026-09-24 to 2026-10-06) that applies to every run, collected in one place so every machine follows the same rules. Most are also in `.claude/skills/amplify/SKILL.md` and `.claude/skills/amplify-plus/SKILL.md`; where those files go into more detail, they win.

## Text and style
- **Text is drawn in code.** The image model never writes text, numbers or logos (it garbles them, and the layout must match the pillar's measured boxes).
- **lowercase everywhere, no em dash, en dash, colon or semicolon** in hooks, headings, subheadings, overlay text and captions (2026-09-29). Real brand and product names keep their capitals. `caption.py check` fails on the punctuation.
- **Emoji when they fit** (2026-09-29), in captions and overlay text (`overlay.py` draws them in colour).
- **Hooks are the trend.** Keep the source's hook mechanic and its formula phrase ("i wish i knew these … sooner", "in case nobody told you"); everything after the formula must be new. Stay in the source's register: common social media phrasing, not oddly specific invented details (2026-09-28).

## Images and video
- **Best models, not cheap ones.** Stills: GPT Image 2.5 Sunburst (`kie.py image --model gpt25s`, won the 2026-10-05 test; aspect 4:3, 3:2 or 2:3 at 2K, square only at 1K) or Nano Banana Pro (`nbp`). Video and motion transfer: Seedance 2.5 (`seedance25`, owner 2026-10-05); Kling 3.0 is the cheaper fallback.
- **Photo-style images look like real phone photos:** grain, uneven light, soft focus, lived-in cluttered places, partial crops; `overlay.py --phone` on every photo slide (2026-09-28).
- **The scene that carries the hook is format** (a clinic, a gym, a desk): recreate that kind of place even when a persona is named (boss test, 2026-10-05).
- **Fictional people only.** Never a real person's likeness, celebrity or otherwise. Personas live in `personas/`.
- **Mascot accounts:** make an original mascot (model sheet first, attached to every image). Never redraw the source's mascot. A faceless source mascot means a faceless new one.

## Brands and selling
- **Caption styles** (2026-09-26): none = no brand anywhere; soft = trend callback, then a bridge that names the brand; hard = the product is on the image or video and in the caption, with the brand's call to action. Soft and hard end with "this is an advertisement." as the last line.
- **Put the product where the source does** (as one tip in a list, a bonus tip, a prop), surrounded by genuinely useful tips (2026-10-05).
- **Real brands:** screenshot their real site (`webshot.py`, `mockup.py`); leave out pages that show other companies' products or real people's faces. Only claims from the brand file; no income promises; no fake credentials ("as a dentist"); no prescription-medicine names (UK ad ban) (2026-09-28 to 2026-10-05).
- Real regulated brands need their own sign-off before posting; say so in `review.md`.

## Process
- Numbers come from code (`measures.json`, `stats.json`, the check tools); judgment from Claude. Say which is which.
- A pillar stays `draft` until the owner says "approve". A successful run doesn't approve it.
- Owner verdicts go into the run's `review.md` ("Owner verdict") and the reusable lesson into the pillar's `learnings.md`.
- TikTok's AI-generated label and commercial content toggle are switched on when posting.
