# Postmortem: a fresh rebuild that passed every gate and still fell short

**What was compared.** The case-study film v4 (`BFlex_DAC2026_film_v4_4K60.mp4`, 116 s, made over five iterations with the authors) was compared with a rebuild made from scratch with this skill (v2, before this revision) from the paper alone (128.6 s, delivered 2026-10-26).

**What the rebuild got right.**
- It re-implemented the method and reproduced Table 1 exactly: 18 and 568,832,054.
- It replayed the Fig. 4 walkthrough and validated all 20 FSMs of Fig. 8f.
- It found a typo in Table 2.
- It passed every gate the skill then had: B1 readability, D1–D5 delivery, E1–E9 figures.

**What the author still saw immediately** (user feedback, 2026-10-27):
- weaker animation dynamics;
- a weaker, mostly static camera;
- concepts not marked precisely and not tied closely to what they describe.

The rest of this document measures those gaps and traces each one to its cause.

![side by side](compare_v4_vs_fresh.png)

## 1. Measured gap

`scripts/motion_audit.py`, 10 fps, 320 × 180:

| | v4 | rebuild |
|---|---|---|
| static seconds (< 0.3 % of pixels change) | **17 %** | **50 %** |
| longest static run | 2 s | 7 s |
| seconds with camera motion | **55 %** | **10 %** |
| camera-motion runs | 18 | 8 |
| mean per-second change | 4.3 % | 0.8 % (5× less) |
| Act III (centrepiece) camera seconds | **57 %** | **0 %** |
| Act III mean change | 5.7 % | 0.6 % (9× less) |

Source inventory:

| craft element | v4 (`examples/bflex/src/film.py`) | rebuild |
|---|---|---|
| camera systems | 7 (waveform follow, cube, stage, tree, unit dive, FF1 cube, race) | 1 stage camera + flat scenes |
| stage camera keyframes | 18 (distance 330–1030, ≈ 3× zoom) | 3 (one tilt, fixed distance) |
| world-anchored annotations (`chip`/`bb_text` at a world point) | 18 | 2 |
| node → table tethers | per write | 1 (one conflict) |
| focus (dimming) windows | 2 | 0 |
| tokens travelling paths | 3 | 0 |
| candidate space shown | pills with every state (ghost/live/pruned) | only reached nodes |
| state table | fixed 16-row address table, `·` for unknown | rows appended as written |
| search-tree PiP / step breadcrumb | yes / yes | no / step counter only |

`linkage_audit.py` on the rebuild, Acts II–III: **24 findings unanchored**. For example, "entry conflict × 6: these settling paths need δ(01, 011) ≠ 011" floated above the graph. v4 instead pinned "earlier edge fixed δ(11,11) = 11" and "path needs δ(11,11) = 10" to the slot, with a ≠ and a tether to the struck table row.

## 2. Why: causes in the skill (fixed in this revision)

1. **The quality bar was one-sided.**
   - Every gate measured legibility, science or delivery: B1, A1–A9, D1–D5, E1–E9.
   - The only motion rules were prohibitions: C5 "no decorative motion", "camera moves follow events", B3 "one change at a time", long readability holds.
   - A film with no motion satisfies all of them, so the gates passed a slide show.
   - *Fix:* gates G1–G4 (`motion_audit.py` + `gate.py --motion`) and L1 (`linkage_audit.py`), calibrated on v4. The principle "restraint is not stillness" goes into SKILL.md and references/14.
2. **The craft existed only inside example code.**
   - Pills, the lagged follow camera, the 18-key stage camera, focus windows, tethers, the fixed-address table, tracers, breadcrumbs and the PiP tree lived in a 2,300-line `examples/bflex/src/film.py`.
   - `scene_kit.py` exposed only overlay, kfv, StageCam and chips.
   - A builder told to start fresh re-derived minimal versions under time pressure.
   - *Fix:* `scripts/motion_kit.py` (`beat_keys`, `lagged`, `View2`, `focus`, `tracer`, `proposal`, `pulse`, `callout_at`, `tether`, `AddressTable`, `pill`, `slot_node`, `stable_loop`, `breadcrumb`).
   - `examples/motion_kit_demo` uses them all and passes G1–G4 and L1.
3. **No camera grammar.**
   - "Camera moves follow events" says when a move is allowed, not that each beat needs one, nor which.
   - *Fix:* the shot table in references/14 (establish, follow, push-in, hold-with-drift, pull-back, reveal, orbit), with minimums per beat and per act.
4. **No linkage rule.**
   - The bar asked that facts "live in the scene or in the narration". A chip floating near the graph satisfied that.
   - *Fix:* the linkage rules (concrete values, pinned with a leader, both sides of a contradiction, rule on the reference element, fixed-address state panels, the full candidate space shown, breadcrumb/PiP), enforced by L1.
5. **Worked-example guidance allowed a dense walk.**
   - The single question "which example?" mixed two things: the instance to *walk* through the mechanism, and the headline design to *replay*.
   - The rebuild walked FF1's 3-bit search: 8 states, up to 49 jobs per step, 16 steps. The density forced a wide, static camera and small chips.
   - v4 walked the paper's 2-bit Fig. 4 example (2 slots per pill, 5 steps) and replayed FF1 on the cube in Act IV.
   - *Fix:* SKILL.md §1 asks these as two questions, and references/13 + 14 §5 make "walk the paper's smallest running example; replay the headline design" the default.
6. **The checkpoints could not see motion.**
   - K3 judged stills; K4 judged a 1-fps contact sheet and dense strips. A static film looks fine in all of them.
   - *Fix:*
     - K3b "Choreography" (shot list + linkage map before engine work);
     - K4 runs the motion and linkage audits;
     - K4 requires one full viewing at 1× with sound, logging every second in which nothing happens;
     - the motion-designer critic now has a checklist.

## 3. Why: execution choices in the rebuild

- **Picture authored on the film clock** (identity EDL) around 0.6 s narration gaps. Mechanism beats had no room for anticipation and action, so holds took the time. *Lesson:* give each mechanism beat its choreography time (4–7 s), then fit the narration; lengthen the gap before the beat rather than shrinking the beat.
- **Effort went to verification and readability fixes, none to choreography.** The verification was worth it (it found a paper typo and reproduced Table 1). But no step in the process asked "where does the camera go here?".
- **"Start from scratch" was read as "do not look at the example".** The user's choice meant: do not reuse the old content. It did not mean: ignore the craft. This revision puts the craft into `motion_kit.py` and references/14, so a fresh build no longer depends on reading example code.

## 4. What did not change

- The science, honesty and delivery rules (A, B, D, E, F) stand. The rebuild's verification depth stays the bar.
- Motion must still carry meaning: G1–G4 measure quantity; references/14 §2 lists the meanings motion may carry.
