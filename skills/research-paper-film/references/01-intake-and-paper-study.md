# 01: Intake and paper study

## Intake checklist

Extract each of the following from the brief. If any is missing, decide it yourself and say what you decided; if a wrong decision would be costly, ask instead.

| Item | Typical default | Notes |
|---|---|---|
| Duration | 60 s silent cut; 110–120 s narrated | Narration roughly doubles the runtime for the same content |
| Format | 3840×2160, 60 fps, 16:9 | Render in a 1920×1080 design space and scale |
| Narration | optional; English | The film must stay understandable without audio |
| Audience | domain experts plus technical newcomers | Two levels: expert-recognisable mechanism, newcomer-readable story |
| Three takeaways | problem, idea, impact | Every scene serves one of them |
| Deliverables | master, MP4s, SRT, stems, storyboard, timing sheet, verification notes, source and reproduce instructions | Settle the list now |
| Hard rules | no fabrication; no stretched speech; licensed audio; never claim unrun checks | Copy them into your task list |

**Follow-up briefs.** A later brief may say "keep the film; audit and polish". Treat the previous deliverables as frozen. Before you start, write down what may change and what may not.

## Reading the paper

```bash
pdftoppm -r 150 -png paper.pdf ref/p          # page images
pdftotext -layout paper.pdf ref/paper.txt     # text; check two-column order
```

1. **Read every page image column by column**, including footnotes, figure captions and table notes. Conditions hide there: "conservatively extrapolated", "average of 5 runs", "16 threads", "0.9 V", "FO4 load".
2. **Crop each figure you will visualize** at high resolution and keep it under `ref/`.
3. **Fill the claim ledger** (template: `templates/verification_table.md`) with one row per number or claim:

   | Claim | Value | Unit / conditions | Source | Planned use |
   |---|---|---|---|---|
   | 3-bit exhaustive search finds valid FSMs (case study) | 568,832,054 | 3-bit state, Q = ¬s2, init 011, ≤ 1 bit flip, 786 s @ 16 threads, avg of 5 | Table 1, §4.1 | counter in Act IV |
   | Accelerator speed-up (typical hw paper) | 3.2× | geomean over 8 workloads, vs GPU X at batch 1, cycle-accurate sim, 1 GHz, 28 nm | Fig. 9 | bars, Act IV |
   | Tail latency (typical systems paper) | −68 % | p99 at 70 % load, trace Y, 16 nodes, mean of 5 runs ± std | Fig. 7 | curve + vspan |

4. **Write down the paper's distinctions** and never blur them in the film or narration:
   - candidate vs valid;
   - behaviour/model vs circuit (schematic) vs post-layout vs measured silicon;
   - simulated vs RTL vs FPGA vs silicon; peak vs sustained; mean vs geomean vs tail;
   - "sampled from" vs "the N simplest";
   - "is" vs "can be modeled as";
   - the tool vs the design produced by the tool (e.g. SeGen vs SeGen-20);
   - the paper's own terms (e.g. "prunes the branch", "entry conflict", "stable transition").

## Minimal re-implementation

The goal is real structures to animate, not a full reproduction.

- **Implement only what the film shows.** Typical cases by archetype (references/13):
  - algorithms: the rules plus one worked search path, and the tree statistics;
  - hardware: a tiny dataflow or schedule model that reproduces the paper's example tile;
  - circuits: a replay of the published state table or waveform;
  - systems: a request trace through the components;
  - ML: tensor shapes through the changed block.
  
  The case study implemented the reference graph, candidate expansion with its pruning rules, one search path, the tree statistics, and a published FSM replay.
- **Results you cannot re-run** (silicon, large training, clusters) are typed from tables with their conditions, or digitized from plots and marked "approx.". Toy models are allowed only as labelled conceptual illustrations.
- **Assert against the paper**:
  - the published example tables;
  - totals (e.g. 18 valid 2-bit FSMs);
  - node and edge counts of published graphs;
  - the published failing sequence.
- **Output one JSON file** (`data/scene_data.json`) consumed by the film. Nothing in the film should hard-code a structure that the JSON could supply.
- **Record discrepancies "for the authors"** in `VERIFICATION.md`, e.g. a table value that disagrees with a figure. Do not silently choose one.
- **Prove absence instead of inventing.** If the user asks for a real instance of something the method may not produce (e.g. a non-converging candidate), search for it. If none exists, report the search size and why; then offer a clearly labelled, hand-built illustration.

## VERIFICATION.md

Start it in Phase 1 and keep it current. For every visual and claim, record:

- **Source**: § / Fig. / Table / footnote.
- **How it was checked**: typed from the table, recomputed by the re-implementation (with the assertion), or re-simulated.
- **Class**: verified, recomputed, or conceptual (preserves relation X).

Time codes refer to a named clock: v3 animation time or film time. Say which.
