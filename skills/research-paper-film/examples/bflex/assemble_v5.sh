#!/usr/bin/env bash
# v5: concatenate rendered chunks, mux the mastered mix (+ optional subtitle
# track), and export the deliverables. Audio is already mastered by
# src/audio4.py (-16 LUFS integrated, <= -1.2 dBTP before encoding).
set -euo pipefail
cd "$(dirname "$0")"
OUT=${OUT:-out/final_v5}
DUR=$(python3 -c "import sys; sys.path.insert(0,'src'); import edl; print(round(edl.DURATION, 3))")
A=src/out/audio_v4
SRT=$OUT/BFlex_DAC2026_film_v5.en.srt
ls $OUT/c*.mkv | sort | sed "s#^$OUT/#file '#; s#\$#'#" > $OUT/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i $OUT/list.txt -c copy $OUT/video_4k60.mkv

# 1) Master: 4K60 H.264 (CRF 15 as rendered) + 24-bit PCM mix, .mov
ffmpeg -y -loglevel error -i $OUT/video_4k60.mkv -i $A/mix.wav \
  -map 0:v -map 1:a -c:v copy -c:a pcm_s24le -t $DUR \
  $OUT/BFlex_DAC2026_film_v5_4K60_master.mov

# 2) Distribution 4K60: H.264 High 5.2 (<= 50 Mbps), AAC 320k, soft English subtitle track (mov_text; the MP4 muxer marks it enabled, so some players show it by default)
ffmpeg -y -loglevel error -i $OUT/video_4k60.mkv -i $A/mix.wav -i $SRT \
  -map 0:v -map 1:a -map 2:s -c:v libx264 -preset medium -crf 18 -maxrate 50M \
  -bufsize 100M -x264-params aq-mode=3 -tune animation -pix_fmt yuv420p -profile:v high \
  -level 5.2 -c:a aac -b:a 320k -c:s mov_text -metadata:s:s:0 language=eng \
  -disposition:s:0 0 -t $DUR -movflags +faststart \
  $OUT/BFlex_DAC2026_film_v5_4K60.mp4

# 3) 1080p60
ffmpeg -y -loglevel error -i $OUT/video_4k60.mkv -i $A/mix.wav -i $SRT \
  -map 0:v -map 1:a -map 2:s -vf "scale=1920:1080:flags=lanczos" -c:v libx264 \
  -preset slow -crf 18 -tune animation -pix_fmt yuv420p -profile:v high -c:a aac -b:a 256k \
  -c:s mov_text -metadata:s:s:0 language=eng -disposition:s:0 0 \
  -t $DUR -movflags +faststart $OUT/BFlex_DAC2026_film_v5_1080p60.mp4

# 4) Audio deliverables: narration, music, SFX stems + final mix (48 kHz / 24-bit WAV)
mkdir -p $OUT/audio
for s in narration music sfx mix; do cp $A/$s.wav $OUT/audio/BFlex_v5_$s.wav; done
ls -lh $OUT/*.mp4 $OUT/*.mov $OUT/audio/*.wav
