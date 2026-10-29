# B-Flex v4: voice casting and narration engine

## What was requested, and what was used

The brief asked for **ElevenLabs Eleven v4** first and **Gemini 3.8 Flash TTS** as the alternative. Neither could be used in this production environment:

| Service | Result |
|---|---|
| `api.elevenlabs.io` | not reachable from the sandbox network (HTTP 000); no API key present |
| `generativelanguage.googleapis.com` (Gemini TTS) | not reachable (HTTP 000); no API key present |
| ElevenLabs connector in the Claude connector registry | exists, but it manages ElevenAgents *voice agents*. It does not expose a text-to-speech generation tool, and it is not connected. |

**Engine used: Kokoro-82M v1.0**, run locally through `kokoro-onnx` 0.6.1 (model files from the `thewh1teagle/kokoro-onnx` GitHub release `model-files-v1.0`).

- **License:** the model weights are Apache-2.0, and the voices ship with the model under the same license. Commercial use is permitted.
- **Not ElevenLabs:** no narration in this package was produced with ElevenLabs or Gemini.

**To swap in ElevenLabs later:**

1. Generate each line of `narration/script.py` (the `tts` field, with the pronunciation guide) in ElevenLabs.
2. Save them as `narration/lines/L01.wav` … `L18.wav`.
3. Run `python3 narration/align.py`, then `src/edl.py` (check), `src/audio4.py`, `src/subtitles.py`, and the render.

The anchors re-place every line automatically. If a line comes out much longer, the overlap check in `edl.py` flags it, and you lengthen the relevant segment.

## Casting procedure (what was actually done)

16 English voices (US and UK, female and male) read the same 5-line test passage. It contains the hardest terms: "SeGen", "Q equals one", "next-state entry", "SPICE", "zero point nine volts", "two point five three times", "transmission-gate flip-flop's".

**Important limitation:** in this environment no one listened to the takes, me included. The casting decision rests on objective measurements, not on listening. The candidate takes are kept in `narration/casting/*.wav` so you can listen and overrule the choice.

Measurements (`narration/cast_eval.py`):

- **Intelligibility.** WER of an independent offline ASR model (sherpa-onnx zipformer, English) against the script.
- **Pace.** Speaking rate in wpm.
- **Prosodic range.** pYIN F0, 10th–90th percentile spread in semitones. A narrow range sounds monotone; a very wide one sounds theatrical.
- **Pause ratio.**

| voice | accent / sex | dur (s) | rate (wpm) | ASR WER | median F0 (Hz) | pitch range p10–p90 (st) | pause ratio |
|---|---|---|---|---|---|---|---|
| bm_lewis | UK M | 27.1 | 177 | 8.8% | 89 | 9.1 | 0.2 |
| am_michael | US M | 28.7 | 167 | 8.8% | 112 | 7.9 | 0.18 |
| **af_heart** | US F | 25.9 | 185 | 8.8% | 196 | 7.1 | 0.18 |
| am_puck | US M | 19.8 | 243 | 8.8% | 109 | 6.1 | 0.13 |
| bf_isabella | UK F | 24.5 | 196 | 8.8% | 198 | 6.0 | 0.17 |
| am_liam | US M | 21.2 | 226 | 10.0% | 126 | 9.7 | 0.14 |
| am_fenrir | US M | 20.8 | 230 | 10.0% | 134 | 7.7 | 0.15 |
| bm_daniel | UK M | 21.4 | 224 | 10.0% | 121 | 6.3 | 0.12 |
| am_onyx | US M | 22.0 | 218 | 10.0% | 85 | 4.8 | 0.15 |
| am_echo | US M | 22.5 | 213 | 11.2% | 106 | 7.4 | 0.16 |
| bm_george | UK M | 25.8 | 186 | 11.2% | 138 | 7.1 | 0.19 |
| af_bella | US F | 26.5 | 181 | 11.2% | 205 | 5.8 | 0.18 |
| bm_fable | UK M | 22.1 | 217 | 12.5% | 113 | 10.0 | 0.08 |
| am_eric | US M | 20.2 | 237 | 12.5% | 155 | 8.7 | 0.13 |
| af_nicole | US F | 39.7 | 121 | 12.5% | 160 | 5.7 | 0.33 |
| bf_emma | UK F | 23.5 | 204 | 12.5% | 182 | 5.1 | 0.17 |


The WER floor of about 9% is the ASR model's own errors on the same words for every voice ("graph" → "graft", "Q equals" → "quee equals"), not narrator errors.

## Decision

**`af_heart` (US English, female), Kokoro speed 0.90.**

- **Intelligibility:** tied for the best WER (8.8%).
- **Pitch range:** 7.1 semitones, which is lively without being theatrical.
- **Engine ranking:** it is the voice the Kokoro project itself ranks highest.
- **Pace:** at the engine's default speed it reads at about 185 wpm, which is too fast for dense technical narration. The speed parameter was set once to 0.90, before alignment, giving about 165 wpm. This is a delivery-pace setting, chosen as part of casting. The narration was never time-stretched afterwards. The animation was retimed to the voice, not the reverse.

**Runner-up: `am_michael` (US male).** It has the same WER, a naturally slower 167 wpm, and a 7.9-semitone range. It is a good choice if a male narrator is preferred: run `VOICE=am_michael python3 narration/narrate.py`, then re-run the pipeline.

## Quality checks run on the final narration

| Check | Result |
|---|---|
| ASR word alignment against the script (`narration/align.py`) | 230 of 236 spoken word-parts matched (exactly or as an equal-length spelling variant); the 6 others were interpolated between neighbours |
| Narration intelligibility inside the final mix (`narration/mix_check.py`): ASR of each clip cut from `mix.wav` vs the same clip from `narration.wav` | 1 word different out of 231 (0.4%). Music and SFX do not mask the voice |
| Time-stretching | none; each clip is the synthesizer's output, trimmed and placed |
