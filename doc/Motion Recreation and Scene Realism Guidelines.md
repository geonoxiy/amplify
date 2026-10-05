# Motion Recreation and Scene Realism Guidelines

How we copy a real person's movement onto a persona and rebuild the scene around them, so the finished video reads as phone footage of a real person in a real place. That means every part of the body moving like a human, a background with real depth, focus and small signs of life, and one light that reaches everything in the frame.

This builds on the Persona Appearance and Environment Guidelines (called "Persona guidelines" below), which cover who the persona is, how they look and how their body reacts. It also builds on the motion transfer route (SKILL step 7) and the P015 learnings, which record what has worked so far. Every tool named here is marked **built** (exists today) or **planned** (in the roadmap, Part 14). Every threshold is **provisional** until we calibrate it (Part 12).

## Part 1: Principles

### 1.1 What makes a video read as real

* **A person is many motions at once.** Weight and limbs, hands and fingers, head, face, eyelids, eyeballs, lips and jaw, breathing, hair, clothes and accessories all move. Around the person, so do the camera, the light, the background and the foreground. Viewers forgive a channel that is plain. They notice any channel that is frozen, too smooth, too regular, or moving without a cause. So each channel gets its own spec, its own measurement and its own reject rule.
* **Nothing perfectly still, nothing moving without a cause.** A frozen background reads as a photo backdrop. A wall that wobbles reads as AI. Things that would move should move the way they really do. Things that can't move should never move.
* **Irregular timing.** Real motion speeds up, slows down, pauses, overshoots and settles. Blinks, gusts, glances and weight shifts come at uneven intervals. Only machines repeat exactly.
* **Coupling.** Things that share a cause move together. One gust moves the hair, the hem, the leaves and the curtain in the same direction, reaching each one in turn. A cloud dims the person and the street at the same moment. A step lands as the hair bounces and the earrings swing. Channels that ignore each other (hair blowing while the trees stay still) are a strong AI tell.
* **Physics is free realism.** Gravity, inertia, contact, light falloff and lens optics all have known numbers. Where a model gets them wrong we can measure the error, and often fix it in code.
* **Copy the source's numbers, not the source.** Measure the source's camera, framing, blur, noise, blink rate, motion energy and background motion. Then hit those numbers with a new person in a new place. Comparing against the source works better than fixed thresholds.
* **Layers (owner rule, P015).** Background, character, foreground. Change the background and the character. Keep the foreground as empty or as busy as the source. Keep the camera angle, the camera movement and the person's placement.
* **One world per shot.** One light setup, one wind, one time of day, one camera. Every layer agrees with it (Persona guidelines 4.1).
* **Phone, not cinema.** The target is a phone in someone's hand: deep focus, a little shake, auto exposure, sensor noise, compression. Shallow cinematic focus, a gimbal-smooth camera and film-style motion blur read as AI or as an advert.
* **No single model does everything.** The pipeline splits the work. Real human motion comes from a driver clip. The look comes from the still. Targeted passes fix specific faults. Physics and optics are done in code. A person looks at every take.

### 1.2 How this document is organised

* Part 2: the pipeline, and the per-shot scene sheet.
* Parts 3 and 4: the body and its secondary motion, one channel at a time. Each channel has four headings: **Real** (how a real human does it), **Track** (what we measure), **Recreate** (how the output gets it right) and **Reject** (what fails a take).
* Parts 5 to 8: the scene. Background and depth, background micro-movement, light, and the camera.
* Part 9: consistency over time. Part 10: shot types. Part 11: choosing drivers.
* Part 12: measurements and calibration. Part 13: review checklist. Part 14: roadmap. Part 15: guardrails.

## Part 2: The Recreation Pipeline

### 2.1 Stages

| Stage | What it produces | Built today | Planned |
| :---- | :---- | :---- | :---- |
| 1. Break down the source | Per-channel tracks: body, hands, face, eyes, mouth, head, camera, light, depth, background motion, beats | `motion.py scan` (33 body points), `layout` (placement, vanishing point, ground edge, camera static or moving), `measure.py` (sharpness, noise, saturation, clutter) | Face mesh with 52 expression scores, iris and head pose; both hands; depth; optical flow; light; audio envelope |
| 2. Scene plan | The scene sheet (2.2): world, depth, lens, focus, micro-motion, light events, method | Written by hand in `package.md` | Scene sheet template in the run folder |
| 3. Character still | Persona in the new place, placed and lit to plan | `kie.py image` (Nano Banana Pro 4K, Seedream 5.0 Pro edit), layout guide, `motion.py fit` | Depth and light checks on the still |
| 4. Clean plate and depth | The same still with the persona removed, plus its depth map | none | `motion.py plate` (image edit) and depth (Video Depth Anything) |
| 5. Performance pass | The persona copies the driver: body, head, face | `kie.py video --model seedance25` in reference mode (the main model, owner decision 2026-10-05); Kling 3.0 Motion Control as the fallback; `splice` | A face pass for close-ups; a local fix pass for hands |
| 6. Background pass | Micro-motion in regions the person never covers; the foreground layer | none | Ambient clip (image-to-video of the clean plate, locked camera) and a region composite |
| 7. Light and lens pass | Matched light, focus from depth, motion blur, camera, noise | `finish` (camera lock or replay, grade, sharpen, grain, pull-back) | Depth-based focus, shutter blur, exposure and white-balance lag, noise by brightness |
| 8. Check | Per-channel numbers, frame tiles, face sheet | `check`, `faces`, `measure.py` | Per-channel check, plus stability, light and depth reports |
| 9. Review | Owner review against the checklist | Part 13 | |

Pipeline rules:

* **Each pass fixes only its own channel and must not undo another.** A face pass must not move the head. A background pass must not touch any pixel the person ever covers. The light pass works on the whole frame at once.
* **Keep the model's own frame wherever it is good.** Swapping a whole layer loses contact shadows, light spill and occlusion, and makes the person look pasted on. Replace regions, not layers (5.10).
* **Measure every pass against the previous pass and the source.** Drop any pass that makes some channel worse.
* **Keep every take and pass in `raw/`**, with the reason in the file name (existing rule).

### 2.2 The scene sheet (per shot)

Filled in before the still is rendered, next to the moment spec (Persona guidelines Part 7). The moment spec says what the person is doing. The scene sheet says what the world, the camera and the light are doing.

| Field | What to decide |
| :---- | :---- |
| World | Place, time, season, weather, wind (direction, strength, gusty or steady), temperature, open windows, heat sources |
| Light plan | Key light (source, direction, hardness, colour temperature), fill and bounce, practical lights in frame, light events during the clip (7.1) |
| Depth plan | What sits in each layer: foreground (0 to 1 m), subject distance, midground (2 to 5 m), background (5 m and beyond) (5.1) |
| Lens and camera | Which camera (front, main, ultra-wide), equivalent focal length, height, distance, tilt, who holds it, handheld or propped, camera movement (5.2, Part 8) |
| Focus | Deep focus (default) or portrait/Cinematic mode as in the source; focus point; expected background blur in pixels (5.3) |
| Focal point | Where the eye should go, and what in the background must stay calmer than the face (5.4) |
| Micro-motion | The 2 to 4 background elements that move, why, and how much (Part 6) |
| Background life | People, vehicles, animals, screens: how many, where, how they move (5.8) |
| Foreground | Empty or busy, as in the source; what, at what depth, how it moves (5.9) |
| Driver | Source clip and segment, face size in pixels, hand size, contacts, how the motion crosses the light (Part 11) |
| Method | Which passes run, chosen from the face size and shot type (3.4, Part 10) |

Worked example (written for us, not the prompt): Willow lip-syncing a talking trend in her kitchen.

* World: Bristol, early October, late afternoon, dry. The kitchen window behind the phone is open a crack, so a gentle draught blows into the room. A pan simmers on the hob beside her.
* Light plan: low sun comes straight through the west window behind the phone. It is a warm, hard key light from slightly left of the lens (her right). The white cupboards and tiles bounce soft fill. The cool ceiling light is off. Light event: a cloud passes at about 8 s. Over 1 to 2 s the light turns soft and cooler, the shadows fade, and the phone's exposure brightens a moment later.
* Depth plan: foreground empty, as in the source. Willow at 1.0 m. Fridge with magnets and the shopping list at 2.5 m. The door to the hall at 3.2 m, the dim hallway beyond at 4 to 6 m.
* Lens and camera: rear main camera (about 24 mm equivalent), propped on the windowsill at chest height, level. The camera is completely still, so any camera motion is wrong.
* Focus: deep focus on her face. The fridge is about 2 px soft at 1080×1920, nothing creamy.
* Focal point: her face. The fridge magnets stay small and low-contrast. Nothing busy directly behind her head.
* Micro-motion: steam from the pan drifts into the room, away from the window. The loose corner of the shopping list flutters in the draught. The flatmate's trailing plants on the windowsill (out of frame, between the sun and her) cast leaf shadows that shimmer on her shoulder and the fridge. Her backlit flyaways lift slightly. All of it moves in the same draught, in the same direction.
* Background life: none (the flatmate is never on camera).
* Driver: a chest-up lip-sync clip, face about 300 px tall. The driver's head stays within about 30° of the lens. Her light doesn't change during the moves.
* Method: performance pass, then the expression, blink and mouth checks. A face pass only if the mouth fails. Leaf shadows and the cloud dimming are done in code (6.5), not by the model.

## Part 3: The Body and Face, Channel by Channel

### 3.1 Weight, balance and the whole body

Real:

* The body is always balancing. Its centre of mass stays over the feet. When it moves past them, the person steps, leans on something or falls. Standing "still", weight shifts every few seconds and the body sways slightly.
* Weight transfer shows. The hip shifts toward the standing leg, the other knee softens, and the shoulders tilt the opposite way to the hips.
* Big moves have preparation and follow-through: a dip before a jump, a wind-up before a throw, an overshoot and a settle after a stop.
* Gravity has fixed timing. A jump with 0.5 s in the air rises about 30 cm. With 0.3 s in the air it rises about 11 cm. Floaty jumps (long time in the air, low height) and falls that feel like slow motion are the most common physics fail.
* Walking: pelvis and shoulders counter-rotate, arms swing opposite the legs, and the head bobs 4 to 5 cm per step. Normal pace is about 1.3 m/s at 100 to 120 steps a minute.
* The shoulder blades move with the arms. An arm raised above shoulder height lifts and rotates the shoulder. Reaching forward rounds the upper back.
* The spine bends with every move. Looking down at a phone pushes the neck forward and rounds the upper back.

Track:

* Built: 33 body points (MediaPipe Pose), limb angles in the image plane, limb energy, tempo, movement label, travel, framing, limb stretching, timing lag.
* Planned: the pose model's world coordinates (metres, centred on the hips), to measure angles in 3D. An arm pointing at the lens looks short in 2D. Also planned: centre of mass against the feet, time in the air against jump height, and weight-shift events.

Recreate:

* Body motion comes from the driver through the motion model.
* The still's pose is close to the driver's first frame (`driver_pose0.png`, built), with the weight on the same leg.
* The persona's proportions differ from the driver's. Contacts are checked in 3.8.

Reject:

* Limb angle error over the threshold (Part 12).
* A body balanced on nothing: centre of mass outside the feet with nothing to lean on.
* Floaty jumps or slow falls.
* Limbs bending the wrong way, stretching (built check), or passing through the body or a prop.

### 3.2 Hands and fingers

Real:

* At rest, the fingers curl in a cascade: the index finger straightest, the little finger most curled, the thumb along the side of the index. Hands are never flat and spread unless they are pressing or gesturing.
* Hands are busy (Persona guidelines 3.3). They gesture slightly ahead of the words, touch the face, hair and clothes, and hold things.
* The grip follows the object. Fingers wrap around it, skin compresses at contact, and tendons show on the back of the hand when the fingers spread.
* When the wrist moves fast, the fingers follow a beat later (loose joints).

Track:

* Planned: MediaPipe Hand Landmarker (21 points per hand, both hands). It gives the curl of each finger, open or closed hand, whether each hand is visible, and the hand-to-face and hand-to-hand distances.

Recreate:

* The motion model copies hand moves at the driver's resolution. Small hands, as in a full-body dance, come out approximate. When hands matter (product shots, gestures in a close-up), pick a driver where the hands are large in frame.
* A product starts in the still, in the persona's hand, with the right grip (Persona guidelines 3.4). The model can't reliably add a prop partway through a clip.
* For a few bad frames: cut to a better take (`splice`, built), or test a local video edit (Seedance 2.5 local editing, Gemini Omni 1.1 Flash, Kling 3.0 Omni transformation; all untested by us).

Reject:

* Extra, missing or fused fingers in any frame. Check by eye in the tile: the hand model always returns 21 points, so it can't count fingers.
* Fingers bending backwards, or hands melting during fast moves or when they cross.
* A grip that couldn't hold the object, or an object passing through the fingers.
* A product label that warps. Readable labels are composited in code, never generated (SKILL rule).

### 3.3 Head and neck

Real:

* The head is never still while someone talks. It nods on stressed words, tilts, and turns toward what the person is thinking about. Listening and thinking have their own moves: a tilt, a slow nod, chin up.
* The eyes lead and the head follows. For a look more than about 20° away, the eyes jump first. The head catches up over 0.2 to 0.5 s while the eyes turn back to stay on the target (3.5).
* The neck shows the move. The side neck muscle stands out on a turn, the throat moves on a swallow, and the skin folds when the chin goes down.
* When walking, the head stays steadier than the body.

Track:

* Built: head angle from the shoulders to the nose (image plane).
* Planned: head turn, nod and tilt angles (yaw, pitch, roll) from the face model's transform; nod and tilt events; head-turn timing against gaze shifts.

Recreate:

* Head motion comes from the driver.
* Big turns toward profile are where identity drifts. In the Willow reference set, about 1 in 4 full-body and three-quarter takes drifted. The still call gets the character sheet (three-quarter and profile). The video model has only the still to go on, so prefer drivers whose turns stay within about 45° of the lens, or check the turns frame by frame.

Reject:

* Head pose error over the threshold.
* The head turning on a rigid neck.
* The face changing identity during a turn.
* A head locked still while talking.

### 3.4 Face and expression

Real:

* Faces move in muscle groups (the FACS action units). A real smile lifts the cheeks and narrows the eyes as well as the mouth. Surprise lifts the brows and widens the eyes. Disgust wrinkles the nose. Concentration lowers the brows and pulls them together.
* Skin moves with the muscles. Smile lines deepen in a smile. Forehead lines appear when the brows lift and fade afterwards. Crow's feet show in a laugh. The chin dimples when the lips press. Moles and freckles move with the skin. Light highlights do not (7.3).
* Expressions are asymmetric and mixed. They build and fade. Micro-expressions last under half a second. The resting face is neutral, not smiling (Persona guidelines 3.2).
* Expressions are reactions. They follow their cause (a sound, a line of the song, a thought) by 0.2 to 0.5 s.

Track:

* Built: `motion.py faces` samples the output, measures face proportions, and flags warped frames.
* Planned: the face model's 52 expression scores per frame (jaw open, smile left and right, inner brow up, brow down, cheek squint, eye squint, nose sneer, lip press, pucker and so on), on both the driver and the output, compared as time series.

Recreate:

* The motion model copies expressions with the motion, but detail scales with face size. At about 150 px (knees-up framing) expressions come out coarse and fast moves smear (P015). Face size decides the method (sizes provisional, from P015 only):

| Face height in the output | Method |
| :---- | :---- |
| Under about 200 px (full body, knees up) | Performance pass only. Accept coarse expressions. Prefer drivers with calm faces and few fast head turns. |
| About 200 to 400 px (waist up) | Performance pass, check expression scores, splice the best windows from several takes. |
| Over about 400 px (chest up, talking head, lip-sync close-up) | Performance pass, then a face pass if the face check fails. Candidates to test on kie: Volcengine video-to-video lip-sync, InfiniteTalk, OmniHuman 1.5, Kling AI Avatar. The face pass runs on a face crop that is blended back. |

* Teeth and the inside of the mouth come from the still. Show the teeth in the still if the mouth will open (P015 round 3).
* The driver's person brings their own way of moving their face. Choose drivers whose style fits the persona (Part 11).

Reject:

* Face proportions jumping (built flag).
* A smile that doesn't reach the eyes.
* Perfectly symmetrical expressions throughout.
* Expressions switching on and off from one frame to the next.
* Skin that doesn't crease with the expression (plastic), or lines that stay after it ends.
* Skin texture swimming: moles sliding, freckles changing.
* Teeth changing count or shape.

### 3.5 Eyes: lids, blinks, gaze and the eyeballs

Real:

* **Blinks.** 15 to 20 a minute at rest, more while talking (up to about 25), fewer while concentrating on a screen. A blink lasts 100 to 400 ms: the lid drops fast and rises more slowly. The gaps are irregular, some 1 s apart, some 8 s. Blinks cluster with gaze shifts, head turns, sentence ends and beat drops. Both eyes blink together.
* **Gaze moves in jumps.** Each jump (a saccade) takes 20 to 100 ms. Then the eyes hold on a point for about 0.2 to 0.5 s before the next jump. The eyes only glide smoothly when following something that moves.
* **The eyes are never dead still.** Tiny jitters and drift continue while they hold on a point, about 1 to 2 a second.
* **Both eyes aim at the same point.** They turn together, and turn slightly inward for something close, such as a phone near the face. Misaligned eyes are a strong AI tell.
* **The eyes lead the head**, and turn back to stay on the target as the head turns.
* **The lids follow the eyeball.** Looking down, the upper lid drops with the eye and covers more iris. Looking up, it lifts. The lower lid rises in a smile or a squint.
* **Pupils react to light.** They shrink in bright light and widen in dim light, taking about a second after the light changes. The iris pattern and colour stay locked (persona file).
* **Catchlights stay with the light.** The reflection of the window or lamp stays in place as the eye rotates, so it slides across the iris. Both eyes show it in matching spots. It disappears when the eye is in shadow.
* **Wet surface.** A thin line of tears along the lower lid and a sheen on the whites. Eyes water in wind and cold.
* **Every gaze has a target and a reason** (Persona guidelines 3.1). The eyes go away to think and come back to make a point. In a selfie video they rest on the screen, just below the lens.

Track:

* Planned: blink events from the face model's blink scores, giving the rate, durations, gaps and timing against head turns.
* Planned: gaze from the iris centre relative to the eye corners (the face model has 10 iris points). That gives direction, number of jumps, holding times, the share of time on the lens, and whether both eyes agree.
* Pupil size isn't reliable at our resolutions: check it by eye.

Recreate:

* Eye motion comes from the driver, at the driver's face size. With small faces the model often drops blinks or lets the eyes drift. Check, then splice or re-take.
* The still: eyes looking where the driver's first frame looks (not at the lens by default), lids matching the gaze, catchlights matching the windows and lamps in the scene.

Reject:

* No blink for over 6 s in a talking or dancing shot.
* Blinks at a regular rhythm, or one eye blinking alone (unless it's a wink).
* Eyes gliding instead of jumping, or not aiming at the same point.
* Eyes on the lens for the whole clip when the source looks away.
* Catchlights that are glued to the iris, missing, or different between the eyes.
* Iris changing colour or shape; lids not following the gaze.

### 3.6 Mouth, lips, jaw, teeth and tongue

Real:

* **Speech moves the jaw on every syllable**, about 4 to 6 a second. The lips shape each sound. They close fully on p, b and m, which is the easiest lip-sync check. The lower lip touches the upper teeth on f and v. The lips round on "oo" and "o" and spread on "ee". The tongue shows briefly on "th" and "l".
* **The mouth leads the sound** slightly: the lips start shaping a sound just before it is heard.
* **Singing and lip-sync** open the jaw wider on held notes. Breaths show before phrases: the mouth opens and the chest lifts.
* **Lips are soft.** They compress on closure, stretch in a wide smile, bunch in a pucker, and stick slightly as they part after a closure.
* **The cheeks and chin move with the mouth.** The nostrils flare on a deep breath.
* **Teeth are locked** (persona file). Count, shape and alignment never change. Some sounds show the lower teeth, some the upper.
* **Sync tolerance.** Viewers notice sound arriving more than about 45 ms before the lips move, or more than about 125 ms after (ITU-R BT.1359). Aim for within 40 ms.

Track:

* Planned: mouth opening (inner lip gap divided by eye spacing) and lip width per frame, closures on p, b and m (opening near zero), and the jaw-open score.
* Planned, for lip-sync content: cross-correlate the mouth opening with the loudness of the audio to get the offset in milliseconds.

Recreate:

* In lip-sync trends the driver's person is already lip-syncing the track, so the performance pass carries it. The sound is added in TikTok at the right offset (P015: a driver trimmed by 1.6 s means the sound starts 1.6 s in).
* For close-ups where the mouth misses the closures: a lip-sync pass on the face crop, driven by the track's audio (to test, 3.4).

Reject:

* Lips moving without the jaw.
* The mouth flapping without full closures on p, b and m.
* Lips out of sync by more than about 40 ms.
* Teeth changing count, shape or colour, or smearing into a white band.
* An empty black mouth interior.

### 3.7 Breathing and small body motion

Real:

* 12 to 20 breaths a minute at rest, faster and deeper after effort, when the chest and shoulders rise visibly and the mouth opens. Breathing moves the chest, belly, shoulders and collarbones. There is a breath in before speaking, and a sigh drops the shoulders.
* Swallows, sniffs, small adjustments (hair pushed back, a sleeve pulled), weight shifts and fidgets mean a "still" person is never a statue (Persona guidelines 3.5).
* Effort shows: neck tendons, flushed skin, heavy breathing after a dance (persona states).

Track:

* Planned: the up-and-down rhythm of the shoulders at rest (breathing rate, where visible), and how much the body moves in the "still" stretches.

Recreate:

* This comes from the driver. A driver that holds still after a dance should still breathe. If the model freezes the body, cut earlier or splice.

Reject:

* A body frozen in the still stretches (a mannequin).
* Breathing at a perfectly regular rhythm.
* No heavy breathing after a hard dance.

### 3.8 Contact and retargeting

Real:

* Contacts are where viewers judge realism. Planted feet don't slide. A hand on the face presses the cheek. Clasped hands touch. A hand on the hip pushes into the fabric. Sitting compresses the cushion. Leaning puts weight into the wall.

Track:

* Planned: foot contacts (ankle and heel points nearly still, at their lowest, for 3 or more frames).
* Planned: self-contacts (hand to face, hand to hand, hand to hip, hand to hair, measured as distance against torso length) and prop contacts.

Recreate:

* The persona's arm length, height and head size differ from the driver's. Contacts can break (a hand that touched the face now hovers) or overshoot (the hand goes into the head). Where contact matters, choose drivers with a build similar to the persona's, and check contacts frame by frame.

Reject:

* Feet sliding more than about 2% of body height while planted.
* A contact in the driver that doesn't happen in the output, or the other way round.
* Body parts passing through each other, props or furniture.
* A seated person floating above the seat, or no compression where the body presses.

## Part 4: Secondary Motion: Hair, Clothes, Accessories and Props

### 4.1 Hair

Real:

* **Hair has weight and lags the head.** It starts moving after the head does, overshoots when the head stops, then settles over 0.5 to 1.5 s depending on length.
* **Length sets the timing.** A hanging ponytail of about 25 cm swings back and forth roughly once every 0.8 s. Longer hair swings more slowly; short hair barely moves. Slow, floaty hair at normal speed looks like slow motion or underwater.
* **Hair collides.** It lands on the shoulders, splits around them, catches on a collar, and sticks to a sweaty neck.
* **Hair stays where it was put.** Hair tucked behind the right ear stays there until a hand or a shake moves it. A strand over the shoulder stays over the shoulder.
* **Texture changes the motion.** Fine straight hair swings as a sheet, curls bounce and spring, thick hair moves in clumps.
* **Wind** (Persona guidelines 4.6, and 6.3 here): strands cross the face in gusts.

Track:

* Hair has no tracker today: look at it in the tiles and at full speed.
* Planned: motion inside the hair region compared with the head's motion, to catch frozen hair or hair that moves on its own.

Recreate:

* The model makes the hair motion from the still. The still must show the persona's real hair texture with flyaways. A polished helmet of hair in the still stays a helmet in motion.

Reject:

* Hair frozen while the head moves, or moving with no head move or wind.
* Hair changing length, parting or colour; strands appearing or vanishing.
* Hair passing through the shoulders or face.
* A ponytail swinging too slowly for its length.

### 4.2 Clothes

Real:

* **Fabric weight and stiffness decide the motion** (Persona guidelines 4.10). Denim and coats move with the body and swing little. Jersey clings and ripples. A loose T-shirt lags and flutters. A skirt swings like a pendulum and wraps the legs on a turn.
* **Wrinkles come and go with the pose.** They gather where fabric is compressed (inside the elbows, at the waist, behind the knees) and flatten where it is stretched. The same pose gives roughly the same folds.
* **Fabric lags and settles.** After a stop, loose fabric keeps moving for a fraction of a second.
* **Prints, logos, seams, pockets, buttons and hems are part of the fabric.** They bend with the folds. They never slide across it, change size, or change number.
* **Fabric reacts to wind, water, sitting and holding** (Persona guidelines 4.5 to 4.10).
* **Light on fabric** is covered in 7.4.

Track:

* No tracker today.
* Planned: a texture-swim check that looks for motion inside the clothing area that doesn't follow the body.

Recreate:

* The model makes the clothing motion from the still. Start from clothes at the right lived-in level (Persona guidelines 4.10). Avoid tiny repeating patterns (fine stripes, small checks): they shimmer and swim in video.

Reject:

* Clothes moving as a rigid shell, or folds frozen while the body moves.
* A print or logo sliding or morphing; buttons or pockets changing; the hem length changing.
* Fabric passing through the body.
* Fine patterns flickering.

### 4.3 Accessories

* Earrings swing with head moves (hoops more than studs). Necklaces slide, swing, and settle into the collarbone. Bag straps slip. Watches and rings stay exactly in place and in number.
* Glasses move rigidly with the head, reflect the light sources, and slightly distort what is behind the lenses.
* Reject: jewellery appearing, vanishing, changing or floating off the body; earrings dead still through a head shake.

### 4.4 Props and products

* Props are non-negotiable (owner rule: we must be able to showcase different products).
* The product is in hand in the still, with the real grip. Its weight shows in the arm and body. It moves rigidly with the hand, with no wobble or change of shape. Its label is real art composited in code when it must be readable. It casts a shadow and reflects the light.
* Putting the product down or picking it up is where models fail: the object vanishes or duplicates. Prefer drivers where the prop stays in hand, or check every frame of the hand-off.
* Reject: the product changing shape, size, colour or label; the object passing into the hand; a floating object; a prop appearing from nowhere.

## Part 5: Background and Depth (the background renderer)

What "renderer" means here: we don't build 3D scenes. We produce a background that obeys the rules a real camera does: depth, perspective, focus, blur, parallax, light and small motion. It is designed in the still, checked against a depth map, and finished in code.

### 5.1 Depth plan

* **Write the depth layers before the still is rendered:** foreground (0 to 1 m from the lens), the subject's distance, midground (2 to 5 m), background (5 m and beyond), and sky or far distance.
* **Give every layer content.** A real room has something at every depth: a chair edge, the persona, a table, a far wall with a door. A flat wall right behind the person removes depth. An empty middle reads as a backdrop.
* **Use all the depth cues, and make them agree:**
  * Overlap: nearer things hide farther ones.
  * Relative size: known objects shrink with distance. Doors are about 2 m tall, kitchen counters about 90 cm, chair seats about 45 cm. Ceilings run 2.4 to 3 m, higher in Victorian houses.
  * Perspective lines meeting at the vanishing point.
  * Texture getting finer with distance (floorboards, bricks, tiles).
  * Light falloff: darker farther from a window or lamp.
  * Haze outdoors: far things lower in contrast and bluer.
  * Focus (5.3).
* **Check the scale.** The persona's height (persona file) against door frames, counters and light switches, so they aren't too big or too small for the room.

### 5.2 Perspective and lens

* **The lens fixes the perspective.** Typical phone lenses in 35 mm equivalent: main camera about 24 to 26 mm, ultra-wide about 13 mm, telephoto 70 to 120 mm, front camera about 23 to 25 mm.
  * A wide lens at arm's length distorts the face slightly (bigger nose, ears hidden, a near hand looks large) and makes the background look far away and small.
  * A telephoto flattens the face and makes the background look big and close.
  * The person and the background must share one lens: the same horizon, the same vanishing point, the same compression.
* **Camera height equals horizon height.** On flat ground, the horizon sits at the height of the lens.
  * With the phone level at eye height, background people's eyes sit on the horizon at any distance.
  * With the phone at waist height, their waists sit on it.
  * This one rule catches most pasted-in background people.
* **Verticals stay vertical when the phone is level.** Tilting up makes them lean in. Tilting down makes them lean out. Built: `layout` measures the source's vanishing point and ground edge and puts the camera height into the prompt wording.
* **Lens distortion.** Phones correct most of it, but the ultra-wide still stretches the corners (a face near the edge looks wider).
* Planned: a horizon check for background people, and a lens estimate from the face (selfie distortion) compared with the background.

### 5.3 Focus, depth of field and blur

* **Phone physics.** A phone 0.5 to 2 m from the subject has deep focus. The far background is soft, not blurred.
  * At 1080×1920, far background edges spread by only about 2 to 5 px with the main camera, more when the subject is closer.
  * The front camera blurs less, and the ultra-wide almost not at all.
  * Objects nearer than about 30 cm to the lens do blur visibly.
  * These figures come from typical phone lens and sensor sizes. Calibrate them against real sources.
* **Creamy blur, bokeh balls and a crisp cut-out subject** mean portrait or Cinematic mode, a real camera, or AI.
  * Use them only when the source has them.
  * Then copy that mode's flaws too: its depth map goes wrong at hair, glasses and the gaps between arm and body, giving edges that are too sharp or a blurred halo.
* **Focus sits on the face** (phones lock onto faces). When the person moves toward or away from the lens, focus follows with a slight lag and sometimes hunts, with a brief soft moment. In Cinematic mode the focus pull is visible.
* **Blur grows smoothly with distance from the focus plane**, in front of and behind it. It never jumps between layers. The floor blurs as a gradient.
* **AI defaults to avoid:** everything equally soft; cinematic shallow focus in a phone shot; a sharp background behind a soft face.

Track:

* Built: overall sharpness (`measure.py`).
* Planned: a depth map per frame from Video Depth Anything (Apache 2.0; the Small model is fast enough for short clips), and local sharpness plotted against depth, for the source and the output.

Recreate:

* Ask for deep focus in the still ("phone photo, everything in focus"), or for the source's portrait mode.
* Planned `finish --dof`: depth-based lens blur with focus tracking the face, matched to the source's measured blur-against-depth curve. The foreground layer is blurred by its distance.

Reject:

* Background blur outside the phone range when the source isn't in portrait mode.
* Blur that doesn't increase with distance.
* A halo or cut-out edge around the person, unless the source's portrait mode shows the same.

### 5.4 Focal point and visual order

* **What draws the eye, in order:** faces, motion, the brightest area, the highest contrast, the sharpest area, saturated colour, readable text. The persona's face should win.
* **Keep a calmer area directly behind the head.** Clutter belongs in the room (Persona guidelines 6.4), not in a tangle right behind the face. It distracts, and it confuses the model at the hair edge.
* **Nothing in the background should be brighter, more saturated or busier than the face**, unless the source does that on purpose. A window may blow out, but then it reads as plain white.
* **Background motion stays smaller than the person's** (6.3).
* **Measure it.** Planned: compare the face region with the background on brightness, contrast, saturation and motion energy, against the same ratios in the source.

### 5.5 Motion blur

* **Blur length equals speed times exposure time**, and the phone chooses the exposure.
  * Outdoors in daylight: about 1/500 to 1/2000 s. Fast hands stay crisp and motion looks slightly choppy.
  * Indoors: about 1/30 to 1/60 s. Swinging hands and hair blur; a still face stays sharp.
* **Everything moving at the same speed blurs the same amount:** hands, hair, a passing car, the background in a fast pan. Models often blur one and not another.
* **Blur follows the motion path.** Rotating parts blur in arcs.

Track:

* Planned: blur on fast-moving parts against their speed, for the source and the output.

Recreate:

* Planned `finish --shutter`: motion blur from optical flow, added only where the model left moving things too sharp for the light level.
* Note from P015: our face at speed was already blurrier than the source's. Add blur only where it is measured as missing.

Reject:

* Crisp fast hands in a dim room.
* A smeared face while the hands stay sharp.
* Even, film-like blur in bright daylight.

### 5.6 Parallax and camera movement

* **When the camera moves sideways or forward, near things cross the frame faster than far things.** A background that moves as one flat sheet behind the person is a backdrop.
* **Handheld shake is mostly rotation**, which creates almost no parallax. So a 2D stabilise or replay (built: `finish --camera`) is fine for it.
* **A walking camera or a pull-back moves the lens**, which needs real parallax. Keep the model's own camera move, or (planned) apply a depth-based 2.5D shift of the layers.
* Reject: a flat background during a real camera move; the background stretching or warping at the edges; layers sliding at the wrong rates (near slower than far).

### 5.7 Object permanence and what's behind the person

* **The person keeps covering and uncovering the background.** What comes back must be what was there before: the same shelf, the same number of books, the same picture. Video models redraw uncovered areas and often change them.
* **Static objects never change:** furniture, frames, sockets, door handles, the number of items on a shelf.
* Planned tracking: compare the background before it is covered with the same area after it is uncovered (against the clean plate), plus a change score for static regions.
* Planned recreation: the clean plate (5.10) gives us the true background to repair uncovered areas.
* Reject: anything in the background changing, appearing or disappearing without a cause.

### 5.8 People, vehicles and life in the background

* **Real places have life that fits the place and time:** a passer-by on the street, a car, a light in a neighbour's window, a distant bus. At home indoors there is usually nobody (Willow's flatmate is never on camera).
* **Background people:**
  * follow perspective (5.2: eyes on the horizon for a level phone at eye height);
  * walk at 1.2 to 1.5 m/s with their feet on the ground and contact shadows;
  * are out of focus by their distance and motion-blurred by the shutter;
  * are never identifiable (fictional, no readable faces).
* **Cars** move along the road's lines, with turning wheels, sliding reflections and unreadable plates.
* Reject: background people floating, sliding, the wrong size for their distance, passing through objects, or sharp enough to recognise; cars with still wheels or off the road's lines.

### 5.9 The foreground layer

* **Owner rule: keep the foreground as empty or as busy as the source.** Never ask the motion model for foreground items. P015 showed it draws floating figures.
* **When the source has a busy foreground** (a passer-by crossing, a branch at the frame edge, leaves, shadows sweeping over), add it in post as its own layer:
  * generated separately (fictional people only, no recognisable faces);
  * placed by depth: larger and more blurred the nearer it is to the lens;
  * lit by the same light plan (7.1) and moved by the same wind (6.3);
  * crossing at a believable speed. Close to the lens, a walking person crosses a vertical frame in about 0.5 to 1 s.
* **Foreground shadows count.** A passer-by's shadow or leaf dapple crossing the persona must darken them too (7.6).
* Reject: foreground items sharp right at the lens; a foreground lit differently from the scene; foreground items that float or overlap things in the wrong order.

### 5.10 How the background gets made (planned build)

1. **Still** with the persona in the place (built, SKILL step 7.4).
2. **Clean plate.** The same still with the persona removed, using an image edit of the still so the light, perspective and lens stay identical. What was behind them is filled in consistently with the room spec.
3. **Depth map** of the plate, and the depth layers written down.
4. **Performance pass** (built: Seedance 2.5 reference mode with the still as @Image1; fallback Kling Motion Control with `background_source` set to the still). The model draws the background from the still and keeps the contact shadows and light spill around the person. Keep its background wherever it holds steady.
5. **Background check** (planned): boiling in static regions, object permanence, and motion energy against the source.
6. **Region replacement.** Where the model's background boils, freezes or forgets, replace just those regions from the plate or from an ambient clip (6.5). Only use areas that the person and their shadow never cover anywhere in the clip (a person mask across all frames, grown by a margin). Never swap a whole layer.
7. **Foreground layer** (5.9), then the light and lens pass (Parts 7 and 8).

## Part 6: Background Micro-Movement

### 6.1 Why it matters

* A real place is never frozen. Air moves, light flickers, things hum. A perfectly still background behind a moving person reads as a photo backdrop.
* AI backgrounds also fail the opposite way: walls and furniture that breathe, wobble and shimmer.
* The rule from 1.1 applies: things that would move, move the way they really do. Things that can't move never move.

### 6.2 What moves and why

| Element | Cause | How it moves | Moves together with |
| :---- | :---- | :---- | :---- |
| Curtains, blinds | Draught from a window, warm air rising off a radiator | Slow sway of a few cm, irregular; heavy fabric slower | The light through them; anything else in the draught |
| House plants | Draught, someone walking past | Single leaves tremble; stems barely move | Curtains, steam |
| Steam (mug, kettle, pan) | Heat | Rises and curls, faster near the source, fades within 15 to 30 cm, bends with the draught | The draught direction |
| Dust in a sunbeam | Air currents | Slow drifting specks, visible only inside the beam | The sunbeam |
| Candle flame | Air | Flickers, leans in a draught | Its light on nearby surfaces and on the person (7.6) |
| Screens (TV, laptop) | Content | Slow changes, glow on nearby surfaces; generic content only (Persona guidelines 6.10) | Their light on the room |
| Clocks, fans, washing machine | Mechanical | Regular: the one place exact repetition is right | |
| Reflections (windows, mirrors, glossy surfaces) | Camera and people moving | Shift with the camera and the people; a mirror shows the scene correctly reversed | The camera path |
| Tree leaves and branches | Wind | Leaves flutter fast, twigs sway, branches move slowly, trunks never; gusts come in waves | Other trees, grass, hair, clothes, all in one direction; a gust reaches upwind things first |
| Grass, weeds | Wind | Ripples travelling with the wind | Trees |
| Clouds | Wind higher up | Slow drift in one direction; at most a few percent of the frame in 15 s, usually less | Cloud shadows, light dimming (7.6) |
| Dappled leaf shadows | Leaves moving | Shimmer on the ground, walls and the person, in time with the leaves above | The leaves |
| Flags, washing lines, bin bags | Wind | Flap and billow, irregular | Wind |
| Water (puddles, fountains) | Wind, rain, people | Ripples; reflections break up | Rain |
| Birds, insects | Life | Brief and rare | |
| Distant traffic and people | Life | See 5.8 | Perspective |
| Traffic lights, shop signs | Cycles | Tens of seconds per cycle; a change within 15 s is rare | |
| Heat shimmer | Hot surfaces | Only over hot tarmac or roofs on a hot day | |
| Rain, snow | Weather | Falling at the right speed, hitting and wetting surfaces (Persona guidelines 4.5) | The wet look on everything |

### 6.3 Rules

* **Every motion has a cause in the scene sheet.** No wind in the plan, no blowing leaves.
* **One wind.** Its direction and gust timing are shared by everything it touches: hair, clothes, leaves, steam, smoke, flags. A gust reaches things in order along its direction.
* **Amplitude follows stiffness.** Leaves move more than twigs, twigs more than branches, and trunks not at all. Thin curtains move more than heavy ones, light fabric more than heavy fabric.
* **Distance shrinks motion on screen.** The same sway far away covers fewer pixels and moves more slowly across the frame.
* **Irregular, not looping.** Gusts vary in strength and timing. A visible loop, such as the same flutter every 2 s, is a tell. Only machines repeat.
* **Subtle by default.** Background motion supports the person and never competes with them. Stay near the source's background motion energy.
* **Not on the beat.** The background doesn't move with the music.
* **Focus and motion blur apply here too** (5.3, 5.5).
* **Light moves with its cause.** Moving leaves move their shadows. A flickering flame flickers its light. A passing cloud dims the whole scene (Part 7).

### 6.4 AI boiling or real motion

* **AI faults that look like micro-motion but are failures:** wall textures crawling, straight edges wobbling, furniture breathing (scaling in and out), patterns or text shimmering, objects morphing between frames, flickering brightness or colour in static areas, the background melting where the person passes.
* **The test.** Real motion has a cause, a direction and coherence: neighbouring leaves move alike. Boiling is random, small and everywhere, including on things that can't move.
* **Planned tracking:** optical flow on the background after removing the camera path (built: `camera_path`).
  * Static regions such as walls and furniture should show almost no flow. The leftover flow is the boiling score.
  * It is compared with the same score on the source, whose static regions give the real floor (sensor noise and compression).
  * Also planned: motion energy for each planned moving element, and frame-to-frame brightness flicker in static regions.

### 6.5 How micro-motion gets made (planned)

1. **Plan it** in the scene sheet: which 2 to 4 elements move, why, and how much.
2. **If the performance pass already moves them believably, keep it.**
3. **Otherwise make an ambient clip.** Run image-to-video on the clean plate with a locked camera, asking only for the planned motion (for example "only the curtain moves gently in a draught, the camera is locked, nothing else moves"). Candidate models to test: Kling 3.0 video, Veo 3.1, Wan 3.0, Seedance 2.5. Reject any clip where static things move (boiling score).
4. **Composite the ambient clip only inside the planned regions** (curtain, window, plant, sky). Feather the edges, and use only areas the person never passes through (5.10 step 6).
5. **Make simple effects in code.** Steam and dust as particle overlays, light flicker as brightness modulation of the lit area, cloud dimming as a slow exposure change across the frame, leaf dapple as a moving light mask over the person and the wall. Code-made effects are cheap, repeatable and boil-free.

## Part 7: Light

### 7.1 One light plan per shot

* **Write the light plan in the scene sheet before the still:**
  * the key light (sun, window or lamp): position, direction, size and colour temperature;
  * the fill (bounce from walls, sky light);
  * practical lights in frame (lamps, screens, candles);
  * anything that changes during the clip (a cloud, a flicker, the person moving into the sun).
* **Colour temperatures:**
  * daylight about 5500 to 6500 K;
  * overcast and shade bluer, 6500 to 7500 K;
  * warm household bulbs about 2700 K;
  * cool LEDs about 4000 K;
  * screens bluish.
  * Mixed light gives each side of the face a different colour (Persona guidelines 4.2).
* **Everything takes its light from the plan:** face, hair, clothes, floor, walls, props, background people and the foreground layer.
* **Light doesn't change on its own.** The sun moves about 15° an hour, so within a 15 s clip it is fixed. Changes come from causes: clouds, flicker, a door opening, the person moving through the light.

### 7.2 Light on a moving body

* **The light stays put while the body moves through it.**
  * Turning toward the window brightens the face and swaps the shadow side.
  * Stepping back into the room darkens them, because light falls off fast with distance from a window or lamp.
  * Raising an arm drops its shadow across the torso.
  * Bending forward darkens the face.
* **Self-shadowing moves with the pose.** Arms shade the body, hair shades the forehead and neck, the chin shades the neck, the brows shade the eye sockets.
* **Shadow edges.** Hard in direct sun and from small bulbs, soft from windows and overcast sky. A shadow gets softer the farther it falls from the thing casting it.
* **The AI tell:** the person keeps the still's lighting all the way through, like a sticker, whatever they do.

### 7.3 Highlights and skin

* **Shine on skin stays pinned to the light, not to the skin.** As the head turns, the highlights on the forehead, nose, cheekbones and lips slide across the face, while moles, freckles and pores move with the skin. A highlight glued to the same patch of skin through a head turn has been painted on.
* **Shine increases with effort** (sweat after a dance) **and through the day** (Persona guidelines 2.9).
* **Backlight.** Ears, nostril edges and fingers glow warm. A rim of light outlines the hair and shoulders and moves around the edge as the person turns.
* **Bounce.** A bright floor lights under the chin, a coloured wall tints the near cheek, a white T-shirt lights the chin.

### 7.4 Light on clothes in motion

* **Folds shade and catch light as they form and flatten**, so the shading changes with every fold.
* **Material sets the look.** Cotton is matte. Satin and silk carry bright moving highlights. Leather and vinyl carry sharp moving reflections. Knit shows soft texture shadows. Sequins and glitter twinkle as the angle changes.
* **Thin fabric glows when backlit:** light through a sleeve, the outline of an arm in a thin shirt.
* **Wet and sweaty fabric darkens and shines** (Persona guidelines 4.5).

### 7.5 Light in the eyes and hair

* Catchlights: see 3.5.
* The rim light and the colour shift in hair (Persona guidelines 4.4) move as the head moves. The shine band on straight hair slides along the strands as the head tilts.

### 7.6 Shadows on the world, and light events

* **The person casts a shadow** on the floor and walls that matches the light direction and moves in sync with them. There is a contact shadow at the feet and wherever they touch a surface.
* **The body blocks light.** Stepping between a lamp and the wall darkens the wall.
* **Skin and clothes bounce a little light** onto nearby surfaces (a white shirt near a wall).
* **Light events reach everything at once:**
  * a passing cloud dims the person and the street together over a second or two;
  * a flickering candle flickers on the face;
  * a screen's changing glow lights the face;
  * headlights at night sweep across the room;
  * a passer-by's shadow sweeping over the person darkens them too.
* **Mains flicker.** In the UK (50 Hz), some LED and fluorescent lights flicker 100 times a second and can show as slow rolling bands in phone video. Add it only when the source shows it.

### 7.7 Phone exposure and white balance

* **The phone adjusts exposure and white balance automatically, with a lag of roughly 0.3 to 1 s.** Walk toward a window and the image brightens, then corrects. Move into warm lamp light and the colour shifts, then settles.
* **Highlights clip** (a blown-out window), shadows block up, and HDR lifts faces.
* Planned: a `finish` option that follows the scene's measured brightness with that lag, for shots where the light on the person changes. Off by default; on when the source shows it.

### 7.8 Tracking and matching the light

* **Planned `motion.py light` report, per frame:**
  * face brightness;
  * the face's shadow side (left cheek against right cheek, which gives the light direction);
  * face colour against neutral surfaces in the scene;
  * background brightness;
  * whether catchlights are present.
* **It flags:** the light direction on the face flipping; the face not changing when the scene's light changes (or the reverse); the face colour drifting away from the scene's.
* **Matching** (when layers are combined, or a pass shifts the person's colours): match the person's colour and brightness to the scene around them in code, near the edge of the person mask.
* **Relighting models:** UniRelight, Lumen, Relit-LiVE and GR3EN (all 2026 research) need large GPUs and aren't on kie, so they are a watch list only.
* **The surest light is the still.** Render the still with the light plan right: direction, hardness, colours, shadows on the floor. Pick drivers whose movement through the light fits that plan, for example no walking from shade into sun if the still is in shade.

Reject:

* The person lit like a sticker, unchanged as they turn or move.
* Highlights glued to the skin.
* Shadow direction disagreeing between the person and the room.
* No cast or contact shadow, or shadows that don't move with the person.
* Face colour not matching the room's light.
* A light event that changes the room but not the person, or the reverse.
* Catchlights that don't match the windows and lamps.

## Part 8: The Camera (phone capture)

### 8.1 Handheld or propped

* **A handheld phone has leftover shake after stabilisation:** small, irregular, mostly rotation, with slow drift and occasional corrections. Breathing adds a slow sway. Walking adds a bob at the step rate.
* **A phone propped on a shelf is completely still**, so any camera motion there is wrong.
* Built: `camera_path` tracks the background, and `finish --camera` either locks the camera or replays the driver's real path.
* Owner feedback (P015): the camera should not move so much. Kling sometimes invents pans and pull-backs, so measure every take.
* Reject: a camera smoother than a hand (gimbal glide) when the source is handheld; invented pans or pull-backs; shake that is regular or wave-like.

### 8.2 Sensor and processing

* **Rolling shutter.** Fast pans lean vertical lines, and walking can add a jelly wobble. It only shows in fast camera moves; don't add it otherwise.
* **Noise.** Stronger in dark areas and dim scenes, with colour speckle in the shadows, weaker in bright areas. It changes with exposure.
  * Built: `finish --grain` (even grain).
  * Planned: noise by brightness, matched to the source's noise at each brightness level.
* **Sharpening and HDR.** Phone video has edge sharpening (slight halos) and local tone mapping. Skin is not smoothed.
* **Compression.** TikTok re-encodes, so fine texture (hair, foliage, noise) gets blocky in motion. Don't over-sharpen before upload.
* **Frame rate.** 30 fps (sometimes 60). Output is 30 fps (built).
* **Slow motion.** Phone slow motion (120 or 240 fps) has short exposures (crisp motion) and more noise indoors. A slowed 30 fps clip shows blur and stutter. Match the source's type. There is no frame-interpolation model on kie, so slow motion is done locally.
* **Lens.** Flare and ghost reflections from bright lights move opposite to the light as the camera moves. A smudged lens adds haze around lights.
* **Autofocus:** see 5.3.

### 8.3 Who is holding the phone

* **Selfie video** (front camera, arm's length): the camera moves with the arm, the face stays central, the background swings as the person turns, and the eyes rest on the screen (Persona guidelines 3.1).
* **Propped phone:** completely still, framing slightly off, the person drifts in and out of the best spot.
* **A friend filming:** rear camera, moves to follow, reframes a beat late. The friend never appears or speaks, and never goes in the prompt (P015 rule).

## Part 9: Consistency Over Time

* **Identity holds in every frame**, including turns, blinks, laughs and fast moves.
  * Built: face proportions (`faces`).
  * Planned: identity scored against the persona's refs, using a face-similarity model whose licence allows commercial use. Many popular face-recognition models are research-only.
* **Locked traits stay locked:** moles, teeth, eye colour, hair parting, jewellery, nail polish, outfit details (Persona guidelines 1.1).
* **Counts don't change:** fingers, buttons, earrings, items on a shelf.
* **No texture boiling** on skin, hair, clothes or the background (6.4).
* **No flicker.** Brightness and colour stay steady unless the light plan changes.
* **Real speed.** A model that slows the motion (floaty) or rushes parts of it shows up in timing against the driver (built: lag in `check`).
* **Cuts.** In a fast-cut edit the world stays the same between shots (same light, same state of the clothes, same clutter) unless time passes. Each shot's camera and light follow the same plan.
* **Loops.** A clip meant to loop has no visible seam: pose, hair and background all match at the loop point.
* **Long clips drift more.** Split long sources into segments that share the same still and join them at matching poses. Built: `splice` for takes of the same driver. Planned: joining across segments.

## Part 10: Shot Types (owner's coverage list)

| Shot type | Channels that matter most | Method | Known limits |
| :---- | :---- | :---- | :---- |
| Full-body dance, trend moves | Body, weight, foot contacts, hair, clothes, camera | Seedance 2.5 reference mode from the source (Kling Motion Control as the fallback); still at the driver's framing; `finish --camera` | Face coarse at about 150 px; spins and hair flips smear for 0.2 to 0.3 s (P015) |
| Talking or lip-sync close-up | Face, eyes, mouth, head, breathing, light on the face | Chest-up driver (face over about 400 px); performance pass, then a face pass if needed (to test); sound offset | Untested; teeth need refs |
| Walking, travelling | Gait, contacts, parallax, camera bob, background life | Keep the model's camera; check parallax; background people by perspective | Kling pans to follow (P015 run-02); locking the camera costs a big zoom |
| Props and products | Hands, grip, rigid product, label | Prop in hand in the still; drivers with large hands in frame; label in code | Hand-offs fail |
| Slow motion | Timing of hair and clothes, motion blur, noise | Match the source's type (high frame rate or slowed); interpolate locally | No interpolation model on kie |
| Fast-cut edits | Consistency across shots, cut timing | One still per shot, shared refs and light plan; cut on the source's beats | Every cut is a new generation, so things drift |
| Busy foreground (people walking by, trees, clouds, shadows, wind) | Foreground layer, wind coupling, light events | Layers added in post (5.9, 6.5) | Planned |

## Part 11: Choosing and Preparing Drivers

* **The driver sets the ceiling on motion quality.** Choose:
  * one continuous shot with one person, head to waist or wider (built rules in `scan`);
  * hands visible when hands matter;
  * a face big enough for the shot type (Part 10);
  * few fast head turns and hair flips when face realism matters;
  * a still or gently handheld camera;
  * movement through light that fits our still.
* **Performance casting.** The driver's person brings their own mannerisms: expression style, tempo, gaze habits. Prefer drivers whose style fits the persona's repertoire. Willow is dry, deadpan and low-key, so an exuberant performer would give her someone else's personality.
* **A similar build** where contact matters (3.8).
* **Persona motion clips** (Persona guidelines 3.5). A team member filmed acting out the persona's moves, with written consent, is the cleanest driver for talking and everyday shots: our timing, framing and light, mannerisms that fit the persona, and no credit needed. Film on a phone in good light, against a plain background, at the target framing, 3 to 30 s.
* **Prepare the driver:** trim to after any pull-back (P015), keep the source's speed, note the beats and the sound offset, and measure the layout (built).
* **Credit:** `dc @creator` (built, `driver.json`).

## Part 12: Measurement

Measure every channel on the driver (or source) and on the output with the same code. Compare against the source wherever possible. Calibrate on real footage first, the same way the limb angles were calibrated: the driver against itself, shifted in time, mirrored, and against another person.

| Channel | Measure | Tool | Status | Provisional pass / fail |
| :---- | :---- | :---- | :---- | :---- |
| Body pose | Limb angle error per body part, timing lag | `check` | Built | ≤20° / >35° |
| Body in 3D | Angle error from world coordinates | `check` | Planned | Calibrate |
| Placement | Nose height, body centre, torso size | `layout`, `check` | Built | Reported; no threshold yet |
| Foot contact | Slide while planted, as % of body height | `check` | Planned | ≤2% / >5% |
| Self and prop contact | Share of the driver's contacts kept | `check` | Planned | ≥80% kept |
| Jumps | Time in the air against height | `check` | Planned | Within 25% of real gravity |
| Hands | Finger curl error, hand visibility | `check` | Planned | Calibrate |
| Head | Turn, nod and tilt error | `check` | Planned | ≤10° / >20° |
| Expression | Correlation of expression scores (jaw open, smiles, brows, squints) | `check` | Planned | r ≥ 0.6 / r < 0.3 |
| Face shape | Frames with proportion outliers | `faces` | Built | Aim ≤5% (P015 round 3 reached 7.5%) |
| Identity | Similarity to the persona's refs | new | Planned | Calibrate |
| Blinks | Rate, gap regularity, longest gap | `check` | Planned | Rate within ±40% of the driver; no gap over 6 s while talking |
| Gaze | Direction error, share on the lens, jumps, both eyes agreeing | `check` | Planned | Share on the lens within 15 points of the driver |
| Mouth | Opening correlation, closures kept, sound offset | `check` | Planned | Offset within ±40 ms; ≥80% of closures kept |
| Stillness | Small body motion in the still stretches | `check` | Planned | Above zero and near the driver |
| Camera | Path, pan and zoom per take | `camera_path`, `finish` | Built | Owner: minimal movement |
| Boiling | Flow in static regions after removing the camera path | `stability` | Planned | ≤1.5× the source |
| Flicker | Brightness change in static regions | `stability` | Planned | ≤1.5× the source |
| Micro-motion | Motion energy per planned region | `stability` | Planned | 0.5 to 2× the source |
| Permanence | Background change after being uncovered | `stability` | Planned | Calibrate |
| Depth and blur | Sharpness against depth; background blur in px | `depth` | Planned | Phone range, or the source ±1.5 px |
| Focal point | Face against background: brightness, contrast, saturation, motion | `stability` | Planned | Same order as the source |
| Light | Light direction on the face, brightness moving with the scene, colour against the scene | `light` | Planned | No direction flips; calibrate the rest |
| Look | Sharpness, noise, saturation, brightness | `measure.py` | Built | Grade gap gives the finish settings |
| Source frames | Near-duplicate frames of the source | `check` | Built | 0 |
| Extra people | People count | `check` and eyes | Built | 0 (look too: the score misses blurry figures) |

Calibration plan:

1. Pick 6 to 10 real phone clips covering the Part 10 shot types (sources already in `content-bank/`, plus persona motion clips once filmed).
2. Run every measure on the real footage. This sets the real floor for noise, boiling, blink rates and the rest.
3. Run the same measures on past outputs where the owner's verdict is known (P015 run-01 rounds and run-02 takes).
4. Set each threshold between real footage and rejected output.
5. Update this table and SKILL step 7.

Numbers show where to look; eyes decide. Always look at a frame tile every 0.5 s (edges included), the face sheet, and the clip at full speed and at quarter speed.

## Part 13: Video Realism Review (reject list)

This extends Persona guidelines 10.2. Any hit means a re-take, a splice, a fix pass or a reject.

How to watch:

* Full speed with the sound.
* Quarter speed for faces, hands and frame edges.
* The background alone: cover the person and watch for boiling and missing micro-motion.
* The first and last second, where models drift.
* Side by side with the source (built: `_compare.jpg`).

Body and face:

* Feet sliding; floaty jumps; a body balancing on nothing; limbs passing through things.
* Wrong finger count, melting hands, an impossible grip.
* A rigid neck, a head frozen while talking, identity changing on a turn.
* A smile without the eyes, symmetrical or switching expressions, skin not creasing, moles sliding.
* No blinks, regular blinks, gliding eyes, eyes not aimed at the same point, catchlights glued to the iris.
* Lips without the jaw, no closures on p, b and m, out of sync, teeth changing.
* A frozen mannequin body in the still stretches.

Secondary motion:

* Hair frozen, floating, changing length, or moving with no cause.
* Clothes moving as a shell, prints sliding, details changing.
* Jewellery changing or still; props changing shape or floating.

Background and depth:

* Static things wobbling, breathing or morphing (boiling).
* A frozen backdrop where the scene should be alive.
* Background objects changing after being covered.
* Motion that loops, motion with no cause, wind going different ways.
* Blur wrong for a phone, or not growing with distance.
* No parallax during a real camera move.
* Background people at the wrong scale, floating, or recognisable.
* Floating figures or objects in the foreground.
* Something behind the head pulling the eye from the face.

Light:

* The person lit like a sticker; highlights glued to the skin.
* Shadow directions disagreeing; missing cast or contact shadows.
* Light events that reach the room but not the person.
* Face colour not matching the room.

Camera and time:

* Gimbal-smooth or invented camera moves.
* Uniform grain on a dim scene; over-sharpened.
* Flicker; slowed or rushed motion; drift across cuts; a seam at the loop point.

## Part 14: Tool and Model Roadmap

Ordered by value for effort. Phases 1 to 3 run locally with no new paid calls. Phase 4 is paid testing.

**Phase 1: the tracker (`motion.py scan` and `check`).**

* Add the Face Landmarker (478 points, 52 expression scores, iris, head pose) and the Hand Landmarker (21 points per hand), on both driver and output. Both run in our pinned MediaPipe 0.10.35, and the face model is already used by `faces`.
* Add the pose model's world coordinates.
* Write a per-channel report: blinks, gaze, mouth, head, hands, contacts, foot slide, jumps, stillness.
* Calibrate on real footage and the P015 takes (Part 12).

**Phase 2: scene checks.**

* `motion.py stability`: optical flow with OpenCV (already installed, no new dependency) for boiling, flicker, micro-motion per region, object permanence and focal point.
* `motion.py light`: light direction, brightness moving with the scene, colour against the scene, catchlights.
* `motion.py depth`: Video Depth Anything Small (Apache 2.0; adds PyTorch as a dependency), with the blur-against-depth curve.

**Phase 3: finish passes.**

* `finish --dof`: depth-based lens blur, with focus tracking the face.
* `finish --shutter`: motion blur only where it is missing.
* Noise by brightness, and the exposure and white-balance lag.
* Region replacement from the plate or an ambient clip, and the layered foreground composite.
* Code-made steam, dust, flicker, cloud dimming and leaf dapple.
* Better person mattes for compositing: the current MediaPipe mask is coarse at the hair. SAM 2 (Apache 2.0) is the candidate.

**Phase 4: generation tests (paid; one driver per test, costs logged by `kie.py`).**

* Clean plate (image edit) and ambient clips (image-to-video with a locked camera).
* Performance pass A/B, done 2026-10-05 on a 10 s P015 driver: Kling 3.0 Motion Control, Seedance 2.5, Wan 3.0, MiniMax H3 and Gemini Omni 1.1 (log: `content-bank/_model-tests/runs/2026-10-05_top-models/`). **Owner decision: Seedance 2.5 is the most accurate, so it is the main model** (SKILL step 7.5). It takes our still as a reference image (@Image1) plus the driver as a reference video (@Video1); a first frame can't be combined with a reference video. Billing covers reference plus output seconds (1900 credits for 10 s + 10 s at 1080p). Still to try: the track as reference audio (motion and lip-sync in one call), and Wan Animate 2 and Kling 4.0 once they are on kie. Run the source-frame duplicate check on every take, since the source video goes into the model.
* Face pass on a chest-up talking driver: Volcengine video-to-video lip-sync, InfiniteTalk, OmniHuman 1.5, Kling AI Avatar.
* Local fix pass: Seedance 2.5 local editing, Gemini Omni 1.1 Flash, Wan 2.7 Video Edit.

**Phase 5: the persona motion library.** Team-filmed persona motion clips (with consent), indexed by action: walk, sit down, talk, laugh, pick up a mug, mirror selfie.

**Licences.** Check every open-source model's licence for commercial use before building on it. Several face-recognition and matting models are non-commercial or GPL.

## Part 15: Guardrails

* **Motion only, never a likeness.** The persona copies how a real person moves, never their face, body or voice. `preflight` only accepts characters from `personas/` or a run folder (built).
* **Facial performance transfer copies expressions, not identity.** The face in the output is always the persona's (identity check).
* **No reposting the source.** New person, new place, no source frames (duplicates = 0). No Wan "replace" mode, which keeps the source video and only swaps the person.
* **Credit the moves:** `dc @creator`.
* **Background and foreground people are fictional and unrecognisable.** No real addresses, number plates or brand logos unless a brand is paying (Persona guidelines 6.10).
* **Team-filmed drivers need written consent**, and only their motion is used.
* **Adults only.** No sexualised motion; no body before-and-afters (persona rules).
* **The AI-generated content label is always on.**
