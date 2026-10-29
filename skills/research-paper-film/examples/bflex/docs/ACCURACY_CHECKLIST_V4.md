# B-Flex v4: technical accuracy checklist

v4 changes the clock, the look, the sound and the words. It does not change any data. Every graph, tree, table and number on screen is still produced by `src/bflex_model.py` / `data/scene_data.json`, or typed from the paper's tables. Those checks are in `VERIFICATION.md` (they still hold; its time codes refer to the v3 clock). This list covers what is **new in v4**: every narrated claim and every on-screen text added in v4.

Legend:

- ✅ checked against the paper, or recomputed.
- ⚠ wording chosen deliberately; see the note.

## A. Narration, line by line

| Line | Claim (as spoken) | Source | Check |
|---|---|---|---|
| L01 | A flip-flop's job: on a rising clock, capture D and hold it | §1; RBG definition §3.1.1 (R = D on CK↑) | ✅ positive-edge D-FF |
| L02 | "This one, from the earlier tool SeGen, passes its test vector" | §2, Fig. 2; SeGen = [10] | ✅ original vector Q = 0,0,0,0,0,1,1 matches (re-simulated) |
| L03 | "Change one transition, and it outputs zero where it must output one" | Fig. 2 modified vector | ✅ modified step 6: expected Q = 1, SeGen-20 gives 0 (re-simulated). On screen: "D 1→0 replaces CK 1→0" |
| L04 | "Every flip-flop is a state machine" | §3 | ✅ |
| L04 | "With three state bits, candidate tables exceed ten to the nineteenth" | §4.1 / Table 1 note: 4³² | ✅ 4³² = 1.845 × 10¹⁹ > 10¹⁹ (on screen: ≈ 1.8 × 10¹⁹) |
| L05 | "Beyond brute force" | Table 1: brute force at 3 bits ~10⁶ years (extrapolated) | ✅ on screen with "(extrapolated, Table 1)" |
| L06 | "B-Flex starts from behavior instead" | §3: behavior graph first, then FSM generation | ✅ |
| L07 | "Its reference behavior graph holds every input order a D flip-flop must handle" | §3.1.1: every admissible single-pin input change | ✅ |
| L08 | "The failing vector is one path through it" | asserted in `film.py` (every replay step is an RBG edge) | ✅ |
| L08 | "the graph demands Q = 1 where SeGen gave 0" | RBG node (01, Q=1) after CK↑ with D = 1; SeGen-20 step 6 | ✅ asserted |
| L09 | "Candidates grow edge by edge; each edge must map onto the graph" | §3.2, validation condition (1) | ✅ |
| L10 | "Here the clock falls, so Q must stay 0. Two candidates output 1. Wrong output: pruned." | §3.2.2, Fig. 4: of 4 destinations, 00 and 10 (Q = 1) are rejected | ✅ real first job group of the re-implementation |
| L11 | "a path needs an entry that an earlier edge already fixed. Entry conflict: branch cut." | §3.2.2 "entry conflict" | ✅ real depth-5 conflict: δ(11,11) needed = 10, fixed = 11 by edge (01,11)→(11,11) |
| L12 | "Pruning early makes the two-bit search 20,000 times faster than brute force" | Table 1: 162 s → 0.00784 s, 2.07 × 10⁴× | ✅ 162 / 0.00784 = 20,663; spoken rounded, exact on screen |
| L13 | "At three bits, B-Flex finds 568 million valid behaviors" | §4.1, Table 1: 568,832,054 | ✅ exact value on screen |
| L13 | "in about thirteen minutes" | §4.1 / Table 1: 786 s with 16 threads (average of 5 runs) | ✅ 786 s = 13.1 min; "16 threads" on screen |
| L14 | "Twenty of the simplest were synthesized into transistor-level circuits" | §4.2–4.3: 20 sampled from the 468 with C_FF ≤ 20 (known 2-bit FFs excluded), synthesized with the [10] flow | ⚠ "of the simplest" = of the 468 lowest-complexity FSMs. Exact selection rule is on screen in the breadcrumb |
| L15 | "One of them, FF1, captures data in two state steps" | Fig. 8f FF1 table: capture (CK↑, D = 1) walks 101 → 100 → 000 | ✅ two transitions, replayed from the table |
| L16 | "In SPICE, at 0.9 volts" | §4.3, Table 2 | ✅ conditions on screen: 28 nm CMOS, FO4, worst-case D transition |
| L16 | "its sequencing overhead is 2.53 times lower than a transmission-gate flip-flop's" | Abstract; Table 2: 19.1 ps vs 48.2 ps | ✅ 48.2 / 19.1 = 2.524, which the paper states as 2.53×. "lower sequencing overhead", never "faster" |
| L17 | "at a higher energy cost" | Table 2: FF1 2.26 fJ vs TGFF 1.53 fJ | ✅ numbers on screen |
| L18 | "a broader flip-flop design space, searched exhaustively" | title | ✅ |

## B. Keeping the two achievements apart

| Requirement | How v4 meets it |
|---|---|
| Scale (568M valid behaviors) is not a circuit claim | L13 says "valid behaviors", and the counter caption reads "valid 3-bit-state FF FSMs". The breadcrumb labels this stage *behavior* (teal) |
| Circuit performance belongs to FF1 only | L15 "One of them, FF1"; L16 "*its* sequencing overhead". The race shows only FF1 vs TGFF, labelled *circuit* (amber) in the breadcrumb |
| No implication that all mechanisms reach 2.53× | The scatter shows all 18 Table 2 FFs. The other B-Flex circuits sit at 31–61 ps, so the spread is visible. FF1's energy cost is spoken and printed |

## C. On-screen text added or changed in v4

| Text | Source | Check |
|---|---|---|
| "node = (D, CK, Q) · edge = one input pin changes · amber = rising clock edge, the only edge that may change Q" | §3.1.1 | ✅ |
| "Prior automated FF search stops at 2-bit states." / "Brute force at 3-bit: ~10⁶ years (extrapolated, Table 1)" | §1, Table 1 | ✅ (moved from the v3 caption band into the scene) |
| "2-bit runtime (Table 1) · brute force 162 s → B-Flex 0.00784 s · 2.07 × 10⁴× faster" | Table 1 | ✅ |
| "bars grow at the same rate: 20 ps per second of film" | construction (`V_PS = 20`, race segment at slope 1 in `edl.py`) | ✅ race segment slope verified = 1.00 in the timing sheet |
| "The cost: energy vs. sequencing overhead · all 18 flip-flops of Table 2 · 0.9 V · FF1 2.26 fJ vs. TGFF 1.53 fJ" | Table 2 | ✅ |
| "at 0.4 V: FF6 is 1.71× faster than TGFF, with a 3.00× narrower metastability window" | §4.4, Table 2 | ✅ 0.74/0.43 = 1.72 (paper: 1.71×); 0.18/0.06 = 3.00 |
| Scatter point labels "FF1 2.26 fJ", "TGFF 1.53 fJ" | Table 2 | ✅ |
| Step markers (STEP 1, 2, 3–4, 5) and their one-line titles | §3.2, Fig. 4 | ✅ |
| "expected Q" and "reference: Q = 1" now in blue (reference colour) | — | semantic colour only |

## D. Removed in v4 (and why)

| Removed | Reason |
|---|---|
| The bottom caption band (two-line sentences) | The narration and the SRT carry the sentences. Keeping both would duplicate the text and collide with subtitles. Every fact that existed only in a caption was moved into the scene (section C) |
| 2-bit search-space count (3¹⁶ ≈ 4.3 × 10⁷) | It was on screen for under 2.5 s, and the narration goes straight to the 3-bit count. Kept in `VERIFICATION.md` |
| On-graph tags "X1 stays at 11", "X2 11 → 01", "no contradiction → both branches kept" | They were visible for under 2.5 s. The STEPS 3–4 marker states the result ("no contradiction → both branches kept") for 3.5 s, and the δ table still shows the inferred entries |
| "s0 s1" row header during the Act I pull-back | Visible for 0.5 s. The same state labels appear on the square's nodes |
| Dot grid, glow, bloom, grain, vignette | white visual identity (brief) |

## E. Discrepancies carried over (for the authors)

These are unchanged from v3; see `VERIFICATION.md` §5:

- C_FF of FF4 and FF5 recomputes to more than 20.
- The 3-bit initial input is not stated in the paper.
