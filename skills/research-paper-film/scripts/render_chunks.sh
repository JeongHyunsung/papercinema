#!/usr/bin/env bash
# Resumable, parallel chunked render. Run from the directory that holds the
# film module (and engine.py / render.py, or put scripts/ on PYTHONPATH).
#
#   FILM=film DUR=119.1 CHUNKS=8 JOBS=4 W=3840 FPS=60 OUTDIR=out/final ./render_chunks.sh
#
# A chunk whose log ends with "done" is skipped, so a killed run can simply be
# re-run. Choose JOBS from free RAM: 4K frames + motion-blur accumulation are
# heavy, and OOM kills are silent (the log just stops). To wait for workers,
# use  pgrep -f "[r]ender.py"  (a bare pattern matches the waiting shell).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
FILM=${FILM:-film}; DUR=${DUR:?set DUR (seconds)}; CHUNKS=${CHUNKS:-8}
JOBS=${JOBS:-4}; W=${W:-3840}; FPS=${FPS:-60}; OUT=${OUTDIR:-out/final}
mkdir -p "$OUT"
export FILM W FPS OUT HERE
chunk() {
  s=$1; e=$2; n=$(printf "c%07.2f" "$s")
  if grep -q "^done" "$OUT/$n.log" 2>/dev/null; then echo "skip $n"; return; fi
  PYTHONPATH="$HERE:${PYTHONPATH:-}" python3 "$HERE/render.py" video --film "$FILM" \
    --w "$W" --fps "$FPS" --start "$s" --end "$e" --codec x264 \
    --out "$OUT/$n.mkv" > "$OUT/$n.log" 2>&1
}
export -f chunk
python3 - "$DUR" "$CHUNKS" "$FPS" <<'PY' | xargs -P "$JOBS" -L 1 bash -c 'chunk $0 $1'
import sys
dur, n, fps = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
# chunk edges on whole frames
edges = [round(round(dur * k / n * fps) / fps, 4) for k in range(n + 1)]
for a, b in zip(edges, edges[1:]):
    print(a, b)
PY
bad=0
for l in "$OUT"/c*.log; do grep -q "^done" "$l" || { echo "UNFINISHED: $l"; bad=1; }; done
[ $bad = 0 ] && echo "all chunks done" || echo "re-run to finish (check RAM / dmesg for OOM)"
