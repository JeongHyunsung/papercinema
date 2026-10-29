# B-Flex v4: QA reviews

The three reviews below were carried out by the AI that produced the film (Claude). They are **not** independent human reviews, and nobody in this environment watched the film with sound. Each finding is tied to evidence that can be re-run:

- frame strips extracted from the rendered video;
- the automated readability audit (`src/audit.py`);
- ASR checks of the narration in the final mix (`narration/mix_check.py`);
- loudness measurements with ffmpeg `ebur128` (true peak);
- the arithmetic in `ACCURACY_CHECKLIST_V4.md`.

Items marked **fixed** were changed before the final render. Items marked **open** are known limitations.

## 1. Scientific review

| # | Finding | Status |
|---|---|---|
| S1 | Every narrated number matches the paper or recomputes from it: 10¹⁹ vs 4³²; 20,000 vs 2.07 × 10⁴; 568 million; "about thirteen minutes" vs 786 s; 2.53× vs 48.2/19.1; higher energy, 2.26 vs 1.53 fJ (checklist §A) | pass |
| S2 | Scale and circuit claims are kept apart. "valid behaviors" is never called circuits, and "one of them, FF1 … its" never generalizes 2.53× | pass |
| S3 | The race is still at slope 1 on the v4 clock, so bar durations stay proportional to the picoseconds and the on-screen claim "20 ps per second of film" is true. Verified in the timing sheet (segment 52.40→55.35, slope 1.00) | pass |
| S4 | The v3 caption band carried facts that would have disappeared with it: the brute-force ~10⁶ years, the 2-bit runtime 162 s → 0.00784 s, the energy values, and the FF6 0.4 V result. Each is now drawn in its scene (checklist §C) | fixed |
| S5 | L14 "Twenty of the simplest" compresses the selection rule (20 sampled from the 468 with C_FF ≤ 20, excluding known 2-bit FFs). The breadcrumb names the 468 / C_FF ≤ 20 stage. Acceptable compression; flagged ⚠ in the checklist | accepted |
| S6 | Removing the 2-bit count 3¹⁶ removes the only on-screen 2-bit search-space number. The narration never needed it, and the 2-bit *runtime* result is still shown | accepted |
| S7 | Discrepancies for the authors are unchanged from v3: the C_FF of FF4 and FF5, and the 3-bit initial input | open (paper) |

## 2. Cinematic review

| # | Finding | Status |
|---|---|---|
| C1 | **White identity.** No glow, grain, bloom, vignette or grid remains. The only shadows are on the two floating "documents" (the δ table and the tree PiP). Glow highlights became faint flat tints | pass |
| C2 | The glow at the playhead in Act I left grey ghost discs on white | fixed (removed) |
| C3 | The Reference-Behavior-Graph header was crossed by the graph's long arc edge. A white knockout now sits behind the header block | fixed |
| C4 | Scatter: the title lines overlapped the y-axis, and the 0.4 V footnote collided with the TGFF label. Both moved into the empty top-right, above the legend | fixed |
| C5 | Unit chart: the v3 additive light-on-dark compositing made the 568M square nearly invisible on white. It now uses alpha-over teal, with the growing front darker | fixed |
| C6 | **Rhythm.** Speech-led stretches alternate with three silent beats: step 1 (about 5 s), steps 3–4 (about 4.7 s), and the post-rejection hold. The silent beats give the music room and let the δ table be read, so the contrast is intended | pass |
| C7 | The opening 0–3.5 s shows only the pin labels under L01. Mitigation: the test vector now starts at about 3.6 s, during L01's "capture D and hold it". It is still the slowest-looking moment of the film | partly fixed |
| C8 | **Runtime.** 116.3 s is over the 110 s target (see the revision log §6) | open |
| C9 | **Sound.** Voice-to-bed separation is about 15 dB or more under speech: music is ducked 9 dB and sits around −26 LUFS before ducking. In the final mix, ASR of the narration differs from the clean narration by 1 word in 231 (0.4%). Loudness is −16.0 LUFS integrated, with true peak −1.2 dBTP on the PCM master and on both AAC files (measured; see §4) | pass |
| C10 | The music bed and SFX are procedural sketches, not composed music. They are licence-clean, but a composer or licensed library cue would lift the film. The stems are separate, so the music can be replaced without touching the voice | open (suggestion) |

## 3. First-time viewer review (no prior knowledge of the paper)

Walk-through of what a newcomer must understand at each point, checked against what is on screen and what is said at that moment (time codes on the v4 clock):

| t | Must understand | Said | Shown | Verdict |
|---|---|---|---|---|
| 0:00–0:15 | What a flip-flop must do; SeGen-20 passes one test but fails a reordered one | L01–L03 | Waveform, checks ①–⑥, ⑥ turns red. "expected Q" (blue) vs "SeGen-20 output" (red), readable 3.35 s | clear |
| 0:15–0:27 | Why exhaustive 3-bit search is hard | L04–L05 | 4³² ≈ 1.8 × 10¹⁹; prior search stops at 2-bit; brute force ~10⁶ years | clear |
| 0:28–0:40 | The reference graph is the full spec, and the failing vector is one path in it | L07–L08 | Legend line (node / edge / amber); replay ①–⑥. "reference: Q = 1" / "SeGen-20 output: Q = 0" for 3.85–4.15 s (was 0.55 s) | clear. This was the brief's main readability defect |
| 0:41–0:50 | Candidate states sit over the reference node with the same Q | L09 | Callouts Q = 0 → 01, 11 / Q = 1 → 00, 10 (3.0–3.3 s); STEP 1 marker | understandable. Step 1 itself is not narrated |
| 0:50–1:00 | Wrong-output pruning | L10 | "CK falls → Q must stay 0" (5.3 s); the Q = 1 candidates turn red; "no reference edge"; "wrong output → branch pruned" (3.8 s) | clear |
| 1:00–1:01 | Steps 3–4 | — | STEPS 3–4 marker: "infer δ entries · no contradiction → both branches kept · the check repeats" | adequate. A newcomer may not follow the δ-table rows in detail |
| 1:01–1:09 | Entry conflict | L11 | "path needs δ(11,11) = 10" (5.05 s) ≠ "earlier edge fixed δ(11,11) = 11" (4.15 s); table row turns red; "branch pruned" | clear. This is the hardest idea, and it got the longest exposure |
| 1:09–1:23 | Speed and scale | L12–L13 | Full 2-bit tree, 2.07 × 10⁴×; exact counter to 568,832,054; "vs. 18 at 2-bit"; "786 s · 16 threads" | clear |
| 1:24–1:36 | From behaviors to circuits, and what FF1 does | L14–L15 | 468 with C_FF ≤ 20 → 20 synthesized → FF1's capture walk 101 → 100 → 000 | clear. FF1's fast state readouts are deliberately transient |
| 1:37–1:50 | 2.53× lower sequencing overhead, under stated conditions, at an energy cost | L16–L17 | Race at constant rate; 2.53× for 4.0 s; scatter of all 18 FFs with FF1 2.26 fJ vs TGFF 1.53 fJ | clear |

**Main residual risks for a newcomer:**

- The δ table is dense. Its role is explained by the tethers and the step markers, not by the narration.
- "ESTG" is never spoken. The film says "candidate", which is intentional, but the paper's term is not taught.

## 4. Technical checks on the delivered files

Measured on the files in `out/final_v4/` after the final assembly; values are filled in from ffprobe and ebur128.

| File | Video | Frames | Duration | Audio | Integrated | True peak | LRA |
|---|---|---|---|---|---|---|---|
| BFlex_DAC2026_film_v4_4K60_master.mov | h264,3840,2160,60/1 | 6978 | 116.300000 s | pcm_s24le,48000 | -16.0 LUFS | -1.2 dBTP | 5.5 LU |
| BFlex_DAC2026_film_v4_4K60.mp4 | h264,3840,2160,60/1 | 6978 | 116.300000 s | aac,48000 | -16.0 LUFS | -1.2 dBTP | 5.5 LU |
| BFlex_DAC2026_film_v4_1080p60.mp4 | h264,1920,1080,60/1 | 6978 | 116.300000 s | aac,48000 | -16.0 LUFS | -1.2 dBTP | 5.5 LU |
| audio/BFlex_v4_mix.wav |  |  | 116.300000 s | pcm_s24le,48000 | -16.0 LUFS | -1.2 dBTP | 5.5 LU |

- **Frame accuracy.** 6978 frames = 116.3 s × 60 fps in all three video files. The 8 render chunks were concatenated losslessly; frame counts were checked per chunk (864 × 7 + 930).
- **Subtitles.** 25 SRT cues, embedded as a soft `mov_text` track (off by default) in both MP4s, and shipped as a separate `.srt`.
- **Picture check.** Frames grabbed from the encoded 4K MP4 at 0:12.9, 0:37.6, 0:43.8, 0:54.3, 1:05.4, 1:21.2, 1:28.6, 1:42.6 and 1:47.6 match the corresponding stills rendered directly from the source.
- **Narration intelligibility in the final mix.** 1 differing word in 231 (`docs/qa_mix_intelligibility.txt`).
- **Audio ends with the picture.** Music and SFX fade over the last 1.6 s. The audio files are trimmed to 116.3 s.

