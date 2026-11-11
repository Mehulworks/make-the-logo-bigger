# Prompts

Two prompts. The first is the finished film as a single brief: start with that one. The second
is where it started: the brief the first draft was built from.

The finished-film prompt did not exist while the film was being made. The film got here
through a long back-and-forth, and [DIRECTION.md](DIRECTION.md) explains each decision. This
prompt condenses all of those decisions into one brief, so you can see the whole specification
in one place or start your own version from it.

It has not been tested as a one-shot prompt. Expect a first draft that needs the same kind of
watching and correcting that the direction log describes.

## 1. The finished film in one prompt

Everything in the published version, as a single brief. Replace `[your name]` before using it.

```text
Build a 110-second animated short called "Make the logo bigger" about how a designer's job
changed from 1990 to today. Landscape 1920x1080, 30 fps, original music and sound, captions
burned in. It will be posted as a video and also published as a page people can play.

DELIVERABLES
1. index.html: ONE self-contained page (inline CSS and JS) that is the whole film.
2. A soundtrack synthesised in code (Python with numpy/scipy is fine). No samples, no
   recordings, no licensed music.
3. A render script that turns the page into an MP4, and a .srt subtitle file.

ARCHITECTURE
- One function, window.__seek(t), puts the whole page into its state at time t. Every CSS
  animation is paused and pinned to t through document.getAnimations() (currentTime = t*1000).
  Nothing plays in real time, so the same t always gives the same frame.
- Each era is its own <section> with a start time and its own theme tokens. Keep the scene
  data separate from the playback engine, so the scenes can be reused in an interactive
  scrubber later.
- Render mode (?film=1): no player chrome, no sound. A headless browser steps frame by frame,
  screenshots, and pipes JPEGs into ffmpeg, one encoded file per scene, then the files are
  joined and the soundtrack is added. Force the sRGB colour profile when rendering.
- Player mode: the film waits on its end card behind a "Play the film with sound" button
  (browsers block sound until a click). Once playing, the soundtrack is the master clock: if
  the picture drifts more than 80 ms from the audio, re-base it onto the audio. Controls:
  play/pause, restart, timeline scrub, mute, jump to era, hide controls. Centre and scale the
  1920x1080 stage to fit any window, including a phone.
- Captions, spoken lines and sound cues all live in the page as data with timings, so the
  subtitle file and the soundtrack are generated from the same source as the picture.

LAYOUT (every era)
- Left column: the year, the client's request, the second voice, the job line, fact chips.
- Right: the action, about 960x720.
- One subtitle bar at the bottom of the frame, white on near-black, the same in every era.

STRUCTURE AND TIMING
0:00  Hook (4 s)
0:04  1990 · Pixels arrive (10 s)
0:14  1998 · The wild web (14 s)
0:28  2009 · Pocket screens (14 s)
0:42  2014 · Flat and systematic (14 s)
0:56  2019 · Multiplayer (14 s)
1:10  Today · 2023–now, ending on the punchline (24 s)
1:34  End card (16 s)

Each era from 1998 on has two beats. First the client's request and the joke in it. Then
someone who cannot use the result speaks up, and the designer fixes it on screen. A job line
is added at the end of each era, so the job visibly grows. The client is never named: on
screen it is only ever "The client".

HOOK
Black screen, the year 1990. A message from "The client" types out: "Can you make the logo
bigger?" Caption: "It started with one request."

1990
Look: 1-bit pixels, grey bevelled window, floppy disks.
Request (fax): CAN YOU MAKE THE LOGO BIGGER?
Action: the logo is dragged bigger; a dialog says "Resizing… 4 minutes remaining."
Caption: "Saved across 3 floppy disks. Disk 2 is missing."
Job: "The job: make it look right."
Chip: 1990 · Photoshop 1.0 ships (Windows follows in 1993)

1998
Look: tiled starry background, scrolling marquee, under-construction bar, visitor counter.
Request (email): "Subj: FW: RE: can we add an intro??"
Action: LOADING INTRO… 3%. A "Skip intro" button dodges the cursor.
Caption A: "The intro was longer than the website."
Second voice (email from a visitor using a screen reader): "What does this page say?"
Fix: a screen-reader strip reads "image. image. image. spacer dot gif." The designer adds
alt text; it now reads "Welcome to our homepage."
Caption B: "Read aloud, the homepage said: “image, image, image.”"
Job: "+ Make it work without seeing it."
Chips: 1997 · Dreamweaver 1.0 ships / 1999 · WCAG 1.0 becomes a W3C Recommendation

2009
Look: leather, linen, stitching, glossy buttons.
Request (glossy text message): "Does it work on my phone?"
Action: the desktop page shrinks onto a phone; text size reads 4 px; a thumb taps three
links at once.
Caption A: "It fit on the phone. You needed tweezers to tap it."
Second voice (someone on a bus, one hand free): "I can't hit the button."
Fix: the layout reflows to one column, text goes to 16 px, the button grows to thumb size,
the screen reader says "Contact. Button."
Caption B: "One hand. Moving bus. Tiny button. Design for that."
Job: "+ Make it fit every screen and every thumb."
Chips: 2009 · VoiceOver screen reader ships on the iPhone 3GS / 2010 · “Responsive web
design” coined

2014
Look: flat colour, tile grid, paper-like cards.
Request (flat chat message): "Can it look the same everywhere?"
Action: the logo becomes a component; a counter ticks to "128 screens updated"; a design
system committee stamps it APPROVED, next meeting Q3.
Caption A: "Approved by the design system committee. Next meeting: Q3."
Second voice (someone with low vision, and anyone outdoors): "I can't read the grey text."
Fix: a contrast check on thin light-grey text reads 1.6 : 1 ✗ FAIL. One colour token
changes from #CCCCCC to #595959 and every screen updates: 7 : 1 ✓ PASS AA.
Caption B: "Thin grey text on white. Elegant. Unreadable."
Job: "+ Make it a system. Make it readable."
Chips: 2013 · Atomic Design · 2014 · Material Design / WCAG AA · text contrast of at least 4.5:1

2019
Look: clean product-design canvas, coloured cursors, comment pins.
Request (comment pin): "Can I get edit access?"
Action: fourteen named cursors swarm in (PM, Eng, Legal, CEO…); the client retypes the
headline to "MAKE IT POP!!"; reactions pop up.
Caption A: "The client is in the file now."
Second voice (people invited to test it): sticky notes: "I use a screen reader." "I'm
colour-blind." "I read right to left." "Dark mode, please. It's 2 a.m."
Fix: the artboard switches to dark mode, mirrors to right-to-left (use placeholder bars,
not real words), then gains labels and status shapes, not just colours. Each note gets a ✓.
Caption B: "Then we invited the people we were designing for."
Job: "+ Make it with the people it's for."
Chips: 2016 · Figma’s first public release / 2018 · WCAG 2.1 is published

TODAY · 2023–now (label it this way; never a single year)
Look: translucent frosted glass, soft coloured light.
Request (typed into an AI prompt bar): "Can't AI just do this?"
Action: 48 logo versions appear in 0.8 s; one balloons to fill the panel.
Caption A: "AI made 48 versions in 0.8 seconds."
Second voice (an automated accessibility check): it scans the grid: "Low contrast: 40 ·
Alt text says “image”: 26 · Pass: 2". These numbers are invented for the story.
Fix: the designer picks one of the two that pass and nudges it 2 px.
Caption B: "Two worked for everyone. The designer knew which two."
Job: "+ Make the call."
Chips: 2025 · prompt-to-app tools and “vibe coding” / 2025 · the European Accessibility
Act starts to apply

THE PUNCHLINE (inside the Today section, no separate year)
Everything passes; "Ready to ship ✓" appears. The client types: "Love it. Can you make the
logo bigger?" The designer's cursor hesitates and sighs. The laptop lid closes halfway,
pauses and opens again (a generic, unbranded laptop; no person shown). Then the cursor
slowly drags the logo bigger, and the drag keeps going until the logo fills the frame. Its
colour becomes the end card's background, so there is no cut.
Caption: "Some requests never change."

END CARD
Title "Make the logo bigger", the six logo styles from 1990 to Today, and the six job lines.
A statistic counts up to 95.9%: "of the top million home pages still have detectable
accessibility failures. WebAIM Million, 2026."
Captions: "The requests kept changing. The job kept growing." / "The job isn't finished." /
"Captions were made for deaf and hard-of-hearing viewers. You just read a whole video of them."
Sign-off, small, bottom right, last 3 seconds only: "Directed by [your name]".

CURSOR REACTIONS (the designer is the cursor; no drawn characters)
1990 tapping foot during the progress bar · 1998 sweat drop chasing "Skip intro" ·
2009 squint at the thumb · 2014 bounce and sparkle when the contrast passes ·
2019 shrinks back when the swarm arrives · Today bounce when two pass · ending sigh.
Keep each under a second, small, never flashing.

TRANSITIONS
Each era enters in its own period's way: a CRT switch-on (1990), a slow image load (1998),
a slide (2009), a circular reveal (2014), a zoom (2019), a blur-in (Today).

SOUND
One original theme in C major at 120 BPM, re-orchestrated per era: chiptune (1990), synth
band (1998), pumping pop (2009), clean plucks (2014), marimba groove (2019), ambient pads
(Today), everything together on the end card. The lead melody rests while the second voice
speaks. About 110 synthesised sound cues timed to the picture: fax, modem, a screen reader
made of tones, stamp, sticky notes, sigh, a riser as the logo grows. When the lid closes,
muffle the music. Master to -16 LUFS with no clipping. The film must still work fully muted.

RULES
- No real logos, screenshots, app icons, wallpapers or copied operating-system UI. Evoke
  each era with original shapes. Real product names appear only as plain text in the chips.
- The client's logo is one original abstract shape, restyled in every era.
- Open-licensed fonts only.
- Captions: at least 2 seconds on screen; give every section enough time to be read.
- Pass and fail are shown with ✓ and ✗ as well as colour, never colour alone.
- Nothing flashes more than three times a second.
- The joke is always on the design or the tool, never on the person. Describe people by
  their situation ("on a bus, one hand free"), not as a category. Every inclusion beat ends
  with a visible fix.
- Keep the fact chips exactly as written. If you think one is wrong, tell me instead of
  changing it.

HOW TO WORK WITH ME
1. Restate the plan in 10 bullets or fewer and list your assumptions before coding.
2. Build the hook and one era first, show me frames, then build the rest.
3. Before a full render, screenshot the busiest moment of every scene and look at it.
4. Test before saying anything works, and tell me what you could not check, such as how the
   music actually sounds.
```

## 2. Where it started

This brief produced the first draft: a 48-second film in which the client asked for the same
thing in every era. [DIRECTION.md](DIRECTION.md) explains what changed and why.

```text
Build a ~45-second animation called "Make the logo bigger: 1990 to today" as ONE
self-contained HTML file (inline CSS and JS). I will screen-record it.

TECHNICAL
- Fixed stage of 1080x1920 (vertical) by default; ?ratio=16x9 switches to 1920x1080
  and the same scenes reflow.
- In vertical, keep all text inside the middle 1080x1350 band, clear of the top and
  bottom 15%.
- Deterministic timeline: identical on every play.
- Controls: play/pause, restart, jump to era, hide controls for recording.
- Build each era as its own scene with its own theme tokens. Keep scene data separate
  from the playback engine: I will reuse these scenes later for an interactive scrubber.
- Captions are burned in, at least 48px tall at 1080 wide, max ~10 words, on screen at
  least 2 seconds.
- No real logos, trademarks, copied OS or app UI. Evoke each era with original shapes.
  Real product names appear only as plain text in the fact chips.
- Open-licensed fonts only.

STRUCTURE
One client sends the same request in every era: "Can you make the logo bigger?"
Three things evolve together: how the request arrives, the visual style of the whole
frame, and the client's logo, which restyles itself each era.

1990  1-bit pixels, grey bevelled window, floppy disks. Request arrives by fax.
1998  Tiled background, under-construction bar. Request arrives by forwarded email.
2009  Leather, linen, stitching. Request arrives as a glossy text message.
2014  Flat colour, paper cards. Request arrives as a flat chat message.
2019  Clean canvas, coloured cursors. Request arrives as a comment pin.
Today Translucent glass. The client types into an AI prompt bar.

Each era ends on one punchline caption plus a small fact chip tying it to a real,
sourced milestone.

TONE
Witty and relatable. Every joke is a real pain point of its era. The ending is warm,
not anti-AI: tools got faster, and the designer's value moved toward judgement.

HOW TO WORK WITH ME
1. Before coding, restate the plan in 10 bullets or fewer and list your assumptions.
2. Build the hook and era 1 first and show me, before you build the rest.
3. Test before saying it works. Tell me what you tested and what you couldn't.
```
