# Review · P016 run-01 · Bolt Pharmacy

## 7-point format check against the six source posts

| Point | Source (P016) | This run | Match |
|---|---|---|---|
| Structure | hook box + 5–15 item list, product mid-list | hook box + 6–12 item list, Bolt at #4–#6 | yes |
| Hook | six insider/curiosity mechanics | five of the six mechanics, one per post, labelled in package.md | yes |
| Camera & motion | masked/gloved worker busy in a real professional room, not addressing camera | masked/gloved pharmacy worker busy in a pharmacy back room, not addressing camera | yes (pharmacy instead of dental clinic, on purpose) |
| Pacing | one long hold, dense text | one 9–12 s shot, dense text | yes |
| Text overlay | white boxes, black text, hook top, list over chest | same, via boxlist.py (panel on a, b; strips on c, d, e) | yes |
| Audio | unknown | silent, sound picked in the app | n/a |
| Arc | "you didn't know this" → quick wins | same; e keeps the playful trick payoff | yes |

## Numbers from code

- `boxlist.py check`: all five specs pass (no banned punctuation, list ends at or above 80% of the height).
- `caption.py check --brand brands/boltpharmacy.md`: caption_a … caption_e all PASS (hard style, product named,
  disclosure last, no never_say words).
- Hook word overlap with the closest source hook: a 36%, b 42%, c 45%, d 12%, e 100%. Above the 30% guide on four
  of five because each keeps its mechanic's formula phrase ("in case … told you", "small habits that … (big time)",
  "i wish more people knew", "10 amazing fun facts") as trend wording, per amplify-plus rule 2. Flagged for the owner.
- `originality.py` not run: the pillar's originals are grid screenshots, not downloaded posts, so there is no source
  text or video to compare against. Every list item and every frame is new.

## Known limits

- The pillar comes from one screenshot (Low confidence): no source captions, sounds, lengths or performance numbers.
- Seedance renders at 720p (718x1280); boxlist scales it to 1080x1920, so the picture is a little soft (the text is
  drawn at full resolution).
- On post a the list panel covers the worker's hands; the uniform, gloves and shelves still carry the scene.
- Mounjaro is not named anywhere (prescription-only medicine, see package.md). Bolt Pharmacy's own compliance team
  must review every post and caption before anything is published; this run is not a legal review.

## Tester ratings
Pending.

## Owner verdict
Pending.
