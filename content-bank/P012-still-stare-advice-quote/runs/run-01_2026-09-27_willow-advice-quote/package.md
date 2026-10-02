# P012 · run 01 · Willow · advice quote (friendships)

**Mode:** Trend rider · **Caption style:** none (no brand, no disclosure; the pillar's caption is empty). Pillar = format (one locked, very tight close-up of a still face in a dark room, the credited quote on screen from 0 s in pale yellow, a trending song). Persona = Willow's face and body only (`personas/willow`); room, clothes, credit line and wording come from the pillar and the run.

## Text on screen (a new quote in the pillar's shape)
```
My nan told me this about
friendships, she said:

“Every friendship has a season
that feels easy and a season
that feels like work. In the
easy season you will wonder why
you ever worried. In the hard
season you will be sure it’s over.
When you feel like walking
away, stay.”
```
Shape: a credit line, a two-state contrast (an easy season, a hard season), the moment you want to quit, and a one-word command (`stay`). Word overlap with the source text: **23.7%** of our unique words (9 shared function words: a, and, be, feel, in, my, said, that, the), longest shared run 2 words ("in the"). None of the source's sentences or its "drowning out of love" line is reused. The topic (friendships) and the credit are my choices: no topic was given.
**The credit line:** the source credits a therapist with saving a relationship. Following the pillar's rule, this run credits a plain, non-clinical source (a grandmother) and claims no outcome. The anecdote is still invented, so the AI-generated label matters.

## Shot (1 shot, 5.0 s, locked camera)
Selfie video, term 1 (front camera, no phone in shot). Willow's face fills the top 45% of the frame with her eyes at about 21% of the height; still, closed mouth, serious, glassy-eyed, one slow blink. Plain black crew-neck, a dark bedroom at night with a dim warm lamp, the faint edge of a curtain and a shelf. The bottom half is dark cloth, clear of everything.

## Text style
Pale yellow `#fcffb0` (the source's measured colour), TikTok Sans Medium, **no outline**, sentence case, centred, 11 lines including one blank line, block x 18 to 82%, y 43.8 to 75.7% of the frame (source: 16.3 to 84%, 41.2 to 73.6%), over the black top with the first line just under her chin.

## Caption and hashtags (`caption.txt`, style none)
**Empty**, like the source (no caption, no hashtags). Untested option: 2 to 3 topic hashtags such as `#friendship #advice #realtalk`. TikTok's AI-generated content label ON.

## Sound
Same sound as the source: **"Younger Years" by Zach Bryan** (album "American Heartbreak"), TikTok sound ID `7099926205368895489`, a 60 s sound, not an original sound.
- `output/final_with_sound.mp4`: the video with the source's 5.11 s clip of the sound, cut to 5.03 s with a 0.3 s fade-out. `output/final.mp4` stays silent.
- `sound/younger-years_zach-bryan_source-clip.m4a` (the audio track of the source video, copied without re-encoding) and `sound/sound.json`.
- **Licence:** this is a commercially released song. TikTok's own data flags it `isCopyrighted: true` and `is_commerce_music: false`, so a business or brand account may not be allowed to use it and a file with the song baked in is likely to be muted or blocked. The licensed way is to post the silent `final.mp4` from a personal account and pick the sound in TikTok by name or ID.
- The source's speech transcript read "Letting go, moving on, keeping strong and finding God" over the song. I could not check by ear whether that is a voice in the mix; if it is, this clip carries it.

## Production (what was actually run)
- **Start frame:** Nano Banana Pro, 2K, 9:16, Willow's reference attached. Two generations ($0.18): the first had the right look but her face too low, the second was worse (bigger and lower), so the first was fixed in code (no third generation): shifted up 18% of the height, the empty wall cropped and the dark cloth at the bottom extended by mirroring. Both rejected takes are in `raw/`.
- **Animation:** Kling 3.0 image-to-video, standard, 5 s, silent (`kie.py video`), 716×1284, 24 fps ($0.35).
- **Text:** drawn in code (`tools/textclip.py --fill #fcffb0 --stroke 0`), scaled and cropped to 1080×1920 at 30 fps, burned in for the whole clip, H.264.
- **Cost:** 106 credits = **$0.53** (2 images at 18 credits, 1 clip at 70). `costs.json` has every call.
- **Output:** `output/final.mp4` (silent), `output/final_with_sound.mp4`, `output/preview.jpg`, `output/video_check.json`, `output/word_overlap.json`, `output/text_box.json`.

## Posting
No caption. The source was posted on a Saturday at 22:02 UTC (Sunday 06:02 Manila).
