# Setup audit · paste this to Claude Code on a new machine

> **To the person:** open Claude Code with the Amplify folder as the working folder, then say:
> "Read `doc/setup/Setup Audit for Claude.md` and do the audit. Don't make content yet."
> If that file isn't there yet, run `git pull` first. If it still isn't there, your copy is older than 2026-10-06. Ask the owner to push.

---

## To Claude: what this is

The owner (Love) and their boss gave Amplify the same prompt and got very different posts. Amplify only gives the owner's results when four things match the owner's Mac:

1. **The files.** The same tools, skills and instruction files.
2. **The Claude setup.** The same model, the right working folder, and the skills loaded.
3. **The machine setup.** The `.venv`, packages, fonts, Chromium and the kie.ai key.
4. **The model choices.** Only the models in `doc/setup/Approved Models.md`.

Check each one in order, fix what you safely can, and write a report. Don't generate any content during the audit, and don't make paid kie.ai calls. Checking the balance is free.

## Step 1 · Who and where am I

Report these:
- Your model name. If it isn't **Claude Opus 5.5**, say so at the top of the report. The person should switch in the model picker and run the audit again.
- Your working folder. It must be the folder that holds `CLAUDE.md`, `tools/` and `.claude/skills/`. A parent folder or a subfolder means the skills never load. That is the most common cause of very different results.
- The skills you can see. `amplify`, `amplify-account-copy` and `amplify-start` must be in your skill list. If they aren't, the working folder is wrong or the files are missing.
- Any other content, marketing or social-media skills or plugins you can see, such as a "content-creation", "marketing" or "social" plugin. List them. For Amplify requests, the `amplify*` skills must be used, not those. They can take over a prompt like "copy this account". The owner runs only the `ecc` plugin, which has no content skills that compete with Amplify.
- Whether a `CLAUDE.md` exists at the root and you read it at the start.

## Step 2 · Is this copy up to date with GitHub

Run:
```
git status -sb
git fetch
git log --oneline -5 origin/main
git log --oneline -5
```
Report:
- whether this copy is behind `origin/main`. If it is and there are no local edits, run `git pull`.
- every locally modified tracked file (`git status`). Edits to files in `tools/`, `.claude/skills/`, `CLAUDE.md` or `doc/` change how Claude works. Show `git diff --stat` and ask the person before you undo anything.
- whether this is a real git clone (`.git` exists) or a downloaded ZIP. A ZIP can't `git pull`, so recommend re-cloning.

## Step 3 · Compare the files with the owner's Mac

Run (Windows: `./.venv/python.exe` instead of `./.venv/bin/python`; if `.venv` isn't set up yet, use any Python 3):
```
./.venv/bin/python tools/manifest.py compare
```
It compares this folder with `doc/setup/owner-manifest.tsv`, the owner's full file list with hashes. Put the whole output in the report, sorted into these groups:
- **missing, github**: this copy didn't pull. Fix it with `git pull`.
- **missing, unpushed**: the owner hasn't pushed these yet. Only the owner can fix this. List the files.
- **missing, local**: downloaded media and finished renders kept out of git on purpose. They don't affect new runs. Mention the count only.
- **different, github**: this copy has local edits to files that came from GitHub. Name each one.
- **extra in tools/, .claude/ or doc/**: files the owner doesn't have. These change Claude's behaviour. Name each one.

## Step 4 · Is the machine set up like the owner's

Run:
```
./.venv/bin/python tools/doctor.py
```
Report every FAIL and WARN line, with the README step that fixes it. The test render at the end compares slides with the owner's own render:
- `same` means it renders the same as on the owner's Mac.
- `close` is expected on Windows (look-alike fonts).
- `FAIL` means it renders differently. Look at `.cache/doctor/` and describe what you see.

Also check:
- `.claude/settings.json` exists and sets `PYTHONUTF8=1`.
- `.env` has a `KIE_API_KEY` line. Never print the key itself.

## Step 5 · Model choices

Read `doc/setup/Approved Models.md` and confirm you will follow it.

If this folder has earlier run folders made on this machine (`content-bank/*/runs/*/costs.json` not in the owner manifest), list the models they used. Flag any model that is not approved. A non-approved model, or no `kie.py` at all (art drawn some other way), is a likely cause of the difference.

## Step 6 · The report

Write `doc/setup/audit-report_<YYYY-MM-DD>.md` with:

1. **Verdict**: "same setup as the owner" or "differs", in one line.
2. **Fixed**: what you fixed in this audit (e.g. ran `git pull`).
3. **For the person to fix**, ranked by impact on results:
   1. wrong model, or wrong working folder (skills not loading)
   2. missing or locally edited tools, skills or instruction files
   3. a competing content plugin or skill
   4. `doctor.py` FAILs (packages, Chromium, fonts, key)
   5. models used outside the approved list
   
   Each item gets one line on what's wrong and one line with the exact fix (command, README step, or menu).
4. **For the owner**: files listed as "missing, unpushed". The owner needs to push these.
5. **Raw output** of `manifest.py compare` and `doctor.py`.

Then tell the person the verdict and the top three fixes in a short message.

## What not to do during the audit

- Don't edit files in `tools/`, `.claude/` or `doc/` (the report is the only new file). Don't delete anything, and don't commit or push.
- Don't run `git reset --hard` or `git checkout --` on files with local edits without asking the person first.
- Don't make paid kie.ai calls or generate content.
