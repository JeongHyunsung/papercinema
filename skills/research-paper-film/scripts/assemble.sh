#!/usr/bin/env bash
# Concatenate rendered chunks, mux the mastered mix (+ optional SRT), export
# deliverables. Duration always comes from DUR (-t), never -shortest: with a
# subtitle stream, -shortest truncates the film at the last cue.
#
#   NAME=MyPaper_film DUR=119.1 OUTDIR=out/final MIX=out/audio/mix.wav \
#   SRT=out/final/MyPaper_film.en.srt ./assemble.sh
#
# Note: the MP4 muxer marks a mov_text subtitle track as enabled, so some
# players show it by default; ship the .srt separately as well.
set -euo pipefail
NAME=${NAME:?}; DUR=${DUR:?}; OUT=${OUTDIR:-out/final}; MIX=${MIX:?}; SRT=${SRT:-}
(cd "$OUT" && ls c*.mkv | sort | sed "s#^#file '#; s#\$#'#" > list.txt)
ffmpeg -y -loglevel error -f concat -safe 0 -i "$OUT/list.txt" -c copy "$OUT/video.mkv"

# 1) master: video as rendered (H.264 CRF 15) + 24-bit PCM
ffmpeg -y -loglevel error -i "$OUT/video.mkv" -i "$MIX" -map 0:v -map 1:a \
  -c:v copy -c:a pcm_s24le -t "$DUR" "$OUT/${NAME}_master.mov"

SUBIN=(); SUBMAP=(); SUBC=()
if [ -n "$SRT" ]; then
  SUBIN=(-i "$SRT"); SUBMAP=(-map 2:s)
  SUBC=(-c:s mov_text -metadata:s:s:0 language=eng -disposition:s:0 0)
fi
# 2) distribution, full resolution
ffmpeg -y -loglevel error -i "$OUT/video.mkv" -i "$MIX" "${SUBIN[@]}" \
  -map 0:v -map 1:a "${SUBMAP[@]}" -c:v libx264 -preset medium -crf 18 \
  -maxrate 50M -bufsize 100M -x264-params aq-mode=3 -tune animation \
  -pix_fmt yuv420p -profile:v high -level 5.2 -c:a aac -b:a 320k "${SUBC[@]}" \
  -t "$DUR" -movflags +faststart "$OUT/${NAME}.mp4"
# 3) 1080p60
ffmpeg -y -loglevel error -i "$OUT/video.mkv" -i "$MIX" "${SUBIN[@]}" \
  -map 0:v -map 1:a "${SUBMAP[@]}" -vf "scale=1920:1080:flags=lanczos" \
  -c:v libx264 -preset slow -crf 18 -tune animation -pix_fmt yuv420p \
  -profile:v high -c:a aac -b:a 256k "${SUBC[@]}" -t "$DUR" \
  -movflags +faststart "$OUT/${NAME}_1080p.mp4"
# 4) measure what you deliver
for f in "$OUT/${NAME}.mp4" "$OUT/${NAME}_1080p.mp4"; do
  echo "== $f"; ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"
  ffmpeg -nostats -i "$f" -filter_complex ebur128=peak=true -f null - 2>&1 \
    | grep -E "I:|Peak:" | tail -2
done
