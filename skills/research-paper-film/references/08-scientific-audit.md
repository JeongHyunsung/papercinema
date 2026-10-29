# 08: Scientific audit and narration polish

Use this when the brief says, for example, "preserve the film; do a paper-grounded audit; polish the narration; two review passes; keep the runtime; list the deliverables".

## Ground rules

- **The paper is the authority.** Read all of it again: every column, figure, table and footnote. Also inspect the rendered figures as images.
- **Roles (references/18 §10).** Pass 1 is a fresh reviewer's work: it audits and changes nothing. The narration polish below is done by a generator from the reviewer's table, only if the user wants it; Pass 2 is again a fresh reviewer.
- **Audit what was delivered, not what you remember building:**
  - frames of the delivered file, one per second, on contact sheets (`review_pack.py`);
  - an ASR transcript of the delivered file's own audio track (or its subtitle file);
  - the on-screen strings, read from the 1080p stills; the readability audit's JSON string inventory exists only where the film's code is at hand (the generator side), so the reviewer reads text from the frames.
- **Never write "reviewed" for a scene you did not inspect.** Say how each scene was inspected.

## Classes

| Class | Meaning | Action |
|---|---|---|
| V | verified against the paper | none |
| TI | technically incorrect | must fix |
| PM | potentially misleading | fix the wording or add the missing condition |
| AMB | ambiguous | disambiguate |
| CV | conceptual visualization: an abstraction that preserves a stated relation | state the relation in the docs |
| NV | not verifiable from the paper; recomputed by the re-implementation | label as recomputed |

## Pass 1: evidence table

Write one row per claim, ordered by time on the **new** clock:

| Time | Claim (narration *italic*, on-screen `code`) | Visual | Paper | Class | Correction |

These kinds of findings came up in the case study:

- **"is" vs "can be modeled as".** "Every flip-flop *is* a state machine" (PM) → "can be *modeled as*".
- **Tool vs design.** "where SeGen gave 0": SeGen is the tool; the failing design is SeGen-20.
- **Missing condition.** "Brute force ~10⁶ years" without "1 thread" (incomplete, PM).
- **Wrong selection rule.** "Twenty of the simplest" → "Twenty of the 468 simplest were *sampled*".
- **Wrong deliverable type.** "circuits" → "transistor-level *schematics*" (§4.2).
- **Wrong mechanism.** "captures data in two state steps" → "its state settles in two steps, and Q flips on the first" (replayed from the published table).
- **Missing qualifier.** "Edge by edge" → "one *stable* transition at a time; each must *match an edge* of the reference graph", using the paper's validation rule and its StableSucc.
- **Under-specified definition.** "an entry an earlier edge already fixed" → "a table entry that an earlier transition set *differently*", i.e. the actual definition of an entry conflict.
- **Missing scope.** Counts presented without their search-space constraints → add the constraints on screen. Example: "§4.1 search space: Q = ¬s2 · initial state 011 · ≤ 1 bit flip".

## Narration polish

1. **Accuracy first, then naturalness.** Fix clipped fragments, unidiomatic verbs ("holds every input order" → "covers") and ambiguous referents.
2. **Keep unchanged lines byte-identical.** Reuse their WAVs.
3. **Re-voice only the changed lines,** with the same voice, speed and engine (`regen.py`). Place them at natural speed and re-align.
4. **Re-check the EDL** for overlaps. Report the runtime change (e.g. 116.3 s → 119.1 s).
5. **Write `LANGUAGE_LOG.md`.** For every changed line: before → after, and the reason, tagged *Accuracy* or *Naturalness*.

## Pass 2: verify the new render

- A fresh reviewer repeats every Pass 1 check on the new file from `review_pack.py`: frames, stills (on-screen strings), ASR transcript or subtitles.
- It repeats the SRT check, loudness and contact sheets.
- The generator updates the timing sheet and the transcript (generator-side artifacts).
- **Close out every Pass 1 finding,** each with the new time and the evidence.
