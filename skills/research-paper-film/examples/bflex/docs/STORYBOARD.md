# B-Flex — Storyboard & Timing Sheet (v3, comprehension cut)

**Runtime** 62.2 s · 3840×2160 · 60 fps · readable without audio.
All times are the constants at the top of `src/film.py` (the "timing sheet" block). `film.CUES` exports them to `src/audio.py`. Sources: § section · T table · F figure (see `VERIFICATION.md`).

## Editing rules

| Tempo | Used for | Examples |
|---|---|---|
| **Fast** | Repetition and scale | X1 links fast-forwarded (0.32 s each), remaining 2-bit tree (1.4 s), 568M fill (accelerating) |
| **Moderate** | Camera moves, changes of representation | Waveform → square → cube, graph → lifted candidate, cell → FF1 cube |
| **Slow** | Mechanisms and comparisons | Act I's reordered transition; Act I's vector replayed on the RBG; wrong-output pruning; entry conflict; the 2.53× reveal |

Every slow beat follows **anticipation → action → consequence → hold**. Camera moves, caption changes and new highlights never happen in the same instant: the camera settles first, then the caption, then the event.

**Persistent anchors.** The same numbered markers ①–⑥ appear on Act I's waveform and Act II's graph. One palette is used throughout: teal = valid, coral = pruned, amber = rising clock edge / inferred / headline. The δ table is fixed at screen right during Act III, and a tether links each node to the row it writes. The PiP search tree is the real tree. In Act IV a breadcrumb separates FSMs (behavior, teal) from circuits (SPICE, amber).

## Pacing map (what the viewer must understand before the next scene)

| t | Scene | Tempo | Must be understood before moving on |
|---|---|---|---|
| 0.8–4.0 | Test vector applied; six checks | moderate (tracking) | a single test vector passes |
| 4.0–4.5 | Rewind to ⑥ | anticipation | — |
| 4.5–5.2 | ⑥ becomes D 1→0; Q goes coral against expected Q | **action → consequence** | the same FSM fails another order |
| 5.2–6.05 | **Hold** | slow | — |
| 6.05–7.4 | Pull back; SeGen-20's states fly into the 2-bit square | moderate | these are the FSM's states |
| 7.5–8.25 | `3¹⁶ ≈ 4.3×10⁷` | hold | 2-bit search space |
| 8.25–8.85 | Extrude to 3 bits (no text change) | moderate | — |
| 8.85–10.05 | `4³² ≈ 1.8×10¹⁹` · prior search stops at 2-bit · brute force ~10⁶ years | hold | why 3-bit is hard |
| 10.05–11.9 | Collapse → **B-Flex** · tagline | moderate | — |
| 11.9–14.25 | Reference Behavior Graph builds (camera close → full) | moderate | nodes (D,CK,Q), edges = one pin change |
| 14.3–16.4 | **Act I's failing vector replayed** on the static graph, markers ①–⑥; step ⑤ amber (Q→1) | slow | the vector is one path through the graph |
| 16.4–17.15 | Consequence + hold: `reference: Q = 1` / `SeGen-20 output: Q = 0` | hold | the graph covers every input order |
| 17.15–19.0 | Tilt; nodes lift and split into states (struts = λ) | moderate | candidate states sit over the Q they output |
| 19.0–19.95 | Callouts `Q = 0 → 01, 11` · `Q = 1 → 00, 10`; δ panel slides in | hold | a candidate edge needs a reference edge beneath it |
| 19.95–21.85 | **STEP 1** start pair (01, 11) + tether to row 7 | moderate → hold | the starting point and its δ entry |
| 21.85–22.4 | Camera to step-2 framing | moderate | — |
| 22.4–23.05 | Anticipation: floor edge lit, `CK falls → Q must stay 0` | slow | the condition |
| 23.05–23.9 | Four candidate destinations proposed | action | — |
| 23.95–24.75 | Q = 1 candidates coral; ghost floor edge `no reference edge`; others dimmed | **consequence** | why they fail |
| 24.75–25.25 | Branches retract; PiP stubs coral; `wrong output → branch pruned` | decision | the search decision |
| 25.25–26.05 | **Hold** | slow | — |
| 26.05–28.9 | **STEP 3** X1 (stay 11) and X2 (11 → 01): two alternative values in row (00,11), tethers; `no contradiction → both branches kept` | moderate | instantiation = inferring δ entries |
| 28.9–30.2 | **STEP 4** X1 fast-forwarded: three real edges, each over a lit floor edge | **fast** | the check repeats |
| 30.2–30.85 | Camera push to the conflict region | moderate | — |
| 30.85–31.45 | Anticipation: amber floor edge `CK rises with D = 1 → Q must become 1`; unrelated nodes dimmed | slow | the condition |
| 31.45–32.95 | Path 01 → 11 (infer δ(11,01)=11, tether row 13) → needs 10 | action | — |
| 33.05–33.65 | Earlier edge L1 re-lit; `earlier edge fixed δ(11,11) = 11` ≠ `path needs δ(11,11) = 10`; row 15 coral ✕ | **consequence** | the contradiction and its dependency |
| 33.65–34.05 | Branch retracts; `branch pruned`; PiP node coral | decision | — |
| 34.05–34.7 | **Hold** | slow | — |
| 34.7–36.7 | PiP expands; remaining 2-bit tree grows | **fast** | repetition at scale |
| 36.7–37.95 | Hold: `18 valid FSMs` · 162 s → 0.00784 s | hold | — |
| 37.95–39.15 | 18 leaves become 18 cells | moderate | 1 cell = 1 valid FSM |
| 39.15–42.55 | **CLIMAX 1** — fill + exponential pull-back; counter = exact cells drawn | **fast, accelerating** | scale |
| 42.55–44.55 | Impact; square dims; number, `vs. 18`, `786 s · 16 threads` appear one by one | **hold (2 s)** | the magnitude |
| 44.55–46.65 | 468 FSMs (C_FF ≤ 20) as a unit histogram | moderate | simplest behaviors kept |
| 46.65–47.8 | Unordered block; 20 turn amber: `20 synthesized to transistor level` | moderate | FSM → circuit |
| 47.8–48.45 | Dive into FF1's cell | moderate | — |
| 48.45–51.6 | FF1's FSM (Fig. 8f): fast steps, slow capture 101 → 100 → 000 | moderate → slow | the mechanism found |
| 51.6–52.4 | Capture flash → race start line; layout and conditions | anticipation | what is measured, and how |
| 52.4–54.8 | Both circuits' overhead bars grow at 20 ps/s; FF1 stops at 19.1 ps; TGFF runs to 48.2 ps | action (static camera) | — |
| 54.9–55.35 | Bracket draws | consequence | — |
| 55.35–56.8 | **CLIMAX 2** — `2.53×` fades in · `19.1 ps vs. 48.2 ps` | **controlled reveal + hold** | significance, with conditions |
| 56.8–59.0 | Race axis becomes the Table 2 scatter: energy cost and all 18 FFs | moderate → hold | the trade-off |
| 59.0–62.2 | Title card | hold | — |

## Act IV breadcrumb
`valid FSMs (behavior) ▸ 468 simplest · C_FF ≤ 20 (behavior) ▸ 20 transistor-level circuits (circuit) ▸ FF1 vs. TGFF in SPICE (circuit)`. The current stage is lit; FSM stages are teal and circuit stages amber.

## Race conditions on screen (verbatim from §4.3 / Table 2)
`two circuits · 28 nm CMOS · 0.9 V · FO4 load · SPICE · worst-case D transition` · `FF1 · B-Flex · 32 T` · `TGFF · baseline · 24 T`.
