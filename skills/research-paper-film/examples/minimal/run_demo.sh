#!/usr/bin/env bash
# End-to-end smoke test of the skill's scripts on a ~11 s toy film.
# Needs: KOKORO_DIR and SHERPA_DIR (see scripts/narration/*.py), ffmpeg,
# pip: pycairo numpy scipy pillow soundfile pyloudnorm kokoro-onnx sherpa-onnx cairosvg
set -euo pipefail
cd "$(dirname "$0")"; D=$(pwd); S=$D/../../scripts
export PYTHONPATH="$S/narration:$S"
echo "== 1 narration"; (cd narration && python3 $S/narration/narrate.py && python3 $S/narration/align.py)
echo "== 2 EDL";       (cd src && python3 $S/edl.py)
DUR=$(cd src && python3 -c "import edl; print(edl.DURATION)" 2>/dev/null)
echo "== 3 stills";    (cd src && python3 $S/render.py stills --w 960 --times 1 4 9 --stills-dir ../out/stills)
echo "== 4 audit";     (cd src && python3 $S/audit.py film ../out/audit.json --budget 2.5)
echo "== 5 subtitles"; (cd src && python3 $S/subtitles.py ../out/final/demo.en.srt)
echo "== 6 audio";     python3 make_audio.py
(cd src && python3 $S/audio/mix.py --duration $DUR --lines ../narration/lines \
   --music ../out/audio/music_src.wav --sfx ../out/audio/sfx_src.wav --out ../out/audio)
echo "== 7 render";    (cd src && FILM=film DUR=$DUR CHUNKS=3 JOBS=3 W=640 FPS=30 OUTDIR=../out/final bash $S/render_chunks.sh)
echo "== 8 assemble";  NAME=demo DUR=$DUR OUTDIR=out/final MIX=out/audio/mix.wav SRT=out/final/demo.en.srt bash $S/assemble.sh
echo "== 9 QA";        ffmpeg -y -loglevel error -i out/final/demo.mp4 -ac 1 -ar 16000 out/final/demo_audio.wav
(cd narration && python3 $S/narration/srt_check.py ../out/final/demo_audio.wav ../out/final/demo.en.srt ../out/srt_check.txt | tail -1)
(cd narration && python3 $S/narration/mix_check.py ../out/audio/mix.wav ../out/audio/narration.wav ../out/audio/placement.json > ../out/mix_check.txt; tail -1 ../out/mix_check.txt)
python3 $S/contact_sheet.py out/final/demo.mp4 --fps 1 --cols 4 --w 320 --out out/sheet.png
echo "== gates (K4-K6)"
(cd src && python3 $S/gate.py --audit ../out/audit.json --videos ../out/final/demo.mp4 ../out/final/demo_1080p.mp4 \
   --srt-report ../out/srt_check.txt --mix-log ../out/mix_check.txt)
echo "== 10 figures";  python3 figs/make_figs.py
python3 $S/figures/verify_vectors.py figs/out out/figs_sheet.png
echo "== figure lint (K7)"
python3 $S/figures/lint_figs.py figs/out --sequence step
echo "demo OK"
