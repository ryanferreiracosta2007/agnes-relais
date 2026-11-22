import sys, subprocess, render as R, audio as A, dent_videos as DV, make_nuit as MN
from PIL import Image
import cairo
from ink import W, H
VIDS = {'haleine': (DV.build1, 'Dentifrice_Sketch_Haleine', 122), 'promo': (DV.build2, 'Dentifrice_Presentation', 112)}
name, mode = sys.argv[1], sys.argv[2]
build, out, bpm = VIDS[name]; shots, mute = build(); sh = shots[0]
if mode == 'stills':
    ts = [x * 0.5 + 0.25 for x in range(int(sh.dur * 2))]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); ims = []
    for t in ts:
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint(); R.draw_frame(ctx, sh, t); ctx.restore()
        surf.write_to_png('frames/_d.png'); ims.append(Image.open('frames/_d.png').convert('RGB').resize((180, 320)))
    cols = 8; sheet = Image.new('RGB', (180 * cols, 320 * ((len(ims) + cols - 1) // cols)))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 180, (i // cols) * 320))
    sheet.save(f'frames/{name}_sheet.jpg'); print(name, 'dur', round(sh.dur, 2))
else:
    R.render_video(shots, f'out/{name}_v.mp4')
    v, fx = R.audio_events(shots)
    A.write_wav(f'out/{name}_mix.wav', A.mix(sh.dur, v, fx, 'clips', bpm=bpm, mute=mute, mus_gain=0.42))
    MN.finish(f'out/{name}_v.mp4', f'out/{name}_mix.wav', f'out/{name}_tmp.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'out/{name}_tmp.mp4','-map','0:v','-map','0:a','-c:v','copy','-af',
                    'volume=1.5dB,alimiter=limit=0.89:level=false','-c:a','aac','-b:a','192k','-movflags','+faststart',
                    f'final/{out}.mp4'], check=True)
    print('ok', name, round(sh.dur, 2))
