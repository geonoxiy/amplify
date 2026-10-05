---
name: amplify-account-copy
description: "Copy a whole TikTok or Instagram account's content system for the user's own brand or account (e.g. 'copy @bluebro.fit for my account pagepilot.ai', 'clone this account for my brand', 'do what @x does for us'). Fixed defaults so every machine makes the same choices without asking. Use together with the amplify and amplify-plus skills."
---

# Copy an account for a brand

Read with `.claude/skills/amplify/SKILL.md` and `.claude/skills/amplify-plus/SKILL.md`. Worked example (owner's machine, 2026-10-06): @bluebro.fit → @pagepilot.ai, `content-bank/P006-numbered-tip-cards/runs/run-01_2026-10-06_pip-pagepilot-product-page-tip/` (read its `package.md` before the first run on a new machine).

"Copying an account" means: rebuild the account's **system** (recurring character or persona, card look, formats, how it sells) in the user's brand, with new characters, wording and art. It never means redrawing the account's mascot or reusing its posts.

## Defaults (use them without asking; the user can override any of them in the request)

| Choice | Default |
|---|---|
| Source data | The existing extraction: `content-bank/_sources/<handle>/summary.md` and the pillars whose `creators` include the handle (`bank.py list`). No re-fetch. If the account isn't in the bank, run the amplify **extract** command on the profile first (latest 20 posts). |
| Brand | `brands/<id>.md` matching the user's account or handle. If none exists, make one from `templates/brand.md` with facts read from the brand's own site only, and say it needs the user's check. |
| Format | The account's most-used **slideshow** pillar (most source posts; ties → higher median views). For @bluebro.fit that is P006 numbered tip cards. |
| Size | **One carousel of 5 slides**: hook, 3 content slides, the product slot. If the pillar's range is larger, cut content slides, never the hook or the product slot, and note it in `review.md`. |
| Character | Mascot-led source → the brand's own mascot in `personas/` if one exists (PagePilot → `personas/pip.md`); otherwise create an original one: same role (faceless if the source's is faceless), a different body shape, the brand's main colour, a theme from the brand's name or logo. Model sheet first (`kie.py image --model gpt25s --resolution 2K --aspect 3:2`), saved to `personas/<id>/refs/sheet.png` plus `personas/<id>.md`. Human-led source → a fictional persona from `personas/`. |
| Look | The pillar's layouts, boxes and font roles. Colours from the brand (sample the live site); background a light tint of the brand colour. Brand mark top-left: the mascot's head plus the brand name. |
| Topic | What the brand's customers need to learn, in the brand's category (from the brand file's "What it is"). Tips must be true and general, and must not invent statistics. |
| Selling | The source's product slot (for P006, the bonus-tip slide). The brand's real site on a phone or laptop (`webshot.py`, checked for other brands and faces), product claims only from the brand file. Caption **hard** when the product is on a slide, otherwise **soft**. |
| Hook | The pillar's most-used hook formula, formula phrase kept, the rest new (amplify-plus rule 2). Label the mechanic in `package.md`. |
| Art | GPT Image 2.5 Sunburst (`gpt25s`) at 2K, aspect 4:3 (square only renders at 1K), the model sheet as reference, plain white background, "no text, no letters, no numbers, no logos". |
| Render | Text in code: `tools/tipcards.py` (P006 cover, tip and bonus layouts), `tools/cards.py` (P005). For P007, P008 or another pillar without a renderer, write a new tool file on top of `cards.py`, never edit the existing ones. |

## Steps
1. Load the account's summary and pillar, the brand file, and the brand's mascot or persona file.
2. `bank.py run <P###> "<mascot> <brand> <topic>"`, then restore `content-bank/index.md` with `git checkout` if the run changed it.
3. Character sheet if new, then the slide art; look at every image (pose, prop, colours, nothing touching the edges) and redo wrong ones, keeping them in `raw/` with the reason in the name.
4. Real-site screenshot for the product slot (`webshot.py <url> --device iphone15` or `--device air13`).
5. `spec.json` → render → look at the slides (text clear of art, nothing overlapping).
6. `caption.json` → `caption.py check` (must pass), `originality.py` (report the hook formula words if the hook flags), `measure.py check --record` per slide.
7. `package.md` (mapping table: source account → brand version, hooks with mechanics, slide table, caption, posting notes, cost) and `review.md` (7-point check, numbers, limits, verdict pending).
8. Report to the user: the preview, the choices made from these defaults, the check numbers, what to switch on when posting (AI label, commercial content toggle).
