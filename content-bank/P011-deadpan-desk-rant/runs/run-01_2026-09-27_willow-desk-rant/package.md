# P011 · run 01 · Willow · deadpan desk rant (lunch break)

**Mode:** Trend rider · **Caption style:** none (no brand, no disclosure). Pillar = format (one locked shot of about 5 s, text on screen from 0 s, typing hands at the bottom edge, deadpan look). Persona = Willow's face and body only (`personas/willow`); clothes, office, prop and wording come from the pillar and the run.

## Text on screen (new joke in the pillar's two-sentence shape)
```
Please explain why a
coworker who takes a real
lunch break and still hits
every deadline is somehow
the problem. Relax, Greg,
eating away from my desk
did not sink the
department.
```
Grievance sentence, then a sarcastic address to a named coworker with an absurd understatement, like the source, but every word is new. Word overlap with the source text: **17%** (5 shared function words: did, not, still, the, who; longest shared run 2 words). The source's name ("Karen") and punchline are not reused. Topic (a real lunch break) is my choice: no topic was given.

## Shot (1 shot, 5.0 s, locked camera)
Selfie video, term 1 (front camera propped on the desk, no phone in shot). Willow sits upright at a lived-in office desk, typing on a white keyboard, eyes rolled up and away then a slow side-glance, mouth closed, deadpan. A pencil behind her ear (the source's prop was sunglasses on the head), oatmeal knit cardigan over a white tee (no print), dark green mug at the bottom left (the source's cup was bottom right), sage-green office wall with a cork pinboard of blank notes, a plant, folders and charger cables.

## Text style
White TikTok Sans Medium, thin black outline (TikTok Classic, as in the source), centred, 8 lines, block x 22.6 to 77.4%, y 54.6 to 78.8% of the frame (source: 21.5 to 78.6%, 52.2 to 76.6%), over the cardigan, clear of the face and hands.

## Caption and hashtags (`caption.txt`, style none)
`The department will survive.` + `#worktok #9to5 #workhumor #worklife #relatable`
TikTok's AI-generated content label ON (Willow is fictional; the footage is AI-generated).

## Production (what was actually run)
- **Start frame:** Nano Banana Pro, 2K, 9:16, Willow's reference attached ($0.09).
- **Animation:** Kling 3.0 image-to-video, standard, 5 s, silent (`kie.py video`), 716×1284, 24 fps ($0.35). Kling used the start frame as a reference and pulled the framing back a little, showing more of the room than the still.
- **Text:** drawn in code (`tools/textclip.py`), scaled and cropped to 1080×1920 at 30 fps, burned in for the whole clip, H.264, **no audio**.
- **Cost:** 88 credits = **$0.44**. `costs.json` has every call.
- **Output:** `output/final.mp4` (5.03 s, 1080×1920, silent), `output/preview.jpg`, `output/video_check.json`, `output/word_overlap.json`, `output/text_box.json`.

## Caption variants (2026-09-28, added to the existing render — no new video)
The video is unchanged (`output/final_with_sound.mp4` is the one to post). Two caption options were added for it:

**No sell** (`caption_none.json` → `caption_none.txt`, same text as the run's original `caption.json`):
```
The department will survive.

#worktok #9to5 #workhumor #worklife #relatable
```

**Soft sell** (`caption_soft.json` → `caption_soft.txt`), brand: **Bolt Pharmacy** (`brands/boltpharmacy.md`), a real, GPhC-registered UK online pharmacy offering clinician-led weight-loss prescriptions:
```
Everyone has a coworker who treats doing your job well, and still having a laugh while you do it, like a personal insult. The rest of us are just trying to get through the day.

Bolt Pharmacy makes getting through the day a little easier too: a quick online check, a UK clinician sorts it, and it's one less thing on your plate.

#worktok #9to5 #workhumor #boltpharmacy

This is an advertisement.
```
Bridge is on the *service* (fast, low-hassle, online) — never on weight loss, a medicine name or an outcome. See the compliance note in `brands/boltpharmacy.md`: this is a real prescription-medicine business, `caption.py` only catches word-level slips, and the finished caption needs a compliance review by Bolt Pharmacy before posting.

## Sound
Same sound as the source: **"Ghost on the Walls" by Wren Whispers** (album "Faint Morning Light"), TikTok sound ID `7647885082065471534`, a 33 s sound that is not an original sound.
- `output/final_with_sound.mp4`: the video with the source's 5.13 s clip of the sound, cut to 5.03 s with a 0.3 s fade-out (`tools/sound.py attach`). `output/final.mp4` stays silent.
- `sound/ghost-on-the-walls_wren-whispers_source-clip.m4a`: the clip on its own (the audio track of the source video, copied without re-encoding), with `sound/sound.json` (title, author, album, sound ID, flags, source post, loudness, caveats).
- **Licence:** it is third-party music. The licensed way is to post `final.mp4` and pick the sound in TikTok by its name or ID (the file with the sound baked in may be muted or restricted). TikTok's own data lists it as **not** commercial-library music (`is_commerce_music: false`), so a business or brand account may not be allowed to use it. Check on the account that will post.

## Posting
Caption as above. The source was posted on a Wednesday at 14:45 UTC.
