"""Writes captions.srt from the same timeline the video is rendered from,
so the subtitle file can never drift out of sync with the picture.

Includes both the burned-in captions and the spoken lines, which are labelled
with their speaker, so the file doubles as a transcript.
"""
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
timeline = json.loads((REPO / 'tools' / 'timeline.json').read_text())
cues = sorted(timeline['subs'] + timeline['spoken'])


def stamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


blocks, previous_end = [], 0.0
for n, (start, end, text) in enumerate(cues, 1):
    if start < previous_end - 1e-6:
        raise SystemExit(f'cue {n} overlaps the one before it: {text!r}')
    previous_end = end
    blocks.append(f'{n}\n{stamp(start)} --> {stamp(end)}\n{text}\n')

(REPO / 'captions.srt').write_text('\n'.join(blocks), encoding='utf-8')
print(f'captions.srt: {len(cues)} cues, shortest on screen {min(e - s for s, e, _ in cues):.1f}s')
