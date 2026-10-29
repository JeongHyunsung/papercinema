#!/usr/bin/env bash
# Resumable 4K60 render (v5, 119.1 s): 8 chunks, N parallel workers; finished chunks are skipped.
set -u
cd "$(dirname "$0")/src"
OUT=${OUTDIR:-../out/final_v5}
mkdir -p $OUT
JOBS=${JOBS:-4}
chunk() {
  s=$1; e=$2; n=$(printf "c%05.1f" $s)
  if grep -q "^done" $OUT/$n.log 2>/dev/null; then echo "skip $n"; return; fi
  python3 render.py video --w 3840 --fps 60 --start $s --end $e --codec x264 \
    --out $OUT/$n.mkv > $OUT/$n.log 2>&1
}
export -f chunk; export OUT
printf "%s\n" "0 14.4" "14.4 28.8" "28.8 43.2" "43.2 57.6" "57.6 72" "72 86.4" "86.4 101" "101 119.1" | \
  xargs -P $JOBS -L 1 bash -c 'chunk $0 $1'
