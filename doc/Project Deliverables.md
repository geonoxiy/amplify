# **Scope of Work: TikTok Content Pillar Engine**

**Duration:** 2 weeks (10 working days) · **Owner:** Love Caranza · **Reviewer:** Anyone from the Amplify team

## **1\. Goal**

**Week 1:** Given a TikTok link (one post, or a creator's account), the system pulls the content, breaks down its format, and saves it as a reusable **pillar** in a **content bank**. A pillar must be clear enough that AI can reproduce the format from it. This covers both slideshows and short-form videos (up to 60 seconds).  
**Week 2:** The output is finished files: rendered PNG slideshows and a rendered sample video. Any pillar can be combined with our own style, on command: *"Create a content about X using pillar Y."*

**Two uses, one engine:** **Own brand** (the user owns an established brand and wants any inspiration rebuilt in their exact branding) and **Trend rider** (the user doesn't own the source and wants to ride what is working online). The user picks the mode per run; see the D1 guideline, section 1.1.

## **2\. Definitions**

| Term | Meaning in this project |
| :---- | :---- |
| **Post link** | A link to one public TikTok slideshow or video, e.g. `tiktok.com/@user/photo/123…` |
| **Creator link** | A link to a public TikTok account, e.g. `tiktok.com/@user` |
| **Pillar** | A reusable **content format recipe** taken from real posts: structure, hook formula, slide-by-slide or shot-by-shot pattern, timing (for videos), text style, visual style, and caption/hashtag pattern. It is **topic-free**: it describes *how* content is made, not *what* it's about. *(This differs from the usual marketing meaning of "content pillar," which is a topic theme. Topics are recorded as tags only.)* |
| **Content bank** | A folder of pillar files plus one index listing every pillar (ID, name, source, summary). |
| **Mode** | How a run treats My Style and the source. **Own brand:** the profile is the user's full, established brand and is followed strictly. **Trend rider:** a light profile, and trend-defining details (sound, timing, hook wording when it is the trend) stay as in the pillar. Both modes use the same originality check. |
| **Visual class** | What a slide or shot is of. Static: humans, 2D characters, web or app UI screenshots, environments and places, movie/TV/film snippets, memes (plus "Other" for anything new). Dynamic (short-form and long-form): humans, 2D characters. Recorded per slide or shot; defined in D1, section 2.16. |
| **Caption style** | How a run's caption treats a brand, chosen per run: **none** (no brand mention anywhere), **soft** (a trend caption, then a brand bridge in the second part) or **hard** (the product is on the image or video and named in the caption). Soft and hard carry the disclosure "This is an advertisement." Section 4.1. |
| **Brand profile** | One file per brand or product (`brands/<name>.md`): name, handle, product, every spelling that counts as a mention, allowed claims, words never to say, call to action, disclosure wording and real product photos. Only loaded for soft and hard runs. |
| **My Style profile** | One file describing our own voice, audience, brand words, visual preferences, persona (the character, look and settings used in AI images and video) and do-not rules. |
| **Content package** | What the system outputs when creating content: hook options, slide-by-slide text **plus visual direction**, caption, hashtags and a posting suggestion. For slideshows, it includes rendered PNG slides: phone-artifact formats are built in HTML, and photo-based formats use AI-generated images based on the scraped references. For videos, it includes a storyboard (script, voiceover, shot list with timings, on-screen text, sound), and selected videos are rendered as MP4. |

## **3\. Deliverables**

### **Week 1: Scraping and pillars**

| \# | Deliverable | What exactly |
| :---- | :---- | :---- |
| D1 | **TikTok Scraping & Extraction Guideline** (doc) | What data we collect from TikTok and how, what the AI analyzes (structure, hooks, text, visuals, caption, hashtags), the **visual data model** (text placement and image details per content type, and how content outside the known types is described), known limits, and the **Pillar Template** (section 5). Covers slideshows and short-form videos: transcript, shot cuts, key frames, on-screen text timing and pacing. |
| D2 | **Post-link extraction** | Input: one post link. Output: the post's data (caption, hashtags, stats, date, sound, all slide images; for videos, the video file, transcript, shot list and key frames) plus **1 pillar** saved to the content bank. |
| D3 | **Creator-link extraction** | Input: a creator link. Output: data from their **latest 20 posts** (or all, if fewer), or from a chosen date range, a **creator summary** (topics, posting frequency and times, best-performing formats, implied audience, and the brand system: mascot or logo, palette, fonts, layout templates) plus **1–4 pillars** saved to the content bank. |
| D4 | **Content bank v1** | At least **10 pillars** from the test sources (5 post links \+ 3 creators), all following the Pillar Template, listed in the index. Test sources: the cop-dad "rules" post (Ashley, Warden app), 1–2 text-story (SMS/iMessage) creators, and the rest picked by hand from currently trending slideshows and videos. Each pillar gets its own folder with the originals and one folder per run (section 11). |

### 

### **Week 2: Adapting and creating**

| \# | Deliverable | What exactly |
| :---- | :---- | :---- |
| D5 | **My Style profile** | Filled in from a short questionnaire and/or by running D3 on our own TikTok account. Includes the persona used in AI images and video. In Own brand mode, D3 on the brand's own account is how the agent learns the branding that already exists. |
| D6 | **Create command** | `Create a content about [X] using pillar [Y]` returns a content package. Pillars can be called by ID or name. Optional `mode: brand` (default) or `mode: trend`. Optional `caption: none` (default), `soft` or `hard`, with `brand: <name>` for soft and hard (section 4.1). Also supports Create \[N\] variations of X using pillar Y (different stories, framings and twists), and a series mode for multi-post formats like text stories (up to 5 episodes). Includes helper commands: **list pillars** and **show pillar Y**. |
| D7 | **10 sample content packages** | Across at least **5 different pillars** and at least 5 different topics, for review. Split: 8 slideshows rendered as PNG (2 phone-artifact formats, e.g. one text-story and one app-proof listicle like the cop-dad post, plus 6 photo or text-overlay formats) and 2 videos (1 rendered MP4, 1 storyboard). |
| D8 | **How-to guide \+ demo** | A 1–2 page guide (how to extract, how to create) and a 10-minute live demo or recording. |

## **4\. How pillars and our style combine**

* **The pillar controls:** structure, number of slides, slide roles, hook formula, pacing, text density, layout.  
* **My Style controls:** voice, wording, brand terms, audience, persona (who appears and where), colors/fonts (if set), do-not rules.  
* **If they conflict,** My Style wins on *voice and brand*, and the pillar wins on *format*.  
* **Own brand mode:** My Style is the full established brand and is followed strictly, including the brand's own people, characters and assets when the owner supplies them. The output is also checked against the brand's own posts.  
* **Trend rider mode:** My Style can be light. Details that define the trend (sound, timing, hook wording when it is the trend itself) stay with the pillar.

### **4.1 Caption styles**

Chosen per run with `caption: none | soft | hard`, separately from `mode` (brand or trend). The default is `none`, so a run never mentions a brand unless asked. Soft and hard need a brand profile; `none` never loads one.

| | **none** | **soft sell** | **hard sell** |
| :---- | :---- | :---- | :---- |
| **What it is** | Content for its own sake | A trend or format the brand rides; the brand is only tied in through the caption | An advertisement for one specific product |
| **Image or video** | No brand, product or logo | Follows the pillar. No brand required on it | The product is clearly on it (shown or named), placed where the pillar's product slot says |
| **Caption** | The pillar's caption formula, nothing about a brand | A short callback to the source post or trend (no brand words), an optional source credit for screenshot-sourced pillars (e.g. `Source: r/AskReddit 🔗`), then a bridge of 1 to 2 sentences that names the brand. A stretched link is fine; a false claim is not | Names the brand **and** the product, says what it is and why, ends with the call to action |
| **Disclosure** | None | "This is an advertisement." appended as the last line | "This is an advertisement." appended as the last line |
| **Hashtags** | The pillar's pattern; no brand tags | The pillar's pattern; brand tags allowed | Brand and product tags allowed |

* **Disclosure is appended last** by default: the content plays first and the ad line is the formality at the end, matching how the technique reads on screen. A brand profile can set `disclosure_position: start` instead, for a run that needs the line to show before TikTok cuts the caption at "more". The wording comes from the brand profile (default: "This is an advertisement."). It is separate from TikTok's own commercial content disclosure and AI-generated label, which stay on when posting (section 9).
* **Soft sell technique:** take the most basic essence of the source post or trend (a callback, no brand yet), credit the source if it was screenshotted, then connect that essence to the product — even a stretched connection is fine, a false claim is not — and close with the disclosure.
* **Checked in code** (`tools/caption.py`): style and required parts, brand words only where allowed, disclosure present or absent, the brand's never-say list, length. The image or video for a hard sell is checked by eye.
* **Hard sell and format:** the pillar still controls format. If the pillar has no product slot, the product goes in as a visible prop (no extra slide or ad text) and the package flags it for the owner.
* **Real products, not generated ones:** image models garble labels and logos. Hard-sell images use the brand's real product photos as references, and any label or logo text is drawn or pasted in code.
* **Claims:** only what the brand profile lists as allowed. No medical claims, no invented reviews or studies, in any style.

## **5\. Pillar Template (every pillar has all of these)**

1. **ID \+ name**, e.g. `P004 – Soft-sell listicle`  
2. **Source:** link(s), creator, date collected  
3. **Summary:** one sentence on what this format is  
4. **Best for:** the goals or topics it suits  
5. **Structure:** slide count and slide-by-slide roles (e.g. hook → tip → tip → product → CTA)  
6. **Product slot:** which slide the product sits on, how it is worked into the story, and the soft-sell framing  
7. **Proof device:** the phone artifact used as proof, if any (chat thread, screenshot, map, receipt, notes app)  
8. **Series structure:** for multi-post formats, the episode arc, cliffhangers, and where the product appears across episodes  
9. **Video timing (videos only):** duration, what happens in the first 2 seconds, shot list with timings, pacing (cuts per second), camera setup and movement, voiceover or sound, and on-screen text timing  
10. **Hook formula(s):** fill-in-the-blank templates, plus reference examples, and hook mechanics: why the hook works (credibility, curiosity gap, stakes) and how slide 1 earns the swipe  
11. **Slide text rules:** words per slide, capitalization, tone, point of view, language, emoji  
12. **Visual style:** visual class (main class, plus any others in the mix), image type, composition, colors (hex codes), text overlay (font or closest match, color, outline/box, position, and the text placement pattern with its box range in % of the frame; D1, section 3.2). For selfies, the exact term (selfie, person taking a selfie, photo of a selfie, mirror selfie; D1, section 2.17)  
13. **Caption formula** and **hashtag pattern** (count and types)  
14. **Performance context:** views/likes of the source posts (for reference only)  
15. **Do / Don't** list  
16. **Confidence:**  
    * **High:** the pattern appears in 3 or more posts  
    * **Medium:** it appears in 2 posts  
    * **Low:** it appears in only 1 post (so every post-link pillar starts Low)

## **6\. Targets (pass/fail acceptance)**

**Week 1: signed off on Day 5**

- [ ] D1 guideline delivered and reviewed  
- [ ] Post-link extraction succeeds on **at least 4 of 5** test posts: every template field filled, all slides or the full video downloaded  
- [ ] Creator-link extraction succeeds on **all 3** test creators (using the backup method if TikTok blocks)  
- [ ] Content bank has **at least 10 pillars (from trial testings)**, indexed  
- [ ] **Replication test:** for 3 pillars, a fresh AI session given *only the pillar file* writes a new post outline, and Amplify testers judge it "same format as the source" in **at least 2 of 3**

**Week 2: signed off on Day 10**

- [ ] My Style profile approved  
- [ ] Create command returns a full content package for any pillar in the bank  
- [ ] **10 sample packages** rated 1–5 by Amplify testers on three questions:  
      1\. Does it follow the pillar's format?  
      2\. Does it sound like our style?  
      3\. Could we use it with light edits?  
- [ ] Target: an **average of at least 4** on each question, and **at least 8 of 10** marked "usable with light edits"  
- [ ] Every rendered sample passes the **originality check** (section 12\)  
- [ ] How-to guide delivered and demo done

## **7\. Timeline and check-ins**

| Day | Work | Check-in |
| :---- | :---- | :---- |
| 1 | Kickoff, confirm definitions and test sources, approve Pillar Template | ✅ Kickoff |
| 2 | Guideline v1; post-link data collection working for slideshows and videos |  |
| 3 | Post → pillar extraction; run on 5 test posts |  |
| 4 | Creator-link collection \+ creator summary \+ pillars |  |
| 5 | Run on 3 creators; content bank of 10+ pillars | ✅ **Week 1 sign-off** |
| 6 | My Style profile |  |
| 7 | Create command v1; slideshow renderer (PNG) |  |
| 8 | Generate 10 samples (8 slideshows, 2 videos) → Amplify testers rate them | ✅ Feedback |
| 9 | Improvements from feedback; render the sample video; helper commands |  |
| 10 | Guide, demo, handover | ✅ **Final sign-off** |

## **8\. Out of scope (not included unless agreed separately)**

* **Long videos** over 60 seconds. Short-form videos (up to 60 seconds) and slideshows are fully supported. The visual classes already cover long-form, so the bank is ready for it later.  
* Private accounts; platforms other than TikTok (Instagram, YouTube, etc.)  
* Auto-posting or scheduling to TikTok  
* A web app or dashboard. It runs in **Claude Code on my computer**; outputs are files in a shared folder.  
* More than 20 posts per creator, or tracking performance over time. Section 14 lists what we want but doesn't fit this budget.

## **9\. Assumptions and dependencies**

* **Public data only.** TikTok may block automated access. If it does, a paid scraping service is used as backup (**estimated under $10, needs Amplify's approval**).  
* AI usage runs on the existing Claude subscription. Image, video and voice generation is paid by Amplify through a separate prepaid account (section 13).  
* Scraped posts are used **for internal analysis only**. Pillars store patterns, and source images or text are never reposted.  
* **Film and TV snippets.** Snippets available online are used without licensing. The rights holders can still file takedowns or mute audio on a post, and Amplify accepts that risk.  
* **Disclosure.** Phone-artifact and persona formats (made-up chats, "my dad was a cop" framings) present invented stories as real. Brand posts made from them should use TikTok's commercial content disclosure; turning it on when posting is the client's responsibility. Realistic AI-generated people or scenes also need TikTok's AI-generated content label. Soft and hard captions also state "This is an advertisement." as their first line (section 4.1); that line does not replace TikTok's own toggle.

## **10\. Known risks**

| Risk | Plan |
| :---- | :---- |
| TikTok blocks automated access | Backup method (paid service), or reduce to the latest 10 posts |
| AI misreads a visual detail (e.g. exact font) | Fonts are recorded as "closest match"; I review every pillar before it's saved |
| Pillars from a single post are thin | Marked Low confidence; creator pillars are preferred for key formats |
| Output too close to the original (flagged as unoriginal) | Originality check on every run (section 12): new person and setting, no near-duplicate frames, no copied lines |
| Video downloads get blocked, or videos are slow to process | Same backup scraping service; videos capped at 60 seconds |
| The rendered AI video looks fake or loses the format | Test with short clips first; fall back to a faceless edit (stock clips, AI voice, captions) for the sample MP4 |
| The AI tool account isn't funded in time | The fal.ai account (section 13) is needed by Day 6, before rendering starts on Day 7 |

## 11\. Content bank folders

Every pillar has its own folder. Downloads are kept.

- **content-bank/index.md:** one line per pillar (ID, name, source, summary, confidence).  
- **content-bank/P001-name/pillar.md:** the pillar file (template in section 5).  
- **P001-name/originals/\[post ID\]/:** everything downloaded for each source post: slides or video, post data (caption, hashtags, stats, sound, date), and for videos the transcript, shot list and key frames.  
- **P001-name/runs/run-01\_\[date\]\_\[topic\]/:** one folder per run or version: the content package, the rendered output (PNG slides or MP4), the prompts and AI models used with their cost, and review.md (scores, originality check, feedback).  
- **P001-name/learnings.md:** feedback from the runs, turned into general rules.  
- **content-bank/\_sources/\[creator\]/:** downloaded posts that don't match a pillar yet.

## 12\. How similarity is judged

Two separate questions: are two source posts the same pillar, and is our output the same format without being a copy?

- **Format fingerprint:** every post is scored on 7 points: structure (slide or shot count and roles), hook (slide 1, or the first 2 seconds of a video), camera and motion (visual class and shot type, e.g. selfie in a car, mirror selfie), pacing (length and cuts per second), text overlay (style, position, density), audio (trending sound, voiceover or speech), and emotional arc or payoff.  
- **Same pillar:** two posts belong to the same pillar when they match on at least 5 of the 7 points, and structure and hook both match. Length, cuts and text position are measured in code; the rest is judged by Claude against the pillar, and I review it.  
- **Format match (our output):** a run passes when it matches its pillar on at least 6 of the 7 points and Amplify testers rate "follows the format" 4 or higher.  
- **Originality check (our output):** the movement, framing and structure can stay the same, but at least the person and the setting must change. No slide or frame may be a near-duplicate of an original (checked with an image-similarity score in code), no line of text is copied (under 30% word overlap with the source), and the script or voiceover is new. Trending sounds can be reused. In Trend rider mode, hook wording that is the trend itself (e.g. a meme caption) can also be kept, but the images and setting must still be new. A source's 2D characters are never reused. Film and TV snippets found online can be used, but they come from the film or series itself (not from the source creator's post), and the crop, text and arrangement must be new, so the near-duplicate check compares the whole slide, not the film frame alone. This keeps posts from being flagged as unoriginal.  
- A run must pass both checks.

## 13\. AI generation tools (paid by Amplify)

- **Ask:** a fal.ai account with **$50 in prepaid credits** (no subscription). One account covers AI images (e.g. Nano Banana, Seedream, Flux, about $0.03–0.15 per image), AI video including motion transfer (e.g. Kling Motion Control, about $0.07 per second) and AI voice. It connects to Claude Code through fal's official MCP server.  
- **Optional:** ElevenLabs Starter ($6 a month) for more natural voiceovers.  
- **Estimated pilot spend:** about $5–15 for images (around 150 images including retries) and $15–25 for video (short test clips plus the final sample). $50 leaves room for retries.  
- **Setup:** Amplify creates the account with a company card, loads the credits, creates an API key and shares it with me privately (not in this doc). I add the key to Claude Code on my computer. Prepaid credits work as a spending cap.  
- The paid scraping backup (under $10, section 9\) is separate.

## 14\. Realistic in 2 weeks, and stretch goals

**Realistic (what the 2 weeks cover):**

- Extraction from post links and creator links (latest 20 posts), for slideshows and short-form videos up to 60 seconds, with the originals kept.  
- A content bank of at least 10 pillars, using the folders in section 11\.  
- The similarity rules and originality check in section 12\.  
- My Style profile, the create command, variations and helper commands.  
- 10 samples: 8 PNG slideshows (2 phone-artifacts) and 2 videos (1 storyboard, and 1 rendered MP4 of up to 15 seconds for one pillar).  
- How-to guide and demo.

**Stretch goals (wanted, but not realistic in 2 weeks):**

- Rendering any video format on demand: talking heads with lip-synced speech, multi-scene edits, product demos. The pilot renders one video type; each other type needs its own pipeline.  
- Rendered MP4s for every video sample instead of storyboards.  
- A consistent AI persona (same face and voice across many posts).  
- Applying pillars to a client's real persona and photos (needs their assets first).  
- Automatic trend discovery.  
- Auto-scheduling, and learning from how posted content performs.  
- Instagram and other platforms; more than 20 posts per creator.
