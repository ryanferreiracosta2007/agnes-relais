import sys, subprocess, json, render as R, audio as A, nuit, sketch
nuit.T.update({'classement': dict(seul=2.4, n3=4.1, n3b=6.44, n2=8.42, n2b=10.78, n1=13.18, win=14.72),
               'choc': dict(ou=3.32, ml=5.08, franchement=7.26),
               'chat_ines': {}, 'chat_moi': {},
               'm3': [0.9, 2.6, 3.65, 5.3, 6.2, 6.9], 'm4': [2.35, 4.0]})
VID = {'Classement': nuit.classement, 'ChocPrix': nuit.choc, 'Discussion': nuit.chat, 'SketchDuo': sketch.build}

def finish(v, wav, out):
    m = subprocess.run(['ffmpeg','-hide_banner','-i',wav,'-af','loudnorm=I=-14:TP=-1:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}')+1])
    af = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
    subprocess.run(['ffmpeg','-v','error','-y','-i',v,'-i',wav,'-map','0:v','-map','1:a','-c:v','copy','-af',af,'-c:a','aac',
                    '-b:a','192k','-ac','2','-shortest','-movflags','+faststart',out],check=True)

def build(name, video=True):
    sh = VID[name](); dur = sum(s.dur for s in sh)
    if video: R.render_video(sh, f'out/{name}_v.mp4')
    v, fx = R.audio_events(sh)
    A.write_wav(f'out/{name}_mix.wav', A.mix(dur, v, fx, 'clips'))
    finish(f'out/{name}_v.mp4', f'out/{name}_mix.wav', f'out/Parfum_{name}.mp4')
    print('ok', name, round(dur, 1), flush=True)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stills':
        from PIL import Image
        for n in ['Classement', 'ChocPrix', 'Discussion']:
            sh = VID[n](); R.stills(sh, 'x', per=3)
            fs = [f'frames/st_{s.name}_{k}.png' for s in sh for k in range(3)]
            sheet = Image.new('RGB', (200 * 6, 356 * ((len(fs) + 5) // 6)))
            for i, f in enumerate(fs): sheet.paste(Image.open(f).resize((200, 356)), ((i % 6) * 200, (i // 6) * 356))
            sheet.save(f'frames/nuit_{n}.jpg'); print(n, [(s.name, round(s.dur, 1)) for s in sh])
    else:
        build(mode, video=(len(sys.argv) < 3))
