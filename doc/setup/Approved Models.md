# Approved models · owner's list (2026-10-06)

Claude reads this before any paid generation call. **This file wins** over model lines in older files (`.claude/skills/amplify/SKILL.md` still names Nano Banana Pro as the only stills default; that line is older than the 2026-10-05 model test).

If a model is not on the approved list, don't call it. Don't switch to a cheaper model to save credits either. The owner's rule is "best models, not cheap ones". If an approved model fails twice on the same shot, stop and ask the user. Don't try models that aren't on the list.

## 1. The Claude model that runs the skills

| Use | Model |
|---|---|
| Every Amplify session | **Claude Opus 5.5** (`claude-opus-5-5`), picked in the model picker |

- Don't use Sonnet, Haiku, Fast mode, or a low effort setting for content runs. The owner's results were all made with Opus 5.5.
- If you are not Opus 5.5, say so in your first reply, before doing anything else.

## 2. Image and video models (all called through `tools/kie.py`, nothing else)

| Job | Approved model | `kie.py` call | Notes |
|---|---|---|---|
| Illustrated art, mascots, model sheets, designed-card art | **GPT Image 2.5 Sunburst** | `kie.py image --model gpt25s --resolution 2K` | Won the 2026-10-05 still test. Aspect 4:3, 3:2 or 2:3 at 2K; square only renders at 1K |
| Photoreal persona photos (Willow and other human personas), motion-transfer stills | **Nano Banana Pro** | `kie.py image --model nbp --resolution 2K` (4K for motion stills) | Best identity hold with persona refs, up to 8 refs |
| Edit pass on a persona still (less polished skin, real teeth) | **Seedream 5.0 Pro** | `kie.py image --model sd5` | Only as the edit step after `nbp` (SKILL step 7, motion stills) |
| Image-to-video shots, reels | **Seedance 2.5** | `kie.py video --model seedance25` | Default since 2026-10-05. 4 s minimum |
| Motion transfer (persona copies a source video) | **Seedance 2.5**, reference mode | `kie.py video --model seedance25 --ref <still> --ref-video <driver>` | Owner's pick from the 5-model test. Prompt template in SKILL step 7.5 |
| Fallback only | Kling 3.0 / Kling 3.0 Motion Control | `--model kling3` / `kie.py motion --model kling3-mc` | Only when the user asks for the cheaper option, or Seedance can't take the input (e.g. driver limits). Say which and why in `review.md` |

## 3. Not approved without the owner's OK

`nb`, `nb-edit`, `nb2`, `gpt25f`, `gpt2`, `wan3`, `h3`, `omni11`, `kling26-mc`, `wan-move` are in `kie.py` for tests only.

Also not approved: any image or video model outside `kie.py`. That includes Gemini or ChatGPT in a browser, Midjourney, DALL-E, Canva AI, Claude drawing SVG art in place of a generated image, and stock photos.

## 4. Check before you finish a run

- Every model in the run's `costs.json` is on the approved list. List them in `review.md` under "models used".
- Text on slides came from `cards.py`, `tipcards.py`, `overlay.py`, `boxlist.py`, `textclip.py` or `reel.py`, never from the image model. Prompts end with "no text, no letters, no numbers, no logos".
