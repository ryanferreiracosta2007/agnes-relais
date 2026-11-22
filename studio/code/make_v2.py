import sys, subprocess, render as R, audio as A, sketch2, make_nuit as MN
shots, mute = sketch2.build()
if sys.argv[1] == 'stills':
    from PIL import Image
    sh = shots[0]; ts = [x * 0.5 + 0.25 for x in range(int(sh.dur * 2))]
    import cairo
    from ink import W, H
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    ims = []
    for t in ts:
        ctx.save(); ctx.set_source_rgb(0, 0, 0); ctx.paint(); R.draw_frame(ctx, sh, t); ctx.restore()
        surf.write_to_png('frames/_v2.png'); ims.append(Image.open('frames/_v2.png').convert('RGB').resize((180, 320)))
    cols = 8; sheet = Image.new('RGB', (180 * cols, 320 * ((len(ims) + cols - 1) // cols)))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 180, (i // cols) * 320))
    sheet.save('frames/v2_sheet.jpg'); print('dur', sh.dur, sketch2.T)
else:
    dur = shots[0].dur
    R.render_video(shots, 'out/v2_v.mp4')
    v, fx = R.audio_events(shots)
    A.write_wav('out/v2_mix.wav', A.mix(dur, v, fx, 'clips', bpm=124, mute=mute, mus_gain=0.42))
    MN.finish('out/v2_v.mp4', 'out/v2_mix.wav', 'out/v2_tmp.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-i','out/v2_tmp.mp4','-map','0:v','-map','0:a','-c:v','copy','-af',
                    'volume=1.8dB,alimiter=limit=0.89:level=false','-c:a','aac','-b:a','192k','-movflags','+faststart',
                    'final/Parfum_Sketch_v2.mp4'], check=True)
    print('ok', dur)
