# 11: Iteration lessons: start at the final version

The case study (B-Flex, a search/circuit paper) needed five film versions and two figure rounds. Each row below is a **general rule for any CS/EE paper**. The case-study column shows the draft that taught it. Apply every rule from the first draft, so the user does not have to send you round the same loop.

## Meaning before beauty (case study v1 → v2)

| General rule | Case-study draft that taught it |
|---|---|
| Every visual element explains a concept, makes a meaningful transition, or shows a verified number. If you cannot name its job, delete it | A decorative particle field and a field of cubes before the title |
| Each camera move follows an event in the method or a verified number | The camera moved for spectacle |
| Build the scene from the paper's own representation (graph over graph, dataflow on a block diagram, request path, tensor flow) | A flat generic graph for a method that is "candidates over a reference graph" |

## Comprehension (v2 → v3)

| General rule | Case-study draft that taught it |
|---|---|
| Only computed structures, or explicitly labelled concepts | Hand-drawn "enumerate vs validate" sketch trees |
| One change at a time (camera → label → event); mechanisms follow anticipation → action → consequence → hold | Event, caption and camera changed together |
| Tempo is a code: fast = repetition/scale, moderate = representation change, slow = mechanism | One tempo throughout |
| Check dense frame strips (0.3 s) around every mechanism beat before the full render: overlaps, covered nodes, drift under panels, elements too small | Markers overlapped on a bidirectional edge; a chip hid the "≠"; rejected nodes drifted under the table; the race was too small |

## Readability, narration, identity (v3 → v4)

| General rule | Case-study draft that taught it |
|---|---|
| Readability budget from the first cut: labels ≥ 2.5 s, results 3–4 s, reasoning 4–7 s (audit.py) | 109 labels under 2.5 s; the key result readable for 0.55 s |
| No caption band; every fact lives in its scene or in the narration (keep a caption-fact checklist) | Facts existed only in a caption band |
| White identity and flat tints from the start; no glow on white | Dark theme with glow and grain; switching to white left grey ghosts |
| Alpha-over compositing for dense charts on white | An additive unit chart, invisible on white |
| Reserve empty zones for text; knock out behind headers; check every label against the data marks | A header crossed by an arc; a title over an axis; a footnote on a data label |
| Narration-first: script → voice → align → retime the picture; never stretch speech | Animation first, voice squeezed in later |
| Source tags top-right, away from the player's subtitles | Tags bottom-right |

## Audit-proof wording (v4 → v5): patterns for every field

| Pattern (what to check in your script) | Generic fix | Case study before → after |
|---|---|---|
| **Ontology verb** | Use the paper's verb ("modeled as", "approximated by") | "is a state machine" → "can be modeled as" |
| **Tool vs artifact** | Name the artifact that failed or won, not the tool or paper | "SeGen gave 0" → "SeGen-20 gave zero" |
| **The method's real unit and rule** | Say what is actually checked, in the paper's terms | "edge by edge" → "one *stable* transition at a time; each must *match an edge*" |
| **Under-specified condition** | State the defining condition | "an entry already fixed" → "set *differently*" |
| **Missing scope** | Add the space, benchmarks or operating point | "568 million valid behaviors" → "… in its search space" + constraints on screen |
| **Selection rule** | sampled vs top-k vs all; filtered how | "twenty of the simplest" → "twenty of the 468 simplest were *sampled*" |
| **Artifact level** | model / schematic / layout / RTL / FPGA / silicon | "circuits" → "transistor-level *schematics*" |
| **Mechanism detail** | Replay the real data instead of paraphrasing it | "captures in two steps" → "settles in two steps; Q flips on the first" |
| **Missing condition** | Threads, voltage, activity, batch, load, percentile | "~10⁶ years" → "~10⁶ years, 1 thread (extrapolated)" |
| **Provenance** | Say which parts are the paper's figure and which are recomputed | "Fig. 4" on all steps → "steps 1–3 as in Fig. 4 · 4–5 recomputed" |
| **Distinct mechanisms** | Each rule or stage is its own case, with per-case counts including zeros | pruning rules lumped together → "384 · 32 · 0" |
| **Comparative without a metric** | "N× lower <metric>", never "N× faster/better" | "faster" → "2.53× lower sequencing overhead" |
| **Hidden trade-off** | Show the cost right after the headline | energy cost shown after the speed result |
| **Sync** | The key word is spoken while its label is visible | "pruned" said after the label faded |
| **Subtitle timing** | Time cues by spoken-word count | Cues split by character share ended mid-phrase |
| **Spoken style** | One natural sentence per idea; idiomatic verbs | "Wrong output: pruned." → a full sentence |

## Slide figures (figure round 1 → 2)

| General rule | Case-study draft that taught it |
|---|---|
| Purpose-built static compositions, not film captures | Frames captured at chosen times, pasted side by side |
| Everything in its final state; draw transitions as static trails | Mid-animation frames with cells in flight |
| Step sequences: one near-orthographic camera, one crop, the key table enlarged beside the stage, small insets dropped | Each step at the film's own camera; content under the panel; far elements tiny |
| Small text boosted, and every resulting collision fixed (lint: ≥ 9 pt at 12 in) | 12–13 px in-scene text, unreadable on a slide |
| Inter only, verified with `pdffonts` | Mixed mono/display faces; "Inter" silently rendered as Medium |
| Slide figures heavier than film frames: strokes 1.5×, darker greys and faded elements, text one weight up (figkit.BOLD on by default) | Figures that copied the film's hairline weights, so lines and labels read faint on a slide |
| A requested case that cannot occur: search, report, draw a labelled illustration | A requested "real" non-convergence that the method cannot produce |

## Fresh rebuild vs v4 (2026-10): the half the gates could not see

A from-scratch rebuild passed every gate the skill then had and reproduced Table 1 exactly. Yet the author's first reaction was: "less dynamic animation, a less dynamic camera, and concepts not marked and linked as precisely". Full analysis: `examples/bflex/docs/FRESH_REBUILD_POSTMORTEM.md`.

| General rule | What the rebuild did |
|---|---|
| Restraint is not stillness: every second carries a meaningful change (G1–G4) | 50 % static seconds; a 7 s freeze; mean change 0.8 % vs 4.3 % |
| Each mechanism beat: push-in → hold with drift → pull-back (`beat_keys`) | one camera tilt in the whole film; 0 % camera seconds in Act III |
| Follow shots for long structures (waveform, pipeline): the camera rides the moving head (`lagged`, `View2`) | whole waveform shown statically from frame 1 |
| Findings are pinned with values (`callout_at`); contradictions show both facts | 24 unanchored findings; "entry conflict × 6" as a floating chip |
| The built state is a fixed-address panel, tethered to the scene on every write (`AddressTable`, `tether`) | table rows appended; one tether in the whole film |
| Show the full candidate space (pills), not only visited nodes | only reached nodes drawn, so pruning had nothing visible to prune from |
| Walk the paper's smallest running example; replay the headline design | walked FF1's 3-bit search (16 steps, up to 49 jobs each): too dense to push in on |
| Choreography is planned (shot list + linkage map, K3b) and watched at 1× (K4) | checks were stills and 1-fps sheets, which cannot show motion |
| A fresh build still uses the craft: `motion_kit.py`, references/14 | "from scratch" was read as "ignore the example", so the craft was re-derived minimally |

## What the user should never have to say

The skill must catch each of these itself:

- "Labels disappear before I can read them." → B1
- "This is too dark / too glowy for slides." → C2
- "This number has no scope or condition." → A1, A2
- "That's not what the paper says." → A3, A4, and the wording patterns above
- "You didn't show all the cases." → A6, E7
- "The figure is just a screenshot." → E1, E2
- "The font isn't what I asked for." → E4
- "It feels static; the camera never moves." → G1–G4
- "I can't tell what this label refers to." → L1–L5
- "Show me where in the table that happens." → L4

## From the first v4 production
- Peaks were measured, not judged: two of five planned peaks failed W2 on the first cut (setup motion as large as the reveal; a reveal that changed under 1 % of the frame). Both were fixed by moving camera motion onto the reveal. Run `wow_audit.py` at K3b, not only at K4.
- A table outcome that removes something needs its own style: the conflict strike made "prune" cells unreadable; `AddressTable` now has `style="prune"`.
- When the rule stage and a fixed table share the frame, give the stage its own clipped viewport (`cairo` clip + `View2(ax=viewport_w/2)`), so push-ins never slide under the table.

## From an author review of a later production
- **Boxes are not data.** A box with a name told the author nothing; element grids of its contents made duplication and reuse visible. Compute contents from the re-implementation; never type a partition label (one typed label was wrong).
- **Raise the doubt before the ablation.** Showing an ablation's weak result first invited the misreading that the method itself was weak and left the obvious objection unanswered. Doubt → test (held fixed / removed) → result → conclusion.
- **Precision about prior work and aggregates.** Prior work stated the way the paper states it, with examples; a geomean always with its range and win count.
- **Understand the domain before drawing it.** Storage occupancy, per-unit order per step and data paths must be computed (an executable model of the mechanism) and checked against the paper's worked example before any diagram; one uniform-fill animation was wrong and only the trace revealed it.
- **Recurring concepts deserve a canonical glyph.** Storage appeared in six beats drawn six ways; one detailed glyph (ports with counters, element states, occupancy) made every beat sharper and the film coherent.
- **Lint passing is not layout passing.** Raising slide text sizes (figure `BOOST`, glyph `tag_size`) on a layout written with fixed offsets produced overlaps the size lint cannot see (chips over chips, tags out of their glyph, labels through wires). Every offset that sits next to text is computed from measured sizes (`data_kit.text_w` / `eff`), and every rendered figure and every peak frame is *looked at*, not only linted.
- **Wires and leaders route through gaps.** A bus drawn through the centres of the units it feeds crossed every unit label; a table tether drawn as one curve crossed two grids and a legend. Buses run in the gaps between rows with one tap per destination; tethers take `via=` waypoints along channels (around a box if needed); a callout chip is placed where its leader crosses nothing (`align="l"`, 2-line chips for narrow gaps).
- **Ports face their consumer.** A port counter that runs into the next element moves (`port_lab`: side / left / under); a glyph inside a container is fitted to it (`Storage.fit`), with its port arrows shortened (`arrow=`) and its pruned drop reduced (`drop=`) so nothing pierces the container.
- **Data paths go to their consumers, in one direction.** After a prune, a data wire still pointed at the pruned consumers' write ports, and its ends hooked upward short of the port arrows: the picture contradicted the rule it illustrated. Data wires start at a read-port tip and end in the consumers that actually read the data after the event (`data_kit.ortho_wire`: axis-aligned, asserts no doubling back, one tap per consumer; `Storage.port_tip`). Re-check every wire after every state change (prune, refill, retarget).
- **Show a search as a space, not a table of dots.** A search budget drawn as a flat dot grid next to the previous chart read as nothing. The film shows the candidate space, what is removed (greyed, kept visible for contrast), the remaining region highlighted, and the selected few lifted out; every count from the paper, positions labelled illustrative, and the earlier scene fully cleared first. Name pruning precisely (say exactly what is removed and why).
- **Transitions are frames too.** A gate-clean cut still had: one scene's diagram arriving over the previous scene's table, rows sliding over a table, two result charts cross-fading in place, callout leaders through card text and an axis label, and a chip duplicating the label under its own bar. None is visible in a single "hero" still; a 3-s frame sweep plus every scene boundary found all of them in one pass. Scenes that share screen area hand over sequentially (out, then in); leaders end at an element's edge, never inside it.
- **Coverage before polish; economy before speed.** An author asked whether one mechanism had been left out on purpose: it had not, it had been missed, while the result it explains was on screen. The author also asked for a shorter film with no repeated explanations and no unnecessary detail. The fix was a coverage table (every paper mechanism → beat or reasoned omission), one visual per claim (the design space drawn once and recalled, not redrawn as a weaker grid), and a beat list where each beat names the claim it serves; the runtime fell by more than a third with an added mechanism beat and no faster speech (R9–R11).
