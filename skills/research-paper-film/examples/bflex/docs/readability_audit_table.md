| v3 time | label | v3 readable | v4 time | v4 readable | status |
|---|---|---|---|---|---|
| 0:01.60 | `A prior automated flip-flop search validates each candidate against a si` | 2.25 s | — | — | removed (narration / step marker carries it) |
| 0:01.60 | `One test vector. Six transitions. All pass.` | 2.25 s | — | — | removed (narration / step marker carries it) |
| 0:04.75 | `Reorder one transition, and the same design outputs the wrong Q.` | 1.60 s | — | — | removed (narration / step marker carries it) |
| 0:04.75 | `SeGen-20: a 2-bit-state FSM that passes its test vector, yet violates fl` | 1.60 s | — | — | removed (narration / step marker carries it) |
| 0:04.95 | `D 1→0 replaces CK 1→0` | 2.10 s | 0:12.10 | 4.15 s | fixed |
| 0:05.30 | `SeGen-20` | 1.75 s | — | — | removed (narration / step marker carries it) |
| 0:05.30 | `expected Q` | 1.75 s | 0:12.90 | 3.35 s | fixed |
| 0:06.65 | `s0 s1` | 0.40 s | — | — | removed (narration / step marker carries it) |
| 0:07.70 | `3^16` | 0.45 s | — | — | removed (narration / step marker carries it) |
| 0:07.70 | `4 inputs × 4 states = 16 entries · hold or flip one bit` | 0.45 s | — | — | removed (narration / step marker carries it) |
| 0:07.70 | `≈ 4.3 × 10^7` | 0.45 s | — | — | removed (narration / step marker carries it) |
| 0:07.80 | `Table 1 footnote · §1` | 2.00 s | 0:17.25 | 5.70 s | fixed |
| 0:09.00 | `Brute force at 3-bit state: ~10^6 years (extrapolated, Table 1).` | 0.95 s | — | — | removed (narration / step marker carries it) |
| 0:09.00 | `Prior automated FF search stops at 2-bit states.` | 0.95 s | 0:21.25 | 2.65 s | fixed |
| 0:09.05 | `4 inputs × 8 states = 32 entries · hold or flip one bit` | 0.95 s | 0:19.55 | 4.35 s | fixed |
| 0:09.05 | `4^32` | 0.95 s | 0:19.55 | 4.35 s | fixed |
| 0:09.05 | `candidate transition tables` | 0.95 s | 0:19.55 | 4.35 s | fixed |
| 0:09.05 | `≈ 1.8 × 10^19` | 0.95 s | 0:19.55 | 4.35 s | fixed |
| 0:11.15 | `Validate every input order.   Prune while you generate.` | 0.80 s | 0:25.60 | 2.65 s | fixed |
| 0:12.30 | `Nodes: (D, CK, Q).  Edges: one input pin changes.  Q may change only on ` | 1.75 s | — | — | removed (narration / step marker carries it) |
| 0:12.30 | `The reference: every admissible input change, and the Q it must produce.` | 1.75 s | — | — | removed (narration / step marker carries it) |
| 0:16.45 | `reference: Q = 1` | 0.85 s | 0:36.95 | 4.15 s | fixed |
| 0:16.75 | `SeGen-20 output: Q = 0` | 0.55 s | 0:37.25 | 3.85 s | fixed |
| 0:17.65 | `Candidate FSM, lifted above the reference` | 2.25 s | 0:41.50 | 5.05 s | fixed |
| 0:17.65 | `its states sit over the reference node whose Q they output: λ(s) = ¬s1` | 2.25 s | 0:41.50 | 5.05 s | fixed |
| 0:17.80 | `A candidate edge is valid only if a reference edge lies beneath it.` | 2.05 s | — | — | removed (narration / step marker carries it) |
| 0:17.80 | `B-Flex grows the candidate's state graph (ESTG) one stable edge at a tim` | 2.05 s | — | — | removed (narration / step marker carries it) |
| 0:19.20 | `Q = 0  →  states with ¬s1 = 0 : 01, 11` | 0.80 s | 0:43.45 | 3.30 s | fixed |
| 0:19.35 | `Q = 1  →  states with ¬s1 = 1 : 00, 10` | 0.65 s | 0:43.75 | 3.00 s | fixed |
| 0:20.70 | `(D, CK) = (0, 1), s = 11, Q = 0.  Its table entry δ(01, 11) = 11 says: s` | 1.05 s | — | — | removed (narration / step marker carries it) |
| 0:20.70 | `STEP 1` | 1.05 s | 0:47.20 | 2.60 s | fixed |
| 0:20.70 | `Start from a stable input–state pair.` | 1.05 s | — | — | removed (narration / step marker carries it) |
| 0:20.95 | `s = 11 · Q = ¬s1 = 0` | 0.80 s | 0:47.75 | 2.55 s | fixed |
| 0:20.95 | `stable: δ(01, 11) = 11` | 0.80 s | 0:47.75 | 2.55 s | fixed |
| 0:24.05 | `Q = 1` | 0.95 s | 0:54.05 | 3.80 s | fixed |
| 0:24.05 | `wrong output → branch pruned` | 0.95 s | 0:54.05 | 3.80 s | fixed |
| 0:24.10 | `no reference edge` | 1.00 s | 0:54.20 | 3.60 s | fixed |
| 0:26.75 | `STEP 3` | 2.05 s | — | — | removed (narration / step marker carries it) |
| 0:26.75 | `Transition instantiation: infer the δ entries for each choice.` | 2.05 s | — | — | removed (narration / step marker carries it) |
| 0:26.75 | `X1 stays at 11.  X2 passes 11 and settles at 01.  Neither contradicts δ,` | 2.05 s | — | — | removed (narration / step marker carries it) |
| 0:27.05 | `X1  stays at 11` | 1.75 s | — | — | removed (narration / step marker carries it) |
| 0:27.20 | `X1` | 1.60 s | — | — | removed (narration / step marker carries it) |
| 0:27.85 | `X2  11 → 01` | 0.95 s | — | — | removed (narration / step marker carries it) |
| 0:28.00 | `X2` | 0.80 s | — | — | removed (narration / step marker carries it) |
| 0:28.00 | `X2→01` | 0.80 s | — | — | removed (narration / step marker carries it) |
| 0:28.10 | `no contradiction → both branches kept` | 0.70 s | — | — | removed (narration / step marker carries it) |
| 0:29.35 | `Following X1: three more stable edges, each over a reference edge (fast-` | 0.80 s | — | — | removed (narration / step marker carries it) |
| 0:29.35 | `STEP 4` | 0.80 s | — | — | removed (narration / step marker carries it) |
| 0:29.35 | `The same check repeats, edge after edge.` | 0.80 s | — | — | removed (narration / step marker carries it) |
| 0:32.00 | `infer` | 1.95 s | 1:03.55 | 3.35 s | fixed |
| 0:32.00 | `infer δ(11,01) = 11` | 1.85 s | 1:03.55 | 3.25 s | fixed |
| 0:32.70 | `path needs δ(11,11) = 10` | 1.30 s | 1:04.30 | 5.05 s | fixed |
| 0:33.15 | `earlier edge fixed δ(11,11) = 11` | 0.85 s | 1:05.20 | 4.15 s | fixed |
| 0:33.15 | `≠` | 0.85 s | 1:05.20 | 4.15 s | fixed |
| 0:33.25 | `needs 10 · entry conflict` | 1.50 s | 1:05.40 | 4.30 s | fixed |
| 0:33.75 | `branch pruned` | 0.85 s | 1:06.75 | 2.60 s | fixed |
| 0:35.45 | `circled: the step-5 conflict` | 1.05 s | 1:10.40 | 2.75 s | fixed |
| 0:35.55 | `18 valid FSMs.  Brute force 162 s → B-Flex 0.00784 s (2.07 × 10^4×, Tabl` | 2.35 s | — | — | removed (narration / step marker carries it) |
| 0:35.55 | `Repeated over the whole space: the complete 2-bit search.` | 2.35 s | — | — | removed (narration / step marker carries it) |
| 0:35.60 | `Table 1 · tree recomputed with the method` | 2.10 s | 1:10.55 | 3.60 s | fixed |
| 0:38.70 | `1 cell = 1 valid FSM` | 1.65 s | 1:15.70 | 2.75 s | fixed |
| 0:38.70 | `18 valid FSMs` | 1.65 s | 1:15.70 | 2.75 s | fixed |
| 0:38.70 | `2-bit state` | 1.65 s | 1:15.70 | 2.75 s | fixed |
| 0:39.45 | `3-bit state` | 1.15 s | 0:19.55 | 4.35 s | fixed |
| 0:43.20 | `vs. 18 at 2-bit state` | 1.55 s | 1:21.05 | 3.00 s | fixed |
| 0:43.60 | `exhaustive search · 786 s · 16 threads` | 1.15 s | 1:21.20 | 2.85 s | fixed |
| 0:43.75 | `average of 5 runs · cell order is arbitrary` | 1.00 s | 1:21.40 | 2.60 s | fixed |
| 0:45.10 | `C_FF counts literals and product terms of the minimum sum-of-products.  ` | 1.35 s | — | — | removed (narration / step marker carries it) |
| 0:45.10 | `Rank the valid FSMs by logic complexity; keep the simplest.` | 1.35 s | — | — | removed (narration / step marker carries it) |
| 0:45.20 | `§4.2 · Fig. 5` | 1.20 s | 1:24.95 | 2.95 s | fixed |
| 0:45.80 | `1 cell = 1 FSM` | 1.15 s | 1:25.70 | 2.55 s | fixed |
| 0:45.80 | `logic complexity C_FF (literals + product terms, min. SOP)` | 1.15 s | 1:25.70 | 2.55 s | fixed |
| 0:45.80 | `valid FSMs with C_FF ≤ 20` | 1.15 s | 1:25.70 | 2.55 s | fixed |
| 0:46.95 | `20 of them become circuits.` | 0.90 s | — | — | removed (narration / step marker carries it) |
| 0:46.95 | `Sampled from the 468 (excluding known 2-bit-state FFs), synthesized to t` | 0.90 s | — | — | removed (narration / step marker carries it) |
| 0:47.05 | `§4.2 · §4.3` | 0.70 s | 1:28.30 | 2.50 s | fixed |
| 0:47.35 | `20 synthesized to transistor level` | 0.60 s | 1:28.45 | 2.80 s | fixed |
| 0:47.35 | `28 nm CMOS · simulated in SPICE` | 0.60 s | 1:28.45 | 2.80 s | fixed |
| 0:48.95 | `Q = ¬s2 = 0` | 1.85 s | 1:32.25 | 2.20 s | dynamic readout (by design) |
| 0:49.10 | `FF1's FSM: an extra internal state settles in steps before Q captures D.` | 2.30 s | — | — | removed (narration / step marker carries it) |
| 0:49.10 | `Replayed from its table: on the rising edge with D = 1 the state walks 1` | 2.30 s | — | — | removed (narration / step marker carries it) |
| 0:49.15 | `(D, CK) = 0 0` | 0.35 s | 1:32.50 | 0.35 s | dynamic readout (by design) |
| 0:49.15 | `Fig. 8f · validated against the RBG` | 2.15 s | 1:32.50 | 2.55 s | fixed |
| 0:49.30 | `s0 s1 s2 = 111` | 0.35 s | 1:32.65 | 0.35 s | dynamic readout (by design) |
| 0:49.50 | `(D, CK) = 0 1` | 0.35 s | 1:32.85 | 0.35 s | dynamic readout (by design) |
| 0:49.65 | `s0 s1 s2 = 011` | 0.65 s | 1:33.00 | 0.75 s | dynamic readout (by design) |
| 0:50.20 | `(D, CK) = 1 0` | 0.40 s | 1:33.70 | 0.50 s | dynamic readout (by design) |
| 0:50.45 | `s0 s1 s2 = 101` | 0.35 s | 1:33.95 | 0.50 s | dynamic readout (by design) |
| 0:50.60 | `(D, CK) = 1 1` | 1.05 s | 1:34.20 | 2.90 s | fixed |
| 0:50.80 | `Q = ¬s2 = 1` | 0.85 s | 1:34.45 | 2.65 s | fixed |
| 0:50.80 | `s0 s1 s2 = 100` | 0.40 s | 1:34.45 | 0.50 s | dynamic readout (by design) |
| 0:51.20 | `s0 s1 s2 = 000` | 0.45 s | 1:34.95 | 2.15 s | dynamic readout (by design) |
| 0:54.95 | `48.2 ps` | 2.15 s | 1:41.30 | 5.05 s | fixed |
| 0:55.60 | `lower sequencing overhead than TGFF` | 1.50 s | 1:42.35 | 4.00 s | fixed |
| 0:55.85 | `19.1 ps vs. 48.2 ps` | 1.25 s | 1:43.05 | 3.30 s | fixed |
| 0:57.10 | `energy  [fJ]` | 1.70 s | 1:46.35 | 3.50 s | fixed |
| 0:57.10 | `sequencing overhead  T_setup + T_CK→Q  [ps]` | 1.70 s | 1:46.35 | 3.50 s | fixed |
| 0:57.30 | `All 18 flip-flops of Table 2 at 0.9 V.  FF6 at 0.4 V: 1.71× faster than ` | 1.40 s | — | — | removed (narration / step marker carries it) |
| 0:57.30 | `The speed has a cost: FF1 draws 2.26 fJ vs. TGFF's 1.53 fJ.` | 1.40 s | — | — | removed (narration / step marker carries it) |
| 0:57.65 | `B-Flex circuits (5 of 20 reported, Table 2)` | 1.15 s | 1:46.95 | 2.90 s | fixed |
| 0:57.65 | `automated search, SeGen [10]` | 1.15 s | 1:46.95 | 2.90 s | fixed |
| 0:57.65 | `recent flip-flops [2,5,7,9,12,14,16,23,24]` | 1.15 s | 1:46.95 | 2.90 s | fixed |
| 0:57.70 | `FF6` | 1.10 s | 1:47.35 | 2.50 s | fixed |
| 0:59.75 | `Based on FSM Exhaustive Search` | 2.20 s | 1:51.65 | 4.10 s | fixed |
| 0:59.75 | `Exploration of Broader Flip-Flop Design Space` | 2.20 s | 1:51.65 | 4.10 s | fixed |
| 1:00.10 | `DAC 2026  ·  63rd ACM/IEEE Design Automation Conference  ·  Long Beach, ` | 1.85 s | 1:52.40 | 3.35 s | fixed |
| 1:00.45 | `Hyunsung Jeong†    Kyounghun Kang†    Wanyeong Jung    Jongeun Lee` | 1.50 s | 1:52.95 | 2.80 s | fixed |
| 1:00.45 | `UNIST  ·  KAIST          † equal contribution` | 1.50 s | 1:52.95 | 2.80 s | fixed |
| 1:00.65 | `doi.org/10.1145/3770743.3804333` | 1.30 s | 1:52.55 | 3.20 s | fixed |
