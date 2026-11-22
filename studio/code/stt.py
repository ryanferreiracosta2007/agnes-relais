import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
for f in sys.argv[1:]:
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.float32)
    segs,_=m.transcribe(a,language='fr',word_timestamps=True)
    print('==',f)
    for s in segs:
        print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
