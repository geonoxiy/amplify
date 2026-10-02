# Reddit and Letterboxd Screenshot Capture Method

How to capture clean, real screenshots of a Reddit thread (title card plus top replies) or a Letterboxd film (poster/title card plus top reviews), and turn them into a folder of bordered PNGs ready to use as carousel slides.

## Tools and constraints

- Use **Claude in Chrome** (`mcp__claude-in-chrome__*`, the real Chrome browser) for both sites.
- The sandboxed **Claude Browser** pane (`mcp__Claude_Browser__*`) blocks `reddit.com` and `old.reddit.com` outright. Do not try it first.
- Claude in Chrome's `computer` screenshot action does **not** expose a file path. `save_to_disk: true` reports success but nothing lands on disk (confirmed by searching Downloads, browser profile folders and system temp).
- `resize_window` on Claude in Chrome **does** resize the real Chrome window. Your own `computer` screenshots stay pinned at a fixed frame (784x1546 observed) regardless of the size you ask for, so do not try to verify the resize from screenshot dimensions. The page reflow (e.g. Reddit's layout changing) is the real signal.

## The round-trip download technique (how a screenshot gets onto disk)

1. Take a screenshot with `computer` (`action: "screenshot"`). Note the returned `ID: ss_xxxxx`. It is only valid for the rest of the session and expires, so do not reuse it across long gaps.
2. On a blank local page, inject a hidden `<input type="file">` with `javascript_tool`.
3. Call `upload_image` with that `imageId` and a fixed `coordinate` on the input (e.g. `[50, 30]` if positioned at `top:10px;left:10px;width:200px;height:40px`). Coordinates work fine for file inputs, no `find`/`ref` needed.
4. In the **same tab**, run `javascript_tool` again: read `input.files[0]`, `URL.createObjectURL(file)`, build an `<a download>` and `.click()` it. This triggers a real browser download into `~/Downloads`, where Bash can read it.

```js
// step 2: inject input
document.body.innerHTML=''; const inp=document.createElement('input'); inp.type='file'; inp.id='probe';
inp.style.cssText='position:fixed;top:10px;left:10px;width:200px;height:40px;'; document.body.appendChild(inp); 'ready';

// step 4: round-trip download
const inp = document.getElementById('probe');
const file = inp.files[0];
const url = URL.createObjectURL(file);
const a = document.createElement('a');
a.href = url; a.download = 'name.jpg';
document.body.appendChild(a); a.click();
```

### One download per tab

Chrome silently blocks a second automatic download from the same tab (no warning, the file just never lands). **Use a fresh tab for every single download** (`tabs_create_mcp`, navigate to the blank page, inject input, upload, download). Batch steps 2-4 into one `browser_batch` call so it is about 2 tool calls per image. Taking screenshots has no such limit, only the download step does. Only round-trip the 2-4 source images you actually need, not every scroll position.

### Local blank page to host the file input

`about:blank` is not navigable with the `navigate` tool, so serve a trivial local page:

```json
// .claude/launch.json
{
  "version": "0.0.1",
  "configurations": [{
    "name": "render-preview",
    "runtimeExecutable": "python3",
    "runtimeArgs": ["-m", "http.server", "8743", "--directory", "<project>/_render_tmp"],
    "port": 8743
  }]
}
```

Put a one-line `_render_tmp/blank.html` (`<!doctype html><html><body></body></html>`) in place, start it with `mcp__Claude_Browser__preview_start(name: "render-preview")`, and point Claude in Chrome tabs at `http://localhost:8743/blank.html`.

## Window size: differs by site

| Site | Window width | Why |
|---|---|---|
| Reddit | Narrow, **~570-600px wide** (height ~1250px), set **before** navigating to the thread | Reddit reflows to a single-column, sidebar-free, ad-free layout that looks like a phone screenshot. At ~1456px you get the messy 3-column layout. |
| Letterboxd | **Full desktop, ~1446px+ wide**. Do NOT narrow it. | The narrow reflow breaks the layout and the poster image. Poster and synopsis on the left/top, reviews list below is what you want. |

After the capture run, `resize_window` back to a normal desktop size (e.g. 1400x900).

## Reddit: picking which comments to use

Fetch the thread's real comment data from a tab already on the thread (this reuses the page session and avoids Reddit's bot-block on `curl`):

```js
const url = location.pathname + '.json?sort=top&limit=25';
const res = await fetch(url, {headers:{'accept':'application/json'}});
const data = await res.json();
const post = data[0].data.children[0].data;
const comments = data[1].data.children
  .filter(c=>c.kind==='t1' && c.data.body && c.data.body!=='[removed]' && c.data.body!=='[deleted]')
  .map(c=>({author:c.data.author, score:c.data.score, body:c.data.body}))
  .sort((a,b)=>b.score-a.score).slice(0,12);
```

`javascript_tool` truncates long returned text (~1500 chars), so do not rely on reading the JSON back in full. Note which usernames/paragraphs you want and read them off the screenshots while scrolling. Top-sorted comments on the page usually match the top-scored comments in the JSON closely enough.

Capture: one title screenshot, then 2-3 scroll-down screenshots, enough to cover the title plus 8 picked comments.

## Letterboxd: capture notes

- Use the big desktop window (see table above).
- The **title/poster card must include the actual poster image**, not just the title text and synopsis. Wait for images to load before capturing (a prior run got a blank black box where the poster had not rendered yet) and choose a crop box that includes the poster.
- On the reviews page (`/film/<slug>/reviews/by/activity/` or similar), click **"More"** under Popular Reviews to expand and load additional reviews **before** taking scroll-down screenshots, so there is enough on screen to pick 8 distinct reviews.
- Prefer reviews with a visible star rating and some likes, for variety and readability. This mirrors picking top comments on Reddit.

## Cropping into individual cards

Crop each pick out locally with Pillow. Auto-trim to content bounds and add a fixed pad (about 26px on a 784px-wide source) so every card has consistent breathing room and is not cut off mid-text.

```python
from PIL import Image, ImageChops
DL = "/Users/<user>/Downloads"

def tight_crop(src, box, dest_path, pad=26):
    im = Image.open(f"{DL}/{src}").convert("RGB")
    l, t, r, b = box
    r = min(r, im.width - 14)  # trim the scrollbar sliver Chrome renders at the right edge
    c = im.crop((l, t, r, b))
    bg = Image.new("RGB", c.size, (14, 17, 19))  # Reddit dark-mode background; use the page's own bg color for Letterboxd
    diff = ImageChops.difference(c, bg)
    bbox = diff.point(lambda p: 255 if p > 10 else 0).getbbox()
    if bbox:
        left, top, right, bottom = bbox
        left = max(0, left-pad); top = max(0, top-pad)
        right = min(c.width, right+pad); bottom = min(c.height, bottom+pad)
        c = c.crop((left, top, right, bottom))
    data = list(c.getdata())
    clean = Image.new("RGB", c.size)
    clean.putdata(data)  # rebuild the image so no source metadata carries over
    clean.save(dest_path, "PNG")
```

Give each crop `box` generous slack and let the bbox-trim find the real edges. Common mistakes: cutting the bottom too tight (clips the score/reply row) or the top too tight (clips the upvote-pill row on title cards). Always err wide vertically.

## Metadata stripping (required)

The final PNGs must read as ordinary files on any platform. A plain `.crop().save()` still carries over `.info` (ICC profiles, etc.), so rebuild the image from raw pixel data before saving (as in `tight_crop` above), or as a standalone pass:

```python
im = Image.open(f).convert("RGB")
clean = Image.new("RGB", im.size)
clean.putdata(list(im.getdata()))
clean.save(f, "PNG")
```

Verify with `Image.open(f).info`, which should be `{}`.

## Output per idea

Every finished folder, Reddit or Letterboxd, contains **9 images**:

- `00_title.png`: the title/hook card (Reddit) or poster/title card (Letterboxd)
- 8 content cards: `reply_1.png` ... `reply_8.png` (Reddit) or `review_1.png` ... `review_8.png` (Letterboxd)

Plan the capture (how many scroll-down screenshots, how many comments/reviews to pick) around hitting 9. If the source runs thin, scroll further, re-sort, or load more before settling for fewer.

Plus one `caption.txt`:

```
Hook: <short punchy hook matching the title card>

Caption: <1-2 sentence funny/engaging caption>

Source: r/<subreddit> 🔗          <- Reddit only, omit for Letterboxd
#Hashtag1 #Hashtag2 #Hashtag3     <- exactly 3 hashtags
```

Style: casual, emoji-friendly, **no em-dashes** anywhere in generated copy.

### Folder naming

- Reddit: 3-word summary of the thread's main idea, no punctuation (e.g. `Trust Your Gut`, `Rich People Secrets`).
- Letterboxd: the movie title itself (e.g. `The Whisper Man`).

## Cleanup after every capture run

- Close every Claude in Chrome tab opened during the run (`tabs_close_mcp`). They pile up fast, one per download.
- Reverse the narrow-window resize back to normal desktop size.
- `mcp__Claude_Browser__preview_stop` the local server, and delete `launch.json` / `_render_tmp`.
- `rm` the temp source images from `~/Downloads`. Nothing should pile up between runs.


---

# Additions by the Amplify project (2026-09-27)

Everything above is the owner's original method. The sections below add how it is called and how usernames are hidden.

## How it is called

**Reddit**
1. **A link:** the owner gives a thread link and the tool runs the whole method on it.
2. **Discovery:** the owner asks for ideas (optionally naming subreddits). The agent gathers high-traffic threads, shortlists ideas, and the owner approves which ones become content. Nothing is captured before approval.

**Letterboxd**
1. **A title:** the owner gives a movie title and the tool finds the film and runs the method.
2. **Discovery:** the agent gathers high-traffic films, shortlists them, and the owner approves which ones become content.

Discovery only reads public pages. `tools/shortlist.py` applies the same rules and ranking each time (Reddit: not NSFW or stickied, at least 30 comments, ranked by score per hour, at most 2 per subreddit; Letterboxd: at least 8 rated reviews and at least one like, ranked by position on the popular list). Shortlists are saved to `captures/_shortlists/`, finished folders to `captures/reddit/<Folder Name>/` and `captures/letterboxd/<Film Title>/`.

## Blurring usernames

Usernames and avatars are blurred **in the page, before the screenshot**, so the picture only contains blurred pixels and no screenshot coordinates have to be mapped.

1. After the page has loaded and the comments or reviews you need are on screen, run `tools/blur_usernames.js` in the tab (Claude in Chrome's `javascript_tool`). On Reddit, set `window.__blurNames` first from the `author` fields of the thread's `.json`.
2. It walks the page and every open shadow root, collects author names (`author` attributes, profile links, Letterboxd display names), blurs profile links, avatar images and name elements, blurs the name wherever it appears in short text (or anywhere if it is distinctive: a digit, underscore, hyphen or mixed case), and blurs `u/name` and `@name` mentions in long text. The subreddit name and icon are left visible for the `Source: r/<subreddit>` line.
3. Its reply is a short JSON: what it blurred, `leftover` (any known name still visible; must be empty) and `check_by_eye_plain_word_names` (names that are ordinary words and were only blurred in short text or with `u/`; look for them in the screenshot).
4. Run it again after every scroll that loads more content; it skips what is already blurred.
5. Look at every screenshot at full size. If a username or avatar is still legible, `shots.py blur <image> --box L T R B` hides it (pixelated by default, not reversible).
6. Never screenshot a page that has not been blurred, including the title card and the Letterboxd film page.

Tested on a mock page only (light and shadow DOM, avatars, mentions, a subreddit header). The selectors for real Reddit and Letterboxd markup are not verified on the live sites yet, which is why steps 3 and 5 are required.
