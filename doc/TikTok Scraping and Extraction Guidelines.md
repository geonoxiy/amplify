# TikTok Content Pillar Engine: Outline & Data Extraction Guideline

*Draft v4 · September 25, 2026 · This is deliverable D1. Where it differs from Project Deliverables, Project Deliverables wins.*

## Part 1: Agent Outline

### 1.1 What the agent does

Give the agent a TikTok link: one post (slideshow or short-form video, up to 60 seconds) or a creator's account (e.g. @smartshopper858). It studies the posts, breaks down their format, and saves each recurring format as a **pillar** in the **content bank**. It then uses a pillar plus our **My Style profile** to create new content on any topic or product (the same product the account promotes or a completely different one): rendered PNG slideshows, video storyboards, and a rendered sample video.

**Core principle:** separate format (how the account makes its posts) from content (what one specific post is about). Learn the recipe, never copy the content. Every output must pass the originality check (Project Deliverables, section 12).

**Two ways to use it.** The same engine serves two kinds of user. The **mode** is chosen per run:

| | A. Own brand | B. Trend rider |
| :---- | :---- | :---- |
| Who | Owns the platform and already has an established brand. Wants AI in their content creation. | Doesn't own the source. Wants to ride what is working online on their own platform. |
| What they give | Inspiration posts or videos from anywhere. | Trending posts, videos or accounts. |
| What they get | The inspiration's format rebuilt in their exact, established branding (persona, characters, colors, fonts, voice, brand assets), so it passes as one of their own posts. | The trend's format rebuilt quickly for their platform, with a new person, setting and script. |
| My Style profile | The full brand profile, followed strictly. Best built by running creator extraction on their own account, so the agent learns the branding that already exists. | A light profile (niche, persona, voice). More of the format and trend details stay as the pillar has them. |
| Who wins on a conflict | My Style wins on everything the viewer sees or hears as brand (look, voice, wording). The pillar wins on format. | The same rule, but details that define the trend stay with the pillar: sound, timing, and hook wording when the wording is the trend itself (e.g. a meme caption). |
| Extra check | **Brand check:** put next to the brand's own posts, can it be told apart? | **Trend check:** how old the source post is and how fast it is growing (views per day since posting, from the stats), so the trend is still live. |

Both modes share the same extraction, pillars and originality check. Neither copies the source: the recipe is reused, the content isn't. In Own brand mode the brand's own people, characters and assets (supplied by the owner) may appear in the output; the source account's never do.

### 1.2 Pipeline

1. **Input**: a post link or a creator link. Optional: the number of posts (default: the latest 20) or a date range.  
   * A date range lets the user gather posts from a specific period only. Instead of gathering data from the whole profile, getting a portion of the posts is a faster and more targeted function.  
   * TikTok lists posts newest first, so an older range means paging further back through the post list. That listing is cheap (no downloading); only the posts inside the range are downloaded.  
2. **Collect**: download each post: slide images or the video file, caption, hashtags, sound, metadata, engagement and top comments. Downloads are kept in the pillar's originals folder (Project Deliverables, section 11).  
   * **Why download instead of browsing:** without downloading we could still get the caption, hashtags, stats, sound, posting times and comments, but not the visuals (slide text, fonts, colors, layout) or a video's shots and voiceover. The only other way is screenshotting TikTok in a browser, which is slower, lower quality (TikTok's buttons cover part of each slide) and can't capture audio.  
   * **Token cost:** downloading itself costs no tokens (a script does it); tokens are spent on what Claude reads. Estimates for 20 slideshow posts of 6 slides, to be measured on the first run: download then analyze is about 6–12K tokens per post (about 150–250K in total); browsing TikTok directly is about 25–40K per post (about 500–800K in total). Downloading is roughly 3–5× cheaper, faster and more accurate, and posts can be re-analyzed later without scraping again.  
3. **Extract**: analyze every post (every slide, or every shot of a video) using the data guideline in Part 2, recorded in the structure of the visual data model in Part 3. For videos: detect the shot cuts, pull one key frame per shot, transcribe the speech, and read the on-screen text with its timing.  
4. **Group into pillars**: compare the posts' format fingerprints (Project Deliverables, section 12). Posts that match on at least 5 of the 7 points, including structure and hook, form one pillar. A creator link gives 1–4 pillars; a post link gives 1 pillar at Low confidence. Posts that match no pillar are kept in `_sources`.  
5. **Generate**: input = pillar + My Style profile + topic/product + mode (Own brand or Trend rider) (+ number of variations, or series mode for multi-post formats). Output = a content package: rendered PNG slides for slideshows; a storyboard for videos, with selected videos rendered as MP4.  
6. **Check**: each run is checked for format match and originality (Project Deliverables, section 12).  
7. **Review**: human feedback from Amplify testers, saved in the run's review file. Feedback that applies beyond one run is saved as a general rule in the pillar's learnings file.

*Scheduling (Postiz / Content Queue) and learning from how posted content performs are stretch goals (Project Deliverables, section 14).*

### 1.3 The four style layers

* Structure: slide or shot count, story arc, recurring formats, where the product appears.  
* Voice: how the slide or on-screen text, the voiceover and the caption are written.  
* Visuals: what the picture is of (visual class, section 2.16), images, layout, colors, composition, typography, who appears and where.  
* Timing (videos only): length, what happens in the first 2 seconds, pacing, shot order, and how text and sound line up with the cuts.

### 1.4 Build & training loop

1. Build the agent.  
2. Run it on the first account (e.g. @smartshopper858).  
3. Review the output. The first ones will be wrong, so give specific feedback per layer (structure / voice / visuals / timing).  
4. Regenerate. Each regeneration is a new run folder, so every version is kept. Repeat until the output is good.  
5. Save feedback as general rules (not only fixes for that one account) so the agent gets better at extraction itself.  
6. Run it on a new account (slideshow or video).  
7. Check whether it learned from the previous rounds (fewer corrections needed). Give feedback if not.  
8. Repeat the cycle until replication is consistently good.

**How to measure "good":**

* Side-by-side test: put a generated post next to real posts from the account. Can someone tell which one is generated?  
* Replication scorecard (1–5 per round): structure · slide/on-screen voice · caption voice · typography · images & colors · layout · timing & pacing (videos) · hashtags.  
* Format match and originality check: both must pass (Project Deliverables, section 12).  
* Mode test: in Own brand mode, the brand check (a generated post next to the brand's own posts). In Trend rider mode, the trend check (source still live, output still on-trend).  
* Learning check: the number of feedback rounds needed per new account should go down over time.

## Part 2: Data Extraction Guideline

Everything the agent extracts, grouped by source. Data is extracted per slide (or per shot for videos), rolled up per post, then grouped into pillars.

### 2.1 Account-level data

* Identity: handle, display name, profile photo style (face, logo, aesthetic image), bio text, link in bio and where it leads (product, app, shop, link hub).  
* Size: followers, following, total likes, total posts.  
* History: date of first post, account age, posting volume over time (from the post list, without downloading every post).  
* Niche & implied audience: category and language(s), worked out from the posts, bio and hashtags.  
  * Real audience data (age, gender, region) is not public; TikTok only shows it in the creator's own analytics. Instead we record an **implied audience**, guessed from the content, the persona, the language and currency used, and what commenters say, and labeled as inferred.  
* Monetization: products promoted, affiliate links, TikTok Shop, brand partnerships, "paid partnership" labels. Read the link in bio and where it leads: post data often leaves the link out, so open the public profile page in the browser pane. If it is a link hub (Linktree or similar), record its products and prices. Never sign in, sign up or buy.  
* Organization: pinned posts (and why they are pinned, usually top performers), playlists/series.  
* Persona: faceless vs. personal. Is the account presented as a real person? What persona is implied (student, mom, budget-saver, etc.)? Is the person AI-generated? If a character or mascot fronts the account, record it in the brand system (2.18).

### 2.2 Post-level metadata

* ID & link: post URL/ID, date collected.  
* Post type: photo slideshow or video; number of slides, or video length.  
* Timing: publish date, time (normalized to one timezone), day of week, post age at the time of collection.  
* Engagement: views, likes, comments, shares, saves/favorites.  
* Derived rates: engagement rate ((likes \+ comments \+ shares \+ saves) ÷ views), save rate, share rate, comment rate. Compare posts by rates, not raw numbers.  
* Labels: sponsored/paid partnership, AI-generated label, \#ad disclosures. Promotion signals: an @brand mention, a brand hashtag or an instruction to search or download an app can mark a promotion even when no ad label is set. Record them as inferred sponsorship or affiliate, never as fact, with the posts and slides where they appear.  
* Tags: tagged accounts, location, product links/anchors.  
* Series: part of a series ("part 2"), playlist.  
* Top comments: text and like count of the top 10–20 comments (no commenter usernames). Used for recurring questions, sentiment, whether viewers ask about the product, and what they quote back.

### 2.3 Posting schedule & cadence

* Frequency: posts per day and per week (average and range).  
* Timing: posting hours and days (day × hour heatmap).  
* Consistency: gaps between posts; regular schedule vs. bursts.  
* Multiple posts per day: spacing between them.  
* Format rotation: do formats alternate (e.g. listicle → story → listicle)?  
* Topic rotation: order and frequency of each topic.  
* Product frequency: how often the product appears (every post, 1 in 3, etc.).  
* Timing vs. performance: do certain hours/days consistently do better?

### 2.4 Content structure (per post)

* Slide or shot count: per post, and the typical range per format.  
* Format type: e.g. listicle ("5 things…"), POV/storytime, before/after, tutorial/steps, ranking/tier list, comparison (this vs. that), myth vs. fact, "things I wish I knew", day-in-the-life, haul/finds, quotes, screenshot-style (Reddit, texts, notes app), text-message story, reaction, meme.  
* Slide or shot roles (narrative arc): label each slide or shot as hook, context, value/tip, twist, product, proof, recap, CTA, or outro. Record the sequence, e.g. hook → tip → tip → product → tip → CTA.  
* Hook: how slide 1 (or the first 2 seconds) differs from the rest (bigger text, different image, question, no image, emotional close-up).  
* Payoff placement: where the best/most important info sits (to keep people swiping or watching).  
* Swipe devices: numbering (1/6), "keep swiping", cliffhangers, "the last one…".  
* Product integration: present or not, and on which slide or shot · how it appears (product photo, app screenshot, text mention, shown in use, "the one that changed everything" framing) · hard sell vs. soft sell (organic recommendation vs. clear ad) · how it is named (brand name, "this app", "link in bio") · how it is tied to the topic (e.g. the product solves the problem the post is about).  
* Proof device: the phone artifact used as proof, if any (chat thread, screenshot, map, receipt, notes app).  
* Series structure: for multi-post formats (e.g. text-message stories), the episode arc, cliffhangers, and where the product appears across episodes.  
* CTA: on the slides/screen or only in the caption; wording; placement.  
* Recurring series/templates: named series, repeated formats with the same layout.

### 2.5 Video timing & editing (videos only)

* Length: total duration.  
* First 2 seconds: what is seen, heard and written before the viewer decides to stay.  
* Shot list: each shot's start and end time, shot type, what happens, and camera setup (e.g. selfie in a car, mirror selfie, talking head, screen recording). Selfie setups use the exact terms in 2.17. Animated and motion-graphic videos (a character on a plain background, items swapped with hard cuts) can hide their cuts from the default detector; use the fallback in Part 5. In such videos a unit is a segment (one exercise, one step), not necessarily a filmed shot.  
* Camera movement & performance: handheld vs. static, zooms, turns; gestures and expressions (e.g. crying to camera, turning to the mirror).  
* Pacing: cuts per second and average shot length; where the pace speeds up or slows down.  
* On-screen text timing: when each text appears and disappears, and whether it is synced to the beat or the speech.  
* Captions/subtitles: auto-captions, word-by-word captions, style and position.  
* Transitions & effects: jump cuts, zooms, speed ramps, green screen, split screen, filters.  
* Loop: does the ending lead back into the start?
* Progress devices: trackers, counters, ticks, step numbers or checklists that change during the video: what changes, and when (relative to each cut).  

### 2.6 Visual style: layout & composition (per slide or key frame)

*Sections 2.6–2.8 say what to look at. Part 3 defines how each item is recorded: the frame record (3.1), text blocks (3.2) and the image module for the frame's class (3.3).*

* Canvas: aspect ratio and resolution (9:16 1080×1920, 3:4, 1:1), orientation.  
* Background type: photo, illustration, AI image, screenshot, product shot, solid color, gradient, collage/grid, filmed footage.  
* Visual class: what the picture is of (humans, 2D characters, UI screenshots, environments, film/TV snippets, memes, or other). Recorded first, per slide or key frame: section 2.16.  
* Subject: people (face visible, faceless, hands only, back view), objects, products, scenery, food, rooms, text only.  
* Shot type: close-up, wide, flat lay, POV, over-the-shoulder, screen capture. For selfies, use the four exact terms in 2.17 (selfie, person taking a selfie, photo of a selfie, mirror selfie), never just "selfie".  
* Subject placement: centered, rule of thirds, left/right, top/bottom.  
* Negative space: where the empty area is and whether the text sits on it.  
* Layout: full-bleed image, image \+ text block, split screen, grid/collage (number of cells), border/frame, stacked screenshots.  
* Layering: stickers, emojis, arrows, circles, highlights, logos, watermarks on the image.  
* Safe zones: whether text and key elements avoid the TikTok UI areas (top bar, bottom caption area, right-side buttons).  
* Consistency: same layout on all slides vs. a different hook slide; same layout across posts.

### 2.7 Visual style: colors & image treatment

* Color palette: top 5 dominant colors per slide or key frame (hex codes), and the account-wide palette.  
* Temperature: warm, cool, neutral.  
* Saturation & brightness: muted/desaturated vs. vivid; dark/moody vs. bright/airy.  
* Contrast: high vs. low.  
* Filter/grading: film, grain, vintage, VSCO-style, black & white, blur, vignette.  
* Aesthetic category: e.g. Pinterest aesthetic, clean girl, minimal, cozy, dark academia, luxury, meme/lo-fi, stock/corporate.  
* Image quality & realism: high-res vs. intentionally lo-fi; real photo vs. AI vs. illustration.  
* Image sourcing clues: Pinterest-style, stock, own photos, AI, screenshots. The scraped images are the references our AI-generated images are based on (with a new person and setting).  
* Brand colors: recurring accent colors in text, boxes and highlights.

### 2.8 Typography: text on slides and on screen

* Text content: exact text per slide or per on-screen text block (OCR), keeping line breaks.  
* Font: family (TikTok native: TikTok Sans/Classic, Typewriter, Handwriting, Neon, Serif; or a custom font), weight (regular/bold). Recorded as the closest match.  
* Size: relative to frame height; headline vs. body size.  
* Case: lowercase, Sentence case, Title Case, ALL CAPS.  
* Text style: plain, outline/stroke, drop shadow, highlight box (TikTok background styles), box color and opacity.  
* Text color: main color and emphasis color.  
* Emphasis: highlighted/colored keywords, bold, underline, emojis used as emphasis.  
* Alignment: left, center, right.  
* Position: top/middle/bottom; bounding box as % of the frame (x, y, width, height).  
* Text blocks: number of text blocks per slide; hierarchy (title \+ subtext).  
* Density: words and characters per slide, lines per slide, words per line. Hook slide vs. body slides.  
* Numbering style: "1.", "\#1", "1/5", "tip 1:", emoji numbers.

### 2.9 Language style: slide text, on-screen text and voiceover

* Hook formula: curiosity gap, "POV:", "things nobody tells you about…", numbered list, bold/controversial claim, relatable struggle, question, challenge ("I tried X for 30 days"), warning ("stop doing X"), result-first ("how I saved ₱10k…"), authority ("my dad worked homicide for 30 years…").  
* Hook mechanics: why the hook works (credibility, curiosity gap, stakes) and how slide 1 or the first 2 seconds earn the swipe or the watch.  
* Point of view: first person (I/me), second person (you), third person.  
* Tone: relatable, authoritative, funny, sarcastic, aspirational, vulnerable, urgent, chill.  
* Sentence form: full sentences vs. fragments; statements vs. questions.  
* Punctuation habits: no periods, ellipses, exclamation marks, dashes, parenthetical asides.  
* Vocabulary: slang, Gen Z terms, niche jargon, reading level, filler words ("literally", "lowkey").  
* Language mix: English, Filipino, Taglish; when and how it switches.  
* Specificity: use of numbers, prices, timeframes, brand names.  
* Emotional triggers: FOMO, relief, shock, nostalgia, validation, humor.  
* Slide-to-slide flow: how one slide or shot leads into the next; recurring transitions.  
* Signature phrases: catchphrases or lines repeated across posts.  
* Errors and polish: spelling and grammar mistakes, and layout slips (a wrong slide order, a repeated slide). A mistake that repeats is a trait of the account; a one-off is an accident. Record them as errors, not as style, so the generator doesn't copy them unless the user asks.  
* Emoji use: frequency, which emojis, position in the text.

### 2.10 Caption

* Full text: exact caption.  
* Length: characters, words, lines.  
* Structure: e.g. hook line → body → CTA → hashtags.  
* First line: what shows before "more", and whether it works as its own hook.  
* Relation to the post: repeats the hook, adds context, asks a question, adds a joke, or is unrelated.  
* CTA type: save, follow, comment, share, link in bio, "part 2?".  
* Audience prompts: questions that invite comments.  
* Mentions: @ tags (brands, other creators).  
* Emojis: count, which ones, placement (start, end, between lines).  
* Formatting: line breaks, spacing, bullet symbols, case.  
* Search keywords: keywords written for TikTok search (SEO).  
* Disclosures: \#ad, \#sponsored, affiliate notes.  
* Sell style of the source (Project Deliverables, section 4.1): **none** (no brand anywhere), **soft** (a trend caption, with the brand tied in later) or **hard** (the product is on the collateral and named in the caption). Record where the brand first appears (first line, second part, hashtag only). A pillar's caption formula (Pillar Template item 13) is written brand-free, so a soft-sell run can use it as Part 1.

### 2.11 Language style: caption

* Same dimensions as 2.9 (point of view, tone, vocabulary, punctuation, language mix, emoji), recorded separately, because the caption voice often differs from the post's voice (e.g. serious slides, joking caption).  
* Caption vs. post voice gap: note the differences explicitly so the generator reproduces both.

### 2.12 Hashtags

* Full list: every hashtag per post, in order.  
* Count: per post; average and range.  
* Placement: end of caption, inline in sentences, first comment.  
* Type: broad/generic (\#fyp, \#viral, \#foryou) · niche/community (e.g. \#budgettok, \#studytok) · topic-specific (tied to the post's subject) · branded (the account's own tag or series tag) · product/brand (the promoted product's tag) · trending/seasonal.  
* Reuse: a fixed set on every post vs. rotated per topic (core set \+ variable set).  
* Formatting: lowercase vs. CamelCase; language.  
* Size: hashtag popularity (view counts, where available): big vs. mid vs. small.  
* Link to pillars and topics: which hashtags go with which pillar (format) and which topic.

### 2.13 Audio

* Sound: name and author; original vs. trending vs. licensed music. Count how many sounds are the creator's own and how many are someone else's (including another creator's "original sound").  
* Mood/genre: chill, sad, upbeat, dramatic.  
* Reuse: same sounds across posts?  
* Voice: voiceover, speech to camera, or text-to-speech; the transcript; real or AI voice. Music makes speech-to-text invent words. Count speech only if the transcript passes the checks in Part 5; otherwise record "no speech".  
* Sync: whether cuts and text changes land on the beat.

### 2.14 Topics

*In this project "pillar" means a format, not a topic. Topics are recorded as tags only.*

* Topic: main topic and sub-topic per post.  
* Topic mix: share of posts per topic.  
* Audience problem: the need or pain point each post addresses.  
* Trend/seasonal hooks: holidays, paydays, events.

### 2.15 Performance signals

* Top vs. bottom: compare the top 5 and bottom 5 of the 20 posts by format, hook type, slide or shot count, image style, text density, pacing, posting time, topic, product placement, hashtags.  
* Engagement breakdowns: per format, per topic, per hook type.  
* Save/share ratio: high saves = useful content; high shares = relatable content.  
* Comment themes: what viewers ask for or complain about.  
* Output: "what works" rules that the generator weighs more heavily. Views and likes are recorded in the pillar for reference only.

### 2.16 Visual class (what the picture is of)

Every slide or key frame gets one visual class, recorded before its layout and colors (2.6–2.8). The class decides what else the agent records and how we recreate the image. A post lists its main class and any others it mixes (e.g. a selfie hook plus text cards). If a slide is a known meme template or reaction image, its class is **meme**. A meme caption on a selfie is a text style, so that slide stays **humans**.

**Static content (slideshows, per slide):**

| # | Class | Includes | Also record | How we recreate it |
| :---- | :---- | :---- | :---- | :---- |
| 1 | **Humans** | Photos of people: portraits, selfies (2.17), mirror shots, candids, groups, hands or back only. | Face visible or hidden, number of people, pose, expression and gaze, outfit, framing, camera height, setting, how cluttered it is. | AI image of the My Style persona with its reference set: a new person and setting, phone-photo realism. |
| 2 | **2D characters** | Illustration, cartoon, anime, comic, stickman, mascot, stickers. | Art style, line and shading, palette, character design (proportions, face, outfit), expression set, recurring or one-off character, speech bubbles. | Art in the same style. Own brand: the brand's own character sheet. Trend rider: a new original character. Never the source's character or any existing franchise character. |
| 3 | **Web or app UI screenshots** | Chat threads, notes, feeds, forum threads, search results, maps, receipts, settings screens, app-store pages. | App or site, device and OS look, light or dark mode, status bar, real or fake UI, cropping, highlights and arrows, the exact text. | Built in HTML and rendered to PNG with our own text. Recreated real platforms are disclosed fiction. Never invented reviews or quotes presented as real (the P003 rule). |
| 4 | **Environments and places** | Rooms, streets, landscapes, travel spots, cafes, with no main person. | Place type, time of day, light, weather, camera height and angle, lens feel, clutter, real or generated, landmark or not. | AI image of a new setting. No false "I was here" claims. |
| 5 | **Movie, TV and film snippets** | Stills or clips from films or series, used as the image or as a reaction. | Still or clip, crop and letterbox, subtitle style, what the scene is used to say (reaction, relatable moment), the title if identifiable. | Use a snippet of the same or a similar scene found online. No license needed. Take it from the film or series itself, not from the source creator's post. The crop, text and arrangement must be new. If no good snippet exists, recreate the moment with original visuals (persona or 2D character). |
| 6 | **Memes** | Image macros, reaction images, "when…" captions, template-based jokes. | Template name, text position and style, caption formula, whether the wording itself is the trend. | Reuse the layout and caption formula with new images. Keep the hook wording when it is the trend itself. Recreate the picture if it is a specific person's photo. |

The "Also record" column is a summary. The full field list for each class is in 3.3.

**Not in the list yet:** anything else is recorded as **Other** with a short name, using the open describer in 3.4. When three posts land in the same Other, it is promoted to a class. Likely candidates: designed cards (text and simple graphics, no photo), product and object shots, food, charts and infographics, animals.

**Dynamic content (videos, per shot):**

| # | Class | Includes | Also record | How we recreate it |
| :---- | :---- | :---- | :---- | :---- |
| 1 | **Humans** | On-camera people: talking head, selfie video, mirror video, POV, skit, get-ready-with-me, dance, walk-and-talk. | Camera setup (selfie terms in 2.17), what the person does (speaks, lip-syncs, reacts, silent), gaze, gestures, expressions, voice (own, voiceover, text-to-speech), setting. | Storyboard from the pillar with the persona. The pilot renders one video type (Project Deliverables, section 14). |
| 2 | **2D characters** | Animation, cartoons, anime, motion graphics with characters, stickman, whiteboard, animated illustrations. | Art style, animation feel (limited or smooth), character design and consistency, lip sync or captions, voice, backgrounds, camera moves. | Storyboard with a character sheet. Rendering needs its own pipeline (stretch goal). |

* The two dynamic classes cover short-form (up to 60 seconds) and long-form (over 60 seconds) alike, so the bank is ready for both. Long-form stays out of the pilot (Project Deliverables, section 8): it is not extracted or generated yet.  
* A video's shots use the two dynamic classes. Anything else inside a video (a screen recording, a film clip, a meme card) is recorded as a shot type within it. If a video is mostly something else, class it Other.

### 2.17 Selfie vocabulary

Selfie terms are easy to mix up, and image generators mix them up too (in P004, a prompt for a front-camera selfie kept putting the phone in shot). Always use the exact term, never just "selfie". The team's example photos only illustrate the terms. They are not references for generation.

| Term | Who holds the camera | Camera points at | Phone in shot? | Focal point | Perspective |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **1. Selfie** (the photo itself) | The subject | The subject, straight on: front camera or arm's length | No (an arm or a thumb may reach into the foreground) | Face and upper body | First person |
| **2. Person taking a selfie** | Someone else, or a camera set up outside the scene | The subject in the act of taking a selfie | Yes, held outstretched | The person, the phone and their surroundings | Third person |
| **3. Photo of a selfie** | Someone, from very close | A phone screen that is showing a selfie photo | Yes: the phone is the subject | The screen | Third person, macro or close-up |
| **4. Mirror selfie** | The subject | Their own reflection in a mirror | Yes, usually in hand and often covering the face | The person in the mirror, full or half body | Taken by the subject, but looks like a third-person shot |

Term 4 is our addition: the team's three terms don't cover it, and P004 uses it.

**Prompt phrasing** (use these, then add the persona, setting and mood):

1. `high angle arm length selfie photo of a woman smiling into front facing camera`. Add "no phone visible" and a wide-angle, close crop.  
2. `third person shot of a person holding a smartphone outstretched taking a selfie`  
3. `close up shot focusing on a phone screen showing a selfie photo with blurred background`  
4. `full-length mirror selfie, phone held at face height, reflection in the mirror`

**If you can't tell which it is, ask two questions:**

1. Who is holding the camera? The subject means 1 or 4. Someone else means 2 or 3.  
2. What is the camera looking at? The subject directly is 1. The subject's reflection is 4. A person holding out a phone is 2. A phone screen is 3.

Angle and expression are separate descriptors (high angle, low angle, eye level, lying down, smug, smiling). Record them next to the term, not instead of it. In videos the same terms apply per shot: a selfie video is term 1 in motion.

### 2.18 Brand system (account-level visual identity)

Recorded once per account, in the creator summary, from the pillars and the code measurements. In **Own brand** mode this is what the agent must reproduce exactly. In **Trend rider** mode it is what we deliberately do not copy: we substitute our own.

* Mascot or recurring character: name, design (silhouette, colors in hex, signature features and items), art style, pose and prop library, how it appears with equipment or text, and whether a clean model sheet exists (if not, the owner must supply one).  
* Logo or watermark: what it is, where it sits (box in %), how big, and whether it appears on every slide and video.  
* Palette: the account-wide colors (measured: `creator_stats.py` clusters the per-slide and per-shot palettes) and the role of each (background, accent, headings, body, highlights, badges).  
* Typography: heading and body fonts (closest match), sizes, case, and any inconsistency between formats.  
* Layout templates: the named layouts (cover, content slide, grid, ranking, CTA…) with their box ranges, so a new post can be laid out without looking at the source.  
* Recurring devices: arrows, badges, trackers, overlays, closing slides.  
* Formats and sizes: slide and video dimensions, slide counts, video lengths.  
* Voice and captions: caption pattern, hashtag pattern, point of view, sentence style.  
* Errors to leave out: typos and layout slips that repeat (2.9).  
* Promotion pattern: where and how products and partners appear (2.4) and what is disclosed (2.2).

## Part 3: Visual Data Model

Part 2 lists what to look at. This part defines how the visuals are recorded, so that every slide or key frame, of any content type, ends up in the same structure and any two posts can be compared. It has one universal record (3.1 and 3.2), one add-on module per visual class (3.3), a method for describing content that fits no class (3.4), video additions (3.5) and a roll-up from frames to a post (3.6).

### 3.0 Recording rules

* **One frame record per slide, or per key frame of a video.** It has four parts: the frame itself (canvas, layers, composition, color and light), the **text blocks**, the **image module** for the frame's class, and how the image was made.  
* **Text and image are recorded separately.** The same text style often sits on very different images, and one image can carry several text blocks.  
* **Positions are percentages of the frame.** The origin is the top-left corner, x runs right and y runs down, from 0 to 100. A box is `[x, y, width, height]`. Every box also gets a zone on a 3×3 grid (top, middle, bottom × left, center, right), read at the box's center. Percentages keep 9:16, 3:4 and 1:1 comparable. Record the aspect ratio too.  
* **Every field says how it was obtained.** `code`: measured from pixels or data, never estimated. `vision`: judged by Claude from the image. `meta`: from the post data. A † means it could be measured in code but is not built yet (today: the subject box over time in videos, and beat and word timing). Until then Claude estimates it and labels it "estimated".  
* **Describe, don't identify.** Never name a real person from their face. A film or series can be named only from visible clues (title text, subtitles, a watermark, the caption) or an unmistakable scene. Fictional characters can be named.  
* **Say when unsure.** Give the value plus "uncertain" instead of guessing. Every unit gets an overall confidence: high, medium or low.  
* **Full detail once, differences after.** See 3.6.

### 3.1 The frame record (every class)

| Group | What to record | How |
| :---- | :---- | :---- |
| Canvas | Aspect ratio, resolution, orientation. Letterbox or pillarbox bars (yes or no, size in %). A border, rounded corners or drop shadow around the whole image. Whether the slide is a crop of a bigger screenshot. | code (aspect, resolution, letterbox bars), vision |
| Layers | Every layer from back to front: type (background photo, subject, screenshot card, icon, sticker, arrow, circle, text block, logo, watermark, UI chrome), its box, opacity and any effect (blur, shadow, cut-out outline). Background kind: photo, solid, gradient, mesh gradient or blurred blobs, pattern, texture. Icons and graphics: style (outline, filled, duotone, emoji, 3D), stroke weight, color, container (circle, rounded square, none) and what it stands for. | vision |
| Composition | Focal point (x, y). Subject box and zone. Crop tightness (extreme close-up to wide). Negative space: the one or two largest empty regions, as boxes. Balance (left, right, centered, top or bottom heavy). Depth: what sits in the foreground, middle and background. Symmetry. Grouping: elements that read as one unit and how they are arranged (icon left with a text stack right, centered stack, two columns, grid). Where the eye goes first, second and third. | vision |
| Safe zones | Whether any text block or key element overlaps TikTok's top bar, right-side button column or bottom caption area. Margin from each edge in %. | code (overlap with the TikTok zones; the zone sizes are not calibrated yet), vision |
| Color | Top 5 colors (hex and share of pixels). Average brightness, contrast and saturation. Temperature (warm, cool, neutral). Grade or filter (film, VSCO-style, black and white, faded, oversaturated, a dimming layer under the text). | code (palette, brightness, contrast, saturation), vision |
| Light | Source (window, overhead, flash, ring light, screen glow, sun, studio), direction, hard or soft, time of day, color cast. | vision |
| Texture and quality | Sharpness, grain or noise, JPEG compression, lens artifacts, phone-photo signs (flash glare, slight blur, auto-HDR look), and anything that reads as AI-generated. | code (sharpness, noise), vision |
| Origin and realism | How the image was made: photographed, screenshot, screen recording, film still, illustration, rendered graphic, AI-generated, stock, composite. Real, stylized or abstract. Intentionally lo-fi or polished. | vision, meta |
| Image similarity | Perceptual hash, for near-duplicate checks against other slides and posts (Project Deliverables, section 12). | code (perceptual hash, distance between images) |

### 3.2 Text blocks (any class; one row per block)

| Group | What to record | How |
| :---- | :---- | :---- |
| Content | Exact text with its line breaks. Language. Word and character count. Reading-order number. | vision (OCR) |
| Origin | Which kind of text it is. **Overlay:** added by the creator on top of a photo or clip. **Designed:** part of a card or graphic the creator built, with no image under it. **In-image UI:** text inside a screenshot or app. **In-scene:** signs, labels, packaging, clothing. **Subtitle:** film or TV subtitle, or a burned-in auto-caption. **Meme text:** part of a meme template. **Bubble:** speech or thought bubble, caption box, sound effect. **Mark:** watermark, logo, handle. Only overlay text is text we place ourselves. The rest belongs to the image. | vision |
| Role | Hook, headline, subhead, body, list item, number, label or pill, caption, quote, punchline, attribution, CTA, sticker text. | vision |
| Box and position | Box `[x, y, w, h]` and zone. Alignment (left, center, right). Rotation in degrees. Margin from each edge. What it is anchored to (frame center, an edge, an object, another text block). Number of lines and words per line. | vision (approximate, about ±2–3%) |
| Typography | Font family (closest match) and whether it is a TikTok native style (Classic, Typewriter, Handwriting, Serif, Neon) or a custom font. Weight, italic, case. Size as % of frame height. Line spacing. Letter spacing (tight, normal, wide). | vision |
| Color and treatment | Fill color (hex). Outline (color, thickness as % of the font size). Shadow (color, blur, offset). Background box or highlight (color, opacity, padding, corner radius). Gradient. Emphasis inside the block: which words differ, and how (color, bold, highlight, underline, emoji). | vision, code (sampled hex) |
| What is under it | What the text sits on: negative space, the subject's face, the subject's body, a product, a busy background, a solid card. Contrast ratio between the text and the pixels behind it. Legibility aids (outline, box, shadow, dimming layer). | vision, code (contrast from the box) |
| Timing (videos) | Time in and out (seconds). Entrance and exit animation (pop, fade, typewriter, word by word, slide, none). Whether it moves. Sync (beat, speech, cut). Position changes over time. | code (shot times), vision |

**Text placement patterns.** Record one pattern name for every text block, together with its numbers, so a pillar can say both "top headline" and "y 12–20%". If none fits, name a new one and give the numbers.

| Pattern | What it looks like | Common in |
| :---- | :---- | :---- |
| Center block | 2 to 5 lines centered mid-frame, usually over a photo | Hooks on photo slides |
| Top headline | A short title in the top third, the image below | Tutorials, listicles |
| Bottom caption | Lines in the lower third, over the scene or the subject's lower body | Reactions, storytime |
| Lower-third label | A small tag or name bar near the bottom, left aligned | Videos, interviews |
| Full-frame text card | The text is the whole image, on a solid, gradient or textured background | Quotes, tips, notes |
| Stacked card | Pill label, big title and body lines in a fixed order on a solid color | Designed cards |
| Icon lockup | An icon or badge on one side with a text stack beside it (title, body, label, chips) | Designed cards, explainers |
| Numbered heading | A rank number, a title and a short accent underline in a row at the top-left, body text below, the illustration under it | Tips, ranked lists, program days |
| Card grid | Text and pictures inside a grid of equal cards (name, picture and caption per card) | Workout plans, product lists |
| Score badge | A colored rounded label with a score or rating next to a heading | Rankings, reviews |
| Callout | Text with an arrow, circle or line pointing at part of the image | UI screenshots, product shots |
| Meme top and bottom | Text at the top and bottom edges | Image macros |
| Bubble | Text in a speech or thought bubble or caption box | 2D characters |
| Sticker cluster | Several small texts, emojis or stickers scattered over the frame | Collages, hauls |
| Subtitles | Burned-in dialogue lines near the bottom of a clip | Film and TV snippets, talking videos |
| Corner mark | A small handle, logo or watermark in a corner | Everything |

### 3.3 Image modules (one per visual class)

Filled in on top of 3.1 and 3.2, chosen by the frame's visual class (2.16). A frame that mixes classes (for example a photo with a screenshot card on it) fills the module for each layer, and its class is the one that carries the message. **A character-led card** (an illustrated mascot on a text card) is classed by the layer that carries the message. A cover or a diagram where the character is the picture is `2d-characters`. A card where the text, numbers or grid carry the message and the character is the pictogram is `designed-card`. Either way, fill the 2D characters module for the mascot layer. Recreating it is a composite: an HTML card layout plus character art placed as layers.

**Humans**

* People: how many, who is in shot (one person, a pair, a group, a crowd in the background), and their presentation (apparent age range and style). The presentation is recorded only to choose a fitting persona, never to identify anyone.  
* Face: visible, partly hidden (hand, phone, hair, mask), hidden, or not in shot (back view, hands only, cropped).  
* Framing: extreme close-up, close-up, head and shoulders, waist-up, three-quarter, full-length. Headroom (% above the head). Which body parts are cut off.  
* Camera: the selfie term (2.17). Angle (eye level, high, low, overhead, tilted). Distance. Lens feel (wide-angle distortion, flat telephoto). Handheld or fixed. Horizon tilt.  
* Pose and action: posture, head tilt, gaze (to camera, off camera, down, at an object), expression, mouth, gesture, what the hands hold or touch.  
* Styling: outfit pieces with their colors, hair, accessories, makeup level, props.  
* Setting: room or place type, background items, clutter (low, medium, high, backed by an edge-density score that is meaningful for photos, not for text-heavy cards or screenshots), time of day.  
* Realism markers: skin texture, flash glare, motion blur, lighting mismatches, anything that reads as real or as AI.

**2D characters**

* Art style: flat vector, hand-drawn or sketch, anime or manga, western cartoon, comic or halftone, pixel art, chibi or kawaii, stickman or doodle, paper cut-out. If it is really a 3D cartoon, record it as Other with 2D characters as the nearest class.  
* Line and fill: outline weight and color, even or varying line, fill (flat, cel, gradient, textured), shading, highlights.  
* Character design: type (human, animal, object, abstract), proportions (head-to-body ratio), eyes, mouth, signature features, outfit, 3 to 5 character colors (hex), number of characters.  
* Pose and expression: pose, emotion, action, viewing angle (front, side, three-quarter).  
* Composition: character scale and position, background (plain, gradient, full scene, none), panels (count, gutters), speech bubbles (shape, tail direction, placement).  
* Consistency: recurring or one-off, the same design on every slide, whether a model sheet is needed to recreate it.  
* Character bible (for a recurring character): a short spec a fresh session can reproduce: silhouette and proportions, fixed colors (hex), face or mask details, signature items (a watch, a logo), what is never shown, the pose and prop library seen so far, and how the character meets equipment or text. Diagram uses: color-coded regions, highlight overlays (e.g. a muscle in red), callout insets, before/after pairs.  
* Rights: original, or an existing franchise character (name it). Franchise characters are recorded but never recreated.

**Web or app UI screenshots**

* Source: app or site, platform (iOS, Android, desktop, web), device look, light or dark mode, status bar contents (time, battery, signal), language.  
* Screen type: chat thread, feed, post, comments, forum thread, notes, search results, map, checkout, receipt, settings, app store, dashboard, email, calendar.  
* Structure: the elements from top to bottom (header, list items, bubbles, avatars, buttons, keyboard, tab bar), their count and order, spacing, corner radius, and the system font.  
* Content: exact text per element. Who says what (sent and received bubbles). Timestamps. Counts (likes, replies, ratings). Usernames are not stored (Part 6).  
* Edits by the creator: crop (what was cut off), zoom, highlights, circles, arrows, underlines, blur or black bars, stacked or overlapping screenshots (count, offset), drop shadow, rounded corners, the background behind the screenshot.  
* Authenticity: real or fabricated. A real public source or an invented one. If invented, the disclosure it needs (Project Deliverables, section 9).

**Environments and places**

* Place: type, indoor or outdoor, generic or a named landmark, decor or era style (minimal, maximalist, cottagecore, industrial, vintage, futuristic), season, weather.  
* Camera: vantage point (eye level, high, low, aerial, POV, through a window or door), lens feel, framing (wide, detail, symmetrical), lines that lead the eye, depth layers.  
* Light and time: golden hour, blue hour, night with neon, overcast, harsh midday, warm indoor, natural window light.  
* Contents: main objects and props (a list), how cluttered or tidy, people present (none, small, a background crowd), text in the scene (signs).  
* Realism: photographed or generated, how polished, image quality.

**Movie, TV and film snippets**

* Form: still or clip. For a clip, its length and whether the original audio plays.  
* Placement: how the snippet sits in the frame (full-bleed, letterboxed with bars, blurred extended background, inside a card), crop, zoom, the source's aspect ratio, freeze frame.  
* Look: era and grade, film grain, genre feel, black and white.  
* Identification: title, season and episode, or scene, only from visible clues (3.0). If unknown, write "unidentified" and describe the scene.  
* Scene: who or what is in it (described, not identified by face), the action, the emotion, and why it is funny or fitting.  
* Burned-in text: subtitles or captions from the source (position, style), and any watermark or channel logo.  
* Role: reaction, punchline, evidence, mood, reference or quote, and how the overlay text relates to it.  
* Find query: a short search description (scene, action, mood, genre) so a similar snippet can be found online for our own version.

**Memes**

* Template: its name if known, its type (image macro, multi-panel, reaction image, screenshot meme, caption over photo, object labeling, exploitable), and how old or fresh it is.  
* Layout: panel count and grid, the role of each panel (setup, reaction, punchline), the number of text slots and where each sits.  
* Text style: classic meme style (bold sans, white with a black outline, all caps) or a clean caption, and its alignment.  
* Caption formula: the fill-in-the-blank slots (e.g. "when [situation] like [reaction]") and the joke mechanic (relatable, irony, contrast, absurdity).  
* Picture: what it shows (a person, an animal, a cartoon, a screenshot), and whether it can be swapped for a new picture without losing the joke.  
* Trend status: whether the wording or the template is itself the trend (Trend rider mode, 1.1).

**Dynamic classes (humans and 2D characters in video).** Each key frame takes the frame record and the module above. The motion and timing additions are in 3.5.

### 3.4 Describing content that fits no class

Six static classes and two dynamic ones will not cover everything. The agent never forces a slide into a class that doesn't fit. It uses the open describer below and logs the result, so nothing is lost and new classes can be added from evidence.

**When to use it.** A frame is **Other** when the module in 3.3 can't describe the things that matter in it, or when the picture is mainly something else: designed cards (text and simple graphics on a built background, no photo), product or object shots, food, charts and infographics, animals, collages and moodboards, abstract or AI art, maps, diagrams, stock footage without people. If a class fits only part of the frame, fill that class's module for that layer and use the describer for the rest.

**The open describer (answer in this order, every time):**

1. **What is it?** One plain sentence with no jargon, as if describing it to someone who can't see it.  
2. **How was it made?** Photographed, screenshot, screen recording, illustrated, rendered graphic, AI-generated, film still, stock, composite, or unknown.  
3. **What is in it?** The main elements as a list, each with a box and its role (subject, proof, decoration, background, text carrier).  
4. **What does it do in the post?** Hook bait, proof, evidence, punchline, mood, explanation, product display, transition, filler.  
5. **Nearest class.** Which known class is closest, what they share, and what doesn't fit.  
6. **What makes it recognizable?** Three to five traits a viewer would notice, each marked **essential** (the format breaks without it) or **incidental** (it can change).  
7. **The universal record.** The frame record (3.1) and the text blocks (3.2) are always filled in, whatever the class. This is what keeps an unknown slide comparable to known ones.  
8. **How to recreate it.** The method (AI image, HTML render, drawn graphic, chart from code, snippet found online, an asset supplied by the user), the assets needed, the difficulty, and the risks (someone's likeness, a brand or franchise, a claim that would be false).  
9. **A name and a definition.** A short lowercase, hyphenated name (e.g. `product-flat-lay`), a one-line definition, and the fields this class would need beyond 3.1 and 3.2.  
10. **Confidence.** High, medium or low, and what the agent is unsure about.

**The Other log.** Every Other frame is added to `content-bank/_other-classes.md`: name, definition, post IDs, count, proposed fields, status. Similar names are merged. When three different posts land in the same one, the agent proposes it as a new class and the user approves it (the Other rule in 2.16). An approved class gets a row in 2.16 and a module in 3.3.

**Drafts for the likely candidates.** These are not classes yet. Use these fields while logging them as Other.

| Name | Fields on top of 3.1 and 3.2 |
| :---- | :---- |
| product-or-object | Product type, brand visible, hero angle, background (plain, lifestyle, held in hand), props, packaging text, scale cues, lighting (studio or natural), reflections, number of items, arrangement (single, flat lay, lineup). |
| food | Dish or drink type, cuisine, plating (home or restaurant), camera angle (overhead, 45°, close-up), steam or motion, hands in shot, surface and props, portion, food color against the background. |
| designed-card | A card built in a design tool from text and simple graphics, with no photo: tip cards, quote cards, checklists, icon cards. Background kind (solid, gradient, mesh gradient or blurred blobs, texture, paper), text hierarchy, number of text blocks, alignment, arrangement of grouped elements (icon left with a text stack right, centered stack, columns), icons and graphics (style, stroke weight, color, container, what each stands for), pills and chips, decoration (frames, quote marks), font pairing, watermark, fill ratio (how much of the card is text).; diagram elements (highlight overlays, score badges colored by value, progress trackers, split strips, callout insets with leader lines, before/after pairs); product mockups (a tablet or phone showing the product or an app); grids of cards (rows × columns, card style, what each card holds). |
| chart-or-infographic | Chart type, axes and labels, number of data points, highlighted value, colors per series, icons, source line, what can be read at a glance, whether the numbers are real or illustrative. |
| animal | Species, number, pose, expression, setting, human present, camera angle, style (photo, video still, cartoon), how the caption relates to it. |
| collage-or-moodboard | Number of cells, grid pattern (equal, mixed, overlapping), what each cell is (with its own class), gaps and borders, background color, what unifies it (color, filter, theme). |
| abstract-or-ai-art | Style, dominant shapes, color story, texture, any figures, a prompt-like description, the feeling it is meant to give. |

### 3.5 Video additions (dynamic classes)

Each key frame gets the frame record (3.1), text blocks (3.2) and the module for its class (Humans or 2D characters). On top of that, each shot gets a motion and timing record:

| Group | What to record | How |
| :---- | :---- | :---- |
| Camera motion | Static (tripod), handheld, pan, tilt, zoom in or out, push-in, whip pan, orbit, follow. Speed and shake. | code (optical-flow estimate), vision |
| Subject motion | What the subject does over the shot (speaks, turns, walks, gestures, dances, lip-syncs), how fast, in which direction, whether it loops. | vision |
| Framing over time | Subject box at the start and end of the shot. Punch-ins or crops added in editing. Vertical reframing of horizontal footage. | vision, code† |
| Text track | Every text block with its time in and out, its box at each keyframe, animation and sync (3.2, Timing). | vision, code (shot times) |
| Progress devices | Trackers, counters, ticks or step numbers: what changes and at which second (relative to each cut). | vision, code (shot times) |
| Captions | Auto-caption or word by word: style, position, highlight color, lines shown at a time. | vision |
| Cuts and transitions | Cut type (jump, match, hard, cross-dissolve, whip, zoom, glitch) and shot length. Effects: green screen, split screen, filters, speed ramps, freeze frames. | code (cuts), vision |
| Audio and picture sync | Which cuts, text changes or gestures land on the beat or a spoken word. | code† (beat and word times), vision |
| 2D characters only | Animation type (full, limited, cut-out, motion graphics, kinetic type, whiteboard). Frame-rate feel (on ones, twos, smooth). Loops. Lip sync (mouth flaps or none). Camera moves in drawn scenes. Character consistency between shots. | vision |

Long-form videos (Project Deliverables, section 8) are sampled the same way, with one key frame per scene, once they are in scope.

### 3.6 From frames to a post

* **Template first.** Find the post's layout template or templates: the parts of the frame record that stay the same across slides (font, box position, palette, background type, layer order) and the parts that change. Record the template in full once, from the hook slide and one body slide, then write every other slide as differences ("same as slide 2, except…"). This keeps token use down and shows the pattern directly.  
* **Constants and ranges.** For every numeric field, keep the range across slides and posts (for example "text center y 34–41%, 4 to 7 words per line"), so pillar rules are ranges and not single values. Note which fields never change (the format's fixed parts) and which vary (the content).  
* **Hook against body.** Record how the hook slide differs from the rest in the same fields: bigger text, a different class of image, no image, a different placement.  
* **Continuity between slides.** Whether the subject, pose, room or framing repeats, and what changes (for example only the outfit). Note it when a change is the whole point of the format.  
* **Class mix.** The list of classes in the post, and the slide numbers where each appears.  
* **What must survive.** From the "essential" traits (3.4, item 6), write the few things a recreation must keep for the format to hold, and the things it may change.  
* These feed the format fingerprint (Part 4) and the pillar's Visual style field.

## Part 4: From Extracted Data to Pillars

* Sample size: the latest 20 posts per creator, or a chosen date range. A single post link gives a Low-confidence pillar.  
* Grouping: posts are grouped by their format fingerprint (7 points: structure, hook, camera and motion, pacing, text overlay, audio, emotional arc). The visual class and selfie term (2.16–2.17) belong to the camera and motion point. Two posts are the same pillar when they match on at least 5 of the 7 points, and structure and hook both match (Project Deliverables, section 12). One account's shared brand (fonts, colors, logo, mascot) makes camera, text and audio match across most of its posts; structure and hook are what separate its formats.  
* Number of pillars: a creator link usually gives 1–4 (Project Deliverables, D3). If more formats each clear the rule with 2 or more posts, save them all as drafts and tell the user; don't merge distinct formats or drop one to reach the target.  
* Rules + examples: every Pillar Template field stores a rule (e.g. "lowercase, 8–15 words per slide") plus real examples from the originals. Visual rules use the ranges and the fixed and varying parts from 3.6, including the text placement pattern and its box range.  
* Confidence: High when the pattern appears in 3 or more posts, Medium in 2, Low in 1.  
* Do / Don't list: things the account never does (e.g. never uses periods, never shows faces).  
* Pillar file: follows the Pillar Template (Project Deliverables, section 5).  
* Creator summary (D3): topics, posting frequency and times, best-performing formats, implied audience, the brand system (2.18) and the promotion pattern (products, plugs, what is disclosed).  
* Where it's saved: each pillar gets its own folder with the originals and one folder per run (Project Deliverables, section 11).

## Part 5: Extraction Methods

* Posts, metadata, engagement: scraper (yt-dlp for videos, gallery-dl for photo slideshows). If TikTok blocks it, a paid scraping service (e.g. Apify) is the backup: under $10, needs Amplify's approval. The link in bio is not always in the post data: read it from the public profile page in the browser pane (never sign in, sign up or buy).  
* Slide images and videos: download at full resolution and keep them in the pillar's originals folder.  
* Video shots: shot-cut detection in code (ffmpeg / PySceneDetect) gives the cut times; one key frame is taken per shot. If the default threshold finds under 4 cuts in a video of 8 seconds or more (typical of animated videos with hard cuts on a plain background), it retries at a finer threshold and records which one it used (`shot_detector`). A shot under 0.15 seconds is merged into the one before it.  
* Speech: transcription with Whisper (runs locally, free). Music makes it invent words even when its own no-speech score is 0, so a segment counts as speech only if its compression ratio is within 0.8–2.4 and it doesn't stretch 1 to 3 words over 6 seconds or more. The others are flagged `suspect`, and a video counts as having speech only if some segment passes.  
* Slide and on-screen text, position and timing: OCR with bounding boxes (vision model) on slides and key frames.  
* Visual class and selfie term: vision model (Claude), per slide or key frame, using the tables in 2.16–2.17. Recorded before layout and colors.  
* Frame records and text blocks (Part 3): Claude fills them in from the downsized slides and key frames. Text boxes are approximate (about ±2–3%). Before a record is saved, the box check draws every recorded box onto the slide and the result is looked at, so a misplaced box is caught.  
* Code measurements for the visual model (`prepare.py` and `measure.py`): palettes; brightness, contrast and saturation; sharpness and noise; an edge-density clutter score; letterbox bars; perceptual hashes and the distance between images (near-duplicate check); text-against-background contrast and sampled text color from a box; overlap of a text box with the TikTok UI zones; and camera motion per shot from optical flow (static, handheld, pan, tilt, zoom). The bands (soft, sharp, low or high clutter) are rough. The TikTok UI zone sizes are placeholders until they are calibrated on a real screenshot. Still not built (†): the subject box over time, and beat and word timing. Text fill is sampled as the dominant non-background color. For text on a colored bar, badge or pill, set the fill and background by hand: the tool measures against the surrounding card.  
* Creator statistics: the top-5 and bottom-5 rankings by rate only include posts with at least 5,000 views (a tiny post can top a rate ranking on a few likes), and a separate ranking by views is kept. The account-wide palette is clustered from every per-slide and per-shot palette.  
* Content outside the known classes: the open describer in 3.4, with the result added to the Other log (`content-bank/_other-classes.md`).  
* Font, text style, layout, composition, image type: vision model (Claude) using a fixed checklist based on 2.6–2.8.  
* Colors: palette extraction in code (k-means on pixels) → hex codes.  
* Language, hooks, tone, topics: language model analysis across all posts.  
* Audio: sound metadata; transcription if there is speech.  
* Performance: calculated rates \+ top vs. bottom comparison.  
* Similarity: length, cuts and text position are measured in code; near-duplicate frames are caught with an image-similarity score; the rest of the fingerprint is judged by Claude and reviewed by me.

## Part 6: Guardrails

* Learn the recipe, not the content: never reuse the source account's images, footage, slide text or script word for word. The person and the setting must change (originality check, Project Deliverables section 12).  
* Never keep the source person's face or voice in generated output. Never reuse a source's 2D character. Film and TV snippets may be reused when they are available online (no license needed), but they are taken from the film or series itself, never lifted from the source creator's post.  
* In Trend rider mode, hook wording that is the trend itself (a meme caption, a trend phrase) may be kept as is. The images, setting and everything else must still be new.  
* Downloads are kept for internal analysis only and are never reposted.  
* Don't store commenter usernames or personal data; keep only comment text for themes.  
* Describe people, never identify them: don't name a real person from their face, in a post or in a film or TV snippet (3.0).  
* Scraping can break and bends platform terms; prefer official APIs where possible.  
* Disclosure: keep \#ad rules and TikTok's commercial content disclosure when promoting products, and use TikTok's AI-generated content label for realistic AI people or scenes. Source accounts often skip these (no ad label on repeated app plugs, no AI label on AI-made illustrations). That is not permission: our own versions carry the disclosures.
