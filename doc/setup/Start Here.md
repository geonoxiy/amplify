# Start here · Amplify for new people

Read this once after you get access to the repo. It covers what Amplify is, how to set it up, how to check the setup, and how to ask for content so you get the same quality as the owner.

---

## 1. What Amplify is

Amplify studies TikTok and Instagram posts that perform well and turns each one into a **pillar**: a reusable recipe for that kind of post. A pillar records the hook formula, the slide layouts, the text boxes, the pacing and how it sells. Amplify then makes **new** posts from that recipe for our personas (Willow, Verde, Pip) or for a brand (PagePilot, Bolt Pharmacy), with original characters, wording and art.

It is **not an app you click**. It is a set of instructions (Claude "skills") and Python tools. You talk to **Claude Code**, and Claude runs the tools for you.

- The thinking is done by Claude: reading the post, choosing the pillar, writing hooks and prompts.
- The images and video come from AI models through `tools/kie.py`, paid with your kie.ai credits.
- All text on slides is drawn in code, never by the image model, so it's always sharp and correctly spelled.
- Every result is checked in code (captions, originality, layout) before you see it.

**It only works properly in Claude Code with Claude Opus 5.5.** ChatGPT, Gemini or a chat window in a browser can't run the tools. They'll give you different, weaker posts even with the same prompt. That is what happened in the boss's first test.

---

## 2. What you need before you start

| Need | Why | Where |
|---|---|---|
| The **Claude desktop app** with a plan that includes Claude Code | Runs everything | claude.ai/download, then use the **Code** tab |
| **Git** (Windows: Git for Windows) | Downloads the repo and updates | git-scm.com |
| **Miniconda** | Builds the Python environment with ffmpeg | docs.conda.io/miniconda |
| A **kie.ai API key with credits** | Pays for AI images and video | kie.ai. 1 credit = $0.005 |
| Access to the GitHub repo `geonoxiy/amplify` | The tools | Ask the owner for an invite |
| *(optional)* the **Amplify files** Drive folder | Past renders, downloaded source posts, saved paid generations | Link in the README |
| *(optional)* the **Claude in Chrome** extension | Only for Reddit and Letterboxd screenshots | Chrome Web Store |

---

## 3. The setup journey (about 20 minutes, done once)

1. **Open the Claude app → Code tab.** Pick or make an empty folder for the project.
2. **Pick the model: Claude Opus 5.5** in the model picker. Keep it on for every Amplify session.
3. **Ask Claude:**
   > clone https://github.com/geonoxiy/amplify and set it up using the README
   
   Claude downloads the repo and runs README steps 2 to 4:
   - the Python environment with ffmpeg
   - the packages
   - the pose tracker
   - the browser used for website screenshots
   
   It then asks for your kie.ai key and puts it in `.env`. That file never goes to GitHub.
4. **Reopen the Code tab on the `amplify` folder itself** (the one with `CLAUDE.md` inside). This is the step people miss. If Claude is opened on the parent folder, it never sees the skills and makes generic content.
5. *(optional)* **Drive files.** Download the Amplify files folder and tell Claude where the zips are. Claude merges them in (README step 6).
6. **Check the setup.** Say:
   > check my setup
   
   Claude runs the two checks in section 4 and tells you what to fix.
7. **Try it for free.** Say:
   > list pillars
   
   You should see the pillar table (P001 to P016). Then say:
   > show pillar P006

---

## 4. How to know your setup is right

Two commands do the checking. Claude runs both when you say "check my setup". You can also run them yourself (Windows: `./.venv/python.exe` instead of `./.venv/bin/python`):

```
./.venv/bin/python tools/doctor.py
```
Checks the Python environment, packages, ffmpeg, the website-screenshot browser, fonts, your kie.ai key (free balance check), that Claude's instruction files are present, and whether you're behind GitHub. It then **renders a test carousel and compares it with the owner's own render**:
- `same` means your slides come out the same as on the owner's Mac.
- `close` is normal on Windows, because the fonts are free look-alikes.
- `FAIL` means something renders differently. Fix every FAIL before making content.

```
./.venv/bin/python tools/manifest.py compare
```
Compares your files with the owner's full file list. It tells you:
- **missing, github**: you need to `git pull`.
- **missing, unpushed**: the owner hasn't uploaded these yet. Tell them.
- **missing, local**: only big media files, which you can get from Drive. Fine to skip.
- **different**: someone edited a tool or skill on your machine.
- **extra in tools/, .claude/ or doc/**: files the owner doesn't have. They change how Claude behaves.

For a full written report with ranked fixes, say:
> Read doc/setup/Setup Audit for Claude.md and do the audit

The report is saved to `doc/setup/audit-report_<date>.md`. Send it to the owner if anything is unclear.

**Every time the owner says there's an update:** say "pull the latest and check my setup". Claude runs `git pull`, `doctor.py` and `manifest.py compare`.

---

## 5. How to ask for things (the commands)

Use plain words, but include the parts in the right-hand column. Claude fills in the rest with the owner's defaults instead of asking you questions.

| You want | Say | Include |
|---|---|---|
| A new pillar from one post | `extract https://www.tiktok.com/@creator/video/123…` | The post link (TikTok or Instagram) |
| A creator's whole format system | `extract https://www.tiktok.com/@creator` | The profile link. Takes the latest 20 posts |
| See what's in the bank | `list pillars` · `show pillar P006` | Nothing |
| A post from a pillar | `create content about <topic> using pillar P006 for persona pip caption hard brand pagepilot` | Topic, pillar, persona, caption style, brand |
| Copy an account's system for your brand | `copy @bluebro.fit for my account pagepilot.ai` | Source account and your brand |
| Reddit or Letterboxd screenshots | `capture reddit <thread link>` · `capture letterboxd "<film>"` | The link or film title |
| Ideas to pick from | `find reddit ideas r/AskReddit top 10` · `find letterboxd ideas` | Subreddits and how many |
| A website on device mockups | `mockup https://example.com` | The URL |
| Check your setup | `check my setup` | Nothing |
| Spending so far | `how much have we spent` | Nothing. Claude runs `kie.py spend` |

**Caption styles:**
- `none`: no selling at all.
- `soft`: the brand is woven in naturally.
- `hard`: a clear product pitch.

Soft and hard both need a brand file in `brands/`, and both end with the disclosure line.

### Requests that work well vs badly

| Bad (vague: Claude has to guess) | Good (specific: uses the system) |
|---|---|
| "make me a tiktok for pagepilot" | "create content about product page tips using pillar P006 for persona pip caption hard brand pagepilot" |
| "make something like this" + a screenshot | "extract https://www.tiktok.com/@creator/photo/123…" then "create content … using pillar P0xx" |
| "make it viral" | name the pillar whose hook you want, or say "use the pillar's most-used hook formula" |
| "use a real influencer's face" | "for persona willow". Real people's faces are never used |
| "draw the bluebro mascot but blue" | "copy @bluebro.fit for my account …". You get an original mascot with the same role |

**Tips for good results:**
- **Extract first, create second.** If the post or account isn't in the bank yet, extract it. Claude refuses to make content from a vague idea of an account.
- **One request, one run.** Ask for one carousel or one video at a time, look at it, then ask for changes ("redo slide 3, the arm is cut off").
- **Name the brand by its file.** Valid names are `pagepilot` and `boltpharmacy`. For a new brand, say "make a brand file for <site>". Claude reads only the brand's own site and asks you to check the file.
- **Approve pillars.** New pillars start as `draft`. Say "approve P0xx" once you're happy with what was extracted.
- **Don't pick models.** Claude uses the approved list in `doc/setup/Approved Models.md`. Don't ask for ChatGPT, Midjourney or "the cheap one".

---

## 6. What you get back

Every create request makes a **run folder**: `content-bank/<pillar>/runs/run-NN_<date>_<name>/`.

| File | What it is |
|---|---|
| `output/` | The finished slides (PNG) or video (MP4). Post these |
| `caption.txt` | Paste-ready caption, already checked |
| `package.md` | The plan: source → your version mapping, hooks, slide table, caption, posting notes, cost |
| `review.md` | The quality check with real numbers (originality, caption check, layout), its limits, and a verdict |
| `costs.json` | Every paid AI call and its price |

When posting: switch on TikTok's **AI-generated content** label, and the **commercial content** toggle for soft and hard sells. Videos come out silent; add the sound inside TikTok.

**What things cost (owner's real runs):**

| Run | Cost |
|---|---|
| A 5-slide mascot carousel (P006) | about $0.30 |
| A Willow photo post | $0.10 to $0.50 |
| A mascot workout reel | about $1.70 |
| A motion-transfer dance video | $5 to $11 |

Claude sets a spending cap per run and reports the total.

---

## 7. The rules Claude follows (so you know why it says no)

1. Text is drawn in code, never by the image model.
2. lowercase, and no em dash, en dash, colon or semicolon in hooks, overlays and captions.
3. Learn the format, never copy the content. New wording, characters and art, checked by `originality.py`.
4. No real people's faces, and no other account's mascot.
5. Brand claims come only from the brand file, never from words on its `never_say` list.
6. Only approved AI models.

The full list with the reasons is in `doc/Owner Rules.md`.

---

## 8. If something goes wrong

| Problem | Fix |
|---|---|
| Claude makes generic content and doesn't mention pillars | Wrong folder, or not Opus 5.5. Reopen the Code tab on the `amplify` folder, pick Opus 5.5, then say "check my setup" |
| `doctor.py` says FAIL | Say "fix the doctor failures". Each line names the README step |
| "kie.ai key" fails | Key missing or out of credits. Check `.env` and your kie.ai balance |
| Results look different from the owner's | Say "Read doc/setup/Setup Audit for Claude.md and do the audit", then send the report to the owner |
| Instagram or TikTok won't download | Say so to Claude. It can import a post you saved by hand (`fetch_insta.py --file`) |
| You changed a tool by accident | `manifest.py compare` lists it. Say "undo my changes to tools/<file>" |
