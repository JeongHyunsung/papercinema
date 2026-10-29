# 05: Score, SFX, mix and master

## Licence-clean by construction

- **Synthesize music and effects in numpy.** Sample nothing (`scripts/audio/synth.py`).
- **Instruments:**
  - `pad_chord`: detuned saws, low-passed, with fades;
  - `bell`: inharmonic partials with an exponential decay;
  - `tick`: a short sine plus noise;
  - `thump`: a sub with a pitch drop;
  - `whoosh`: band-passed noise with a rising or falling envelope;
  - `stab`: a short chord.
- **Space:** `reverb` convolves the signal with a decaying noise impulse response, low-passed.
- **Assets from elsewhere:** record each one's licence in the docs.

## Cueing

- **Cue table.** `film.CUES` exports the named event times. Audio events in animation time map to film time with `edl.inv`.
- **Sound follows the semantics:**
  - tick: a check;
  - low thump: a pruning decision;
  - bell: a result;
  - swell: a scale climax;
  - whoosh: a camera move.
- **Spacing.** Keep sounds sparse under narration, and let the silent beats carry the music.

## Peaks (references/15)

- Each peak gets one sound shape, landing on the reveal frame:
  - `riser(d)` placed at `t_reveal − d` (d = 1.5–2.5 s), at most one per peak;
  - `Track.duck(t_reveal − 0.35, t_reveal, db=-18)` on the music bus: the pre-hit silence;
  - `hit()` on the reveal (sub thump + chord stab + bell partial).
- **Hits are reserved for peaks.** A hit anywhere else teaches the viewer that hits mean nothing.
- Export the reveal times (film time, after `edl.inv`) to `cues.json`; `wow_audit.py` checks each is within 80 ms of its reveal.
- The voice still wins: ducking applies to the riser and the hit as to any SFX. If the key word and the hit collide, move the reveal into a narration gap and let the word follow the hit.

## Mix (`scripts/audio/mix.py`)

1. **Narration stem.** Place each clip from `placement.json` at its natural speed, with a 6 ms edge fade. High-pass at 70 Hz and level to −17 LUFS.
2. **Speech mask.** Build a mask from the word timings, then a ducking envelope from it: 150 ms pre-roll, 450 ms release, 120 ms smoothing.
3. **Music:** level to −26 LUFS, duck 9 dB. **SFX:** level to −25 LUFS, duck 5 dB.
4. **Tail.** Fade music and SFX out over the last 1.6 s of the picture.
5. **Voice limiter.** Limit the voice alone (−4 dBTP), re-level it, then limit again (−3). The bus limiter then only touches rare peaks. Report the share of speech samples reduced by more than 1 dB and by more than 3 dB.
6. **Bus.** Level to −16 LUFS integrated. Apply a 4×-oversampled look-ahead peak limiter at −1.2 dBTP, iterating level-then-limit 3 times.
7. **Exports.** Stems as 32-bit float, so nothing clips at mix level. The mix as 24-bit PCM, 48 kHz. Also write `placement.json`.

## Measure every deliverable

```bash
ffmpeg -nostats -i film.mp4 -filter_complex ebur128=peak=true -f null - 2>&1 | tail -12
```

- **Loudness:** the integrated value should be −16 ± 0.5 LUFS.
- **Peak:** the true peak should be ≤ −1 dBTP after AAC encoding. Check the encoded files; AAC can add overshoot.
- **Intelligibility:** run `narration/mix_check.py`. It runs ASR on each clip cut from the mix vs the clean narration. The case study measured 1 word in 231 different (0.4%).
