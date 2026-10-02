# Amplify: TikTok Content Pillar Engine

An agent that turns a TikTok link into a reusable content format (a **pillar**) and then makes new posts in that format, for our own personas or for a brand (no sell, soft sell or hard sell). It also captures Reddit and Letterboxd screenshots and puts real websites on laptop and phone mockups.

It is not a standalone app. It is a **Claude skill** (`.claude/skills/amplify/SKILL.md`) plus the Python tools in `tools/`. You open this folder in the Code tab of the Claude desktop app and talk to Claude; Claude runs the tools. It works on Mac and Windows.

## What you can ask for

| You say | You get |
|---|---|
| `extract https://www.tiktok.com/@creator/photo/123…` (one post) or `extract https://www.tiktok.com/@creator` (a profile) | The posts downloaded and broken down, saved as pillars in `content-bank/`. A profile also gets a creator summary |
| `create content about <topic> using pillar P005 for persona willow caption soft brand pagepilot` | A content package (hooks, slide or shot plan, caption) plus rendered PNG slides, or an MP4 for the video pillars below. `caption` is `none`, `soft` or `hard`; soft and hard need a brand file in `brands/` |
| `capture reddit <thread link>` / `capture letterboxd "<film title>"` | 9 cleaned screenshots (usernames blurred) and a `caption.txt` in `captures/` |
| `find reddit ideas r/AskReddit top 10` / `find letterboxd ideas` | A ranked shortlist of threads or films. Nothing is captured until you pick numbers |
| `mockup https://example.com` (runs `mockup.py make`) | The live site screenshotted at real device size and placed on 9 laptop and 7 phone templates |

Anything not on this list can still be asked in plain words; the skill file tells Claude which tool does what.

## Setup (once, on Mac or Windows)

You need: the **Claude desktop app**, **Git** (on Windows: Git for Windows), **Miniconda**, a **kie.ai API key** (pays for AI images and video), the **[Amplify files](https://drive.google.com/drive/folders/1_2bNZz_jpjGRbOFUtdJIZkNzoUmn4_vB)** folder in Google Drive and, for Reddit and Letterboxd, the **Claude in Chrome** extension.

In the Code tab, open a folder for the project and ask Claude: *"clone this repo and set it up using the README"*. Claude runs these steps and then asks you for your kie.ai key.

| Step | Mac | Windows |
|---|---|---|
| 1. Download | `git clone <this repo's URL> amplify` | same |
| 2. Python environment with ffmpeg | `~/miniconda3/bin/conda create -p ./.venv python=3.12 ffmpeg -c conda-forge --override-channels -y` | `~/miniconda3/Scripts/conda.exe create -p ./.venv python=3.12 ffmpeg -c conda-forge --override-channels -y` |
| 3. Packages | `./.venv/bin/python -m pip install -r requirements.txt` | `./.venv/python.exe -m pip install -r requirements.txt` |
| 3b. Pose tracking (motion tool), installed on its own | `./.venv/bin/python -m pip install --no-deps mediapipe==0.10.35` | `./.venv/python.exe -m pip install --no-deps mediapipe==0.10.35` |
| 4. Browser for website screenshots | `./.venv/bin/python -m playwright install chromium` | `./.venv/python.exe -m playwright install chromium` |
| 5. Key | `cp .env.example .env`, then paste the kie.ai key after `KIE_API_KEY=` | same |
| 6. Files from Drive | Open the **[Amplify files](https://drive.google.com/drive/folders/1_2bNZz_jpjGRbOFUtdJIZkNzoUmn4_vB)** folder → Download (top right, or right-click the folder). Drive zips it (into several zips when it's over 2 GB). Tell Claude where the zips are: it unzips them and copies what is inside `Amplify files/` into the amplify folder, merging into the folders already there without deleting anything | same |

Never commit `.env`; it is ignored on purpose. Then open the amplify folder in the Code tab and try `list pillars` to check that everything is in place.

The tools start without step 6, but the Drive files are what let you re-edit past runs (their raw AI art and renders), make new mockup templates from the same inspiration photos, re-analyse a creator from their downloaded posts, and reuse past paid AI generations instead of paying for the same request again. When the owner adds new files, download the folder again and merge it the same way.

**Mac and Windows differences** (the tools handle them on their own, in `tools/portable.py`):
- **Fonts.** Apple's fonts can't be shared, so on Windows the designed slides and the iPhone status bar use free look-alikes from `assets/fonts/`: Barlow Condensed for DIN Condensed, Nunito Sans for Avenir Next, Inter for SF Pro, and Google's Noto emoji for Apple's. Slides look very close, not identical.
- **Speech to text.** Apple Silicon Macs use the GPU. Windows runs the same Whisper model on the CPU: slower, and the first run downloads the model (about 1.6 GB).
- **Text encoding.** `.claude/settings.json` sets `PYTHONUTF8=1` so Windows reads and writes captions, emoji and dashes the same way a Mac does. Keep that file.

## What is in this repo and what is not

| On GitHub (code and text) | In the **Amplify files** Drive folder (large media) |
|---|---|
| `tools/`: every tool | Rendered slides, videos and raw AI art from every run (`content-bank/P0xx/runs/`) |
| `.claude/skills/amplify/`: the agent's instructions | Downloaded TikTok videos and images (`content-bank/_sources/`): other creators' posts, for internal analysis only. Their analysis text is on GitHub |
| `doc/`: scope of work, extraction guidelines, screenshot method | `mockups/inspo/`, `mockups/out/`, `mockups/shots/`: inspiration photos, sample mockups and site screenshots |
| `content-bank/`: the pillars, their source posts (`originals/`, needed by the originality check), learnings and run notes | `.cache/`: past paid AI generations (so the same request isn't paid for twice) and the pose model |
| `personas/`, `brands/`, `templates/`, `assets/`: personas, brand files, blank templates, fonts | |
| `mockups/templates/`: the 16 calibrated device templates | |

Kept in neither: `.env` (each person uses their own kie.ai key) and `.venv/` (2 GB of installed packages, rebuilt by the setup steps). Drive folder: https://drive.google.com/drive/folders/1_2bNZz_jpjGRbOFUtdJIZkNzoUmn4_vB

## Where things stand

| Part | Status |
|---|---|
| Link to pillar (post or profile) | Works. 15 pillars saved, all still `draft` until approved |
| Static recreation (slides) | Works. Rendered runs in P004, P005, P010, P013, P014 |
| Caption styles none / soft / hard | Works, with brand files for PagePilot and Bolt Pharmacy |
| Video recreation | Works for two video types: animated mascot reels (P009, `reel.py`) and short clips with text on screen (P011 and P012, `textclip.py`). Other video formats have no renderer yet |
| Motion transfer (a persona copies a source video's moves, `motion.py` + `kie.py motion`) | Built. The first run (P015) was sent back for more realism, so it is still being tuned |
| Reddit and Letterboxd screenshots | Built. The username blur has been tested on a mock page, not yet on live Reddit and Letterboxd, so every screenshot is still checked by eye |
| Mockups | Works for websites on laptops and phones. Making a template from a social post link is not built yet |
| My Style questionnaire | Not built. Personas are written by hand in `personas/` |
