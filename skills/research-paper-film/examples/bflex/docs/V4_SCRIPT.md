# B-Flex v4: final narration script

Runtime 116.3 s. 18 lines, 212 printed words (222 spoken, numbers read in full).

- **Voice:** Kokoro-82M `af_heart`; see `VOICE_CASTING.md`.
- **Source of truth:** `narration/script.py`.
- **Time codes:** each line's in/out on the v4 film clock. Line L04 is split at its sentence pause into L04a/L04b.

## Script

| # | in | out | on-screen / subtitle text | spoken form fed to TTS (if different) |
|---|---|---|---|---|
| L01 | 0:00.45 | 0:05.01 | A flip-flop has one job: on a rising clock, capture D and hold it. | A flip-flop has one job: on a rising clock, capture dee, and hold it. |
| L02 | 0:05.46 | 0:09.41 | This one, from the earlier tool SeGen, passes its test vector. | This one, from the earlier tool See-Jen, passes its test vector. |
| L03 | 0:09.93 | 0:14.20 | Change one transition, and it outputs zero where it must output one. | Change one transition, and it outputs zero, where it must output one. |
| L04 | 0:15.04 | 0:22.08 | Every flip-flop is a state machine. With three state bits, candidate tables exceed ten to the nineteenth. |  |
| L05 | 0:23.03 | 0:24.34 | Beyond brute force. |  |
| L06 | 0:24.90 | 0:27.24 | B-Flex starts from behavior instead. | Bee-Flex starts from behavior, instead. |
| L07 | 0:28.36 | 0:33.44 | Its reference behavior graph holds every input order a D flip-flop must handle. |  |
| L08 | 0:33.85 | 0:40.33 | The failing vector is one path through it, and the graph demands Q = 1 where SeGen gave 0. | The failing vector is one path through it. And the graph demands queue equals one, where See-Jen gave zero. |
| L09 | 0:40.96 | 0:45.20 | Candidates grow edge by edge; each edge must map onto the graph. | Candidates grow edge by edge. Each edge must map onto the graph. |
| L10 | 0:50.27 | 0:56.59 | Here the clock falls, so Q must stay 0. Two candidates output 1. Wrong output: pruned. | Here, the clock falls, so queue must stay zero. Two candidates output one. Wrong output. Pruned. |
| L11 | 1:01.25 | 1:07.73 | Deeper in, a path needs an entry that an earlier edge already fixed. Entry conflict: branch cut. | Deeper in, a path needs an entry that an earlier edge already fixed. Entry conflict. Branch cut. |
| L12 | 1:09.75 | 1:14.50 | Pruning early makes the two-bit search 20,000 times faster than brute force. | Pruning early makes the two-bit search twenty thousand times faster than brute force. |
| L13 | 1:16.40 | 1:22.78 | At three bits, B-Flex finds 568 million valid behaviors, in about thirteen minutes. | At three bits, Bee-Flex finds five hundred sixty-eight million valid behaviors, in about thirteen minutes. |
| L14 | 1:24.04 | 1:28.49 | Twenty of the simplest were synthesized into transistor-level circuits. |  |
| L15 | 1:31.41 | 1:35.15 | One of them, FF1, captures data in two state steps. | One of them, F F one, captures data in two state steps. |
| L16 | 1:37.17 | 1:46.01 | In SPICE, at 0.9 volts, its sequencing overhead is 2.53 times lower than a transmission-gate flip-flop's, | In spice, at zero point nine volts, its sequencing overhead is two point five three times lower than a transmission-gate flip-flop's, |
| L17 | 1:46.54 | 1:48.00 | at a higher energy cost. |  |
| L18 | 1:50.49 | 1:54.98 | B-Flex: a broader flip-flop design space, searched exhaustively. | Bee-Flex. A broader flip-flop design space, searched exhaustively. |

## Story structure

1. **Problem, with one concrete failure (L01–L05).**
   - A flip-flop's job is stated.
   - The SeGen-20 test passes, then fails when one transition is changed.
   - Why exhaustive search is hard at 3 bits.
2. **The idea (L06–L08).**
   - The reference behavior graph.
   - The *same* failing vector replayed as a path, ending exactly where SeGen-20 is wrong.
3. **One fully worked example (L09–L11).**
   - Edge-by-edge growth with a check against the graph.
   - Wrong-output pruning.
   - Entry-conflict pruning.
   - Steps 1 and 3–4 are shown on screen (step markers) without narration.
4. **Acceleration and scale (L12–L13).**
   - The full 2-bit tree, then the 2.07 × 10⁴ speedup.
   - Achievement 1, **scale**: 568,832,054 valid behaviors at 3 bits.
5. **Achievement 2, circuit performance (L14–L17).**
   - 20 synthesized circuits, then **one** of them, FF1.
   - 2.53× lower sequencing overhead than TGFF at 0.9 V in SPICE, at higher energy.
   - The wording ("one of them", "its") never implies that all valid behaviors or all synthesized circuits reach 2.53×.
6. **Title (L18).**

## Terminology used on screen and in narration

| Term | Meaning in this film | Paper |
|---|---|---|
| flip-flop (FF) | positive-edge D flip-flop: on CK 0→1, Q takes D; otherwise Q holds | §1 |
| state machine / FSM | the FF's internal behavior: states s, next-state function δ(i, s), output λ(s) | §3 |
| candidate tables | all next-state tables where each entry holds or flips one state bit: 3¹⁶ ≈ 4.3 × 10⁷ (2-bit), 4³² ≈ 1.8 × 10¹⁹ (3-bit) | Table 1 note, §4.1 |
| reference behavior graph (RBG) | 8 nodes (D, CK, Q); an edge is one input pin change; the only Q change is on a rising clock edge | §3.1.1, Fig. 1A |
| candidate (ESTG) | the FSM under construction, grown one stable edge at a time; each edge must map onto an RBG edge | §3.1.2, §3.2 |
| wrong output | a candidate destination whose output Q has no matching reference edge, so the branch is pruned | §3.2.2 |
| entry conflict | a new path needs a δ entry that an earlier edge already fixed to another value, so the branch is pruned | §3.2.2 |
| valid behavior | an FSM that passes validation against the RBG ("valid 3-bit-state FF FSM") | §4.1 |
| C_FF | logic complexity: literals + product terms of the minimum SOP; 468 FSMs with C_FF ≤ 20 | §4.2, Fig. 5 |
| transistor-level circuit | one of 20 FSMs synthesized to a schematic (flow of [10]) and simulated in SPICE | §4.3 |
| sequencing overhead | T_setup + T_CK→Q, at the worst-case D transition | §4.3, Table 2 |
| TGFF | conventional transmission-gate flip-flop (24 transistors), the baseline | Table 2 |

## Pronunciation guide

| Term | Say | IPA | Spelled for TTS | Note |
|---|---|---|---|---|
| B-Flex | BEE-flex | ˈbiː.flɛks | Bee-Flex | Letter B + 'flex'; stress on BEE. |
| SeGen | SEE-jen | ˈsiː.dʒɛn | See-Jen | Prior work [10]. Pronunciation not stated by its authors; confirm. |
| SeGen-20 | SEE-jen twenty | ˈsiː.dʒɛn ˈtwɛn.ti | (on screen only) | The 20th FF of SeGen; not spoken. |
| FSM | eff-ess-EM | ˌɛf.ɛsˈɛm | (not spoken) | Narration says 'state machine'. |
| RBG | ar-bee-GEE | ˌɑɹ.biːˈdʒiː | (not spoken) | Narration says 'reference behavior graph'. |
| ESG / ESTG | ee-ess-GEE / ee-ess-tee-GEE |  | (not spoken) | On screen as 'candidate'. |
| D flip-flop | DEE FLIP-flop | ˈdiː ˈflɪp.flɑp | dee flip-flop | 'D' is the data pin; spell 'dee' so it is never read as a grade. |
| Q | KYOO | kjuː | queue | Output pin. Spelled 'queue' to force /kjuː/: in the casting take a bare 'Q' was transcribed by ASR as 'quee'. |
| FF1 | eff-eff ONE | ˌɛf.ɛf ˈwʌn | F F one | Never 'ff-one' or 'fortissimo'. |
| SPICE | SPYSS | spaɪs | spice | Circuit simulator; read as a word. |
| TGFF / transmission-gate flip-flop | trans-MISH-un gate FLIP-flop | tɹænzˈmɪʃ.ən ɡeɪt | transmission-gate flip-flop | Spoken in full. |
| behavioral equivalence | bih-HAY-vyer-ul ih-KWIV-uh-lunss | bɪˈheɪ.vjɚ.əl ɪˈkwɪv.ə.ləns | (not spoken) | Narration says 'behavior'. |
| metastability | MET-uh-stuh-BIL-ih-tee | ˌmɛt.ə.stəˈbɪl.ɪ.ti | (not spoken) | On screen in the scatter footnote only. |
| 2.53× | two point five three times |  | two point five three times | Always 'times lower', never 'times faster'. |
| 0.9 V | zero point nine volts |  | zero point nine volts |  |
| 568,832,054 | five hundred sixty-eight million |  |  | Rounded in speech; exact on screen. |
| δ (delta) | DEL-tuh | ˈdɛl.tə | (not spoken) | Next-state function; narration says 'next-state entry'. |
