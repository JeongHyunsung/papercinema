---
name: "research-paper-film"
description: "Turn any CS/EE research paper into a scientifically verified, narrated, code-generated explainer film and slide figures, refined in a loop: a generator makes each cut, a fresh independent reviewer sees only the video and paper, the user joins every K rounds. Also audits such films."
---

# Research paper → explainer film and slide figures, through an independent review loop

**Input:** a CS/EE paper (PDF), plus an optional brief.

**Output:**
- a cinematic, scientifically faithful motion-graphics film, rendered entirely from code (4K60, narration, subtitles, mastered mix);
- slide figures in the same visual language;
- on request, an audit of an existing film against the paper.

**Origin.** The quality bar, defaults and gates come from a production that took five film versions and two figure rounds of author feedback (case study: B-Flex, DAC 2026, a search-and-circuits paper). A later from-scratch rebuild was scientifically stronger than that film, yet visibly weaker in motion, camera and linkage. That gap is now part of the bar (G and L gates; see `examples/bflex/docs/FRESH_REBUILD_POSTMORTEM.md`). A film that passes every one of those gates can still leave no moment behind, so v4 adds **peaks**: 3–6 planned moments where a verified fact lands with setup, one reveal, sound and camera together, and at most two style breaks per film (W gates; references/15). The first author review of a v4 film then asked for two more things, now gates R1–R11 (references/16): containers show the **elements** they hold, computed from the re-implementation; and the argument anticipates the **skeptic** (doubt → test → result, definitions before use, spread next to every aggregate). The rules apply to **any** CS/EE paper; B-Flex appears only as examples.

**v7: the review loop.** Before v7 the producing agent reviewed its own film as a series of imagined critics, and it saw what it meant rather than what was on screen. Now the work is split (references/18):
- the **orchestrator** (you, the agent talking to the user) runs intake, routes files and talks to the user; it never makes the film;
- the **generator** (one persistent subagent) builds each cut from the paper and the intake brief, passes its own mechanical gates, and revises from the reviewer's feedback only;
- the **reviewer** (a fresh subagent every round) sees only the delivered video and subtitles, the paper, user-supplied data, its own earlier reviews, and the user's comments from the human rounds; it writes the feedback;
- the **user** reviews the cut every K rounds (K asked at intake) and approves the final; either role may ask the user for data, and "there is none" is a valid answer.

The gates still apply: the generator never hands off a cut with a gate FAIL it could fix, so reviewer rounds are spent on what gates cannot see.

**If you were spawned as the generator or the reviewer,** you are not the orchestrator: read what references/18 §1 lists for your role and skip every instruction addressed to the orchestrator (intake, AskUserQuestion, talking to the user).

If `references/`, `scripts/`, `templates/` and `examples/` sit next to this file (the GitHub repo `JeongHyunsung/papercinema`), use them. Every script has a usage docstring.

- `references/18-review-loop.md` — roles, workspace routing, a round, requests to the user, spawning, stopping. **The orchestrator reads it before intake.**
- `references/19-reviewer.md` + `templates/review.md` + `scripts/review_pack.py` — the reviewer's brief, its feedback format, and its video-only view of the film (stills, contact sheets, timeline of picture change, camera and sound, motion gates, loudness, transcript). Only the reviewer reads 19.
- `references/13-paper-archetypes.md` — what to show and how to say it, for 7 paper archetypes. **Read first.**
- `references/14-motion-camera-linkage.md` — camera grammar, meaningful motion, pinned findings, beat choreography. **Read second.** Stills and legibility gates cannot show what it covers.
- `references/15-wow-beats.md` — peaks: the designed moments, their devices, the 2-per-film signature budget, peak sound. **Read third.**
- `references/16-argument-and-data.md` — data-level grounding and the skeptic pass. **Read fourth.**
- `references/17-story-spine.md` — the story arc (title as the answer, one climax, reprise) and the persistent visual spine. **Read with references/02 when storyboarding.**
- `references/00-quality-bar.md` — the definition of done (A–F, G motion, L linkage, W peaks, R argument).
- `references/11-iteration-lessons.md` — general rules learned from every revision, including the fresh rebuild.
- `references/12-critic-loop.md` — the generator's pre-video checkpoints and pre-handoff gates.
- `references/01`–`10` — phase details and a table of pitfalls.
- `scripts/motion_kit.py` + `examples/motion_kit_demo/` — camera direction, focus, tracers, pinned callouts, tethers, fixed-address tables, pills. The demo passes every motion and linkage gate; start the centrepiece act from it.
- `scripts/peak_kit.py` + `examples/peak_demo/` — peak plan and budget (`Peak`, `PeakPlan`), fidelity-safe devices (cascade, collapse, exact counters, number land, log zoom, breath) and the signature breaks (night, spot, accent, flood). The demo passes W1–W7, G1–G4 and L1.
- `scripts/data_kit.py` — computed operand tiles (`loop_nest_tile`), element grids, 3-D tensors, same-element links, load meters, and the canonical `Storage` glyph (ports, counters, element states) + `storage_icon`.
- `scripts/loopnest_sim.py` — the domain model for accelerator papers: cycle-level MACs per PE, storage tiles, fills, reads → destinations.
- `scripts/motion_audit.py`, `scripts/linkage_audit.py`, `scripts/wow_audit.py`, `scripts/argument_audit.py`, `scripts/gate.py` — the measurable gates.
- `scripts/viz_kit.py` + `examples/gallery/` — ready components and one slide figure per archetype.
- `templates/film_plan.md` — fill it in, including the shot list, linkage map and peaks table, before building anything.

## 1. Classify the paper, then ask once

**Classify the paper.** Pick one archetype, or two if it mixes them (references/13). The archetype fixes six things:
- the worked example;
- the mechanism beat;
- the result visuals;
- the conditions every number needs;
- the wording traps;
- the peak candidates (references/15).

| Archetype | Covers |
|---|---|
| A | algorithm / search / optimization |
| B | hardware architecture / accelerator |
| C | circuits / devices |
| D | systems / networking / databases |
| E | ML methods and ML systems |
| F | compilers / PL / verification / security |
| G | signal processing / communications / control / power |

**Ask once, in a single round** (orchestrator): AskUserQuestion for the multiple-choice items (up to four per call), the free-form ones (numbers, examples, constraints) in plain text in the same turn. Skip anything the brief already answers.
1. **Duration and narration.** Target duration and hard limit; narration yes/no, language, voice preference.
2. **Two different examples. Ask them separately; never merge them into one option.**
   - **Walk instance:** the instance the mechanism is walked through in Act III. Default: the paper's own running example at its smallest size, small enough to push in on (references/14 §5).
   - **Replay:** the headline design or result replayed in Act IV.
   - Must every mechanism be shown with a real instance?
3. **Figures.**
   - Which figures: motivation, method steps, key result.
   - Text policy: what the user will type in PPT (titles, legends, captions) and what stays in the figure (chips, labels, numbers, ticks).
   - Slide layout: full width under a title, about 2.2:1.
4. **Constraints and references.**
   - What must be kept or avoided ("keep the pipeline unchanged", "no claims beyond Table 3").
   - Any reference film or style to match.
   - Any moment the author wants to be *the* moment of the film (it becomes a peak; references/15).
   - "From scratch" means new content and data. It never means skipping `motion_kit` or references/14.
5. **Review loop** (references/18 §3).
   - **K:** the user reviews the cut every K rounds (suggest 2; 1 = every round). The final candidate always goes to the user.
   - **Maximum rounds** before the loop stops and asks (suggest 6).

The orchestrator asks these, writes the answers to `gen/BRIEF.md` (generator only) and K to `LOOP.md`, then spawns the generator. The generator fills in `templates/film_plan.md`, including the shot list and the linkage map. After intake, questions to the user go only through the request channel (references/18 §5), from either role; the user may answer with data, a decision, or "unavailable".

## 2. Non-negotiables

- **Fidelity first, spectacle too.**
  - On-screen structures come from the paper, or from a minimal re-implementation that asserts against the paper's figures, tables and worked examples.
  - Results you cannot re-run (silicon, large training, cluster experiments) are typed from tables. If you digitize them from plots, mark them "approx.".
  - Never invent metrics, baselines, topologies, circuits, datasets or conclusions.
  - Label conceptual or arbitrary visuals as such.
- **Every number carries its scope and conditions on screen.** Depending on the field, that means:
  - what space, benchmarks or workloads the number covers;
  - platform: simulated, RTL, FPGA or silicon; node, voltage, frequency;
  - batch size, load level, percentile, dataset and split;
  - number of runs or seeds;
  - flags such as "geomean" or "extrapolated".
  
  Speech may round the number; the screen shows the exact value.
- **Use the paper's distinctions and verbs.**
  - "modeled as" vs "is"; the tool vs the artifact it produced.
  - Sampled vs top-k; model vs schematic vs layout vs silicon.
  - Peak vs sustained; mean vs geomean vs tail.
  - Comparatives name the metric ("3.2× lower p99 latency", never "faster").
  - The trade-off the paper reports is shown right next to the headline.
- **Restraint is not stillness.**
  - No decorative motion, but every second carries a meaningful change: a camera move toward the event, a token on a path, a value written, a branch cut.
  - Gates G1–G4: static seconds ≤ 25 %, no freeze > 3 s, camera motion ≥ 30 % of seconds (≥ 40 % in the centrepiece), mean change ≥ 2 %.
- **Understand before drawing.** Identify the paper's core domain concepts and build an executable model that reproduces the paper's worked examples (accelerators: `scripts/loopnest_sim.py`, a cycle-level loop nest giving occupancy, per-PE MAC order, refills and data paths). Validate it first (`ARGUMENT["model_checks"]`), then derive every label, count, order and timing a mechanism beat shows from its trace.
- **One canonical glyph per recurring concept.** A concept shown in three or more beats (storage, PE, queue, node) gets one detailed glyph with its anatomy alive (storage: `data_kit.Storage`: write/read ports with counters, element states, occupancy), used in every scene and figure. Lay it (and everything beside text) out from measured sizes, never fixed offsets, so it stays clean when slide figures enlarge text; route wires and tethers through gaps.
- **Show the data, not the box.** A mechanism about storage, movement, reuse or partitioning shows each container's contents element by element (2-D grids; 3-D tensors as slabs), computed from the re-implementation and asserted against the numbers on screen. Partition labels are derived, never typed.
- **Cover every mechanism, say each thing once.** List the paper's mechanisms and effects and give each a beat or a reasoned omission; never show a result without the mechanism behind it. One strongest visual per claim; no weaker re-draws, no detail that no claim needs. Meet the runtime by cutting, not by speeding speech (R9–R11).
- **Answer the skeptic.** For each claim, list the doubts a reviewer would raise. If the paper has the answering data, raise the doubt first, say what the test holds fixed and removes, then show the result and its conclusion. Define every baseline and ablation on screen before its first use; ablations never look like the method; aggregates show range and wins; interpretations are attributed to the paper; prior work is described with the paper's own precision.
- **Peaks are earned, never added.**
  - 3–6 peaks per film; each dramatises one claim-ledger entry (setup → tension → one reveal ≤ 0.6 s → hold ≥ 2.5 s), with the sound hit and the spoken key word on the reveal.
  - At most **2 signature breaks** (night / spot / accent / flood) per film, each ≤ 6 s and inside its peak. Everything else stays in the white identity.
  - Drama never strengthens a claim: no overshoot, no unlabelled axis tricks, no slow-motion data, no superlatives the paper does not use; a result peak shows its trade-off within 12 s.
- **Findings are pinned.**
  - A rule outcome or value is drawn on (or leader-linked to) the element it is about, with its concrete values ("path needs δ(11,11) = 10").
  - The method's state is a fixed-address panel, tethered to the scene on every write (gates L1–L6).
- **Speech is never time-stretched.** The picture is retimed to the voice.
- **Audio is licence-clean:** a procedural score and SFX, plus open-licence voice and ASR models.
- **The reviewer stays independent.** It is a fresh subagent each round (never a fork, never a continued one), sees only the deliverable, the paper, `materials/`, its own earlier reviews and the user's input, and never the generator's code, plans, notes or reasons. The generator sees the reviewer only through `review.md`, and the user's comments only through the reviewer. The orchestrator routes files and never paraphrases between them (references/18 §9).
- **Fidelity outranks feedback.** A reviewer or human request that would contradict the paper or a non-negotiable is disputed through the user, never silently applied or ignored (references/18 §6).
- **Never claim a check you did not run.** Reviews say who did them. Deviations from the brief are stated with their trade-off.
- **Language.** Reply in the user's language. On-screen text and narration follow the brief, usually English.

## 3. Defaults for draft 1 (learned from every revision; apply to any paper)

**Story structure** (references/17; the B-Flex-style arc)
- Hook → problem → **title as the answer** (about 20 % in, right after the question it answers) → one connected mechanism → one numerical climax → secondary results with their trade-off → **title reprise** and hold.
- The hook uses no terminology: it shows the cost, then the scale number with its counting assumptions on screen.
- **One persistent visual spine.** One object (a candidate space, a circuit, a pipeline) carries fixed identities from the hook to the closing. Every mechanism operates on it (in B-Flex: expand a candidate, prune on wrong output, prune on entry conflict, keep the valid machines). Detail scenes (tables, stages, charts) cut away and return to it as a mini-map or side panel. Do not build one-off clouds or cards per act.
- Keep distinct operations distinct on the spine, with their own colour and caveat. For example, in B-Flex: pruned for wrong output ≠ pruned for entry conflict, and "not explored" ≠ "proven invalid".
- One hero number, alone on a white stage, with its exact meaning, scope and spread. The doubt it answers is shown before it. Baselines come after it as secondary results, never as "wins everywhere".
- Alternate dynamic shots (camera on the spine) with static ones (tables, charts, the number). Stay on a white stage throughout unless the paper's identity asks otherwise.

**Visual**
- Every element has a job: explain a concept, make a transition, or show a verified number. No decorative particles, no generic circuit-board or "AI" imagery.
- Build the scene from the paper's own representation: graph over graph, dataflow on a block diagram, request path, tensor flow, signal chain.
- **Show the full space, not only the visited part.**
  - Candidate states sit in pills above their reference node: ghost, then live, or pruned.
  - Tiles sit in their buffer slots; requests sit in their queues.
- White identity from the start.
  - Semantic palette: ok/valid (teal), failing/removed (coral), reference/expected (blue), headline (amber), neutral.
  - Flat tints only; no glow, bloom, grain, vignette or grid.
  - Soft shadows only on floating "documents" (a table panel, a PiP).
- Dense charts use alpha-over, with a darker growing front.

**Camera and motion** (references/14 §1–2, `motion_kit`)
- Every scene has a keyframed camera: `StageCam` for stages, `View2` for flat scenes.
- Long structures (waveforms, pipelines) get a **follow** shot that rides the moving head (`lagged`).
- Every mechanism beat gets a **push-in**, a **hold with drift**, and a **pull-back** (`beat_keys`); the zoom range in the centrepiece is ≥ 2×.
- Changes of scale get a **reveal/dive**; 3-D objects get a short **orbit**.
- Meaningful motions only:
  - `proposal` arcs for candidates;
  - a `tracer` token for paths;
  - a `pulse` when something is written or decided;
  - slot state changes;
  - prune (coral, drop, fade);
  - in-place table writes and strikes;
  - `focus` dimming of non-participants;
  - morphs between representations.

**Linkage** (references/14 §3)
- Findings use `callout_at`: a leader and a dot on the referent, ≤ 220 px away, written with values. Both sides of a contradiction are shown at once, with ≠.
- The rule is written on the reference element it comes from ("CK falls → Q must stay 0" on that edge).
- The state the method builds is an `AddressTable` with every address present. A `tether` runs node → row while a write, inference or conflict is shown.
- A step breadcrumb (`breadcrumb`) sits under the act label. Where the method branches, a search-tree PiP shows where we are.

**Peaks** (references/15, `peak_kit`)
- Pick peaks from the claim ledger in this order: the size of the problem (hook) → the one cause with many effects (concept) → a check that always holds (evidence) → an expectation reversed (twist, optional) → the headline number (result).
- One device per peak, matching what the claim *is*: `scale_reveal`, `cascade`, `collapse`, `invariant_counter`, `race`, `reversal`, `before_after`, `number_land`.
- Default signature use: `night` on the concept peak, `accent` on the result peak; or none. Never more than two.
- Sound: one `riser` into the reveal, 250–400 ms of pre-hit silence (`Track.duck`), one `hit` on the reveal frame; no hits outside peaks.
- The peak's key word is written into the narration line so it lands on the reveal.

**Pacing and text**
- Change one thing at a time: the camera settles, then the label appears, then the event happens. Mechanisms follow anticipation → action → consequence → hold.
- Slow is not static: during holds the camera drifts or a token moves.
- Tempo is a code: fast for repetition and scale, moderate for changes of representation, slow for mechanisms.
- **One worked example carries the film.**
  - Act I's failure is replayed in Act II's representation.
  - In Act III, one small instance walks through **every** rule or stage, with the state beside it.
  - Then accelerate to scale, and replay the headline design.
- Each mechanism beat gets 4–7 s of picture. Lengthen the narration gap before it rather than squeezing the beat.
- No caption band: facts live in the scene or in the narration.
- Readability budgets sit in the timing sheet: labels ≥ 2.5 s, results 3–4 s, two-line reasoning 4–7 s.
- Reserve empty zones for text, and use a knockout behind headers. Source tags go top-right and give exact provenance ("Fig. 4" vs "recomputed").
- A data animation whose duration encodes a quantity runs at slope 1, and the on-screen rate it states is true.

**Narration**
- Narration first: script → voice → word alignment → retime the picture (EDL).
- Each key word is anchored so it lands while its label is visible; push-ins land on the key word.
- One natural spoken sentence per idea.
- Acronyms and units are respelled for the TTS; record them in a pronunciation table.
- Subtitles are timed by spoken-word count.

**Figures**
- Never film frames captured mid-animation, and never frames pasted side by side.
- Motivation and key-result figures are purpose-built compositions (viz_kit + the gallery recipe for your archetype).
- Method-step sequences:
  - one near-orthographic camera and one identical crop;
  - the key state table enlarged beside the stage;
  - small insets dropped; small text boosted;
  - Inter only, verified with `pdffonts`;
  - slide contrast on by default (`figkit.BOLD`, `use_contrast()`): strokes 1.5×, faded elements and greys darker, text one weight heavier and 8 % larger;
  - every distinct mechanism or case gets its own figure.

## 4. The review loop, and the generator's checkpoints

**The loop** (references/18 §4). Round r = 1, 2, …:
1. **Generator** builds (round 1) or revises from `rounds/r−1/review.md` (later rounds), passes its gates, and hands off a review cut: `rounds/rNN/deliverable/film.mp4` (1080p30, narration, mastered mix) + `film.srt`. It replies `done`, one gate line, and any requests; never a description of the film.
2. **Human** (r mod K = 0, and every ship candidate): the orchestrator sends the cut to the user and saves the comments verbatim to `rounds/rNN/human.md`. A ship candidate from a non-human round becomes the next round's cut unchanged, reviewed by the user and a fresh reviewer.
3. **Reviewer**: a fresh subagent (`general-purpose`, never `fork`) with the spawn prompt of references/18 §7. It builds its view with `scripts/review_pack.py`, follows references/19, and writes `rounds/rNN/review.md` (`templates/review.md`): verdict SHIP or REVISE, the status of its earlier findings, new findings with severity BLOCKING / MAJOR / MINOR / TASTE and a checkable "Done when", and requests to the user.
4. **Orchestrator** relays requests (references/18 §5), logs the round in `LOOP.md`, tells the user one line (round, verdict, next), and sends the generator only the path of `review.md` (not after a SHIP on a non-human round: that cut goes to the user first).
5. **Stop** when, on a human round, the reviewer says SHIP, the gate line is all PASS and the user approves. If the user approves while the reviewer says REVISE, show the user the open BLOCKING/MAJOR titles and let them choose. A finding open for 3 rounds goes to the user for a decision, which a fresh reviewer writes into that round's review, and the loop continues; at the maximum rounds the loop stops and asks (references/18 §8).

**Generator acting on a review:** every BLOCKING, MAJOR and MINOR finding is fixed to its "Done when" or disputed through the user with evidence; TASTE findings not from the human may be declined. The user's decision is written to `exchange/rulings.md` as id + decision only, and both roles read it.

**Generator checkpoints.** Before the first video exists, the generator checks its own work at K1–K3b. Before every handoff it runs the cut's gates (K4 and K5 rows: motion, linkage, peaks, argument, readability, EDL, loudness and speech). These are mechanical self-checks; judgement is the reviewer's. (The checkpoint names K1–K7 are unrelated to K, the human-review period.)

| Checkpoint | Inspect | Gates |
|---|---|---|
| K1 Facts | Claim ledger, data asserts, film plan | A1, A2, A9 |
| K2 Story | Storyboard + script (speech ≈ words ÷ 2.6 s), walk instance vs replay, **peaks table** (kind, device, claim, key word, signature), **argument map** (claim → doubts → answer) and **data views** (beat → containers → computed contents) | B2, B8, A3–A5, W1, W4 (planned), W7, R1–R5 (planned) |
| K3 Look | 6–10 stills: one per act and one per mechanism beat | C1–C5, B6, L3–L6 |
| K3b Choreography | Shot list + linkage map in the film plan; a 3–5 s 640 px test render of the centrepiece beat, through `motion_audit.py` and `linkage_audit.py`; a 640 px test render of the strongest peak with its sound, through `wow_audit.py` | G3, G5, L1–L5, W2, W3, W5 |
| K4 Cut (before every handoff) | 1080p review cut, readability audit, EDL check, `motion_audit.py --acts --holds`, `linkage_audit.py`, `wow_audit.py --placement --ledger`, `argument_audit.py --audit` | B1, B3–B7, D1, G1–G4, L1, W1–W7, R1–R11 (`scripts/gate.py --motion --wow --arg`) |
| K5 Sound (before every handoff) | Mix readout, in-mix ASR, loudness of the review cut | D2, D3 |
| K6 Deliverables (after approval) | Encoded files: loudness, durations, SRT vs audio, 4K contact sheet, motion audit of the delivered file | D2, D4, D5, G1–G4 (`gate.py`) |
| K7 Figures (after approval) | Figure contact sheet, vector check, lint | E1–E9 (`scripts/figures/lint_figs.py`, `verify_vectors.py`) |

**When the user sees the film**
- Every K-th round, and every ship candidate: the review cut, with a request for comments (they go to the reviewer).
- Whenever either role sends a request.
- After approval and the delivery check: the deliverables in `deliver/` (K6, K7).
- The generator never hands off a cut with a gate FAIL it could fix. A film that fails G1–G4, L1, W1–W7 or R1–R11 has a known defect.

## 5. Phases

Phase 0 and the loop are the orchestrator's; phases 1–7 and 10 are the generator's; phase 8 is shared (the generator's self-check audits, the reviewer's rounds); phase 9 starts with the reviewer.

- **0. Intake** (orchestrator).
  - Set up the workspace of references/18 §2; copy the paper to `paper/paper.pdf`.
  - Classify the paper. Extract the duration, format, narration, audience, three takeaways (problem, idea, impact), deliverables and hard rules.
  - If a follow-up brief preserves earlier work, treat that work as frozen and keep unchanged assets byte-identical.
- **1. Paper study, domain model and re-implementation** (`references/01`, `references/13`, `references/16 §0`).
  - First list the paper's core domain concepts and build the executable domain model; assert the paper's worked examples against it before anything is drawn.
  - Read every page as an image and as text, including footnotes and table notes.
  - Build the claim ledger.
  - Re-implement only what the film shows. Write it to `data/scene_data.json`, with asserts against the paper.
  - Where the paper gives totals (counts, tables), cross-check them with an independent brute force or an exhaustive run when it is cheap.
  - Record discrepancies "for the authors".
  - If a requested instance cannot exist: search for it, report how large the search was, and offer a labelled illustration instead.
- **2. Story, identity and choreography** (`references/02`, `references/14`).
  - Acts: challenge → idea → inside (the centrepiece) → impact (scale or coverage → performance vs the paper's baselines → trade-off, with the headline replay) → title.
  - Write a second-by-second storyboard with a **shot** column.
  - Write the film plan's **shot list** (`beat_keys` rows), **linkage map** (finding → anchor → panel address) and **peaks table** (references/15). The timing constants in `film.py` are the timing sheet; the peaks are a `PeakPlan` in `film.py`, exported to `peaks.json`.
- **3. Engine** (`references/03`, `scripts/engine.py`, `scene_kit.py`, `motion_kit.py`, `viz_kit.py`).
  - pycairo in a 1920×1080 design space; `draw(cv, t)` is pure; call `begin_frame()` first and flush `OVERLAY` last.
  - Overlays are deferred; cameras are keyframed (`beat_keys`, `lagged`); the stage camera is a look-at camera.
  - Scenes are data-driven, with asserts.
  - Motion blur only on fast moves.
  - Build the centrepiece from `examples/motion_kit_demo` and the peaks from `examples/peak_demo`; pass K3b before building the rest.
  - Signature breaks that change the whole raster (night, spot) go in the film's `post(rgb, t)` hook, driven by `PLAN.signature_level(t, name)`.
- **4. Narration and retime** (`references/04`, `scripts/narration/`, `scripts/edl.py`).
  - `script.py` holds `sub` / `tts` / `gap` and a `SPOKEN` table.
  - Cast the voice by ASR WER, pace and pitch range (default: Kokoro `af_heart` at 0.9).
  - Synthesize line by line; align with sherpa-onnx.
  - Retime with the EDL: segments with slopes, word anchors, an overlap check. Give mechanism beats their 4–7 s.
- **5. Audio** (`references/05`, `scripts/audio/`).
  - Procedural score and SFX, cued from `film.CUES`. Each peak: `riser` → `Track.duck` (pre-hit silence) → `hit` on the reveal. Export the reveal cue times to `cues.json` for `wow_audit.py`.
  - Duck under speech. Master to −16 LUFS and ≤ −1.2 dBTP. Export stems.
- **6–7. Subtitles, render, deliver** (`references/04`, `references/06`).
  - During the loop: a 1080p30 review cut with narration, mastered mix and SRT each round, into `rounds/rNN/deliverable/`. After approval: the full deliverables below, into `deliver/`.
  - Cues by spoken-word count.
  - Chunked, resumable 4K60 render. Choose JOBS from free RAM: OOM kills are silent.
  - Assemble with `-t $DUR`, never `-shortest`: master `.mov`, 4K and 1080p MP4s, SRT, stems.
  - Docs zip, and a source zip whose README covers requirements, models, reproduce commands and how to edit.
- **8. QA** (`references/07`, `references/14 §6`, `references/19`).
  - Generator: readability, motion and linkage audits; in-mix ASR; SRT vs the delivered audio; loudness of every file.
  - Reviewer: every round of the loop, then one delivery check on the delivered files and the figures (references/18 §8). Each finding ends fixed, closed by ruling, or open with a reason.
- **9. Scientific audit**, on request (`references/08`, `references/18 §10`).
  - A fresh reviewer audits the delivered file from `review_pack.py` (frames, stills, transcript) and the paper, and writes the evidence table with classes. It changes nothing.
  - If the user wants the corrections made, a generator polishes the wording from that review, accuracy first, keeping unchanged lines byte-identical and logging every change.
  - A fresh reviewer runs Pass 2 on the new render.
- **10. Slide figures** (`references/09`, `scripts/figures/`, `scripts/viz_kit.py`, `examples/gallery/`).
  - Load the film unmodified: in-memory patches (each asserted), HUD functions replaced by no-ops.
  - Build the purpose-built compositions and the step sequences.
  - Export PNG (3×, 300 dpi tag), SVG and PDF, then verify them.
  - Check `pdffonts`: cairo can resolve "Inter" to Medium, so use a renamed "Inter Regular" (`scripts/figures/setup_fonts.py`).
  - Write a README giving the sources, data values, the omitted legend and the caveats.

## 6. Final report

Keep it short:
- what was made;
- how it was verified, naming the actual runs (including the motion, linkage and peak audit numbers);
- the peaks, one line each, and the signature breaks used (≤ 2) as declared C2 exceptions;
- the loop: rounds run, human rounds, findings opened and closed by severity, disputes and rulings, requests and what was unavailable;
- limitations and illustrative elements;
- one natural next step.

Send the files. Do not recap the steps.

## Appendix: quality bar (summary; full version in references/00; use this when references/ is absent)

**A. Science**
- A1: every number is in the ledger with source, unit and conditions.
- A2: every count or average states its scope.
- A3: the paper's distinctions are kept.
- A4: comparatives name the metric; when speech rounds, the exact value is on screen.
- A5: the trade-offs the paper reports appear next to the headline.
- A6: each mechanism, rule or stage is its own case, with per-case counts, zeros included.
- A7: provenance tags are exact.
- A8: no unlabelled conceptual visuals.
- A9: structures are asserted against the paper; un-rerunnable results are typed or marked "approx.".

**B. Pacing**
- B1: readability budgets met (≥ 2.5 / 3–4 / 4–7 s).
- B2: one worked example carries the film; the walk instance is small enough to push in on.
- B3: anticipation → action → consequence → hold, one change at a time.
- B4: each key word lands while its label is visible.
- B5: no caption band, and no fact lost to it.
- B6: no collisions, clipping or drift in any frame.
- B7: the opening moves within 3 s.
- B8: runtime within target, or the deviation stated.

**C. Craft**
- C1: one semantic palette; persistent markers.
- C2: white identity with flat tints, except ≤ 2 declared signature breaks (W4).
- C3: alpha-over dense charts.
- C4: slope 1 for data timing.
- C5: no decorative motion (and no stillness: see G).

**G. Motion and camera** (`motion_audit.py` → `gate.py --motion`)
- G1: static seconds ≤ 25 %.
- G2: no static run > 3 s outside declared holds.
- G3: camera motion ≥ 30 % of seconds, ≥ 40 % in the centrepiece; a push-in and a pull-back per mechanism beat; zoom ≥ 2× in the centrepiece.
- G4: mean per-second change ≥ 2 %.
- G5: every motion has a meaning (references/14 §2).

**L. Linkage** (`linkage_audit.py`)
- L1: every finding is pinned to its referent (`callout_at`); only HUD readouts float.
- L2: findings state the instance with values.
- L3: contradictions show both facts at once, with ≠.
- L4: the method's state is a fixed-address panel, tethered to the scene on each write.
- L5: the full candidate space is visible (ghost / live / pruned).
- L6: a breadcrumb (and a search-tree PiP where the method branches).

**W. Peaks** (`wow_audit.py` → `gate.py --wow`; references/15)
- W1: 3–6 peaks, ≥ 1 concept and ≥ 1 result, ≥ 8 s apart; the first by max(20 s, 20 % of the runtime).
- W2: each reveal is the biggest change of its peak (≥ 2.5× the setup median, ≥ 4 % of the frame).
- W3: one change at a time during the hold.
- W4: ≤ 2 signature breaks, each ≤ 6 s, inside a peak; no undeclared dark-stage second.
- W5: a sound cue within 80 ms of each reveal; hits only in peaks.
- W6: the key word spoken within 0.35 s of the reveal.
- W7: every peak names a ledger claim; a result peak shows its trade-off within 12 s.

**R. Argument and data** (`argument_audit.py` → `gate.py --arg`; references/16)
- R1: comparisons and ablations name the metric and what is held fixed (ablations: what is removed), on screen.
- R2: every baseline, ablation and term is defined on screen before its first comparative use.
- R3: every ablation is preceded by the doubt it answers; every doubt is answered by later data or acknowledged.
- R4: every aggregate shows its spread (range, wins, n).
- R5: mechanism beats about data show computed, asserted element-level contents.
- R6: baselines and ablations never wear the method's colour.
- R7: the domain model is validated against the paper's worked examples, and every data mechanism is drawn from it.
- R8: recurring concepts use one canonical glyph (registered, used ≥ 3 times).
- Look at every figure and every peak frame as an image: no text over text, no leader or wire through a label, nothing outside its container (lint cannot see overlaps).
- **Coverage and economy (R9–R11):** every paper mechanism has a beat or a reasoned omission (a result never appears without its mechanism); each claim gets one primary visual (later beats recall the glyph only to add a fact); every beat names the claim it serves, and the runtime target is met by cutting unneeded detail, never by faster speech (references/16 §3b).
- **Frame sweep at K4 and before the final render:** render 1080p stills every 3 s across the whole film, plus every scene boundary ±0.4 s, and inspect them as 2×2 sheets. Check: text over text, leaders or wires through labels, wire direction and endpoints (port tip → actual consumer), leftovers from the previous scene, two scenes cross-fading in the same screen area (sequence them: out, then in), callouts redundant with a label already under the element (drop them).

**D. Sound and delivery**
- D1: no stretched or overlapping speech.
- D2: −16 ± 0.5 LUFS and ≤ −1 dBTP on every encoded file.
- D3: ≤ 1% ASR difference in the mix.
- D4: SRT timed by spoken words and matching the delivered audio.
- D5: video = audio = EDL duration.
- D6: licences documented; stems delivered.

**E. Figures**
- E1: final state only.
- E2: composed for the slide (≈ 2.0–2.6:1, no empty quadrants).
- E3: text ≥ 9 pt at 12 in width.
- E4: one verified typeface.
- E5: text policy applied.
- E6: step sequences share one camera and one crop, with the key table enlarged.
- E7: every requested case covered; impossible ones as labelled illustrations.
- E8: PNG, SVG and PDF all verified.
- E9: README with sources, data, legend and caveats.

**F. Honesty**
- Every "verified" names its run.
- Reviews say who did them: the independent reviewer agent (fresh context, inputs listed), the user on human rounds; the generator's gate runs are self-checks.
- Deviations are stated.