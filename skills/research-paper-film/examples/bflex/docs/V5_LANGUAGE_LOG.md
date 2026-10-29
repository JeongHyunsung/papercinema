# B-Flex V5: English narration, before → after

**Scope.** 9 of the 18 narration lines changed. Lines L01, L02, L03, L05, L06, L12, L16, L17 and L18 are unchanged: the V4 audio files are reused byte for byte, so the voice is identical there.

**How changed lines were made.** Each was regenerated with the same voice and settings as V4 (Kokoro-82M `af_heart`, speed 0.90) and placed at its natural speed. Nothing was time-stretched.

**Runtime.** 116.3 s → 119.1 s (+2.8 s).

| Line | V4 (before) | V5 (after) | Reason |
|---|---|---|---|
| L04 | Every flip-flop is a state machine. With three state bits, candidate tables exceed ten to the nineteenth. | **A flip-flop can be modeled as a state machine.** With three state bits, candidate tables exceed ten to the nineteenth. | *Accuracy.* The paper *models* a candidate FF as an asynchronous FSM (§3.1.2); a flip-flop is not literally a state machine. The second sentence is unchanged |
| L07 | Its reference behavior graph **holds** every input order a D flip-flop must handle. | Its reference behavior graph **covers** every input order a D flip-flop must handle. | *Naturalness.* "Holds every input order" is unidiomatic; "covers" is what a native editor would write. Same length |
| L08 | The failing **vector** is one path through it, and the graph **demands Q = 1** where **SeGen** gave 0. | The failing **sequence** is one path through it, and the graph **requires Q to stay at one**, where **SeGen-20** gave zero. | *Accuracy.* The failure belongs to the design SeGen-20, not to the tool SeGen (§2). "Stay at one" is exact: Q was already 1 after transition 5, and the reference requires it to hold when D falls. *Naturalness:* "requires … to stay" instead of "demands Q = 1" |
| L09 | Candidates grow edge by edge; each edge must map onto the graph. | Candidates grow **one stable transition at a time**, and each must **match an edge of the reference graph**. | *Accuracy.* B-Flex compares *stable* transitions, after settling, not single-step ones (§3.1.3, StableSucc). It requires a *matching RBG edge*, not a label comparison (validation rule (1)) |
| L10 | Here the clock falls, so Q must stay 0. Two candidates output 1. Wrong output: pruned. | Here the clock falls, so Q must stay at zero. Two **candidate states would output one, so those branches are pruned.** | *Naturalness.* Replaces three clipped fragments with one spoken sentence, and "candidate states" removes an ambiguous referent. "Wrong output" remains on screen (step marker and red label); dropping it from speech lets "pruned" land while the pruning label is still visible (sync) |
| L11 | Deeper in, a path needs an entry that an earlier edge already fixed. Entry conflict: branch cut. | Deeper in, a **settling path needs a table entry that an earlier transition set differently. That entry conflict prunes the branch.** | *Accuracy.* An entry conflict is two *different* values assigned to the same δ entry (§3.2.2); "already fixed" did not say they differ. "Settling path" and "table entry" name the actual objects. "Prunes the branch" is the paper's term; "branch cut" was not |
| L13 | At three bits, B-Flex finds 568 million valid **behaviors**, in about thirteen minutes. | At three **state** bits, B-Flex finds **all 568 million valid state machines in its search space**, in about thirteen minutes. | *Accuracy.* The count is of valid 3-bit-state FF FSMs under the §4.1 constraints (Q = ¬s2, initial state 011, one-bit transitions); it is not an unrestricted enumeration of flip-flops. The constraints are now also on screen. "Behaviors" was replaced with the paper's object |
| L14 | Twenty of **the simplest were synthesized into transistor-level circuits**. | Twenty of the **468 simplest were sampled and turned into transistor-level schematics**. | *Accuracy.* The 20 were *sampled* from the 468 with C_FF ≤ 20, after excluding known 2-bit-state FFs; they are not the 20 simplest. The output was transistor-level *schematics* (§4.2), not fabricated circuits |
| L15 | One of them, FF1, **captures data in two state steps**. | One of them is FF1. **When the clock rises, its state settles in two steps, and Q flips on the first.** | *Accuracy.* Replayed from Fig. 8f: on CK↑ with D = 1 the state walks 101 → 100 → 000, and Q = ¬s2 changes at the first step. "Captures data in two steps" wrongly suggested Q needs both |

## Pronunciation (unchanged voice; spellings fed to the TTS)

| Term | Spoken as | Note |
|---|---|---|
| B-Flex | "Bee-Flex" | unchanged |
| SeGen / SeGen-20 | "See-Jen" / "See-Jen twenty" | SeGen-20 is now spoken in L08. SeGen's own authors have not published a pronunciation |
| Q | "queue" | forces /kjuː/ |
| FF1 | "F F one" | — |
| SPICE | "spice" | — |
| ESTG, RBG, FSM, metastability | not spoken | on screen only. The film says "reference behavior graph", "state machine", "stable transition" |

## Checks run on the changed lines

- **Word alignment.** ASR word alignment of every regenerated line against the script matched all words except four: two in L04, "At" in L13, and one "F" in L15. Those four were timed by interpolation (`narration/words.json`).
- **Subtitles.** Generated from the same `sub` text and the word timings (28 cues). The final check against the rendered film is in `V5_SCIENTIFIC_VERIFICATION.md`, Pass 2.
