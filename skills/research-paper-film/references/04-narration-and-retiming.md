# 04: Narration, retiming and subtitles

## Order of work

script → voice casting → per-line synthesis → word alignment → EDL retime (the picture follows the voice) → mix → subtitles

## Script (`scripts/narration/script_template.py`)

```python
LINES = [
  dict(id="L01", sub="A flip-flop has one job: on a rising clock, capture D and hold it.",
       tts="A flip-flop has one job: on a rising clock, capture dee, and hold it.", gap=.5),
  ...
]
SPOKEN = [("B-Flex", "Bee-Flex"), ("568", "five hundred sixty-eight"), ("Q", "queue"), ...]
```

Each line has three fields:

- **`sub`** is what is printed (subtitles, transcript).
- **`tts`** is the same words respelled for the TTS front end. Use it for:
  - acronyms ("Bee-Flex", "See-Jen", "F F one");
  - single letters ("dee", "queue");
  - numbers in words;
  - commas that force a breath.
- **`gap`** is the edited silence after the line.

`SPOKEN` maps printed tokens to spoken words. The subtitle timer and the SRT checker both use it. Record every respelling in a pronunciation table in the docs.

**Writing rules:**

- Use the paper's terms and keep its distinctions (references/01).
- Use one idea per sentence. Make each sentence one natural spoken unit, not clipped fragments ("Wrong output: pruned.").
- Avoid ambiguous referents ("Two candidates…" → "Two candidate states…").
- Spoken numbers may be rounded ("about thirteen minutes"), but the exact value is shown on screen.
- Don't say what a label already shows if dropping it lets the key word land while the label is still visible.

## Voice casting (`cast_eval.py`)

1. Synthesize the same 5-line passage with every candidate voice.
2. Score each voice on:
   - ASR WER against the script (intelligibility);
   - words per minute;
   - median F0 and 10–90% pitch range in semitones (monotony check);
   - pause ratio.
3. Choose with the numbers plus listening notes. Write the result to `VOICE_CASTING.md`.

Default open stack:

- Kokoro-82M v1.0 (`kokoro-onnx`, Apache-2.0);
- voice `af_heart`;
- speed 0.9.

## Synthesis and alignment

- **`narrate.py`** synthesizes each line, trims leading and trailing silence (−45 dB), writes `lines/Lxx.wav` and `lines.json`, and concatenates the lines with their gaps into `narration_raw.wav` for listening.
- **`align.py`** runs sherpa-onnx zipformer (offline English ASR) on each line to get BPE token start times.
  - Hypothesis words are matched to the `tts` words with difflib.
  - Unmatched words are interpolated between their neighbours.
  - A word ends where the next one starts; the last word ends at the speech end.
  - It prints `matched/total` per line. Report any unmatched words in the docs.
- **`regen.py L04 L08`** regenerates only those lines with the same settings and rebuilds `lines.json`. Unchanged lines stay byte-identical.

## EDL: narration-first retime (`scripts/edl.py`)

The animation keeps its own clock (`t_anim`, the designed timing). The film clock `t` drives it through a monotone, piecewise-linear warp:

```python
SEGMENTS = [  # (t_anim reached, film seconds it takes, note)
  (1.60, 2.3, "pin labels fade in (L01)"),
  (1.75, 1.3, "hold: D, CK, Q"),
  ...
]
ANCHORS = {   # clip -> (index of anchor word in the clip, t_anim event)
  "L02": (7, 3.63),        # "passes" lands on the 6th check
  "L01": (0, None, .45),   # or place by absolute film time
}
SPLITS = {"L04": ("L04a", "L04b", 6)}   # split a line before word 6 (a sentence pause)
```

- **Slopes.** Slope 1 is designed speed, slope ≈ 0 is a hold (the screen is settled; text stays readable), and slope ≈ 0.5 is a moderate move.
- **Clip start** = `inv(t_anim_event) − time of the anchor word inside the clip`. Speech is never stretched.
- **`python3 edl.py`** lists every clip with its gap and flags overlaps (gap < 0.2 s). Fix an overlap by lengthening the segment before the clip.
- **Data-encoding segments keep slope 1.** In the case study, a race of bars at "20 ps per second of film" must play at slope 1, or the on-screen claim becomes false. Verify the slope in the timing sheet.
- **Drive the film by the warp.** `film.draw(cv, t) = draw_anim(cv, warp(t))`. Map the audio cues stored in animation time with `inv`.

## Subtitles (`scripts/subtitles.py`)

- **Split** each line's `sub` into sentences, and long sentences at `: ; ,`, keeping each piece within 2 × 42 characters. Wrap at most 2 lines of 42 characters, never breaking around "=".
- **Time each cue by spoken-word count.** Map print to spoken words with `SPOKEN`, count, and take that many aligned words. Assert that the counts add up to the line's word count; a mismatch means a cue boundary would fall mid-sentence.
- **Pad and clean up timing.** Cues start 50 ms early and end 120 ms late. Minimum length is 1 s. Remove overlaps (≥ 40 ms gap).
- **Check against the delivered audio.** `narration/srt_check.py` runs ASR on the delivered file's own audio inside each cue window and compares it with the cue text.
