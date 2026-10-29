# Changelog

How the skill got here: each version is a fix for what the previous one got wrong on a real production.

It was distilled from a real production, B-Flex (DAC 2026), which needed five film versions and two rounds of figure feedback. The skill turns that history into a **quality bar**, **draft-1 defaults**, **automated gates** and (since v7) an **independent review loop**: a generator makes each cut, a reviewer that never sees how it was made judges it against the paper, and the user joins every K rounds. The full case-study source is in `examples/bflex/`.

**v3: motion, camera and linkage.** A from-scratch rebuild with v2 passed every gate and reproduced the paper's Table 1 exactly. Yet next to the case-study film it was visibly static, with floating annotations:

| | case-study v4 | rebuild (v2 skill) |
|---|---|---|
| static seconds | 17 % | 50 % |
| camera motion | 55 % | 10 % |
| centrepiece camera motion | 57 % | 0 % |
| unanchored findings | — | 24 |

v3 adds:
- the missing half of the quality bar, gates G1–G5 (motion, camera) and L1–L6 (linkage), with a measuring tool for each;
- the craft as reusable components (`scripts/motion_kit.py`) and a 12 s demo that passes them (`examples/motion_kit_demo`);
- a new reference, `references/14-motion-camera-linkage.md`;
- a postmortem, `examples/bflex/docs/FRESH_REBUILD_POSTMORTEM.md`.

**v4: peaks.** A film that passes every gate above can still leave no moment behind. v4 adds:
- 3–6 planned **peaks** per film: setup → tension → one reveal → hold, with the sound hit and the spoken key word on the reveal; each peak dramatises a claim-ledger entry and never strengthens it;
- a budget of **at most 2 signature breaks** per film (night stage, spotlight, accent halo, colour flood), each ≤ 6 s and inside its peak; the white identity holds everywhere else;
- `scripts/peak_kit.py` (plan, budget asserts, fidelity-safe devices, signature effects), `scripts/wow_audit.py` + `gate.py --wow` (gates W1–W7), peak sound in `scripts/audio/synth.py` (`riser`, `hit`, `Track.duck`), a `post(rgb, t)` hook in `render.py`;
- `references/15-wow-beats.md` and a 30 s demo that passes W1–W7, G1–G4 and L1 (`examples/peak_demo`).

**v5: argument rigor, data-level grounding, domain model, canonical glyphs.** From the first author review of a later production (a paper not yet public): named boxes told nothing about the data; an ablation shown before its doubt could be misread as "the method is worse"; one storage concept was drawn six ways; one animation contradicted the method's real step order. v5 adds:
- **understand before drawing**: an executable domain model validated against the paper's worked example, every label/order/timing read from it (`scripts/loopnest_sim.py`: per-cycle MACs per PE, storage tiles, fills, reads with destinations; gate R7);
- **data, not names**: element-level grids and 3-D slabs computed from the model and asserted (`scripts/data_kit.py`: `loop_nest_tile`, `elem_grid`, `tensor3d`, `same_link`, `load_meter`; gate R5);
- **one canonical glyph per recurring concept**: `data_kit.Storage` (read/write ports with counters, per-element states, occupancy, prune) laid out by exact text metrics so it stays clean at film and slide sizes (label thinning, `fit`, port-label placement); `storage_icon` for overviews (gate R8);
- **the skeptic pass**: doubt → test (held fixed / removed) → result → conclusion; definitions before use; spreads with every aggregate (`scripts/argument_audit.py` + `gate.py --arg`, gates R1–R11: plus coverage of every paper mechanism, one visual per claim, and a time budget in which every beat names what it is needed for);
- routed tethers (`via=`) and 2-line, side-placed callouts so leaders never cross content;
- `references/16-argument-and-data.md`.
- `references/17-story-spine.md`.

**v7: the independent review loop.** Through v6 the producing agent reviewed its own film by playing critics in turn, so it judged what it meant rather than what was on screen, and the user saw the film only at the end. v7 splits the work:
- an **orchestrator** (the agent talking to the user) runs intake, routes files and never makes the film;
- a **generator** subagent builds each cut from the paper and the brief, passes its gates, and revises from the reviewer's feedback only;
- a **reviewer** subagent, fresh every round, sees only the delivered video and subtitles, the paper, user-supplied data, its own earlier reviews and, every K rounds, the user's comments; it writes `review.md` (verdict, earlier findings' status, new findings with severity and a checkable "done when", requests);
- the **user** reviews every K rounds (K asked at intake) and approves the final; either role can ask the user for data, and "unavailable" is a valid answer; disputes between feedback and the paper are settled by user rulings;
- `scripts/review_pack.py` builds the reviewer's view from the files alone: 1-fps sheets, 1080p stills every 3 s and at cuts, a timeline of picture change, camera moves, audio level, silences and subtitle windows, the motion gates, loudness and a transcript;
- `references/18-review-loop.md`, `references/19-reviewer.md`, `templates/review.md`.
