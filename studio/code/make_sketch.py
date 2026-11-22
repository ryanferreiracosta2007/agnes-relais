import subprocess, render as R, audio as A, sketch
sh = sketch.build(); dur = sum(s.dur for s in sh)
R.render_video(sh, 'out/sketch_v.mp4')
v, fx = R.audio_events(sh)
A.write_wav('out/sketch_mix.wav', A.mix(dur, v, fx, 'clips'))
subprocess.run(['ffmpeg','-v','error','-y','-i','out/sketch_v.mp4','-i','out/sketch_mix.wav','-map','0:v','-map','1:a','-c:v','copy',
  '-af','loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000','-c:a','aac','-b:a','192k','-ac','2','-shortest','-movflags','+faststart','out/Sketch_Parfum_Duo.mp4'],check=True)
print('ok', dur)
