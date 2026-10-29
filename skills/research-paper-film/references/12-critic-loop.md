# 12: The generator's checkpoints and pre-handoff gates

Since v7 the film is judged by an independent reviewer and, every K rounds, by the user (references/18, 19). The generator does not review its own film by imagining critics. What it does is mechanical and cheap: it checks its pre-video work at K1–K3b, and before **every** handoff it runs the cut's gates (K4, K5) and fixes every FAIL it can. (K1–K7 name checkpoints; they are unrelated to K, the human-review period.) Reviewer rounds are then spent on what gates cannot see. The quality bar is references/00.

## Checkpoints (render small, check, fix, then go big)

| Checkpoint | Artifact you inspect | Gates | Only then |
|---|---|---|---|
| K1: Facts | Claim ledger, `scene_data.json` asserts | A1, A2, A9 | storyboard |
| K2: Story | Storyboard + script, read aloud (word count ÷ 2.6 w/s ≈ speech time), walk instance vs replay, peaks table (references/15), argument map (claim → doubts → answer) and data views (beat → containers → computed contents) | B2, B8, A3–A5, W1, W4 (planned), W7, R1–R5 (planned) | engine work |
| K3: Look | 6–10 stills at 1280 px, one per act and per mechanism beat | C1–C5, B6, L3–L6 | choreography |
| K3b: Choreography | Shot list (every beat: camera move, motions, hold) + linkage map (every finding: anchor element, values, table address) in the film plan; a 3–5 s 640 px test render of the centrepiece beat; a 640 px test render of the strongest peak with its sound through `wow_audit.py` | G3, G5, L1–L5, W2, W3, W5 | full scenes |
| K4: Cut (before every handoff) | The whole film as the 1080p30 review cut, with narration and mix + readability audit + EDL check + `motion_audit.py` + `linkage_audit.py` + `wow_audit.py` + `argument_audit.py` | B1, B3–B7, D1, G1–G4, L1, W1–W7, R1–R11 | K5, then handoff to the reviewer |
| K5: Sound (before every handoff) | `mix.py` readout, `mix_check.py`, loudness of the review cut | D2, D3 | handoff; 4K only after the user approves |
| K6: Deliverables (after approval) | Encoded files: ffprobe, ebur128, srt_check, contact sheet of the 4K file | D2, D4, D5 | report |
| K7: Figures (after approval) | Contact sheet of all figures + `lint_figs.py` + `verify_vectors.py` | E1–E9 | report |

Run `scripts/gate.py` at K4–K6 (with `--motion motion.json --centre <act>` and `--wow wow.json`), `scripts/linkage_audit.py` at K4, and `scripts/figures/lint_figs.py` at K7. They print PASS/FAIL per gate. Stills and contact sheets cannot show motion: a static film looks fine in both. Only the motion audit and a real-speed viewing can.

## Before every handoff

- Run `gate.py --motion --wow --arg` on the review cut, `linkage_audit.py`, the readability audit, the EDL check, `mix_check.py` and the cut's loudness (−16 ± 0.5 LUFS, ≤ −1 dBTP).
- Fix every FAIL you can, re-render the touched chunks, re-run. If one cannot be fixed without breaking a non-negotiable, name it in the gate line and raise it as a request to the user (references/18 §5); never explain it to the reviewer.
- Hand off only `rounds/rNN/deliverable/film.mp4` and `film.srt`. No notes, no change list. Reply `done`, the gate line, and requests.

## Acting on a review

- Read the previous round's `review.md`, `exchange/rulings.md` and `exchange/generator.md`. Nothing else from outside `gen/`.
- Every BLOCKING, MAJOR and MINOR finding gets an outcome in `gen/STATE.md`: fixed (to its "Done when") or disputed (a request to the user citing the paper or brief). Nothing is skipped silently. Findings marked "pending Q…" need no action yet.
- Findings are symptoms; you choose the cure. Fidelity (SKILL.md §2) outranks any reviewer or human request.
- A TASTE finding never overrides the brief and may be declined ("declined: taste") unless it is tagged `source: human`; a `source: human` finding is the user's voice and is MAJOR by default.

## What the user sees, and when

- Every K-th round and every ship candidate: the review cut (the orchestrator sends it; comments go to the reviewer, and reach you only through `review.md`).
- Any request either role makes.
- After approval and the delivery check: the deliverables, a short report (what, how verified, the loop summary, limitations) and one natural next step.

## Intake

The orchestrator asks the intake questions once (SKILL.md §1, including K and the maximum rounds) and writes the answers to `gen/BRIEF.md`. The generator never asks the user directly: anything it needs goes in a request (references/18 §5).

## Frame sweep (generator before a handoff; the reviewer every round via `review_pack.py`)
1080p stills every 3 s and at every scene boundary ±0.4 s, as 2×2 sheets, read one by one. Look for: overlaps (text/text, wire/label, leader/label), wire direction and endpoints, leftovers of the previous scene, in-place cross-fades, redundant chips. Fix, re-sweep the touched spans, then render.

## Economy check (generator at K2; the reviewer judges the cut, references/19 §2.4)
Read the beat list against the claim list. For each beat ask: which claim or definition needs it? Is the same point already made by a stronger figure? Would a first-time viewer miss it if cut? Mark redundant re-draws, ornamental detail and worked cases the rule's condition already covers; cut them before touching speech rate. Then check coverage the other way: every mechanism in the paper's method section has a beat or a reasoned omission.
