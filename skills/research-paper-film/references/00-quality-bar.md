# 00: Quality bar (definition of done)

This is where the case study ended up after five film versions and two figure rounds. Every cut is held to this bar: the generator runs the measurable checks before each handoff (references/12), and the independent reviewer judges the cut against it (references/19).

Most items can be measured; the tool is in brackets.

## A. Science and wording (film, narration, figures)

| # | Criterion | How to check |
|---|---|---|
| A1 | Every number on screen or in speech is in the claim ledger, with source, unit and conditions (threads, voltage, activity factor, "extrapolated", "average of N runs") | ledger vs audit inventory [audit.py JSON] |
| A2 | Every number carries its **scope**: what space it counts, which workloads it is averaged over, at which operating point. Examples: "valid designs in the §4.1 search space: <constraints>"; "geomean over 12 benchmarks"; "p99 at 70 % load"; "post-layout, 28 nm, 0.9 V". It goes on screen, and in speech as "in its search space" / "on these benchmarks" | read each count's label |
| A3 | The paper's distinctions are never blurred: modeled vs is; tool vs design; sampled vs simplest; schematic vs circuit vs silicon; behaviours (scale) vs circuits (performance) | wording pass with the TI/PM/AMB classes |
| A4 | Comparatives name the metric. "2.53× lower sequencing overhead", never "2.53× faster". Rounded speech ("about thirteen minutes") has the exact value on screen | narration vs ledger |
| A5 | The trade-offs the paper reports are shown next to the headline (e.g. the energy cost right after the speed result). No superiority claim the paper does not make | scientist review |
| A6 | Different mechanisms are shown as different things: each rule, stage or failure mode is its own case, with per-case counts, zeros included. Case study: three pruning rules, "384 · 32 · 0" | step figures + breakdown |
| A7 | Source tags are exact about provenance: "steps 1–3 as in Fig. 4 · steps 4–5 recomputed with the method"; "tree recomputed" | read every tag |
| A8 | No unlabelled conceptual visuals. Arbitrary positions are said to be arbitrary (unit-chart cell order, sample positions) | docs + labels |
| A9 | The structures come from code that asserts them against the paper (replayed sequences, totals, published tables). Discrepancies are listed "for the authors" | asserts in film.py / model |

## B. Comprehension and pacing (film)

| # | Criterion | How to check |
|---|---|---|
| B1 | Every string is readable ≥ 2.5 s, headline results ≥ 3–4 s, two-line reasoning ≥ 4–7 s. The only exceptions are live counters, and each is justified | audit.py |
| B2 | One worked example carries the film: the failure from Act I reappears in Act II's model, and Act III walks one instance (a branch, a tile, a request, an input) through every rule or stage | storyboard / film plan |
| B3 | Every mechanism beat is anticipation → action → consequence → hold, with one change at a time (camera, then label, then event) | frame strips at 0.3 s around each beat |
| B4 | A spoken key word lands while its label is visible ("pruned" is said while "branch pruned" is on screen) | EDL anchors + contact sheet |
| B5 | No caption band. Facts live in the scene or in the narration; nothing that only a caption carried is lost | caption-fact list |
| B6 | No layout faults at any frame: no label crosses an edge or arc; no chip covers a node or a ≠ sign; no element drifts under a panel; no clipping; markers on bidirectional edges don't overlap | 1-fps contact sheets + dense strips |
| B7 | The first 3 seconds already move. A static opening while the first line is spoken reads as slow | contact sheet |
| B8 | Runtime ≤ target. If the readability floor forces an overrun, state it as a deviation with the options and their cost | edl.py |

## C. Identity and craft (film)

| # | Criterion |
|---|---|
| C1 | One semantic palette, used everywhere: ok/valid · failing/removed · reference/expected · headline · neutral. The same marker identities appear across acts |
| C2 | White identity: no glow, bloom, grain, vignette or grid; flat tints for emphasis; soft shadows only on floating documents (table panel, PiP). **Exception:** at most 2 declared signature breaks per film (night / spot / accent / flood), each ≤ 6 s and inside a peak (W4, references/15) |
| C3 | Large unit charts use alpha-over, with a darker growing front (additive blending disappears on white) |
| C4 | Data animations keep physical time: segments that encode quantities stay at slope 1, and the on-screen rate ("20 ps per second") is true |
| C5 | Camera moves serve the content: each move follows an algorithmic event or a verified number. No decorative particle fields, no fields of cubes, no generic tech imagery. **Restraint is not stillness:** C5 forbids motion without meaning; G1–G4 require motion with meaning |

## G. Motion and camera (references/14)

A film can pass A–F and still be a slide show. These are measured on the 640 px preview and again on the delivered file with `scripts/motion_audit.py`, then gated by `gate.py --motion motion.json --centre <act>`. Calibration: case-study v4 measured 17 % / 2 s / 55 % / 4.3 %; a fresh build that passed every other gate measured 50 % / 7 s / 10 % / 0.8 %.

| # | Criterion | How to check |
|---|---|---|
| G1 | Static seconds (< 0.3 % of pixels change) ≤ 25 % of the film | motion_audit + gate.py |
| G2 | No static run > 3 s outside declared holds (title card) | motion_audit `--holds` + gate.py |
| G3 | Camera motion in ≥ 30 % of seconds; ≥ 40 % in the centrepiece act; every mechanism beat has a push-in and a pull-back; zoom range ≥ 2× in the centrepiece | motion_audit `--acts`, shot list |
| G4 | Mean per-second change ≥ 2 % | motion_audit + gate.py |
| G5 | Every motion has a meaning from references/14 §2 (proposal, tracer, pulse, write, strike, prune, focus, morph); nothing moves for decoration | the reviewer's frames and per-beat checks (references/19) |

## L. Linkage (references/14 §3)

| # | Criterion | How to check |
|---|---|---|
| L1 | Every finding (a rule outcome or a concrete value: =, ≠, →, ×, δ, pruned, conflict…) is pinned to its referent with `callout_at` (leader + dot, ≤ 220 px away); only HUD readouts float | `scripts/linkage_audit.py` |
| L2 | Findings state the instance with its values ("path needs δ(11,11) = 10"), not only a category ("entry conflict × 6") | the reviewer's scientist pass (references/19) |
| L3 | Contradictions show both facts at once (earlier fact teal, needed fact coral, ≠), pinned to the same element | stills at the beat |
| L4 | The state the method builds is a fixed-address panel (`AddressTable`): every address present from the start, written in place, tethered to the scene element while the event is shown | stills + linkage map |
| L5 | The full candidate space is visible (pills with ghost / live / pruned slots), so pruning shows what it removes things from | stills |
| L6 | A step breadcrumb (and a search-tree PiP where the method branches) says where we are | stills |

## W. Peaks (references/15)

Accuracy, legibility and motion do not make a moment memorable. Peaks are measured with `scripts/wow_audit.py` and gated by `gate.py --wow wow.json`. Calibration: `examples/peak_demo` measured reveal spikes of 12.0–28.9 % of the frame against setup medians of 0.03–0.22 %.

| # | Criterion | How to check |
|---|---|---|
| W1 | 3–6 peaks; at least one concept and one result peak; ≥ 8 s apart; the first lands by max(20 s, 20 % of the runtime) | peaks table / `PeakPlan` asserts |
| W2 | Each reveal is the biggest change of its peak: max per-frame change in [reveal − 0.1, reveal + 0.6] ≥ 2.5× the setup median and ≥ 4 % of the frame | wow_audit `--video` |
| W3 | One change at a time: nothing in the hold changes as much as 60 % of the reveal | wow_audit (WARN) |
| W4 | ≤ 2 signature breaks per film, each ≤ 6 s, inside its peak; no dark-stage second outside a declared night/spot window | `PeakPlan` asserts + wow_audit |
| W5 | A sound cue within 80 ms of every reveal; hits are reserved for peaks | wow_audit `--cues` |
| W6 | The peak's key word starts within 0.35 s of the reveal | wow_audit `--placement` |
| W7 | Every peak dramatises a claim-ledger entry; a result peak shows the reported trade-off within 12 s; no device strengthens a claim (no overshoot, unlabelled axis trick, slow-motion data, or superlative) | wow_audit `--ledger` + the reviewer's scientist pass |

## R. Argument and data (references/16)

A film can be accurate number by number and still lose a careful viewer: a container shown by name rather than contents; an ablation result that reads like the method failing; a gain that invites an obvious objection and never answers it. Measured with `scripts/argument_audit.py` against the on-screen string inventory, gated by `gate.py --arg`.

| # | Criterion | How to check |
|---|---|---|
| R1 | Comparisons and ablations name the metric and what is held fixed; ablations also say what is removed; the wording is on screen | argument map + audit strings |
| R2 | Every baseline, ablation and term is defined on screen before its first comparative use | t_def ≤ t_claim |
| R3 | Every ablation is preceded by the doubt it answers; every doubt is answered by later data or acknowledged in one line | t_raised < t_answer |
| R4 | Every aggregate (geomean, mean, total) shows its spread: range, wins, n | audit strings |
| R5 | Mechanism beats about storage or data show element-level contents, computed (`data_kit.loop_nest_tile` or the model's state) and asserted against the numbers on screen; partition labels derived, not typed | argument map + asserts |
| R6 | Baselines and ablations never wear the method's colour or position | colours in the argument map |
| R7 | The paper's core domain concepts are captured in an executable model, validated against the paper's worked examples; every data mechanism is drawn from its trace (labels, counts, order, timing) | `MODEL_CHECKS` in the argument map |
| R8 | Every concept shown in ≥ 3 beats has one canonical, detailed glyph (storage: ports + counters, element states, occupancy) used in every scene and figure | `glyphs` in the argument map |

## D. Sound and delivery

| # | Criterion | How to check |
|---|---|---|
| D1 | Narration is never stretched; clips do not overlap (gap ≥ 0.2 s) | edl.py |
| D2 | Mix at −16 ± 0.5 LUFS integrated, ≤ −1.0 dBTP on **every encoded file** | assemble.sh readout / ebur128 |
| D3 | Speech intelligible in the mix: ≤ 1% word difference vs clean narration | mix_check.py |
| D4 | SRT cues are timed by spoken words, never break mid-sentence, and match the delivered audio (only ASR spelling variants remain) | subtitles.py asserts, srt_check.py |
| D5 | Durations: video = audio = EDL duration (never `-shortest`) | ffprobe |
| D6 | The audio is licence-clean and documented, and stems are delivered | docs |

## E. Slide figures

| # | Criterion | How to check |
|---|---|---|
| E1 | Every element is in its final state. No mid-animation frames; no film frames pasted side by side | look |
| E2 | Composed for a slide: aspect 2.0–2.6:1 for a full-width figure under a title; no empty quadrants; each panel fills its space | lint_figs.py (aspect) |
| E3 | Text ≥ 9 pt at 12 in placement width (≈ 18 design units for a 1900-unit-wide figure); body labels ≈ 11 pt | lint_figs.py (min size) |
| E3b | Slide contrast: strokes ≥ 1.5× the film's weights, no secondary text lighter than #4B5967, faded elements still clearly visible when projected (figkit.BOLD defaults) | look at the figure at 30 % zoom |
| E4 | One typeface, and it is the face you think: `pdffonts` shows only the intended weights | lint_figs.py / verify_vectors.py |
| E5 | The agreed text policy is applied: no titles, legends or captions if the user types them in PPT; chips, labels, numbers and ticks are kept | look |
| E6 | Step sequences: one camera (near-orthographic), one crop, key table enlarged beside the stage, small insets dropped. Consecutive steps overlay exactly | identical PNG sizes |
| E7 | Every requested case has a figure. A case that cannot occur is drawn as a labelled illustration and explained | README |
| E8 | PNG (3×, 300 dpi tag), SVG and PDF are all present and visually identical; raster-only panels are declared | verify_vectors.py |
| E9 | A README gives each figure's source or construction, its data values (e.g. Pareto coordinates), the omitted legend and every caveat | README |

## F. Process honesty

| # | Criterion |
|---|---|
| F1 | Every "checked" or "verified" in a document points to a run you can name (a file, a command, an output) |
| F2 | Reviews say who did them: the independent reviewer agent (fresh context; inputs listed), the user on human rounds; generator audits are labelled self-checks |
| F3 | Deviations from the brief (runtime, a TTS engine you could not use, unavailable tools) are listed plainly, with the trade-off |
