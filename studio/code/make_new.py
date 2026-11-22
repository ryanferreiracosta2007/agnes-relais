import sys, subprocess, render as R, audio as A, make_nuit as MN, ras_data as RD, noel_data as ND, mini_data as MD, rasoir_videos as RV
RV.WORDS.update({c: RD.words_for(c) for c in RD.CUTS}); RV.WORDS.update({c: ND.words_for(c) for c in ND.CUTS}); RV.WORDS.update({c: MD.words_for(c) for c in MD.CUTS})
import rasoir_noel as RN, rasoir_mini as RM, coldopen as CO
from scenes import clip_len
from PIL import Image
import cairo
from ink import W, H
def co_cadeau():
    sh = RN.build4()[0][0]; T = sh.tl.T
    tbush = T['xn_i2'] + RN.wt('xn_i2', 'BUISSON', 1.6)
    return [CO.make(sh, tbush - 0.5, T['xn_h2'] + 0.62)], None
def co_barbe():
    sh = RV.build1()[0][0]; T = sh.tl.T
    ar0 = T['xr_m2'] + clip_len('xr_m2') + 0.07
    return [CO.make(sh, T['xr_s3'] - 0.6, T['xr_s3'] + clip_len('xr_s3') + 0.35)], None
VIDS = {'mini': (RM.build, 'Rasoir_Mini_Vendeur', 124), 'co_cadeau': (co_cadeau, 'Rasoir_Noel_Cadeau_HOOK', 116),
        'co_barbe': (co_barbe, 'Rasoir_Sketch_Barbe_HOOK', 118)}
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
