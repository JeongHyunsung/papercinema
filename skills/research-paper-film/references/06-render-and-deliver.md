# 06: Render and deliver

## Chunked, resumable 4K60 render

```bash
FILM=film DUR=119.1 CHUNKS=8 JOBS=4 OUTDIR=out/final scripts/render_chunks.sh
```

**How the render runs.**
- `render.py video` pipes raw RGB frames into ffmpeg: x264 CRF 15, `-tune animation`, `-threads 1` per chunk.
- Each chunk logs its progress. The log ends with `done …` when the chunk finishes.
- Chunks that are already done are skipped, so a run that gets killed can simply be restarted.

**Picking `JOBS`.** Estimate the memory per worker: a 4K frame buffer, plus motion-blur accumulation (float32, 4K × n sub-frames), plus numpy layers. OOM kills are silent: the chunk log just stops. To check:
- look at `dmesg`, or at free memory;
- confirm every log ends in `done`;
- re-run to finish the missing chunks.

**Waiting on a render.** Never `pgrep -f render.py` inside a loop whose own command line contains "render.py": it matches itself and waits forever. Instead, use `pgrep -f "[r]ender.py"`, or check for the `done` lines in the logs.

**Disk.** A 2-minute 4K60 render at CRF 15 is a few GB. Delete old chunks and intermediates before you start.

## Assemble (`scripts/assemble.sh`)

1. **Concat** the chunks: `-f concat -c copy`.
2. **Master `.mov`:** video copy (H.264 CRF 15) plus PCM 24-bit audio.
3. **4K MP4:** libx264 High 5.2, CRF 18, `-maxrate 50M`, `-tune animation`, yuv420p, AAC 320k, `+faststart`.
4. **1080p60 MP4:** lanczos downscale, CRF 18, AAC 256k.
5. **Optional soft-subtitle track:** `-c:s mov_text -metadata:s:s:0 language=eng -disposition:s:0 0`.
   - The MP4 muxer still marks the track as enabled, so some players show it by default.
   - This cannot be cleared from ffmpeg; document it and ship the `.srt` separately.
6. **Duration:** always `-t $DUR`, where `DUR` comes from the EDL. Never use `-shortest`: with a subtitle stream it truncates the file to the last cue.

## Deliverables checklist

- **Video:** `NAME_4K60_master.mov`, `NAME_4K60.mp4`, `NAME_1080p60.mp4`.
- **Subtitles:** `NAME.en.srt`.
- **Audio:** stems zip (narration, music, sfx, mix as 48 kHz WAV).
- **Docs zip:**
  - storyboard and timing sheet;
  - `VERIFICATION.md` and the accuracy checklist;
  - QA reviews and the readability audit table;
  - revision log;
  - voice casting;
  - transcript;
  - (audits) the scientific verification report and the language log.
- **Source zip:**
  - `README.md`: what it is; the folder map; requirements (pip packages, ffmpeg, fonts); where to download the models; the exact reproduce commands; how to edit the words, voice, timing and look;
  - all code, `scene_data.json` and `script.py`;
  - no model weights, no rendered media, no paper PDF.

## Verify the deliverables themselves

For every file you deliver, check:
- `ffprobe`: duration, streams, resolution, fps, codecs;
- `ebur128`: loudness and true peak;
- contact sheet at 1 fps;
- `srt_check.py` against the file's own audio;
- the first and last seconds, by looking at extracted frames.
