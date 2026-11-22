import sys, subprocess, os
import render as R, scenes as S, audio as A
CTA = [('CONFIDENTIAL PRIVATE GOLD, DE LATTAFA.', 0.0), ('MOINS DE 25 €.', 3.15), ('CLIQUE SUR LE PANIER ORANGE,', 4.65), ('JUSTE EN DESSOUS.', 6.1)]
body = S.body('cta1', CTA)
hooks = {'A_prix': S.hookA(), 'B_seduction': S.hookB(), 'C_cadeau': S.hookC()}
os.makedirs('out', exist_ok=True)
what = sys.argv[1]
if what == 'body':
    R.render_video(body, 'out/body.mp4')
elif what in hooks:
    R.render_video(hooks[what], f'out/hook_{what}.mp4')
elif what == 'final':
    for k, hk in hooks.items():
        dh = sum(s.dur for s in hk); db = sum(s.dur for s in body)
        v1, f1 = R.audio_events(hk); v2, f2 = R.audio_events(body, dh)
        mix = A.mix(dh + db, v1 + v2, f1 + f2, 'clips')
        A.write_wav(f'out/mix_{k}.wav', mix)
        open('out/list.txt', 'w').write(f"file 'hook_{k}.mp4'\nfile 'body.mp4'\n")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'out/list.txt', '-i', f'out/mix_{k}.wav',
                        '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-ac', '2',
                        '-shortest', '-movflags', '+faststart', f'out/Parfum6_{k}.mp4'], check=True)
        print('ok', k, dh + db)
