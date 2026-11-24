import sys, subprocess, render as R, audio as A, make_nuit as MN
import mini2 as M2, rf_videos as RV, pb_videos as PV, tb_videos as TBV, ss_videos as SSV, fm_videos as FMV
from PIL import Image
import cairo
from ink import W, H
VIDS = {'gal': (PV.build_gal, 'Rasoir_3_Galeres', 116), 'date': (PV.build_date, 'Rasoir_POV_Rendez_Vous', 98), 'doc': (RV.build_doc, 'Rasoir_Documentaire_Poils', 100), 'gerard': (RV.build_g, 'Rasoir_Gerard_la_Barbe', 108), 'dent': (M2.build_dent, 'Dentifrice_Mini_Hamza', 112), 'parf': (M2.build_parf, 'Parfum_Mini_Lea_Noel', 104), 'tb': (TBV.build_tb, 'Dentifrice_Team_Brosse_Mouillee_ou_Seche', 110), 'ss': (SSV.build_ss, 'Parfum_Secret_Santa_Bureau', 106), 'fm': (FMV.build_fm, 'Rasoir_Fin_de_Movember_Bernard', 112)}
name, mode = sys.argv[1], sys.argv[2]
build, out, bpm = VIDS[name]; shots, mute = build(); sh = shots[0]
if mode == 'stills':
    ts = [x * 0.5 + 0.25 for x in range(int(sh.dur * 2))]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); ims = []
    for t in ts:
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint(); R.draw_frame(ctx, sh, t); ctx.restore()
        surf.write_to_png('frames/_m.png'); ims.append(Image.open('frames/_m.png').convert('RGB').resize((180, 320)))
    cols = 8; sheet = Image.new('RGB', (180 * cols, 320 * ((len(ims) + cols - 1) // cols)))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 180, (i // cols) * 320))
    sheet.save(f'frames/new_{name}.jpg'); print(name, 'dur', round(sh.dur, 2))
else:
    R.render_video(shots, f'out/{name}_v.mp4')
    v, fx = R.audio_events(shots)
    A.write_wav(f'out/{name}_mix.wav', A.mix(sh.dur, v, fx, 'clips', bpm=bpm, mute=mute, mus_gain=0.42))
    MN.finish(f'out/{name}_v.mp4', f'out/{name}_mix.wav', f'out/{name}_tmp.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'out/{name}_tmp.mp4','-map','0:v','-map','0:a','-c:v','copy','-af',
                    'volume=1.0dB,alimiter=limit=0.89:level=false','-c:a','aac','-b:a','192k','-movflags','+faststart',
                    f'final/{out}.mp4'], check=True)
    print('ok', name, round(sh.dur, 2))
