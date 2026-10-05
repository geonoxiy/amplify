---
name: amplify-plus
description: "Additions to the amplify skill (2026-10-05): Instagram links (extract from Reels, posts and profiles with tools/fetch_insta.py), and the content-quality rules from the boss's test (the scene that carries the hook is format, reuse the source's hook mechanics, product as a list item, authority and prescription-medicine limits, white-box tip lists with tools/boxlist.py). Use together with the amplify skill whenever extracting from an Instagram link, or creating content from any pillar, especially for a real or regulated brand."
---

# Amplify additions (2026-10-05)

Read this together with `.claude/skills/amplify/SKILL.md`. Where the two differ, this file wins: it records the owner's
boss's test feedback (2026-10-05) and the new Instagram tools. It is a separate file so the boss can download only the
new files.

## New tools

| Tool | Does |
|---|---|
| `fetch_insta.py <reel, post or profile link> [--limit 12]` | Instagram without a login: Reels (yt-dlp, full resolution with sound), photo and carousel posts (the public embed page), a profile's latest ~12 posts → `content-bank/_sources/ig_<account>/<shortcode>/`, same `post.json` fields as `fetch.py` plus `platform: instagram`. Views, shares and saves are usually missing (null) |
| `fetch_insta.py --file <video or images…> --handle <account> [--url …] [--caption …]` | Import a post someone saved by hand, into the same folder layout |
| `fetch_insta.py --stats content-bank/_sources/ig_<account>` | The creator numbers for an Instagram account (ranked by likes). Use it instead of `creator_stats.py`, which needs TikTok view counts |
| `boxlist.py render <spec.json> --bg <still or clip> --out <png or mp4> [--seconds N]` · `boxlist.py check <spec.json>` | White-box hook + numbered list over a photo or clip (P016 look): panel or per-line strips, emoji, the lowercase/punctuation rule enforced, and the list kept above the bottom fifth |

## Extract: Instagram links

- Step 1 (Fetch) for Instagram: `fetch_insta.py <link>`, then the usual `prepare.py` and the rest of the steps.
- A login, search, explore or hashtag link (e.g. `instagram.com/accounts/login/?next=…/explore/search/keyword/?q=…`) is
  a search, not an account, and only logged-in accounts can see it. Say so and ask for post or account links. If only
  a screenshot is available, build the pillar from it (crop each post into `originals/screenshot/`), mark it Low
  confidence and say what's missing (captions, sounds, numbers). P016 is the example.
- Never log in to Instagram or use someone's cookies.

## Create: the three fixes from the boss's test

The test (Bolt Pharmacy from a Snidin-style template) kept the text-box style but lost the visual hook and the viral
hooks. A customer will use the tool directly, so the first output has to be right without a second request.

1. **The scene that carries the hook is format, not persona.** When the pillar's authority or hook comes from the
   setting (a clinic, a pharmacy, a gym floor, a kitchen line), recreate that kind of setting even when a persona is
   named: the persona can be the person in the scene, but the post doesn't move to the persona's home. Write the
   setting class from the pillar's Visual style into every prompt before any persona detail.
2. **Reuse the source's hook mechanics, in its register.** Before writing hooks, list the pillar's hook formulas and
   name the mechanic each one uses (experience + disbelief, insider gap, forbidden knowledge, regret, benefit +
   intensifier, interactive trick, …). Every hook option must use one of those mechanics with the source's rhythm
   and level of drama, and a flat, safe summary ("a few things worth knowing about x") fails this rule at any
   overlap. The mechanic's formula phrase ("in case your … never told you", "small habits that … (big time)",
   "i wish more people knew", "10 amazing fun facts") is trend wording and may stay word for word, which can put
   hook overlap above 30%; everything after the formula phrase must be new, and `review.md` reports the measured
   overlap and names the formula words. In `package.md`, label each hook with its mechanic.
3. **Place the product the way the source does.** If the source hides the product as one tip in a list, the new post
   does the same (position and voice from the pillar's Product slot), surrounded by tips that are genuinely useful and
   specific. The rest of the list is the value; it must not read as rules or a leaflet.

## Limits that hold whatever the template does

- **No fake qualifications.** A fictional or AI person never claims a qualification on screen or in the caption
  ("8 years as a dentist", "as a pharmacist", a name badge). The scene can be a real kind of workplace; the words
  speak for the brand or use second-person insider hooks.
- **No copied health claims.** Learn the format, not the claims. Every tip must be true and general; leave out
  anything a source states without basis (instant cures, "in 3 days" results).
- **Prescription-only medicines (e.g. Mounjaro, Wegovy):** UK law bans advertising them to the public (Human
  Medicines Regulations 2012; ASA/CAP). Never name the medicine, show its pen or pack, or claim weight or body
  outcomes, even when the brand says it is their main product. Sell the brand's service instead (a clinician review,
  an online check, delivery), using only the brand profile's allowed claims. Say this plainly to the user when they
  ask for the medicine by name, and make the best compliant version rather than a weaker one.
- Real, regulated brands still need their own compliance sign-off before posting; say so in `review.md`.
