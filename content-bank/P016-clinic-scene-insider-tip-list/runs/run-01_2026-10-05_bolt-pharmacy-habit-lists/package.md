# P016 run-01 · Bolt Pharmacy · five clinic-scene tip lists

Pillar: P016 Clinic-scene insider tip list (from the six Snidin-style Reels in the boss's test doc).
Brand: `brands/boltpharmacy.md` (real UK online pharmacy, GPhC #9013085). Caption style: hard.
Mode: brand. Persona: none (the scene carries the hook, so the worker is a new, unnamed person; see amplify-plus rule 1).

## What the brief asked for, and what this run does instead

The brief: copy the Snidin template for Bolt Pharmacy, "Mounjaro is main product".
- **Copied in full:** the scene (a real kind of workplace, a masked and gloved worker busy and not talking to camera),
  the white-box hook and list, the six hook mechanics (five used here), the long save-worthy list, and the product
  hidden mid-list in the same voice as the tips.
- **Changed, on purpose:**
  - Mounjaro is never named or shown. It is a prescription-only medicine, and UK law bans advertising those to the
    public (Human Medicines Regulations 2012, ASA/CAP); Bolt's own brand profile lists it under never_say. The product
    tip is Bolt's service instead (online check, a UK clinician reviews every case, delivery), which is how a post can
    lead people to the medicine legally.
  - The scene is a pharmacy, not a dental clinic, because that is Bolt's real workplace. No on-screen qualification is
    claimed for the AI worker, and there is no name badge.
  - Snidin's tips include false health claims (vitamin B2 for instant sleep, creams that "erase" lines in days). These
    lists use only general, well-established habits, and make no weight or body outcome claims.

## The five posts

| Post | Hook (mechanic) | Scene | List | Bolt tip | Length |
|---|---|---|---|---|---|
| a | in case nobody told you before starting a weight-loss plan... (insider gap) | worker sealing a parcel at the dispensing bench | 6 items, one panel | #4 | 9 s |
| b | small habits that make a weight-loss plan actually stick (big time) (benefit + intensifier) | masked worker typing in the consultation room | 12 items, one panel | #5 | 12 s |
| c | i wish more people knew this before trying to lose weight (regret) | masked worker checking cartons against a sheet | 7 items, strips | #4 | 9 s |
| d | things nobody explains when you start losing weight (insider gap, the safe form of "forbidden knowledge") | worker loading parcels into a postal tray | 7 items, strips | #5 | 9 s |
| e | 10 amazing fun facts (interactive trick) | masked worker restocking shelves | 10 items, strips | #6 | 10 s |

Full text of each list: `specs/<post>.json`. The "secrets even doctors won't tell you" mechanic was not used: for a
pharmacy brand it implies clinicians hide health information.

Hook word overlap with the closest source hook (measured: shared words / words in our hook): a 36%, b 42%, c 45%,
d 12%, e 100%. The shared words are each mechanic's formula phrase ("in case … told you", "small habits that …
(big time)", "i wish more people knew", "10 amazing fun facts"), which amplify-plus treats as trend wording that
may stay; everything after the formula phrase, and every list item, is new text.

## Captions (hard sell, checked by caption.py: all PASS)

`caption_a.txt` … `caption_e.txt`. Each names Bolt Pharmacy and its online weight-loss consultation and prescription
service, uses only the brand profile's allowed claims, ends with "check your eligibility, link in bio" and the
disclosure "this is an advertisement." Hashtags: 4 each (topic + #ukpharmacy + #boltpharmacy).

## Production

1. Stills: GPT Image 2.5 (gpt25s, 2K, $0.05 each), `raw/stills/`. Prompts set the scene class first (UK pharmacy
   back room, navy tunic, gloves, mask on three of five), then phone-camera imperfections, then "nothing readable,
   no brand or medicine names".
2. Clips: Seedance 2.5 first-frame, 720p, silent, 9–12 s, `raw/clips/` (`--aspect adaptive` is required for
   Seedance first-frame tasks).
3. Text: `tools/boxlist.py render specs/<post>.json --bg raw/clips/<clip>.mp4 --out output/<post>.mp4`.
4. Silent output: pick a trending sound in the app. Switch on the platform's AI-generated label and its paid
   partnership / commercial content toggle when posting.
