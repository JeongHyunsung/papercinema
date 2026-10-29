# B-Flex PPT figures (final)

**Typeface:** Inter only (Regular, Light, Medium, SemiBold); the PDFs embed nothing else.

- On this system, the plain family name "Inter" resolves to the Medium face. `setup_fonts.py` installs a renamed copy of Inter-Regular as "Inter Regular", so regular text really is Regular.
- Run `setup_fonts.py` once before regenerating.

**Slide contrast (v2):** every stroke is 1.5× thicker. Faded elements and secondary greys are darker. Text is one weight heavier (Light → Regular, Regular → Medium; hero numbers stay Light) and 8 % larger. The settings are in `figlib.BOLD`.

**Text policy:** no titles, legends, captions, source tags or step markers; type those in PPT. Kept: in-figure numbers, node labels, axis ticks and annotation chips.

**Formats:** PNG (3× design scale, 300 dpi tag, white background), SVG and PDF (vector). Every PDF and SVG was rendered back to an image and checked against the PNG.

## 1. Motivation (purpose-built)

| file | content |
|---|---|
| 1_motivation | Left: the SeGen-20 waveform. Transitions 1–5 pass; 6 (D 1→0 replaces CK 1→0) gives the wrong Q. Right: the 2-bit square → 3-bit cube, with 3^16 ≈ 4.3×10^7 → 4^32 ≈ 1.8×10^19 candidate tables. |
| 1a_wrong_output | left half only |
| 1b_search_space | right half only |

The brute-force line (~10^6 years, 1 thread) is the paper's Table 1 extrapolation.

## 2. Key methodology (RBG → 3-D ESTG, step by step)

2a and 2b are the flat Reference Behavior Graph. The figures from 2c on show the 3-D stage, rebuilt for slides:

- **Fixed oblique camera.** It is near-orthographic, so every pill, label and chip is the same size; there are no tiny far-away elements.
- **Enlarged δ table.** The transition table is enlarged ×1.42 and placed beside the stage. Row highlights, the conflict mark and the node → row tethers move with it.
- **No search-tree inset.** The film's small search-tree inset is left out.
- **Identical crop for 2d–2j.** Consecutive slides overlay exactly.

| file | film t3 | content |
|---|---|---|
| 2a_rbg | 14.26 | Reference Behavior Graph |
| 2b_rbg_failing_path | 16.98 | SeGen-20 failing sequence on the RBG |
| 2c_estg_over_rbg | 19.46 | ESTG pills above the RBG nodes (3-D) |
| 2d_step1_start_pair | 21.55 | initial state, first δ entry |
| 2e_step2_wrong_output | 24.55 | **prune case 1: wrong output** |
| 2f_step3_instantiate | 28.45 | two branches (X1 / X2) kept |
| 2g_step4_repeat | 30.15 | the table fills in |
| 2h_step5_entry_conflict | 33.55 | **prune case 2: entry conflict** (the film's depth-5 case) |
| 2i_step5_branch_pruned | 34.35 | branch removed |
| 2j_non_convergence | 22.95 + overlay | **prune case 3: non-convergence (ILLUSTRATIVE)** |

**Caveat on 2j.** Our re-implementation of the search never produces non-convergence: there were 0 cases at 2-bit and 0 in a 3M-node 3-bit run (`find_nonconv.py`). 2j is therefore a hand-built table, δ(00,11)=01 and δ(00,01)=11. Under (D,CK)=00 the state cycles 11 → 01 → 11 … and never settles. It shows what the rule rejects; it is not a search trace.

## 3. Key result (purpose-built)

`3_key_result` reads left to right:

1. **Scale.** 568,832,054 valid 3-bit-state FSMs vs 18 at 2-bit. At true scale the 18 would be ~0.07 units wide, so they are drawn as a corner dot plus a magnifier lens.
2. **Mapping.** The 468 with C_FF ≤ 20, each drawn as a dot in the block with a trail to its cell in the C_FF bars (1, 1, 10, 7, 23, 24, 76, 101, 225). The dot positions inside the block are illustrative, as in the film; the bar counts are the paper's Fig. 5 values.
3. **Sampling.** 20 sampled → circuits.
4. **Pareto.** Table 2, energy vs sequencing overhead for all 18 FFs, with the Pareto front (amber dashed staircase, plus rings on the front points).

Scatter markers (no legend in the figure):

| marker | meaning |
|---|---|
| teal ◆ | B-Flex circuits (5 of 20 reported) |
| amber ◆ | FF1 |
| ○ | recent flip-flops |
| □ | SeGen |
| ▲ | TGFF |

Pareto front, as (ps, fJ): (19.1, 2.26) FF1 · (31.3, 2.25) · (31.5, 1.97) · (31.7, 1.91) · (33.1, 1.62) · (46.9, 0.64) · (57.0, 0.59) · (68.7, 0.57) · (68.9, 0.49).

## Regenerate

From the B-Flex project root, with the film source in `src/`:

```
cd figs
python3 setup_fonts.py                # once
python3 make_figs.py --k 3            # all → out/
python3 make_figs.py --k 1 --preview  # quick PNG preview
```

`src/film.py` is not modified. The figure-only patches are applied in memory (`figlib.py`). The purpose-built figures are in `design.py`.
