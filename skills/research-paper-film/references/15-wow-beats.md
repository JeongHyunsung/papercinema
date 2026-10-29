# 15: Peaks: designed "wow" moments that stay faithful (gates W1–W7)

A film can be accurate (A), legible (B), alive (G) and linked (L), and still leave nothing behind. The viewer understood every beat but remembers no moment. References 02, 11 and 14 remove motion that has no meaning. This reference adds the opposite discipline: **a few planned moments where meaning, picture, camera and sound land together, hard enough to be remembered and retold.**

The craft rule is the same as everywhere else in this skill: **drama is earned by the content, never added to it.** A peak dramatises a fact that is already in the claim ledger. It never makes a claim stronger than the paper does.

## 1. What a peak is

A peak is one moment per key idea or result, built in four phases. Every peak is written into the film plan (`templates/film_plan.md`, Peaks table) and into code as `peak_kit.Peak`.

| Phase | Duration | What happens | Tools |
|---|---|---|---|
| Setup | ≥ 1.5 s | Establish the expectation: the context, the question, "what would you expect?". The camera settles on the referent. | `beat_keys`, `focus` |
| Tension | 0.5–2.5 s (end of setup) | Something accumulates: a slow push, a rising sound, a held breath before the change. Non-participants dim a little more. | `breath()`, `riser()`, `Track.duck()` |
| Reveal | ≤ 0.6 s | **One** change, the biggest of the peak, on one frame-accurate time. The sound hit and the spoken key word land on it. | the device (§3), `hit()` |
| Hold | ≥ 2.5 s (B1) | Quiet. The consequence is readable, the camera drifts, nothing else competes. For a result, the trade-off follows within 12 s (A5). | `callout_at`, drift |

The reveal is a single, legible change: a space lighting up, a cascade of prunes, a bar landing on its exact value, two tangled wires becoming one. If the reveal needs a caption to be understood, it is not a reveal yet.

## 2. How many, and where

- **3–6 peaks per film** (about one per 25–40 s). More and they stop being peaks; fewer and the film is flat.
- **At least one concept peak** (Act II/III: the idea or mechanism) **and one result peak** (Act IV).
- **The first peak lands by max(20 s, 20 % of the runtime)**: the hook (Act I's problem made visible).
- **Peaks are ≥ 8 s apart.** The quiet between peaks is what makes them peaks.
- Typical shape of a 2-minute film: hook (Act I) → concept (Act II) → mechanism or evidence (Act III) → twist (optional) → result (Act IV).

| Kind | Job | Typical act |
|---|---|---|
| hook | the problem or the size of the space, felt | I |
| concept | the one new idea, as a visible cause → effect | II |
| evidence | an invariant or a check that holds at scale | III |
| twist | an expectation reversed (an ablation, a counter-intuitive baseline) | III / IV |
| result | the headline number with its conditions and its trade-off | IV |

## 3. Devices (fidelity-safe; `scripts/peak_kit.py`)

Each device is a *meaning*, not an effect. Pick the one that matches what the paper's claim **is**.

| Device | Meaning | Implementation | Fidelity rule |
|---|---|---|---|
| scale_reveal | "this is how big it is" | close on one item → `log_zoom` out ≥ 3×, then the full space lights up in a ripple from that item | count shown is exact or labelled "conceptual"; cell order labelled arbitrary (A8) |
| cascade | "one decision causes many effects" | `ripple_order` from the decision, `cascade` progress per item, `count_at` counter | every item that changes is a real consequence in the re-implementation; the count is exact |
| collapse | "many become one" (modes, configurations, paths) | `collapse` positions to one target, colours merge | before/after counts are the paper's numbers |
| invariant_counter | "it never fails" | a fast counter of checks next to a counter of failures that stays at 0 | both counters are real (N comparisons from the paper, 0 from the paper) |
| race | "same budget, it gets there first" | best-so-far curves drawn at slope 1 against a shared clock | only with real anytime data; label "supplementary" if not in the paper |
| reversal | "you'd expect X, it's the opposite" | show the expectation first (ghosted prediction), then the measured value | the expectation is labelled as an expectation, not data |
| before_after | "the same thing, without and with" | `wipe` across a split | identical framing and scales on both sides |
| number_land | "this is the number" | value eases to its exact final value with `land` (no overshoot), bar follows | before landing, draw an empty outline ("?"), never a placeholder value such as 1.00 for the method; the number appears only once the bar has landed; no frame shows a value beyond it |

**Never:** an overshooting bar or counter; a truncated axis without a label; a log axis that is not labelled; a slow-motion data animation (C4 still holds: data animations run at slope 1 or say their rate); a superlative the paper does not use ("revolutionary", "massive"); a peak on an "approx." number without that label on screen.

## 4. Signature breaks (style departures): at most 2 per film

The white identity (C2) stays the default for every second of the film except **at most two** signature breaks. Each break must:

- belong to a declared peak (`Peak(signature=…)`), inside that peak's setup→hold window;
- last ≤ 6 s, with eased entry and exit (`PeakPlan.signature_level`);
- point at the referent: the break is about one element, never decoration;
- be listed in the film plan and in the delivery report as a deliberate C2 exception.

| Signature | What it does | Use for | Implementation |
|---|---|---|---|
| night | the whole stage flips to a dark tone, hues preserved | the concept peak: the moment the idea "switches on" | `night_rgb(rgb, d)` in the film's `post(rgb, t)` hook |
| spot | everything outside one referent darkens | a single element that the whole argument turns on | `spotlight_rgb(rgb, centre, r, d)` |
| accent | a soft light halo behind the headline element | the result peak | `accent_glow(cv, p, r, col, a)` |
| flood | the frame floods with a flat semantic tint from the referent | a decisive verdict (a bound, a proof, a removed class) | `flood(cv, col, a, origin, prog)` |

`PeakPlan` refuses a third signature, one longer than 6 s, and one outside its peak. `wow_audit.py` also fails any dark-stage second in the delivered video that is not inside a declared night/spot window.

## 5. Sound for peaks (references/05)

- **Riser into the reveal** (`riser(d)` placed at `t_reveal − d`, d = 1.5–2.5 s), at most one per peak.
- **Pre-hit silence**: duck the score 250–400 ms before the reveal (`Track.duck`). The breath is what makes the hit hit.
- **Hit on the reveal frame** (`hit()`: sub thump + chord stab + bell partial), cued from the same constant the picture uses (`film.CUES`), mapped through `edl.inv` when the picture is retimed.
- **No hits outside peaks.** Ticks, thumps and whooshes keep their small meanings elsewhere; the hit is reserved.
- Narration: write the line so the **key word** of the peak is spoken on the reveal (W6). If it cannot be, put the reveal in a narration gap and land the word right after the hit.

## 6. Picking peaks for a paper (all archetypes)

Look for these in the claim ledger, in this order:

1. **The size of the problem** that the paper makes smaller (a design space, a search, a latency tail, an error rate) → hook, scale_reveal.
2. **The one cause → many effects** at the heart of the method (a rule, an invariant, a shared abstraction, a schedule) → concept, cascade or collapse.
3. **A check that holds every time** (N comparisons, 0 violations; a proof covering all cases) → evidence, invariant_counter.
4. **An expectation the paper reverses** (an ablated variant that does worse than an older baseline; a smaller model winning; a simpler rule that covers more cases) → twist, reversal.
5. **The headline number** (geomean, with conditions) → result, number_land, followed by the trade-off.

Archetype hints are in references/13 (the "Peak candidates" row of each archetype).

## 7. Checks

- **K2 Story:** the Peaks table in the film plan (kind, device, claim id, key word, signature or none). The narration line for each peak contains its key word.
- **K3b Choreography:** a 640 px test render of the strongest peak (setup → hold, with its sound), run through `wow_audit.py --peaks … --video … --cues …`.
- **K4 Cut:** `wow_audit.py` on the full preview with `--placement` and `--ledger`, then `gate.py --wow wow.json`.
- **Peak check** (the independent reviewer, references/19 §2.6; the generator may run it on its own test renders): watch only the peaks (each from t_setup − 2 s to t_hold) with sound. Does each one land without the rest of the film? A day later, would a viewer retell it in one sentence? Is any peak louder than the claim it carries?

## 8. Lessons from the first production with peaks

- **Big camera moves belong to the reveal, not the setup.** A 3 s dive-out during the setup made the setup median as large as the reveal (W2 1.2×). A held shot on the single candidate, then a 0.8 s log-zoom snap-out on the key word, measured 30.8× and reads as the moment.
- **Small data changes need a camera beat.** Bars rising on a chart changed 0.9 % of the frame; a push-in onto the most extreme bar at the reveal made it 16.8× (W2) without touching the data.
- **End the signature after the hold.** A night stage fading out inside the hold is the hold's biggest change (W3); end it in the 0.8 s after t_hold.
- **No placeholder values.** A bar animating down from "1.000" for the method shows a value the paper never reports (W7/A9); show an empty outline until it lands.

## 9. Calibration

`examples/peak_demo` (30 s, toy data): 3 peaks (hook / concept / result), 2 signature breaks (night, accent). Measured at 640 px / 30 fps: reveal spikes 20.1 %, 28.9 %, 12.0 % of the frame vs setup medians 0.03–0.22 %; holds ≤ 0.7 %; all cues 0 ms from the reveals; G1–G4 and L1 also pass (static 0 %, camera 43 %). The negative test (`examples/peak_demo/neg_test.py`: undeclared night, a reveal moved to a quiet second, a claim id missing from the ledger) fails W2, W4, W5 and W7 as intended. W6 needs narration and is not exercised by the demo.
