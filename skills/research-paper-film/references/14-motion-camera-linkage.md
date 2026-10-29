# 14: Motion, camera and linkage (the half of the quality bar that stills cannot show)

A film can pass every legibility, science and delivery gate and still be a slide show. A fresh rebuild of the case study did exactly that: it was scientifically stronger than the original (it reproduced Table 1 exactly) but had these problems:
- **static 50 % of the time**, with a 7-second stretch where nothing moved;
- the camera moving in **10 %** of seconds, and in **0 %** of the centrepiece act;
- **24 findings** floating unanchored in Acts II–III.

The case-study film v4 measured 17 %, 2 s and 55 %. Its centrepiece act had the camera moving in 57 % of seconds, and its findings were pinned to what they describe. This reference turns the difference into rules, components (`scripts/motion_kit.py`) and gates (`scripts/motion_audit.py`, `scripts/linkage_audit.py`, gate.py G1–G4 and L1).

**Restraint is not stillness.** References 02 and 11 ban decorative motion: particles, spectacle camera moves, glow. That rule removes motion *without meaning*. It does not license a picture that waits. Every second should carry a meaningful change: a camera move toward the event, a token travelling a path, a value being written, a branch being cut.

**Restraint is not flatness either.** Even motion with meaning can stay at one level for two minutes. References 15 adds 3–6 planned peaks, where the meaningful change is staged hardest, and a budget of 2 style breaks per film.

## 1. Camera grammar

Every scene has a camera. A flat 2-D scene gets `View2`, a pan/zoom; a stage gets `StageCam`. Each camera is driven by keyframes, never left at a constant.

| Shot | When | Typical move (case study) |
|---|---|---|
| Establish | a new representation appears | wide, slow drift (≤ 3 % of the frame per second) |
| Follow | a signal or token moves along a long structure (waveform, pipeline, request path) | `lagged()` follow of the moving head; the scene pans under it |
| Push-in | a mechanism beat starts | distance × 0.45–0.6 over 0.5–0.8 s, ease in-out, target = the node/tile in play |
| Hold | the finding is read | keep the close framing but **drift** 3–5 % toward the next framing (`beat_keys(drift=…)`), never a dead freeze |
| Pull-back | the consequence is placed in context | back to wide over 0.5–0.8 s; the table/PiP updates during the move |
| Reveal / dive | change of scale (one instance → the whole space, block → histogram) | zoom ≥ 3× with a log-interpolated distance; motion blur on the fastest part |
| Orbit | a 3-D object must be read (cube, stack) | yaw 10–25° over the beat, not continuous spin |

Minimums (gate G3, measured by `motion_audit.py`):
- camera motion in **≥ 30 %** of the film's seconds;
- **≥ 40 %** of the centrepiece act's seconds (the case study had 57 %);
- at least **one push-in and one pull-back per mechanism beat**;
- a **zoom range ≥ 2×** inside the centrepiece act (the case study ran 330–1030, about 3×).

Implementation:
- `beat_keys(t0, wide, [(t_in, t_out, close), …])` generates push / hold-with-drift / pull keys from the beat list in the film plan.
- Put the camera's distance at index 3 and log-interpolate it (`logi=(3,)`).
- Keep a stage shifted left (`ox`) while a side panel is on screen.

## 2. Motion vocabulary (meaningful motion only)

| Motion | Meaning | Component |
|---|---|---|
| Dashed arc drawing from source to candidate | "this destination is being considered" | `proposal()` |
| Token travelling a path, with a trail | "the state settles along this path" / "the request travels here" | `tracer()` + `path_point()` |
| One expanding ring | "this was just written / decided" | `pulse()` |
| Slot changing from dashed to solid | "this state is now instantiated" | `slot_node(state=…)` |
| Element turning coral, dropping and fading | "pruned" | slot `pruned` + fade |
| Value appearing in a fixed table cell, tinted, then settling | "δ entry written / inferred" | `AddressTable` |
| Strike across a cell | "this entry conflicts" | `AddressTable` style `conflict` |
| Non-participants dimming to ≈ 0.3 | "look here" | `focus(t, windows, key)` |
| Counter that only moves when cells move | "the count is real" | exact counters |
| Morph between representations (square → cube, dots → histogram cells) | "same objects, new view" | interpolate positions; never cut |

Minimums (G1, G2, G4):
- **static seconds ≤ 25 %**. A static second is one in which fewer than 0.3 % of pixels change.
- **No static run longer than 3 s**, except declared holds such as the title card (`--holds`).
- **Mean per-second change ≥ 2 %.**

A held, readable label does not make a second static: the camera drifts, a tracer moves, a ring pulses. Readability (B1) and motion (G1–G4) are satisfied together. Labels ride with their objects as billboards, so they stay legible while the camera moves.

## 3. Linkage: every finding points at what it is about

The original's Act III (see the user-supplied frame: "earlier edge fixed δ(11,11) = 11" vs "path needs δ(11,11) = 10", a ≠, a red tether to the table row, a strike) shows the standard:

1. **Concrete, not generic.**
   - Write the instance with its values: "path needs δ(11,11) = 10", "infer δ(11,01) = 11", "CK rises with D = 1 → Q must become 1", "s = 11 · Q = ¬s1 = 0 · stable: δ(01,11) = 11".
   - Do not write a category ("entry conflict × 6") unless it sits next to the instance.
2. **Pinned.** A finding is drawn with `callout_at(anchor, offset, …)`: a chip, a leader line, and a dot on its referent (node, edge, slot, bar). It is placed ≤ 220 px from the referent. Its leader must not cross text: put the chip where the straight leader runs through empty space (`align="l"` places the chip by its left edge beside the referent; a `\n` makes a 2-line chip for narrow gaps). Free-floating chips are allowed only for HUD readouts (step counter, breadcrumb, source tag), and those go in `linkage_audit.py --allow`.
3. **Both sides of a contradiction on screen at once.** The earlier fact (teal) and the needed fact (coral) are stacked, with ≠ between them, both pinned to the same entry.
4. **The rule lives on the reference element.** "CK falls → Q must stay 0" is written on the reference edge being matched, not in a caption.
5. **Fixed-address state panels.** The state the method builds (transition table, buffer, queue, register file) is shown with every address present from the start: unknown cells show `·`. Use `AddressTable`, not a list that grows by appending rows.
   - Every write, inference or conflict happens at its own address.
   - A `tether()` joins the scene element to that address while the event is shown. Route it with `via=[...]` waypoints along the gaps (or around the stage box) so it crosses no grid, label or legend; only the last leg curves into the table.
6. **The full space is visible, not only the visited part.** Above each reference node, a `pill()` holds all candidate states: ghost (dashed) until reached, live when instantiated, pruned when rejected. Self-loops (`stable_loop`) mark stable pairs. Pruning is only legible when the viewer can see what was pruned *from*.
7. **Where are we?** A `breadcrumb("STEP 3", "destination discovery · wrong output")` under the act label. Where the method branches, a search-tree PiP shows the current branch.

Gate L1 (`linkage_audit.py`) fails a finding that is shown unanchored for ≥ 0.6 s. A finding is any string with `=`, `≠`, `→`, `×`, `δ`, "pruned", "conflict", "wrong", "needs", "fixed", "infer", "settles" or "must".

## 4. Beat choreography template (one mechanism beat ≈ 4–7 s)

| t | camera | picture | text |
|---|---|---|---|
| −0.7 → 0 | push-in to the node in play | non-participants start dimming | breadcrumb changes |
| 0 → 0.8 | arrive, drift | proposals draw from the source (dashed) | the rule on the reference edge |
| 0.8 → 1.6 | drift | the rejected candidate turns coral and drops; the accepted one is traced by a token | pinned finding with values |
| 1.6 → 2.4 | drift | the table cell is written in place (tint, pulse); tether node → cell | "infer δ(…) = …" at the arc |
| 2.4 → hold | drift | hold until the readability budget is met (B1) | — |
| end → +0.7 | pull-back to wide | focus releases; the PiP tree adds the branch | — |

Narration-first still applies: the beat is retimed to the voice. Push-ins land on the key word: "pruned" is spoken as the candidate drops.

## 5. Choosing the instance that can be choreographed

The walk instance must be small enough that a push-in fills the frame with its states. **Walk the paper's own smallest running example** (case study: the 2-bit example of Fig. 4: 2 slots per pill, 5 steps, every rule fires). Show the headline design (FF1) as a **replay** in the impact act (its state dot moving on the cube, its waveform). Do not walk the headline design itself.

The fresh rebuild walked FF1's 3-bit search instead: 8 states per input, up to 49 jobs per step, 16 steps. The density forced a wide, static camera and tiny chips. Ask the user the two questions separately (SKILL.md §1, question 2).

## 6. Checks

- **K3b Choreography (before engine work).** Write the shot list and the linkage map in the film plan:
  - every beat with its camera move (`beat_keys` rows);
  - its motions;
  - every finding with its anchor and its table address.
- **K4.**
  - `motion_audit.py preview.mp4 --acts … --holds …` → `gate.py --motion motion.json --centre III`;
  - `linkage_audit.py film --from <Act II> --to <end of Act III>`;
  - **watch the preview once at 1× with sound**, and list every second where nothing happens.
- **Per-beat checks** (the generator while building; the independent reviewer applies the same questions to each cut, references/19 §2.6). For each beat, check:
  - Where is the camera going?
  - What moves?
  - Which element does each finding point at?
  - Can the viewer see the space the pruning removes things from?

## 7. Calibration data

| film | static % | longest static | camera % | camera moves | mean change % | centrepiece camera % | unanchored findings |
|---|---|---|---|---|---|---|---|
| case study v4 (116 s) | 17.1 | 2 s | 54.7 | 18 | 4.27 | 57.1 | — (built before the audit) |
| fresh rebuild (128.6 s) | 50.4 | 7 s | 10.1 | 8 | 0.83 | 0.0 | 24 |
| `examples/motion_kit_demo` (12 s) | 0.0 | 0 s | 75.0 | 3 | 3.01 | — | 0 |

Measured with `scripts/motion_audit.py` at 10 fps on 320 × 180 grayscale. The "camera %" detector also counts cuts and crossfades, so read it together with the shot list.
