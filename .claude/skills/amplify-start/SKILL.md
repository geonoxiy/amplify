---
name: amplify-start
description: "Onboarding and setup check for Amplify. Use when someone is new or setting up ('clone and set it up', 'I just downloaded this', 'how do I use this', 'what can you do', 'help', 'getting started'), asks to check or verify their setup ('check my setup', 'is my setup right', 'pull the latest and check'), or says their results differ from the owner's."
---

# Amplify start: set up, check, and teach the commands

The person-facing guide is `doc/setup/Start Here.md`. Read it first: it is the source for everything you tell them. Keep your messages short, because they read the guide for the details.

## 0. Before anything else
- If you are not **Claude Opus 5.5**, say so in one line and ask them to switch in the model picker before continuing.
- If the working folder is not the one holding `CLAUDE.md` and `tools/`, stop. Tell them to reopen the Code tab on the `amplify` folder itself. The skills don't load otherwise.

## 1. Setting up (new machine)
Follow README steps 1 to 5 in order. If `.venv` already exists, skip what is done. Ask for the kie.ai key only at step 5. Write it into `.env` and never repeat it back. Offer step 6 (Drive files) as optional.

## 2. "check my setup" (also run it at the end of every setup and after every `git pull`)
Run both (Windows: `./.venv/python.exe`):
1. `./.venv/bin/python tools/doctor.py`
2. `./.venv/bin/python tools/manifest.py compare`

Then report in this shape:
- **Verdict**: "ready, same setup as the owner" / "ready, small differences" / "not ready".
- **Fix now**: each FAIL from `doctor.py`, and each "missing, github" or "different, github" file from the compare, each with its exact fix.
  - Fix what's safe yourself: `git pull`, README install steps.
  - Ask before undoing any local edit.
- **Tell the owner**: files listed as "missing, unpushed".
- **Ignore**: "missing, local" media (count only), `close` on Windows fonts.

If they report that results differ from the owner's, run the full audit in `doc/setup/Setup Audit for Claude.md` instead.

## 3. "how do I use this" / "what can you do" / first run after setup
Give this tour in your own short words, taken from `doc/setup/Start Here.md` sections 1, 5 and 6:
1. **What it is** (2 sentences): pillars are recipes learned from real posts, and new posts are made from them with original art. Text is drawn in code.
2. **The commands** as a table: section 5's table, with one good example request per row.
3. **How to ask well**: extract first, create second; name the topic, pillar, persona, caption style and brand; one run at a time; changes by slide number.
4. **What comes back**: the run folder, `output/`, `caption.txt`, `package.md`, `review.md`, the AI label when posting.
5. **A free first try**: offer `list pillars`, then `show pillar P006`.
6. **A cheap first paid try**: about $0.30, for example `create content about product page tips using pillar P006 for persona pip caption hard brand pagepilot`.

End by pointing to `doc/setup/Start Here.md` for the full guide.

## Never during onboarding
- Make paid kie.ai calls (the balance check in `doctor.py` is free).
- Edit files in `tools/`, `.claude/` or `doc/`.
- Commit or push.
