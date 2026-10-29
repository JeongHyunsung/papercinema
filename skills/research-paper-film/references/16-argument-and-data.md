# 16: Argument rigor, data-level grounding, coverage and economy (gates R1–R11)

A film can be accurate number by number (A), legible (B), alive (G), linked (L) and memorable (W), and still lose a careful viewer at two kinds of places:

- **A container with a name instead of contents.** A box labelled "buffer" or "copy" tells the viewer nothing about what is reused, duplicated or wasted. The mechanism is about *which elements* sit where; the picture must show them.
- **A result that invites the obvious objection and never answers it.** An ablated variant that does worse than a baseline can be misread as the method doing worse; a gain over a baseline invites the obvious objection (a larger budget, a weaker baseline, a different setting). If the paper has the data that answers the doubt, the film raises the doubt first and then answers it.

Both come from an author review of a later production. The rules below are general: they apply to any paper in any archetype.

## 0. Understand before drawing: the domain model (R7)

A diagram can only be as precise as the drawer's understanding of the mechanism. Before storyboarding, identify the paper's **core domain concepts**, the ones every later picture depends on, and build an **executable model** of them that reproduces the paper's own worked examples. Then draw only from the model's state.

| Archetype | Core domain knowledge | Executable model | What the film reads from it |
|---|---|---|---|
| B accelerators (and A when the search is over mappings) | mapping → per-level storage occupancy, per-PE MAC order per cycle, refills, data paths (unicast / multicast / reduction) | `scripts/loopnest_sim.py` (cycle-level loop nest: MACs per PE per cycle, tiles per storage instance, fills, reads → destination PEs) | PE labels per cycle, which storage cells are read/written each cycle, refill moments, multicast fan-out, partial-sum accumulation order |
| A algorithms / search | state, transitions, pruning conditions | the re-implemented search with a trace of every step | the tree/state shown, which rule fires where |
| C circuits | node voltages / logic states per event | switch-level or event trace | waveform transitions, which node changes when |
| D systems | request lifecycles, queues | discrete-event simulation | queue contents per time, request paths |
| E ML | tensor shapes and values through the changed component | the forward pass on a small input | shapes, attention patterns, quantised grids |
| F compilers / security | IR before/after each rule; attack steps | the pass applied to the example | rewritten nodes, blocked edges |

Rules:
- **Validate the model against every worked example in the paper first** (every value the paper states for its worked example, asserted from the trace) and keep these as `ARGUMENT["model_checks"]` in the film; `argument_audit.py` fails (R7) if any is missing or false.
- **Derive, never type**, every label, count, order and timing a mechanism beat shows. One early cut animated an accumulation as a uniform fill; the trace showed a different order, so the picture was wrong in a way no reviewer of a still would catch.
- **Replays at a stated rate.** When the film replays cycles, steps or events, it plays at a constant, stated rate ("simulated replay · N cycles / s"), and the replay's landmarks coincide with the narration's (a refill lands on the word "refill").

## 1. Data-level grounding (R5)

**Rule.** Every mechanism beat about storage, data movement, reuse, partitioning, replication, caching, queues or tensors shows the *contents* of each container at element granularity, computed from the re-implementation, never typed.

| Data | Draw it as | Component |
|---|---|---|
| a 1-D or 2-D operand tile (matrix block, weight tile, KV block, cache lines) | a grid with one cell per element, index ranges on the axes ("K0–7", "N0–2") | `data_kit.elem_grid` |
| a ≥ 3-D tensor (conv activations C×H×W, attention heads × tokens × dims) | stacked slabs, back to front, with the sliced axis labelled | `data_kit.tensor3d` |
| the same elements held twice (replication) | the two grids side by side, thin connectors between corresponding cells, "=" | `data_kit.same_link` |
| overlap between partitions (halo, sliding window, multicast) | the shared rows highlighted in both grids | `elem_grid(hl=…)` |
| refills / loads / capacity | an exact counter bar next to the grid | `data_kit.load_meter` |
| a packet, request or token in a queue | the queue's slots, each holding its item's id | slots (motion_kit `slot_node`) |

**Compute, then assert.**
- `data_kit.loop_nest_tile(index_fn, mapping, j, outer)` gives the operand coordinates a storage wrapping loops j..L holds for given outer iterations (for loop-nest papers; `loopnest_sim.LoopNest.tile` numbers that storage as level j−1). Other archetypes: compute the contents from the re-implementation's state (cache sets, queue contents, KV pages).
- Assert the computed cell count against every capacity or traffic number on screen.
- **Derive every partition label from the computed contents.** One early cut labelled two partitions with typed index ranges that the model did not produce. A typed label is a fidelity bug waiting to happen.

### 1b. Canonical glyphs for recurring concepts (R8)

A concept the film shows in three or more beats (a storage, a PE, a queue, a cache line, a node, a packet) gets **one** detailed glyph, designed once, used everywhere (film and figures), with its internal anatomy alive. For storage the canonical glyph is `data_kit.Storage`:

| Part | Shows | Data it reads |
|---|---|---|
| header | name, `used / capacity elements`, level or role | occupancy from the model |
| write port (tab + inbound arrow) | active while data arrives; exact counter ("32 in", "96 loaded") | fills |
| body | one cell per element, banked; per-cell state `empty / valid / live / idle / new`, optional partial fill (partial sums) | tile contents, accumulation |
| read port (tab + outbound arrow) | active while data leaves; destination fan-out ("k × 1:n multicast") | reads → destinations |
| occupancy bar | used / capacity | occupancy |
| pruned | the whole glyph turns coral, drops, fades | rule outcome |

**Layout rules the glyph enforces** (so it stays clean at film and slide sizes): its width covers the header text by exact cairo metrics (`data_kit.text_w`), the level tag shares the name line only when it fits, header baselines follow the rendered text size (`eff`, which includes a figure export's boost), row and column index labels thin out to every k-th when cells are smaller than the text (never overlapping), port tabs grow with their label, port counters sit `side` / `left` / `under` (`port_lab`), and `fit(max_h)` shrinks the cell so the glyph and its ports stay inside a container (`arrow=`, `drop=` for tight containers). Wires that feed many consumers run in the gaps between them with one tap per consumer (a bus), never through the consumers' labels. A data wire starts at a read-port tip (`Storage.port_tip`), flows one way (`ortho_wire` asserts no hook or doubling back) and ends at whoever reads the data *after* the event shown: after a prune, the consumers of the surviving copy, never the pruned one.

`data_kit.storage_icon` is the same glyph at icon size for overviews (e.g. a whole design space). Never draw an ad-hoc box for a concept that has a canonical glyph; list every glyph in the film plan's **Glyph table** and in `ARGUMENT["glyphs"]` (R8 checks that every data mechanism names one).

**Show change, not only state.** A refill is the grid's contents swapping (old cells fade, new cells fill); a reuse is the same cells staying lit across iterations while a counter shows no new loads; a reduction is partial sums accumulating cell by cell until a cell completes.

**Scale it to fit.** If the real tile is too large, show the walk instance's tile (references/13 §5) and say "walk instance" on screen. Never shrink cells below about 12 px at 1080p; split into two grids instead.

## 2. The skeptic pass (R1–R4, R6)

For every claim the film makes, write down the questions a careful reviewer would ask, and what the paper says to each. Typical doubts, by claim type:

| Claim type | Doubts to check |
|---|---|
| speed-up / reduction vs a baseline | Is the baseline searching a smaller space or using less budget? Different hardware, precision, batch? Is the baseline tuned? Is the aggregate driven by a few settings (show range and wins)? Mean vs geomean? |
| ablation ("without X") | What exactly is removed, what is held fixed? Could the ablated variant look like "the method"? Does the ablation also answer a doubt about the main comparison (it often does)? |
| scale / coverage ("finds all", "covers") | All of what space? Under which constraints? Exhaustive or sampled? |
| a correctness or safety claim ("never worse", "sound") | How many cases, chosen how (sampled? exhaustive?), against which model? Ties? |
| a mechanism ("prunes X", "reuses Y") | Does the rule hold for every case it is applied to, or only under a condition? Show the case where the condition fails |
| an interpretation ("because <the paper's explanation>…") | Is it the paper's claim or ours? Label it as the paper's reading |

Then stage what the paper supports:

- **Doubt → test → result.** When the paper has data that answers a doubt, raise the doubt on screen and in the narration *before* the data ("Fair question: does the gain survive when the baseline gets the same budget?"), say what the test holds fixed and what it removes, then show the result with its conclusion ("so the gain comes from the method, not the budget").
- **Acknowledge** a doubt the paper does not answer: one short line, never silence.
- **Define before use (R2).** Every baseline, ablation and term appears with a one-line definition on screen before its first comparative use.
- **Name ablations unmistakably (R6).** "Method-minus-X (ablation: the method without X)", never in the method's colour, never placed where the method usually sits.
- **Aggregates show their spread (R4).** A geomean comes with the range and the win count ("range a–b %, lower in w / n settings").
- **Interpretations are attributed.** "The paper reads this as…"

## 3. Logic-chain check (the generator on the script at K2; the independent reviewer on each cut, references/19 §2.5)

Read the narration as an argument. For every "so", "because", "therefore", "thus" (spoken or implied by a cut):

1. Is the conclusion implied by what has been shown, or does it need a step the viewer has not seen?
2. Is every premise on screen before the conclusion?
3. Would the sentence still be true if a reviewer read it out of context?

Missing steps become beats (often 3–5 s, one line). Over-strong conclusions get the paper's own hedge ("in all n settings", "under the paper's cost model").

Also check **mild over-simplifications** of prior work: "previous methods do A and B" vs the paper's "A, B, or both". Show the distinction when it costs one chip.

## 3b. Coverage and economy (R9–R11): say everything the paper needs, once

**Coverage (R9).** Before the script, list every mechanism, effect and contribution in the paper's method and evaluation sections (one row each: every rule, stage, effect and claimed contribution) with the beat that carries it, or an explicit omission and its reason. A result shown without the mechanism that produces it fails: if the film shows a results figure for an effect, it must show *why* the method produces that effect. (One cut showed such a results figure silently and never explained the mechanism behind it.)

**One visual per claim (R10).** Each claim gets its strongest figure once. Re-drawing the same point with a weaker picture (a flat dot grid of "the space" after a 3-D cloud already showed it; a second chip restating the label under its own bar) costs time and dilutes the good figure. A later beat may return to the same glyph only as a declared *callback* that adds a new fact (the hook's space returns later to show what remains).

**Detail only where an argument needs it (R11).** For each beat, name the claim or definition it is needed for. Detail that no claim needs is cut, not shortened: a second data view in a beat that is about a different rule, a grid that restates a count already on screen, a worked counter-case already stated by the rule's condition, a legend under a table whose column already shows the same categories, placeholder rows that are filled a second later. Fit the target runtime by cutting such beats first, then by tightening narration; never by speeding speech past the voice's natural rate.

Procedure: (1) coverage table, (2) one-visual-per-claim table, (3) beat list with seconds and "needed for", (4) cut until the sum fits the target with the readability holds intact, (5) `argument_audit.py` R9–R11 with `coverage`, `visuals`, `beats`, `target_s`, `duration_s` in `ARGUMENT`.

## 4. Implementation

- `film.ARGUMENT` (exported to `argument.json`) lists the definitions, claims, doubts and mechanism beats with their on-screen times and strings; `scripts/argument_audit.py` checks R1–R11 against the readability audit's string inventory; `gate.py --arg` adds the rows.
- `templates/film_plan.md` has an **Argument map** (claim → doubts → answer/acknowledgement → on-screen wording) and a **Data views** table (beat → containers → computed contents → asserted counts).
- **Skeptic pass:** the generator runs it on the script at K2; the independent reviewer runs it on every cut (references/19 §2.5).

## 5. Calibration

| Issue in cut 1 | Fix in cut 2 |
|---|---|
| Rule beats showed named boxes instead of contents | element grids computed from the model, identical copies linked with `same_link`, the resident part shown against the whole |
| branch labels typed by hand | derived from contents |
| ablation result shown before the doubt it answers | doubt → test → result: the doubt raised first, then what the test holds fixed and removes, then the result and its conclusion |
| headline geomean alone | range and wins next to it |
| storage drawn as plain boxes, differently in each scene | one `Storage` glyph (ports, counters, element states) for every buffer and copy, and as icons in overviews |
| an accumulation animated as a uniform fill | the model's trace: the real order, replayed at a stated rate |
| prior work summarised more narrowly than the paper states it | the paper's own wording, with named prior-work examples |
| one mechanism absent; its results figure shown silently | a short mechanism beat and the results figure as its evidence (R9) |
| over the target runtime; the space drawn twice, a redundant worked case, detail no claim needed | under the target: one space glyph with a later callback, the doubt raised on the ablation chart itself, every beat tied to a claim (R10, R11) |
