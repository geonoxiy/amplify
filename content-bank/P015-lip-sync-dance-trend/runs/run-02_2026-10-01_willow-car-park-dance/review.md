# P015 run-02 · Willow car-park dance · review

**Source:** @zaralarsson post 7683300809983020310 (20 s, 5.3M views, sound "Blue Moon" by Zara Larsson). One static phone on the ground looking up at a dusk parking lot; she starts at the lens, walks back to dance full body, then dances towards the camera to waist up. Fresh run: nothing reused from run-01 except Willow's persona refs.

**Deliverables (owner to choose):**
- `output/option_A_follow_pan.mp4` (recommended): Kling's own camera kept. All checks pass. In the last ~7 s the camera drifts about 10% to follow her (the source phone stays still and she moves left in frame).
- `output/option_B_locked_camera_zoomed.mp4`: camera locked like the source, but hiding the uncovered edges needed a 20% zoom: Willow 10% larger (torso 20.7% vs 18.8%), 4.6 points left, softer (sharpness 188 vs 244), horizon pushed lower.
- `output/compare_source_A_B.jpg`: source, A, B at the same six moments.

## Pipeline used (all new tools on their first real run)
1. Driver 2.7 to 19.5 s of the source (after she steps back from the lens, before the last extreme close-up and the end cut): 16.8 s.
2. `motion.py layout --at start`: she walks towards the camera, so the still matches her starting placement (nose 52.6%, centre 50.7%, torso 16.5%, full body). Open scene: no vanishing point; new far-ground-edge detector: 73.6% (camera at about hip height).
3. Still: Nano Banana Pro twice put the camera at chest or shoulder height (ground edge behind her head), once at a worm's-eye angle; **Seedream 5.0 Pro matched the low angle** (head and shoulders against the sky). `motion.py fit` → predicted nose 52.7 / centre 50.8 / torso 16.1 after the model, no warnings.
4. Two 1080p takes, minimal prompt, background from our still: movement error 5.0° on both (best so far). Both takes **panned the camera to follow her** once she came closer (take A about 10%, take B about 22%, confirmed by direct background matching); take A used.

## Checks (option A)
| | Source | Option A |
|---|---|---|
| Movement error | | 5.0° (arms 6.9, legs 3.9) |
| Placement over the clip (nose / centre / torso) | 47.5 / 50.0 / 18.8 | within 2 points / 8% (check passes) |
| Brightness / saturation / sharpness / noise | 51.3 / 17.7 / 324 / 1.4 | 51.0 / ~17.8 / 244 / ~1.1 |
| Faces | face check finds a face in 68% of samples on the source itself (she is small and often turned away) | 69%: same limit; judged by eye: natural, a short hand-and-hair smear around 13.5 s |

## Tried and rejected (files in `raw/`)
- Locking take A's camera and filling the uncovered edge from our still, then from the clip's own first 3 s: a visible vertical seam at the left edge from ~12 s. Kling's late camera move has parallax (near concrete and far sky shift differently), so no flat correction lines up both.
- "Keep a fraction of the pan": cancelling any share of a pan uncovers that share of the edge; removed from the tool.

## Caption and sound
`golden hour on the top deck 🌆 dc @zaralarsson` (style none, PASS). Pick "Blue Moon" by Zara Larsson in TikTok and start it about 2.7 s in so the moves land on the same beats. AI label on.

## Cost
951 credits ($4.75): four stills $0.43 (two unused for the wrong camera height), two 1080p takes $4.32.

## Owner verdict
Pending.
