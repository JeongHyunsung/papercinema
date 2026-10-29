# 09: Slide figures from the film

Typical request: "Keep the film pipeline intact. Extract clean figures for PPT: one motivation figure, the methodology steps (showing every case of the mechanism), and one key-result figure. Keep the film's style. I will type the text myself."

**Building blocks.** `scripts/viz_kit.py` provides the components (waveform, graph, table panel, axes, bars, lines, scatter with Pareto front, unit histogram, unit block with lens, block diagram, wires, PE/heat grid, pipeline). `examples/gallery/gallery.py` builds one slide figure per paper archetype; copy the closest one and replace its toy data with the paper's numbers.

## First, ask (the answers change what you build)

1. **Text policy.** Which in-figure text stays? A typical answer:
   - remove: titles, subtitles, legends, captions, source tags, act labels, step markers, breadcrumbs;
   - keep: in-scene chips, node labels, numbers, axis ticks and axis titles.
2. **Which example cases.** E.g. "the film's depth-5 conflict".
3. **Requested elements that may not exist**, e.g. a real non-convergence case. Search for one (and report the search size). If none exists, offer a labelled illustration.
4. **Data-plot extras.** E.g. scatter plus a Pareto-front line.

## Lesson: do not just capture frames

The first attempt (rejected) captured film frames at chosen times and pasted them side by side. Three things went wrong:

- **Motivation.** Three separate frames placed next to each other: not space-efficient, with mismatched scales.
- **Key result.** A mid-animation frame, with cells in flight: it reads as a mess.
- **Steps.** Every frame had a different camera framing, and some content was cut off by the panel.

Slides need every element in its final state, compact composition, a target aspect ratio (about 2.2:1 under a title) and legible sizes. One design unit ≈ 0.5 pt when a 1900-unit-wide figure is placed 12 in wide, so body text should be at least 22 units.

## Mode A: purpose-built static compositions (`design.py`)

- **Draw with the same engine and palette as the film,** using the same data (`scene_data.json`, the paper's tables).
- **Don't use time windows or animation state.** Everything is in its final state.
- **Motivation figure, generic form.**
  - Left: the evidence of the problem (a failing trace or waveform, a profile showing the bottleneck, a counter-example).
  - Right: the size of the space or of the gap (a growth diagram, a scaling curve, "x of y" as block + lens).
- **Key-result figure, generic form.** Show the results as the paper's own chain of claims, with arrows and no captions.
  - Scale or coverage → selection → the performance vs cost trade-off.
  - Or: a per-workload comparison with the geomean → a breakdown → a scaling curve.
- **Case-study motivation figure.**
  - Left: the failing waveform. Transitions ①–⑤ pass, ⑥ fails; "expected Q" is blue dashed, "SeGen-20 output" coral, with the reordered transition annotated.
  - Divider.
  - Right: the 2-bit square → 3-bit cube, the same projection as the film, with the counts 3¹⁶ ≈ 4.3×10⁷ → 4³² ≈ 1.8×10¹⁹ and the brute-force estimate.
  - Also export each half alone.
- **Case-study key-result strip** (left → right):
  1. **Scale.** A 568,832,054-cell block vs 18 cells. At true scale the 18 are about 0.07 units, so draw a corner dot and a magnifier lens containing the 18 cells.
  2. **Mapping.** Each of the 468 low-complexity FSMs is a dot in the block, with a faint trail into its cell of the C_FF histogram (bar counts from the paper). The dot positions are illustrative; say so.
  3. **Sampling.** A 4×5 amber block for "20 sampled".
  4. **Pareto.** The energy vs sequencing-overhead scatter of all 18 designs, with the Pareto front as a dashed staircase plus rings. Compute the front in code and list its coordinates in the README.
- **Draw order.** Draw things in the right order (trails under the lens). Use subscripts (C_FF) where the font allows.

## Mode B: film-scene stills for algorithm steps

Keep the scene code; change the framing.

- **Load the film without editing it.** Read `film.py` as text, apply exact-match patches (assert that each target occurs exactly once), and exec it as a separate module. Override the HUD functions with no-ops. `scripts/figures/figkit.py` provides the loader, the text filter and the exporters.
- **Remove unwanted text** with a `DROP` set of exact strings (the text wrapper skips them) plus HUD no-ops.
- **Fixed near-orthographic camera** for every step: e.g. `StageCam(..., D=40000, f=1.36*D)`.
  - Without perspective, far pills and labels are no longer tiny, so the stage fills the area evenly.
  - Pick the tilt (≈ 0.6 rad) by trying 2–3 values on 2–4 representative steps.
- **One identical crop for all steps.** Take the union of the content boxes. Consecutive slides then overlay exactly.
- **Enlarge the key panel.** E.g. the δ transition table ×1.42, beside the stage.
  - Wrap the panel's draw function in a cairo transform (translate, scale about its corner).
  - Inverse-map the node anchor points passed in for the tethers, so the node → row lines still land on the right rows.
  - Apply the same transform to any overlay that redraws rows.
- **Drop small insets** (e.g. a tiny search-tree PiP) when they add height but little information.
- **Small-text boost.** Multiply sizes under 20 units by about 1.15–1.25, in `text` and `measure` alike.
  - Guard against double scaling: `text()` calls `measure()` internally.
  - Then fix the collisions the boost causes: move pill labels clear of node rings, turn a hint into a filled chip so it reads over faded geometry, give a table card room for its bottom label.
- **Off-canvas content.** When the film camera pushes content off-frame, render on a margin canvas (e.g. +300 units on every side) and crop by content.
- **Every pruning case gets a figure,** in the case study: wrong output, entry conflict, and the requested non-convergence. The last one was a **hand-built, labelled** candidate table (δ(00,11)=01, δ(00,01)=11 → 11 → 01 → 11 …), because the re-implementation can never produce it (0 cases in 2-bit, 0 in 3M nodes of 3-bit).

## Slide contrast (default on)

Film frames are watched full-screen; slides are seen small and projected. `figkit` therefore defaults to the following (set `FK.BOLD["stroke"] = 1` and `FK.BOLD["text_k"] = 1` for the film's original weights):

- **Strokes:** 1.5× thicker; arrowheads 1.3× larger.
- **Faded strokes and text:** alpha → alpha^0.6 above 0.12. Near-invisible layers such as trails are untouched, and fills keep their tint.
- **Greys:** `use_contrast()` darkens DIM to #C2CBD2 and GRAPHITE to #4B5967. Call it before loading the film.
- **Text:** one weight up (Light → Regular, Regular → Medium; hero numbers ≥ 40 u stay Light) and 8 % larger. Re-check collisions afterwards; e.g. stack an exponent's approximation under the hero number instead of beside it.

## Mechanism stages as slides
- Drop HUD panels that the slide does not need (an outcome table that another figure already shows): the stage gains the width that boosted text needs. Assign the HUD function a no-op for that export only.
- Boosting small text is only safe when the scene's offsets are computed from measured sizes; otherwise fix the scene (compute positions from `text_w` / `eff`, let boxes grow to hold their contents), not the figure. Figure-only patches are for figure-only choices (a still has no replay rate; a counter duplicated by a header can go).
- Lint (text >= 9 pt) and look: render every figure to JPEG and inspect it for collisions; lint cannot see overlaps.

## Export and verify

- **PNG:** render at 3× with a 300 dpi tag, crop to the content box plus padding, white background.
- **SVG and PDF:** draw the same function on cairo SVG/PDF surfaces, cropped to the same box.
  - Numpy raster layers cannot be vector. Embed them as images, or export those panels as PNG only, and say so.
- **Verify the vectors.** Rasterize every PDF (`pdftoppm -r 20`) and SVG (`cairosvg`), tile them next to the PNGs, and look.
- **Fonts.** `pdffonts *.pdf | awk '{print $1}' | sort | uniq -c` shows which faces are embedded.
  - With cairo's toy font API, "Inter" resolved to **Inter-Medium** (the Medium file also lists the style "Regular").
  - Fix: `setup_fonts.py` installs a renamed copy, "Inter Regular", and the figures use that name.
- **Chat previews.** Chat uploads may cap images at about 8000 px per side. Send downscaled previews; the originals go in the zip.

## README for the figure set

Include:
- the figure table (file, film time or "purpose-built", content);
- the data values used (e.g. the Pareto-front coordinates and the bar counts);
- the marker legend, if the figure omits it;
- the text policy;
- every illustrative element and caveat;
- the regenerate commands;
- the statement that the film source is unmodified.

## Layout recipes (proportions that worked; design units in a 1920-wide space)

The reference implementation is `examples/bflex/figs/design.py` (motivation, key result) and `make_figs.py` (steps).

**Type scale for a figure placed ~12 in wide.** 1 unit ≈ 0.5 pt.

| Use | Size (units) | Font |
|---|---|---|
| Hero numbers | 50–64 | Inter Light |
| Exponent / approximation | 34 | Inter Light |
| Axis names, signal names | 21–32 | Inter Medium |
| Tick and value labels | 19–22 | Inter Regular |
| Eyebrow labels ("3-BIT STATE") | 14–18 | Inter Medium, amber, tracking .14 |
| Absolute minimum | 18 | — |

**Motivation figure (two problems in one figure).**
- **Left ≈ 55%:** the failing waveform, with the failure annotated.
  - Signal rows 135 apart, amplitude ±32, stroke 3.2.
  - Transition markers in a row above, ✓ or ✗ beside each; one coral annotation above the failing marker.
  - "expected" (blue dashed) and "actual output" (coral) labels at the line ends, inside the plot. No separate legend.
- **Thin divider** (DIM).
- **Right ≈ 40%:** the small state graph → arrow → the larger state graph (the larger one drawn ≈ 2× the size).
  - Under each: an eyebrow label, the hero count and the approximation, all baseline-aligned.
  - One coral line for the brute-force estimate.
- Also export each half on its own.

**Key-result strip (scale → mapping → selection → trade-off).**
- **Common baseline.** All panels share one baseline (y ≈ 640), and their top labels share one line.
- **A. Scale.** A 390-unit block (light-teal gradient) with the hero count above it.
  - The tiny comparison set goes inside a magnifier lens (r ≈ 82) on a corner dot; never draw it to true scale.
  - The lens is drawn *after* the trails.
- **B. Mapping.**
  - Unit histogram: 6 cells per row, pitch 8.6, cell 7, bar gap 10; counts above the bars; the axis variable as a subscript label.
  - Trails from dots in block A to their histogram cells: one bezier each, alpha .05.
  - The total (hero, teal) sits top-left of the panel.
- **Selection.** A small amber block (4 × 5 cells) for the sampled subset, with its count above. Arrows link B → selection → C; no extra text.
- **C. Trade-off.** The scatter, with axes and three ticks per axis.
  - Pareto front as an amber dashed staircase plus rings.
  - Only the headline items are labelled (e.g. FF1, TGFF); the legend lives in the README or the slide.
- **Size.** The overall aspect ≈ 3:1 is fine for a full-width results slide. Use separate panels for smaller slots.

**Step sequence.**
- **Stage ≈ 68% / table ≈ 30%.** Stage on the left; the key table (×1.42) at the right, its top aligned with the stage's top row.
- **Same frame for every step.** One camera, one crop.
- **Distinct cases stand alone.** Every distinct case (e.g. each pruning rule) gets its own figure, plus a "before" figure where the comparison helps.
