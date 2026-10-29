# B-Flex film: revision log, v3 → v4

**v3:** 62.2 s, dark, no voice.
**v4:** 116.3 s, white, narrated.

## 1. Order of work (as the brief specified)

| Stage | Output | Where |
|---|---|---|
| 1. Script | 18 lines, 212 printed words / 222 spoken. One worked example (wrong output → entry conflict), then acceleration, then two clearly separated results | `narration/script.py`, `docs/V4_SCRIPT.md` |
| 2. Voice | 16-voice casting by ASR intelligibility, pace and pitch range, then line-by-line synthesis | `docs/VOICE_CASTING.md`, `narration/lines/*.wav` |
| 3. Alignment | Word timestamps from an independent ASR model (token times), matched to the script | `narration/align.py`, `narration/words.json` |
| 4. Retime | The animation follows the voice. Each narration clip is anchored by one word to the animation event it names. The picture clock is remapped around the anchors (holds, moderate moves, slope-1 action). Speech is never stretched | `src/edl.py`, `docs/TIMING_SHEET_V4.md` |
| 5. Music / SFX | Procedural score and effects re-cued to the new clock, ducked under the voice, mastered | `src/audio4.py` |
| 6. Render | 4K60 master, 1080p60, stems, SRT | `out/final_v4/` |

## 2. Visual identity (white redesign, not an inversion)

| v3 | v4 |
|---|---|
| Radial dark gradient background (#0D131C → #05070A) | Solid white `#FFFFFF` (`PAPER`) |
| Ink #E9EDF3, graphite #5B6B80, dim #2A3442 | Text `#17212B`, secondary `#607080`, inactive `#D9E0E5` |
| Teal #4FE3C1, coral #FF5D5D, amber #FFC163 | Teal `#087F8C` (valid), vermilion `#C83F45` (pruned/failure), amber `#B7791F` (rising clock edge / headline) |
| — | **Blue `#2764C5` = the reference.** "expected Q" in Act I, its dashed line, and "reference: Q = 1" and its ring in Act II share one colour, so the viewer links them |
| Bloom, film grain, vignette, filmic tone curve | Removed: clean output (`engine.Post.process_rgb` is an identity) |
| Glowing dots at every highlight | A faint flat tint at about 13% opacity, no glow |
| Dot grid behind Act I | Removed (no grids) |
| — | **Selective soft shadows**, on the δ table panel and the search-tree PiP only: the two "documents" that float above the scene |
| Additive unit-chart compositing (light on dark) | Alpha-over teal on white. Settled cells are mid teal, the growing front full teal |
| Two-line caption band at the bottom | Removed. The sentences are spoken and in the SRT. Facts that lived only in captions moved into the scene (see `ACCURACY_CHECKLIST_V4.md` §C). Step markers sit under the act label |
| Source tags bottom-right | Moved to top-right, so they never collide with player subtitles |
| x264 `-tune grain` | `-tune animation` (flat colour, thin lines) |

## 3. Readability audit (time-coded)

**Method.** `src/audit.py` instruments every text draw call. It steps the film clock at 20 fps and measures, for every distinct string, the longest continuous time it is drawn at ≥ 50% opacity. It ran on v3 and on v4. The full table is in `docs/readability_audit_table.md`; raw data is in `docs/audit_v3.json` and `docs/audit_v4.json`.

**Totals.**

- v3 had **109 labels** on screen for less than 2.5 s.
- In v4: **62 fixed** (now ≥ 2.5 s), **38 removed** (carried by narration or the step marker; see the checklist §D), and **9** remain under 2.5 s.
- All 9 are FF1's live state readout during its fast steps ("(D, CK) = …", "s0 s1 s2 = …", "Q = ¬s2 = 0"). They change with each step by design, like a counter, and the result they lead to ("Q = ¬s2 = 1") holds for 2.5 s.

**Key items.** Complex reasoning had a 4–7 s budget; the others 2.5–4 s.

| Label | v3 at | v3 readable | v4 at | v4 readable |
|---|---|---|---|---|
| **`SeGen-20 output: Q = 0`** (the brief's example) | 0:16.75 | **0.55 s** | 0:37.25 | **3.85 s** |
| `reference: Q = 1` | 0:16.45 | 0.85 s | 0:36.95 | 4.15 s |
| `expected Q` (Act I) | 0:05.30 | 1.75 s | 0:12.90 | 3.35 s |
| Title tagline "Validate every input order. Prune while you generate." | 0:11.15 | 0.80 s | 0:25.60 | 2.65 s |
| `Q = 0 → states with ¬s1 = 0 : 01, 11` | 0:19.20 | 0.80 s | 0:43.45 | 3.30 s |
| `Q = 1 → states with ¬s1 = 1 : 00, 10` | 0:19.35 | 0.65 s | 0:43.75 | 3.00 s |
| `stable: δ(01, 11) = 11` (step 1) | 0:20.95 | 0.80 s | 0:47.75 | 2.55 s |
| `wrong output → branch pruned` | 0:24.05 | 0.95 s | 0:54.05 | 3.80 s |
| `no reference edge` | 0:24.10 | 1.00 s | 0:54.20 | 3.60 s |
| `infer δ(11,01) = 11` | 0:32.00 | 1.85 s | 1:03.55 | 3.25 s |
| `path needs δ(11,11) = 10` (reasoning) | 0:32.70 | 1.30 s | 1:04.30 | 5.05 s |
| `earlier edge fixed δ(11,11) = 11` (reasoning) | 0:33.15 | 0.85 s | 1:05.20 | 4.15 s |
| `branch pruned` (step 5) | 0:33.75 | 0.85 s | 1:06.75 | 2.60 s |
| `vs. 18 at 2-bit state` | 0:43.20 | 1.55 s | 1:21.05 | 3.00 s |
| `exhaustive search · 786 s · 16 threads` | 0:43.60 | 1.15 s | 1:21.20 | 2.85 s |
| `valid FSMs with C_FF ≤ 20` | 0:45.80 | 1.15 s | 1:25.70 | 2.55 s |
| `20 synthesized to transistor level` | 0:47.35 | 0.60 s | 1:28.45 | 2.80 s |
| `2.53×` / `lower sequencing overhead than TGFF` | 0:55.60 | 1.50 s | 1:42.35 | 4.00 s |

**How the fixes were made.** In order of preference:

1. **A hold on the frame where the label is fully visible.** For example, `SeGen-20 output` used to fade in during a 0.65 s window that was then held. The hold now starts *after* the fade-in (segments 16.40 → 16.90 → 17.00 in `edl.py`).
2. **Extending a label's own window** into the following hold or camera move. Examples: the rejection labels now stay through the post-rejection hold; the conflict chips stay until the tree takes over.
3. **Folding** a too-brief tag into a longer-lived marker (steps 3–4), or removing it where the narration says the same thing.

## 4. Story and wording

- **One fully understandable example, then acceleration.**
  - L09–L11 walk one branch from the start pair through wrong-output pruning to an entry conflict.
  - Steps 1 and 3–4 are shown with markers only.
  - The rest of the 2-bit tree grows fast, then the 3-bit fill accelerates.
- **Two achievements, separated in words, colour and position.**
  - Scale: "568 million valid **behaviors**" (teal, behavior stage of the breadcrumb).
  - Circuit performance: "**One of them**, FF1 … **its** sequencing overhead is 2.53 times lower …" (amber, circuit stage), followed by "at a higher energy cost" and the full 18-FF scatter.
- **Wording chosen for accuracy.**
  - "2.53 times lower sequencing overhead", never "faster".
  - "about thirteen minutes" for 786 s.
  - "twenty thousand times" for 2.07 × 10⁴, with the exact figure on screen.

## 5. Sound

| Item | v4 |
|---|---|
| Narration | Kokoro-82M `af_heart`, 24 kHz → 48 kHz, high-pass 70 Hz, placed per clip (no stretching) |
| Music | Procedural pads re-cued from `film.CUES` (now on the v4 clock). Bed at about −26 LUFS before ducking |
| SFX | Procedural ticks, bells and whooshes on the same cues, at about −25 LUFS before ducking. Thinned under the voice |
| Ducking | A speech mask from word timings (150 ms pre-roll, 450 ms release, 120 ms smoothing). Music is ducked −9 dB and SFX −5 dB under speech |
| Loudness | Dialogue peak control first: a true-peak limiter on the voice alone (ceiling −4 then −3 dBTP, re-levelled). It reduces only 3.5% of speech samples by more than 1 dB, and 0.3% by more than 3 dB. Mix normalized to **−16.0 LUFS integrated**, then an oversampled (4×) true-peak bus limiter at **−1.2 dBTP**. After the voice control it barely acts: max −0.44 dB. The encoded AAC files are re-measured in QA |
| Licensing | Music and SFX are synthesized in code: no samples, loops or third-party recordings. The narration voice is Apache-2.0 |
| Stems | `narration.wav`, `music.wav`, `sfx.wav` are exported at mix level. Their sum is the mix before the true-peak limiter: same −16.0 LUFS, but its sample peak reaches +1.1 dBFS, so re-summing in a DAW needs float headroom or a limiter |

## 6. Runtime

**116.3 s.** This is under the hard limit of 120 s, but **6.3 s over the 95–110 s target**.

- **Floor.** The 85 s of speech plus the readability budget sets a floor of roughly 113–116 s for this script. The added time sits in the silent algorithm steps (step 1, steps 3–4) and in the holds that give labels 2.5 s or more.
- **Getting to 110 s or less.** Two options, both of which trade away content:
  - Cut the step-1 annotations and the steps 3–4 visuals (about −4 s).
  - Drop L05 and L17 (about −2.5 s, but L17 carries FF1's energy cost, which is an honesty point).
- **Choice made.** Readability was prioritized over the target. This is a deviation from the brief.

## 7. Limitations and deviations, stated plainly

1. **TTS engine.** ElevenLabs and Gemini TTS were unreachable from this environment, and no keys were available. The narration uses Kokoro-82M (Apache-2.0), run locally. The pipeline accepts ElevenLabs line files as drop-in replacements (`VOICE_CASTING.md`).
2. **Casting.** Done by objective measures (ASR intelligibility, pace, pitch range), not by listening; nobody listened in this environment. The candidate takes are included so a human can confirm the choice.
3. **Runtime.** 116.3 s, over the 110 s target (§6).
4. **Reviews.** The three QA reviews in `QA_REVIEWS_V4.md` were written by the same AI that made the film. They used frame strips, the automated readability audit, ASR checks and loudness measurements. They are not reviews by independent human viewers.
