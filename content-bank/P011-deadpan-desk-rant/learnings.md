# P011 learnings

Feedback from runs, turned into general rules.

## From run-01 (2026-09-27, my own notes, not owner feedback)
- **Kling treats the first frame as a reference, not a fixed frame.** With a persona still of a person at a desk it pulled the framing back and changed the head angle. Plan the text box and face zone against the clip, not the still: look at a frame of the clip before choosing the text height.
- **Prompt for a deadpan human clip:** locked-off camera, small finger movements only, eyes rolled up then a slow side-glance, mouth closed, nothing else moves. This produced a usable 5 s clip in one take ($0.35).
- **Text over a knit cardigan is busier than over plain cloth**, but the thin black outline keeps it readable at 55% of the width.
- **Text style:** the source text is TikTok Classic (white with a thin black outline), confirmed on an enlarged crop. `textclip.py` uses a 0.08 outline ratio (`overlay.py` uses 0.11).
- **Words:** the source rant is the creator's own joke, not a trend phrase, so the hook wording was rewritten (17% overlap) instead of copied.
- **Sound (2026-09-27, owner asked for the source's sound on the replication):** `post.json` and `raw.json` hold the sound's title, author, ID and flags; the source video's own audio track is the clip the source used. `sound.py extract` + `attach` gives a video with the sound and a separate audio file. Keep the silent cut as well, and flag that the sound was not in TikTok's commercial library.
