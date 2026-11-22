import sys, subprocess, numpy as np, json
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
out={}
for f in sys.argv[1:]:
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
    segs,_=m.transcribe(np.frombuffer(raw,np.float32),language='fr',word_timestamps=True)
    out[f]=[(w.word.strip(),round(w.start,2),round(w.end,2)) for s in segs for w in s.words]
json.dump(out,open('words.json','w'),ensure_ascii=False)
for f,ws in out.items(): print(f, ' '.join(f"{w}@{a}" for w,a,b in ws))
