# B-Flex V5: scientific verification report

**Authoritative reference.** H. Jeong, K. Kang, W. Jung, J. Lee, *B-Flex: Exploration of Broader Flip-Flop Design Space Based on FSM Exhaustive Search*, DAC 2026 (7 pages). All seven pages were read column by column, including Figs. 1–8, Tables 1–2 and all footnotes. Figure 2, Figure 4, Figure 5 and Fig. 8f were also checked as rendered images.

**What was inspected.**

- **The V4 film as delivered** (`BFlex_DAC2026_film_v4_1080p60.mp4`):
  - one frame per second (116 frames), reviewed on contact sheets;
  - a narration transcript taken by ASR from the file's own audio track (`v5audit/v4_transcript_asr.txt`);
  - an inventory of every string drawn on screen, with first appearance and readable duration (`docs/audit_v4.json`, 257 strings).
- **The V5 film:** see Pass 2.

All timestamps below are on the **V5 clock (119.1 s)**.

**Classes.**

| Class | Meaning |
|---|---|
| **V** | verified against the paper |
| **TI** | technically incorrect |
| **PM** | potentially misleading |
| **AMB** | ambiguous |
| **CV** | conceptual visualization: an abstraction that preserves the stated relation |
| **NV** | not verifiable from the paper: recomputed with our re-implementation of the method, and labelled as such |

---

## Pass 1: Scientific review, evidence table

### Act I: the challenge (0:00–0:28)

| V5 time | Claim (narration *italic*, on-screen `code`) | Visual | Paper | Class | Correction |
|---|---|---|---|---|---|
| 0:00.5 | *A flip-flop has one job: on a rising clock, capture D and hold it.* | D/CK/Q waveform | §3.1.1 Example: R = MSB(i′) on CK 0→1, otherwise hold | V | — |
| 0:01.6–0:09 | *This one, from the earlier tool SeGen, passes its test vector.* Checks ①–⑥ ✓ | Original Fig. 2 sequence: CK↓, CK↑, D↑, CK↓, CK↑, then ⑥ | §2, Fig. 2 (the original vector passes) | V | — |
| 0:09.9–0:14 | *Change one transition, and it outputs zero where it must output one.* `D 1→0 replaces CK 1→0`; `expected Q` (blue, dashed, stays 1), `SeGen-20 output` (red, falls to 0) at ⑥ | Modified vector, wrong Q at transition 6 | §2: "changing the 6th transition from CK: 1 → 0 to D: 1 → 0 triggers an incorrect next output"; Fig. 2 "Wrong Q" at ⑥ | V | — |
| 0:15–0:18 | *A flip-flop can be modeled as a state machine.* SeGen-20's states fly into the 2-bit square | State sequence re-simulated from the Fig. 2 table | §3.1.2 (FF modeled as an AFSM) | V (narration); NV (re-simulated states) | **V4 said "Every flip-flop *is* a state machine"**: PM, corrected |
| 0:18–0:23 | *With three state bits, candidate tables exceed ten to the nineteenth.* `4^32 ≈ 1.8 × 10^19 candidate transition tables · 4 inputs × 8 states = 32 entries · hold or flip one bit` | 3-bit cube | Table 1 footnote (search-space ratio 4³²/3¹⁶), §4.1 (≤ 1 bit flip) | V | — |
| 0:21–0:25 | `Prior automated FF search stops at 2-bit states.` | text | Abstract; §1 ("constrained to 2-bit FSMs only") | V | — |
| 0:21–0:25 | `Brute force, 1 thread: ~10^6 years (extrapolated, Table 1)` (under the `3-bit state` heading) + *Beyond brute force.* | text | Table 1 (∼10⁶ years at 1 thread, ∼10⁵ at 16 threads; "conservatively extrapolated") | V | **V4 omitted "1 thread"**: incomplete (PM), corrected |
| 0:25–0:28 | `B-Flex` · `Validate every input order. Prune while you generate.` · *B-Flex starts from behavior instead.* | title | §2 end ("validate … across all feasible input-transition orderings"); §3.2 (pruning during generation) | V | — |

### Act II: the reference and the candidate (0:29–0:48)

| V5 time | Claim | Visual | Paper | Class | Correction |
|---|---|---|---|---|---|
| 0:29–0:34 | `Reference Behavior Graph · the complete specification of a positive-edge D flip-flop`; `node = (D, CK, Q) · edge = one input pin changes · amber = rising clock edge, the only edge that may change Q`; *Its reference behavior graph covers every input order a D flip-flop must handle.* | 8 nodes, 16 edges | §3.1.1: Vt = I × O; edge iff (i, i′) ∈ A and o′ = R; A = 8 single-pin transitions; Fig. 1A | V (topology recomputed from A and R; matches Fig. 1A) | — |
| 0:34.5–0:37.5 | *The failing sequence is one path through it.* Markers ①–⑥ replay Act I's modified vector | Path (01,0)→(00,0)→(01,0)→(11,0)→(10,0)→(11,1)→(01,1) | Fig. 2 modified vector; RBG definition | V (every step asserted to be an RBG edge in code) | — |
| 0:37.5–0:42 | *… and the graph requires Q to stay at one, where SeGen-20 gave zero.* `reference: Q = 1` (blue) / `SeGen-20 output: Q = 0` (red) at node 011 | Labels readable for 4.6 s (V4: 0.55 s in v3) | §2, Fig. 2 | V | **V4 narration said "where SeGen gave zero"**, attributing the failure to the tool (PM), corrected. The brief's example label was already fixed in V4 |
| 0:42–0:48 | `Candidate ESTG, lifted above the reference · slots for stable input–state pairs (i, s), each over the reference node (i, λ(s)), with λ(s) = ¬s1`; callouts `Q = 0 → states with ¬s1 = 0 : 01, 11` / `Q = 1 → … : 00, 10` | Floor = RBG (8 nodes); lifted plane = 16 input–state slots; struts = λ | §3.1.3: ESTG nodes are stable (i, s), edges via StableSucc; rule (1): each ESTG edge needs a matching RBG edge (i, λ(s)) → (i′, λ(s′)); §3.2.2 (λ = ¬s1 in the 2-bit example) | CV (the lifting is a picture of the λ-mapping). The two graphs are shown as different structures: 16 vs 8 nodes, related by λ, not identical | **V4 header said "Candidate FSM" and "its states"** and never named the ESTG or *stable* pairs (PM for the RBG/ESTG distinction). Corrected |
| 0:42–0:48 | *Candidates grow one stable transition at a time, and each must match an edge of the reference graph.* | lift, callouts | §3.1.3 (stable transitions, StableSucc), §3.2.1 ("expands the graph one edge at a time"), rule (1) | V | **V4: "Candidates grow edge by edge; each edge must map onto the graph"** gave no notion of stability (PM), corrected |

### Act III: one worked example (0:48–1:16)

| V5 time | Claim | Visual | Paper | Class | Correction |
|---|---|---|---|---|---|
| 0:48–0:51 | `STEP 1 · start from a stable input–state pair`; `s = 11 · Q = ¬s1 = 0`; `stable: δ(01, 11) = 11`; δ row 7 | Init node + table | §3.2.2 ①: (i_init, s_init) = ((0,1),(1,1)); Fig. 4 Depth 0 entry 0 1 1 1 → 1 1 | V | — |
| 0:52–0:55 | `CK falls → Q must stay 0`; *Here the clock falls, so Q must stay at zero.* | Floor edge (01,0)→(00,0) lit | R (CK falling: hold) | V | — |
| 0:54–0:59 | Four destinations under i′ = 00 proposed; 00 and 10 (`Q = 1`) red, `no reference edge`, `wrong output → branch pruned`; *Two candidate states would output one, so those branches are pruned.* | Group X: 01 and 11 survive | §3.2 (i)(b–c), the pruning summary ("Wrong output … detected during transition-destination discovery"), Fig. 4 (red "Wrong Output" branch at the X junction) | V. The rejected states are drawn explicitly, as in Fig. 4's red branch | — (V4 wording polished) |
| 0:59–1:01.5 | `STEPS 3–4 · infer δ entries · no contradiction → both branches kept · the check repeats`; δ rows X1.a, X2.a, X2.b | X1 stays at 11; X2 passes 11 → 01 | §3.2.2 ③–④: X1.a δ(00,11) = 11; X2.a δ(00,11) = 01; X2.b δ(00,01) = 01; "both choices produce valid successor nodes" | V. The film then follows X1 for three more stable edges: the first is Fig. 4's Y1 (δ(11,11) = 11); the next two are recomputed | — |
| 1:03–1:08 | `CK rises with D = 1 → Q must become 1`; `infer δ(11,01) = 11`; `path needs δ(11,11) = 10` ≠ `earlier edge fixed δ(11,11) = 11`; δ row 15 red; `branch pruned`; *Deeper in, a settling path needs a table entry that an earlier transition set differently. That entry conflict prunes the branch.* | Depth-5 conflict on the X1 branch | Pruning summary "Entry conflict: inferred next state entries assign different values to the same (i, s) entry"; §3.2 (ii) | V (mechanism); NV (this specific conflict). It is a real conflict in the re-implemented search tree (path 241→281→283→285→495). **It is not Fig. 4's example**: Fig. 4's entry conflict is branch Z2 at depth 3 (δ(01,11) = 01 vs INIT δ(01,11) = 11) | **V4 tag "§3.2 · Fig. 4 · recomputed" implied that all five steps were Fig. 4's (PM).** Tag now reads `§3.2 · steps 1–3 as in Fig. 4 · steps 4–5 recomputed with the method`. V4 narration "a path needs an entry that an earlier edge already fixed" did not say the values differ (AMB), corrected |
| 1:11–1:16 | Full 2-bit search tree; `18 valid 2-bit-state FSMs`; `416 pruned branches`; `384 wrong output · 32 entry conflict` / `0 non-convergence · 680 nodes · depth 13` | Real tree | Table 1 (18 valid); pruning summary (three conditions) | V (18); NV (the tree statistics are recomputed and labelled `tree recomputed with the method`) | **The three pruning conditions were not distinguished on screen in V4**; the breakdown was added. **Doc error:** V3/V4 `VERIFICATION.md` said "681 nodes"; the data and the screen say 680. Doc fixed |
| 1:13–1:16 | `2-bit runtime (Table 1) · brute force 162 s → B-Flex 0.00784 s · 2.07 × 10^4× faster`; *Pruning early makes the two-bit search twenty thousand times faster than brute force.* | text | Table 1 (2-bit, 1 thread, measured, average of 5 runs) | V ("twenty thousand" rounds 2.07 × 10⁴) | — |

### Act IV: scale (1:16–1:30)

| V5 time | Claim | Visual | Paper | Class | Correction |
|---|---|---|---|---|---|
| 1:16–1:22 | Counter to `568,832,054 valid 3-bit-state FF FSMs`; *At three state bits, B-Flex finds all 568 million valid state machines in its search space* | Unit chart, 1 cell = 1 FSM, exact count at every frame | Abstract, §1, §4.1, Table 1 | V (exact value; cell order is arbitrary and labelled so) | **V4 "568 million valid behaviors" had no scope** (PM). Corrected, and the constraints added on screen (next row) |
| 1:21–1:25 | `vs. 18 at 2-bit state`; `exhaustive search · 787 s · 16 threads (Table 1)`; `average of 5 runs`; `§4.1 search space: Q = ¬s2 · initial state 011 · ≤ 1 bit flip per transition`; *in about thirteen minutes* | text | Table 1 (787 s, 16 threads; footnote: average of 5 runs); §4.1 (Q = λ(s) = ¬s2; (s0, s1, s2) = (0, 1, 1); ≤ 1-bit flips) | V | **V4 showed "786 s"** (the §4.1 text value); Table 1 gives 787 s. Internal inconsistency in the paper (AMB, see §R). V5 cites Table 1 explicitly. "About thirteen minutes" holds for both |
| 1:25–1:30 | `468 · valid FSMs with C_FF ≤ 20`; Fig. 5 histogram 1, 1, 10, 7, 23, 24, 76, 101, 225 (C_FF 12…20); `logic complexity C_FF (literals + product terms, min. SOP)` | unit histogram | §4.2: C_FF = n_P + n_SOP; threshold ≤ 20 → 468; Fig. 5 | V (bar values read from the Fig. 5 image; sum = 468) | — |
| 1:28–1:33 | `20 sampled → transistor-level schematics · known 2-bit-state FFs excluded · 28 nm CMOS · SPICE`; *Twenty of the 468 simplest were sampled and turned into transistor-level schematics.* | 20 amber cells in an unordered block | §4.2 last sentence; §4.3 | V | **V4: "Twenty of the simplest were synthesized into transistor-level circuits"** plus the label "20 synthesized to transistor level". This implied the 20 lowest-C_FF designs and omitted the sampling and exclusion (PM). Corrected in both |
| Act IV breadcrumb | `valid FSMs ▸ 468 simplest · C_FF ≤ 20 ▸ 20 transistor-level circuits ▸ FF1 vs. TGFF in SPICE`, tagged *behavior* / *circuit* | — | §4.1–4.3 | V. It separates mechanisms, selected candidates, synthesized circuits and simulated implementations; nothing implies all 568M were synthesized | — |

### Act IV: FF1 and circuit results (1:33–1:53)

| V5 time | Claim | Visual | Paper | Class | Correction |
|---|---|---|---|---|---|
| 1:33–1:40 | `FF1 · its FSM — published transition table (Fig. 8f)`; state readout; capture 101 → 100 → 000, `Q = ¬s2`; *One of them is FF1. When the clock rises, its state settles in two steps, and Q flips on the first.* | 3-bit cube; teal = settling paths | Fig. 8f FF1 row ((1,1): 5 → 4 → 0); §4.1 (Q = ¬s2) | V (replayed from the table; validated against the RBG). The initial input (0,1) is our assumption (§R) | **V4: "captures data in two state steps"** (AMB: Q changes at the first step, not after two). Corrected. The narration now names the clock edge it describes, and the timing was adjusted so "rises" coincides with the capture (V4 spoke it over a falling clock) |
| 1:40–1:42 | `Sequencing overhead = T_setup + T_CK→Q`; `two circuits · 28 nm CMOS · 0.9 V · FO4 load · SPICE · worst-case D transition`; `B-Flex · 32 T` / `baseline · 24 T`; *In SPICE, at 0.9 volts* | race start line | §4.3 (28 nm, min. length, Wp = 2·Wn, FO4, worst-case D transition); §4.4 (metric definitions); Table 2 (32 vs 24 T) | V | — |
| 1:41.6–1:44 | Bars grow at the same rate (`20 ps per second of film`); FF1 stops at `19.1 ps`, TGFF at `48.2 ps` | race (picture-clock slope 1.00) | Table 2 | V; CV (time-scaled bars) | — |
| 1:44.6–1:48.6 | `2.53× lower sequencing overhead than TGFF · 19.1 ps vs. 48.2 ps`; *its sequencing overhead is 2.53 times lower than a transmission-gate flip-flop's* | reveal | Abstract; Conclusion; Table 2 (48.2/19.1 = 2.524, stated as 2.53×) | V. The metric is sequencing overhead, never CK-to-Q alone or "faster" in general | — |
| 1:48.6–1:53 | `The cost: energy vs. sequencing overhead · all 18 flip-flops of Table 2 · 0.9 V · energy at 10% data activity · FF1 2.26 fJ vs. TGFF 1.53 fJ`; *at a higher energy cost.* | scatter: 5 B-Flex, 9 recent FFs [2,5,7,9,12,14,16,23,24], 3 SeGen [10], TGFF | Table 2 (energy row), §4.3 (10% data activity) | V | **"Energy at 10% data activity" was missing in V4**; added |
| 1:48.6–1:53 | `at 0.4 V: FF6 is 1.71× faster than TGFF, with a 3.00× narrower metastability window` | footnote | §4.4; Table 2 at 0.4 V (0.74/0.43 = 1.72, stated 1.71×; 0.18/0.06 = 3.00) | V. Metastability window = setup + hold, not race immunity | — |
| — | No claim that FF1 has better race immunity (19.5 vs 37.8 ps), lower energy, or fewer transistors (32 vs 24) than TGFF. No reliability claim | — | Table 2; §4.4 (FF1's race immunity is superior only to the pulsed latches [7, 23]) | V (by omission) | — |
| 1:53–1:59 | Title, authors, venue, DOI; *B-Flex: a broader flip-flop design space, searched exhaustively.* | title card | paper header | V. "Exhaustively" is qualified by L13's "in its search space" | **Sync:** in V4, "B-Flex" was spoken over a blank frame before the title faded in. The title now fades in faster and the line lands on it |

---

## Mandatory checks (brief Part III)

| Check | Result |
|---|---|
| **A. SeGen-20 counterexample** | Original and modified sequences are correct (6th transition CK 1→0 replaced by D 1→0). Expected Q holds at 1 while SeGen-20 drops to 0, and the failure is marked at ⑥. The single-sequence limitation is shown by L02/L03 and resolved by L07/L08. The narration attributes the failure to SeGen-20 only (L08 corrected) |
| **B. RBG vs ESTG** | The RBG has observable (D, CK, Q) nodes and admissible input edges. The ESTG is drawn as a separate, lifted structure of input–state pairs mapped down by λ, now named "Candidate ESTG". The two are never shown as identical. The paper's term ESTG is used; "ESG" removed from the pronunciation guide |
| **C. StableSucc** | The narration speaks of *stable* transitions and *settling* paths (L09, L11, L15). Transient steps are shown as settling paths: the X2 path 11 → 01 in the δ table; FF1's 101 → 100 → 000. No claim of electrical correctness beyond the FSM model |
| **D. Search and pruning** | Discovery → instantiation → δ inference follows Fig. 4 for steps 1–3. Wrong output (step 2) and entry conflict (step 5) are shown as distinct mechanisms. Non-convergence is now named in the tree breakdown (0 cases in the 2-bit search). The step-5 conflict is real but not Fig. 4's; now labelled |
| **E. Exploration scope** | 568,832,054 is exact, with the §4.1 constraints on screen and "in its search space" in the narration. 3-bit = three internal state bits. Table 1 runtimes: 18 valid (2-bit); 787 s with 16 threads. Brute force is labelled "extrapolated" |
| **F. Complexity and implementation** | C_FF = n_P + n_SOP; ≤ 20 → 468. 20 sampled, excluding known 2-bit FFs → schematics → SPICE (28 nm). Nothing implies that all FSMs were synthesized, or that any result is measured silicon |
| **G. FF1 vs TGFF** | 2.53× applies to sequencing overhead (T_setup + T_CK→Q) at 0.9 V, 19.1 vs 48.2 ps. The energy cost is shown and spoken. 32 vs 24 transistors are on screen. There are no race-immunity, energy or area claims in FF1's favour |
| **H. Reliability** | The film makes no reliability claim. Fig. 6 (5k-run Monte Carlo) is not depicted, so there is nothing to over-generalize |

---

## Technical inaccuracies identified in V4 and corrected in V5

1. **L08** attributed the wrong output to "SeGen" (the tool) instead of SeGen-20 (one design). *PM → fixed.*
2. **L09** described edge-by-edge growth with no notion of *stable* transitions or of matching an RBG edge. *PM → fixed.*
3. **L11** said a path needs an entry an earlier edge "already fixed", without saying the values differ. *AMB → fixed.*
4. **L13** said "568 million valid behaviors" with no scope; the count is of FSMs under the §4.1 constraints. *PM → fixed in narration; constraints added on screen.*
5. **L14 and the block label** said "twenty of the simplest were synthesized into … circuits". The 20 were *sampled* from the 468 after excluding known 2-bit FFs, and became schematics. *PM → fixed.*
6. **L15** said "captures data in two state steps", but Q changes at the first step. *AMB → fixed. The capture is also re-timed so "rises" coincides with the rising clock on screen.*
7. **L04** said "Every flip-flop *is* a state machine"; the paper *models* candidates as AFSMs. *PM (minor) → fixed.*
8. **On screen, "786 s · 16 threads":** Table 1 reports 787 s. Now `787 s · 16 threads (Table 1)`; the discrepancy is listed in §R.
9. **On screen, brute-force ~10⁶ years:** the single-thread condition was missing. *Fixed.*
10. **On screen, "Candidate FSM … its states":** now "Candidate ESTG … slots for stable input–state pairs (i, s) …" *Fixed.*
11. **On screen, the source tag over steps 1–5 implied they were all Fig. 4.** Now separates Fig. 4 (steps 1–3) from recomputed steps 4–5. *Fixed.*
12. **On screen, pruning conditions not distinguished.** `384 wrong output · 32 entry conflict` / `0 non-convergence` added. *Fixed.*
13. **On screen, energy condition missing.** "energy at 10% data activity" added. *Fixed.*
14. **Documentation:** "681 nodes" in `VERIFICATION.md` corrected to 680, matching the data and the screen. "ESG / ESTG" in the pronunciation guide corrected to ESTG.
15. **Synchronization:**
    - "B-Flex" (L18) was spoken before the title appeared.
    - "pruned" (L10) was spoken after the pruning label had gone.
    - "When the clock rises" (L15) needed to land on the capture.
    *All three fixed (see Pass 2).*

## §R. Remaining ambiguities that the paper does not resolve

1. **786 s vs 787 s.** §4.1 says 786 s; Table 1 lists 787 s for 16 threads (both are averages of 5 runs). V5 shows Table 1's value and says "about thirteen minutes".
2. **"7 orders of magnitude" (§1)** vs Table 1, which reports the 3-bit speedup as N/A because the brute-force baseline is extrapolated. The film makes no orders-of-magnitude speedup claim for 3-bit; it states only the measured 2-bit speedup.
3. **3-bit initial input.** §4.1 fixes the initial *state* (011) but not the initial input. FF1's replay assumes (D, CK) = (0, 1), as in the 2-bit example; FF1 is stable at ((0,1), 011) under its table.
4. **Wrong-output pruning, two descriptions.** §3.2 (i)(c) collects only states with λ(s′) = o′, so wrong outputs are never queued. The pruning summary and Fig. 4 instead present wrong output as a pruned branch detected during discovery. The film follows Fig. 4 and shows the rejected states explicitly.
5. **"Outperform TGFF in both speed and reliability" (§1).** For FF1, Table 2 race immunity (19.5 ps) is below TGFF's (37.8 ps). Which B-Flex FFs the sentence refers to is not specified. The film makes no reliability claim.
6. **Rounded ratios.** 48.2/19.1 = 2.524 and 0.74/0.43 = 1.72 recompute slightly differently from the paper's 2.53× and 1.71×. The paper presumably used unrounded SPICE values. The film quotes the paper's figures.
7. **C_FF of FF4 and FF5.** Recomputed from the Fig. 8f tables, it exceeds 20 (29 and 22) under our minimum-SOP convention. This may come from a different literal-count convention or don't-care handling. The film shows no per-FF C_FF.
8. **The step-5 conflict and the tree statistics** (680 nodes, depth 13, 384/32/0) come from our re-implementation; the paper does not print them. They are labelled "recomputed".
9. **SeGen's pronunciation** is not documented by its authors. "See-Jen" is our choice.

---

## Pass 2: Language and production review of the rendered V5

Everything below was checked on the **rendered output files** in `out/final_v5/`, not on the source.

### What was inspected

- **Frames.**
  - One frame per second of the 1080p file (119 frames), reviewed on contact sheets (`v5audit/v5sheet_*.png`).
  - Full-resolution crops of every new or changed on-screen label, taken from the final 4K file.
- **Words.** The delivered audio track was transcribed by an independent ASR model, cue window by cue window, and compared with each subtitle cue (`narration/srt_check.py`; result in `v5audit/v5_subtitle_vs_audio.txt`).
- **Readability.** The V5 timeline was re-audited (`docs/audit_v5.json`): 259 strings. The only ones readable for less than 2.5 s are FF1's live state readouts, which change with every step by design.
- **Files.** Streams, frame counts and loudness of every delivered file:

| File | Video | Frames | Duration | Audio | Integrated | True peak | LRA |
|---|---|---|---|---|---|---|---|
| BFlex_DAC2026_film_v5_4K60_master.mov | h264,3840,2160,60/1 | 7146 | 119.100000 s | pcm_s24le,48000 | -16.0 LUFS | -1.2 dBTP | 3.2 LU |
| BFlex_DAC2026_film_v5_4K60.mp4 | h264,3840,2160,60/1 | 7146 | 119.100000 s | aac,48000 | -16.0 LUFS | -1.2 dBTP | 3.2 LU |
| BFlex_DAC2026_film_v5_1080p60.mp4 | h264,1920,1080,60/1 | 7146 | 119.100000 s | aac,48000 | -16.0 LUFS | -1.2 dBTP | 3.2 LU |
| audio/BFlex_v5_mix.wav |  |  | 119.100000 s | pcm_s24le,48000 | -16.0 LUFS | -1.2 dBTP | 3.2 LU |

- **Picture.** 7146 frames = 119.1 s × 60 fps in all three video files.
- **Runtime.** 119.1 s, under two minutes. That is +2.8 s versus V4, spent only on holds that the longer, corrected sentences needed.
- **Subtitles.** The track embedded in both MP4s was extracted and compared with the `.srt`: 28/28 cues identical, with 0 ms timing difference.
  - The MP4 muxer marks the `mov_text` track as enabled, so some players show it by default.
  - The V4 notes said "off by default". That was not accurate, and is corrected here.

### Problems found in this pass, and fixed before delivery

1. **Subtitle cue boundaries drifted mid-sentence.** The V4 method split cues by character share. For example, "A flip-flop can be modeled as a state machine." ended before "state machine" was spoken. Cues are now timed by spoken-word count (`subtitles.py`, `n_spoken`). After the fix, every subtitle cue matches the delivered audio: the 26 word differences out of 281 are ASR spelling variants of the same sounds ("graf", "qu"/"u" for Q, "sea gen" for SeGen, "flipflop").
2. **The tree-HUD pruning breakdown ran off the right edge of the frame** ("… 0 non-conve"). It was split into two lines.
3. **The §4.1 search-space line touched the unit square.** It was shortened.
4. **The brute-force line sat 30 px from the frame edge.** It was shortened (the "3-bit state" heading above it carries the context).
5. **Sync.**
   - L10's "pruned" now lands while `wrong output → branch pruned` is still visible.
   - L15's "when the clock rises" now coincides with FF1's rising-edge capture (word at 1:35.3, capture 1:35.5–1:36.5). In V4 it was spoken over a falling clock.
   - L18's "B-Flex" now coincides with the title (the fade-in was shortened from 0.75 s to 0.40 s of animation time).

Fixes 2–4 were re-rendered (chunks 14.4–28.8 s and 57.6–86.4 s) and re-checked in the final 4K file.

### Narration continuity

- **Same voice.** The nine regenerated lines use the same voice, speed and front end as the nine reused V4 lines.
- **Loudness per line.** Reused lines: −22.2 ± 0.34 LUFS. Regenerated lines: −22.1 ± 0.23 LUFS.
- **Pitch.** Median F0 is 202 Hz (reused) vs 201 Hz (regenerated).
- **No splices inside sentences.** Every line is its own clip, separated by edited silence, so there are no splice points inside a sentence. The minimum gap between consecutive clips is 0.31 s.
- **Mix.** The mix chain is unchanged from V4: music ducked −9 dB and SFX −5 dB under speech; −16 LUFS; true peak −1.2 dBTP.

### Limits of this review

- **No human listening.** No one in this environment listened to the film with sound. Language quality was judged from the script, and intelligibility from ASR.
- **Not independent.** Both review passes were done by the same AI that produced the edits. They are not independent expert reviews.

