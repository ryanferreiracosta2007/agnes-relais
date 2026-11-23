"""Transcription mot à mot (faster-whisper medium int8, fr) -> format RAW « mot@t »"""
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel('medium', device='cpu', compute_type='int8')
for f in sys.argv[1:]:
    raw = subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    segs, _ = m.transcribe(a, language='fr', word_timestamps=True)
    toks = []
    print('==', f)
    for s in segs:
        print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
        for w in s.words: toks.append(f"{w.word.strip().replace(' ', '_')}@{w.start:.2f}~{w.end:.2f}")
    print('RAW', ' '.join(toks))
