# 13: CS/EE paper archetypes: what to show, and how to say it

Most CS/EE papers fit one archetype, or a mix of two. The archetype decides five things:

1. the **worked example** that carries the film;
2. the **mechanism beat**, i.e. the centrepiece of Act III;
3. the **result visual**;
4. the **conditions** every number must carry;
5. the **wording traps** the audit will catch.
6. the **peak candidates**: the moments worth staging as peaks (references/15).

Pick the archetype in Phase 0. Write the choice into the film plan (`templates/film_plan.md`). The figure components live in `scripts/viz_kit.py`; `examples/gallery/` has one figure per archetype.

## Universal structure (every archetype)

| Act | Job | Universal pattern |
|---|---|---|
| I. Challenge | Make the problem *visible* | One concrete failure or bottleneck, as evidence (a trace, a waveform, a profile, a counter-example). Then the size of the space or of the gap |
| II. Idea | The one new idea, as a mechanism | The paper's own representation (graph, dataflow, schedule, encoding), built from real data, with Act I's example replayed inside it |
| III. Inside | How it works | One branch or one tile or one request walked through every rule or stage, with the state (table, buffer, queue) beside it. Then accelerate to scale |
| IV. Impact | Verified results with conditions | Scale or coverage first, then performance on the paper's own baselines, then the reported **trade-off** |
| V. Title | Credit | Title, venue, DOI, authors as printed |

## Archetype table

### A. Algorithm / search / optimization

*Covers:* DSE, SAT/SMT, scheduling, synthesis, pruning, graph algorithms.

| Element | What to use |
|---|---|
| Worked example | The paper's running example, or the smallest instance your re-implementation solves, with a pruned branch per rule |
| Mechanism beat | Search tree or state graph growing over the **full candidate space** (pills with ghost slots); a **fixed-address** state table filled in place and tethered to the node on every write; each pruning or bounding rule firing as its own case, pinned with its values; camera push-in per rule; the per-rule breakdown, including zero counts |
| Result visual | Search space vs explored (block + lens); runtime vs baseline (bars, log axis); found solutions → selection → quality Pareto |
| Conditions | Search-space constraints, threads/cores, time limit, average of N runs, "extrapolated" |
| Wording traps | "all solutions" vs "all within the constrained space"; "optimal" only if proven; enumerated vs valid vs selected |
| Peak candidates | hook: one candidate → the whole space (scale_reveal); concept: one rule fires and a whole subtree is cut (cascade); evidence: N checks, 0 violations (invariant_counter); twist: the unconstrained search does worse (reversal); result: runtime or quality landing on the exact value (number_land) |

**viz_kit:** `graph`, `table_panel`, `unit_block` + `lens`, `unit_histogram`, `bars`, `scatter` + `pareto`.

### B. Hardware architecture / accelerator

*Covers:* dataflow, NPU/GPU features, memory hierarchy, NoC, PIM.

| Element | What to use |
|---|---|
| Worked example | One tile or layer moving through the dataflow (DRAM → buffer → PE array → output), with reuse made visible |
| Mechanism beat | Data movement on a block diagram (`wire` reveal with `p`); PE-array occupancy heat over time; a stall the design removes, shown on a `pipeline` chart |
| Result visual | Normalized speed-up and energy vs baselines per workload, plus the **geomean**; area and power breakdown; roofline if the paper uses one |
| Conditions | Simulated / RTL / FPGA / silicon; process node; frequency; precision; batch size; workloads and baselines exactly as in the paper; normalization point |
| Wording traps | "faster" (throughput? latency? at what batch?); "energy-efficient" (per op? per inference? at iso-area?); mean vs geomean; simulated results presented as measured; peak vs sustained |
| Peak candidates | hook: the data that has to move, at scale (scale_reveal); concept: the stall or the redundant transfer disappears across the whole PE array at once (cascade / before_after); many traffic patterns collapsing into one (collapse); result: geomean speed-up or energy landing (number_land), area next to it |

**viz_kit:** `block`, `wire`, `grid_array`, `pipeline`, `bars`, `lines`.

### C. Circuits / devices

*Covers:* digital cells, analog/mixed-signal, flip-flops, SRAM, I/O.

| Element | What to use |
|---|---|
| Worked example | The waveform or transfer behaviour that fails in prior work and works here; a state replay from the paper's table |
| Mechanism beat | Waveforms with numbered transitions; the state graph or schematic region that changes; a timing race at **slope 1** (physical time on a fixed scale, e.g. "20 ps per second of film") |
| Result visual | Delay / energy / area scatter with the Pareto front; corner or voltage sweeps (`lines`); a comparison table vs prior art |
| Conditions | Node, VDD, corner, temperature, load (e.g. FO4), activity factor, pre- vs post-layout, simulated vs measured, number of transistors |
| Wording traps | Schematic vs layout vs silicon; "faster" without naming the metric; hiding an energy or area cost |
| Peak candidates | hook: the failing waveform; concept: the race lost in prior work and won here, at slope 1 (before_after); evidence: every corner passes (invariant_counter); result: the point that moves onto the Pareto front (number_land), energy or area cost next to it |

**viz_kit:** `waveform`, `marker_row`, `graph`, `scatter`, `pareto`, `lines`, `table_panel`.

### D. Systems / networking / distributed / OS / databases

| Element | What to use |
|---|---|
| Worked example | One request (or transaction, or packet) traced through the components, with queues visible; the slow path in prior work vs the new path |
| Mechanism beat | Request flow on a block diagram; a queue building up and draining; a timeline (Gantt) of contention vs the new schedule |
| Result visual | Throughput–latency curves (p50/p99) with the knee; CDFs; time-breakdown bars; scaling with nodes or cores |
| Conditions | Hardware, cluster size, workload/trace, load level, percentile, warm-up, number of runs, error bars |
| Wording traps | Average vs tail latency; peak vs sustained throughput; a speed-up at one load point stated as general |
| Peak candidates | hook: the queue that builds up; concept: the new path drains it (before_after / collapse); twist: the tail, not the mean; result: p99 landing at the stated load (number_land), cost next to it |

**viz_kit:** `block`, `wire`, `pipeline` (timeline), `lines` + `vspan`, `bars`.

### E. ML / AI methods and ML systems

| Element | What to use |
|---|---|
| Worked example | One input traced through the model or pipeline; the failure mode of the baseline on a real example from the paper |
| Mechanism beat | Tensor shapes flowing through blocks; the changed component lit up (attention pattern, quantization grid, routing); a training or inference step |
| Result visual | Accuracy vs cost Pareto (FLOPs, latency, memory); ablation bars; scaling curves (log axes) |
| Conditions | Dataset and split, metric, model size, number of seeds (± std), hardware for latency, batch, precision, training budget |
| Wording traps | Best-of-N seeds as typical; SOTA claims beyond the paper's table; latency on unnamed hardware; "understands" or "reasons" |
| Peak candidates | hook: the baseline's failure on a real input; concept: the changed component lighting up across the tensor (cascade); twist: an ablation that reverses the expectation (reversal); result: the Pareto point landing (number_land) with seeds ± std |

**viz_kit:** `block`, `grid_array` (attention / quantization), `lines` (log), `scatter` + `pareto`, `bars`.

### F. Compilers / PL / verification / security

| Element | What to use |
|---|---|
| Worked example | A small program, IR snippet or attack trace from the paper; the transformation or proof step applied to it |
| Mechanism beat | AST/IR/CFG graph rewriting, one rule at a time; a lattice or abstract-state table filling; the attack path being blocked |
| Result visual | Speed-ups per benchmark with the geomean; bugs found and found-only-by-us; overhead distributions |
| Conditions | Benchmark suite and version, baseline compiler and flags, hardware, threat model |
| Wording traps | "sound" or "complete" only as proven; "secure" vs "mitigates under the threat model" |
| Peak candidates | hook: the attack path or the slow loop; concept: one rewrite rule firing across the IR (cascade); evidence: all cases proved (invariant_counter); result: geomean speed-up or bugs found landing (number_land), overhead next to it |

**viz_kit:** `graph`, `table_panel`, `bars`, `lines`.

### G. Signal processing / communications / control / power electronics

| Element | What to use |
|---|---|
| Worked example | One signal through the chain (block diagram), with its spectrum or constellation before and after |
| Mechanism beat | Block diagram with the new block lit; time and frequency views side by side; loop response |
| Result visual | BER vs SNR, efficiency vs load, Bode/step response: `lines` with log axes and direct labels |
| Conditions | SNR definition, channel model, bandwidth, sampling rate, load range, measured vs simulated |
| Wording traps | Gains at one operating point stated as general; simulated stated as measured |
| Peak candidates | hook: the corrupted constellation; concept: it snaps into place when the new block switches on (before_after / collapse); result: the BER curve dropping past the target (number_land) at the stated SNR, cost next to it |

**viz_kit:** `block`, `wire`, `lines` (log), `waveform` (for digital control).

**Search pipelines (any archetype with a search stage).** Draw the stages over one picture of the space: the full candidate cloud → what each stage removes (greyed, not deleted) → what remains (highlighted) → the selected few lifted out. Counts come from the paper; positions are labelled illustrative; the pruning is named exactly as the paper defines it (dominated, incompatible, infeasible…), never relabelled as a Pareto front unless it is one.

## Choosing the worked example (all archetypes)

1. **Prefer the paper's own running example, at its smallest size.** It is already verified, and readers recognise it. It must be small enough that a push-in fills the frame with its states, roughly ≤ 4 slots per reference node and ≤ 8 steps. Every rule must still fire.
1b. **Walk one instance, replay another.** The instance walked through the mechanism (Act III) and the headline result replayed in Act IV are usually different things. Case study: walk the 2-bit Fig. 4 example; replay FF1 on the cube. Walking the headline design's full search makes the centrepiece too dense to choreograph (references/14 §5).
2. **Otherwise take the smallest instance your re-implementation handles** that triggers every mechanism you will show. Assert it.
3. **The example must fail in the prior approach and succeed in the new one.** That contrast is Act I → Act II.
4. **If a mechanism never fires on real instances, say so.** Report the size of the search. Show a labelled illustration only if the user asks.

## What cannot be re-implemented

Silicon measurements, large-scale training, cluster experiments and similar results cannot be rerun. For those:

- **Type the numbers from tables** with their conditions. Mark them **V**.
- **Digitize from plots** only when no table exists. Mark them "approx., digitized from Fig. N" on screen and in the ledger.
- **A toy model is allowed only as an explicitly labelled conceptual illustration** (e.g. a small analytical or cycle-level model that shows *why* a mechanism helps). Never present its numbers as the paper's.

## Pronunciation and units (narration)

- **Acronyms.** Respell anything a TTS might misread, then record each respelling in the pronunciation table. Examples: "N P U" → "en pee you"; "SRAM" → "ess-ram"; "FF1" → "F F one"; "B-Flex" → "Bee-Flex".
- **Units.** Speak them as words ("picoseconds", "femtojoules", "milliseconds at the ninety-ninth percentile"). Screens show the symbols.
- **Multipliers.** Say "2.5 times lower latency", not "2.5x". Name the metric every time.
