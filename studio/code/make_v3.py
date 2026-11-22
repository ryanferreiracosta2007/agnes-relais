import sys, subprocess, render as R, audio as A, sketch3 as SK, make_nuit as MN
shots, mute = SK.build()
if sys.argv[1] == 'stills':
    from PIL import Image
    import cairo
    from ink import W, H
    sh = shots[0]; ts = [x * 0.5 + 0.25 for x in range(int(sh.dur * 2))]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf); ims = []
    for t in ts:
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint(); R.draw_frame(ctx, sh, t); ctx.restore()
        surf.write_to_png('frames/_v3.png'); ims.append(Image.open('frames/_v3.png').convert('RGB').resize((180, 320)))
    cols = 8; sheet = Image.new('RGB', (180 * cols, 320 * ((len(ims) + cols - 1) // cols)))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 180, (i // cols) * 320))
    sheet.save('frames/v3_sheet.jpg'); print('dur', round(sh.dur, 2))
else:
    dur = shots[0].dur
    R.render_video(shots, 'out/v3_v.mp4')
    v, fx = R.audio_events(shots)
    A.write_wav('out/v3_mix.wav', A.mix(dur, v, fx, 'clips', bpm=118, mute=mute, mus_gain=0.42))
    MN.finish('out/v3_v.mp4', 'out/v3_mix.wav', 'out/v3_tmp.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-i','out/v3_tmp.mp4','-map','0:v','-map','0:a','-c:v','copy','-af',
                    'volume=1.5dB,alimiter=limit=0.89:level=false','-c:a','aac','-b:a','192k','-movflags','+faststart',
                    'final/Parfum_Cadeau_Noel.mp4'], check=True)
    print('ok', dur)
