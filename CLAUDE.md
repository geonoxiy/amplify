# Amplify · read this first, every session

Amplify turns TikTok and Instagram posts into reusable content formats (pillars, in `content-bank/`) and makes new posts in those formats for personas (`personas/`) and brands (`brands/`). It is a set of Claude skills plus the Python tools in `tools/`. The results depend on following the skills and the tools exactly. Improvising outside them is what makes one person's output differ from another's.

## Setup
- Claude must run with this folder (the one holding this file) as the working folder, or the skills don't load.
- The owner's results are made with **Claude Opus** (Opus 5.5 as of 2026-10). If you are a different model, say so in your first reply so the user can switch in the model picker.
- **Image and video models: only the ones in `doc/setup/Approved Models.md`.** That file wins over older model lines in the skills.
- Different results from the owner's? Run the audit in `doc/setup/Setup Audit for Claude.md`.
- On a new machine, or after a `git pull`, run `./.venv/bin/python tools/doctor.py` (Windows: `./.venv/python.exe tools/doctor.py`) and fix every FAIL line with the README setup steps before making content. If `.venv` doesn't exist yet, do the README setup first.

## Every content request goes through the skills
Before any other step, load these with the Skill tool:
- `amplify` for anything about pillars, extracting posts or profiles, creating content, Reddit and Letterboxd captures, mockups.
- `amplify-plus` as well, every time you create content or extract from Instagram.
- `amplify-account-copy` as well, when the user asks to copy, clone, mirror or "do what @account does" for their brand or account.

Never make content from a general idea of the account. Always start from the pillars in `content-bank/` (extract first if the account or post isn't in the bank yet), the brand file in `brands/`, and the tools.

## Rules that hold in every run (full list with reasons: `doc/Owner Rules.md`)
1. **Text is drawn in code, never by the image model.** Image prompts end with "no text, no letters, no numbers, no logos". Slides are rendered with `cards.py`, `tipcards.py`, `overlay.py`, `boxlist.py`, `textclip.py` or `reel.py`.
2. **lowercase, and never an em dash, en dash, colon or semicolon** in hooks, headings, overlay text and captions (real brand names keep their capitals). `caption.py check` must pass.
3. **Learn the format, never copy the content.** New character, wording and art. `originality.py` on every run. Never redraw another account's mascot, and never use a real person's likeness.
4. **Brands:** only claims from the brand file; never its `never_say` words; real-brand UI is a real screenshot of their own site (`webshot.py`, `mockup.py`), checked for other brands and real faces; soft and hard sells end with the disclosure line.
5. **Ask few questions.** Use the defaults in the skills. Ask only when a choice changes cost a lot or a soft or hard sell has no brand file.
6. Every run gets `package.md`, `review.md` (with the measured check numbers) and its outputs in the run folder. Look at every generated image before using it.
