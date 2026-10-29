# 02: Story, storyboard and visual identity

## Narrative skeleton (≈60 s silent, ≈120 s narrated)

Per-archetype variants are in references/13.

| Act | Job | Generic pattern | Case study (B-Flex, a search/circuit paper) |
|---|---|---|---|
| I. Challenge | Hook the viewer and show why the problem is hard | One concrete failure or bottleneck shown as evidence (a trace, a waveform, a profile, a counter-example), then the size of the space or of the gap | A prior tool's design passes its single test vector; one reordered transition makes it output the wrong Q. The state space then grows from a 2-bit square to a 3-bit cube, 3^16 → 4^32 tables |
| II. Idea | Show what is new, not just that it exists | The paper's own representation, built from real data, with Act I's example replayed inside it | A reference behaviour graph covers every input order. Act I's failing vector is replayed as one path through it. Candidates lift above the graph as states |
| III. Inside | The centrepiece: how it works | One instance walked through every rule or stage, with the state (table, buffer, queue) beside it; then acceleration to scale | Step-by-step growth with a transition table: wrong-output pruning, then entry-conflict pruning. A PiP shows the real search tree |
| IV. Impact | The strongest verified numbers, with conditions | Scale or coverage, then performance against the paper's baselines, then the reported trade-off | Exhaustive count with its runtime; selection to schematics; one design replayed; a slope-1 race (2.53× lower sequencing overhead); then the energy trade-off across all 18 designs |
| V. Title | A memorable close | Title, venue, DOI, authors as printed | Wordmark, title, DAC 2026, DOI |

**One worked example carries the film.** Pick it with references/13 ("Choosing the worked example"), and reuse it across acts. Persistent markers (①–⑥) make the link visible.

## Tempo grammar

| Tempo | Used for |
|---|---|
| Fast | repetition and scale: fast-forwarded links, tree growth, a million-cell fill |
| Moderate | camera moves and changes of representation |
| Slow | mechanisms and comparisons |

- **Slow beats** follow anticipation → action → consequence → hold. Slow is not static: during a hold the camera drifts, a tracer runs or a pulse marks the write.
- **Never change two things in the same instant.** The camera settles first, then the caption or label, then the event.
- **Holds are where text is read.** Size them with the readability audit (references/07-qa.md).

## Camera and motion are part of the storyboard

Every row of the storyboard names its **shot**, not only its content: establish / follow / push-in / hold-with-drift / pull-back / reveal / orbit (references/14 §1). Every mechanism beat is choreographed with the template in references/14 §4, and gets **4–7 s of picture time**. If the narration gap is shorter, lengthen the gap before the beat (EDL); never shrink the beat into a cut. A storyboard row reading "graph shown, label appears" with no camera or motion entry is unfinished.

## Storyboard and timing sheet

**`STORYBOARD.md`** is a pacing map. Each row covers one time range and gives:

- scene and tempo;
- what must be understood before moving on;
- source (§, Fig., Table).

**The timing sheet is code.** Put named constants at the top of `film.py` (`T_STAGE`, `T_S1`, `T_CONF`…) and export them as `film.CUES` for the audio. After a narration retime, generate the film-clock timing sheet from the EDL (`timing_sheet.py` (a per-project script; the case study's is `examples/bflex/src/timing_sheet.py`)).

## Identity tokens (white identity used in the case study)

```
INK      #17212B  primary text and lines
GRAPHITE #607080  secondary text, axes
DIM      #D9E0E5  inactive or ghost
TEAL     #087F8C  ok / valid / ours
CORAL    #C83F45  failing / removed / violated
AMBER    #B7791F  headline / inferred / the event to watch
BLUE     #2764C5  the reference / expected value: one colour links Acts I and II
PAPER    #FFFFFF  background
```

- **Colours are semantic and used consistently everywhere.** Never use a colour for decoration.
- **On white:**
  - no glow, bloom, film grain, vignette or grid;
  - highlights are faint flat tints (≈13% opacity);
  - soft shadows only on floating documents, such as a table panel or a PiP.
- **Additive light-on-dark compositing becomes invisible on white.** Use alpha-over with a darker growing front.
- **Typography: one family.** Inter for UI and figures; a mono font for data labels in the film is optional. In slide figures, use Inter only (see the font pitfall).
- **Keep source tags away from the subtitle area.** Put them top-right, not bottom.
