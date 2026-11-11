#!/usr/bin/env bash
# Builds the finished film from index.html. Needs node, python3 and ffmpeg.
#   ./tools/build.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p out

echo "1/6  rendering scenes"
node tools/render.mjs

echo "2/6  synthesising the soundtrack"
python3 tools/audio.py

echo "3/6  writing subtitles"
python3 tools/subtitles.py

echo "4/6  joining scenes"
ls out/s*.mp4 | sort -V | sed "s|^|file '$PWD/|; s|$|'|" > out/scenes.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i out/scenes.txt -c copy out/picture.mp4

echo "5/6  mastering audio to -16 LUFS and muxing"
RAW=$(ffmpeg -hide_banner -nostats -i out/audio_raw.wav -af ebur128 -f null - 2>&1 | awk '/^ +I:/ {print $2}' | tail -1)
GAIN=$(python3 -c "print(round(-16 - ($RAW), 2))")
ffmpeg -y -loglevel error -i out/audio_raw.wav \
  -af "volume=${GAIN}dB,alimiter=limit=0.84:attack=3:release=60:level=disabled" -ar 48000 out/audio.wav
ffmpeg -y -loglevel error -i out/picture.mp4 -i out/audio.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/make-the-logo-bigger.mp4

echo "6/6  encoding the soundtrack the browser page plays"
ffmpeg -y -loglevel error -i out/audio.wav -c:a libmp3lame -b:a 160k -ar 48000 soundtrack.mp3

echo
echo "done: out/make-the-logo-bigger.mp4"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 out/make-the-logo-bigger.mp4
