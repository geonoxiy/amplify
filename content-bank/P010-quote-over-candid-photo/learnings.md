# P010 learnings

Feedback from runs, turned into general rules.

## From run-01 (2026-09-25, my own notes, not owner feedback)
- **Put the text where there is nothing to cover.** The model put Willow's chin at ~46% of the frame even when asked for her head in the top quarter. Check the face position before choosing the text height; the source's ~47% only works if the faces are above it. Otherwise move the block down over plain clothing.
- **No lettering on clothes.** A printed graphic tee came out as garbled words, which reads as AI and competes with the overlay. Ask for a plain tee or a print with no letters.
- **Low-light flash look:** ask for "only the flash lights her, the room falls into near-black". Without it the room comes out bright and clean.
- **Text style:** this source used a soft shadow and no thick outline (P004 used the thick Classic outline). Use `overlay.py --style shadow --weight 700`. Estimated from one screenshot; confirm on a larger view.
- **Text style may have been Classic after all (2026-09-27 note).** A later source (P011) showed TikTok's native text as white with a thin black outline when seen on an enlarged crop. P010's soft shadow reading came from one small screenshot; if the P010 source is ever downloaded, recheck on a large frame.
