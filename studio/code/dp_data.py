# -*- coding: utf-8 -*-
"""Découpe des voix « Détecteur de bobards » (Black Friday) : Inès (Leda) et David (Puck), parfum Lattafa.
   Transcription de contrôle faster-whisper OK (« en dessous », « panier orange »). « la TAFA » = Lattafa (son correct)."""
import sklib, subprocess
RAW = {
 'dp_ines': "Tu@0.00 crois@0.14 encore@0.32 aux@0.60 promos@0.78 du@0.94 Black@1.14 Friday_?@1.36 Sauf@2.46 lui.@2.66 Le@3.62 Confidential@3.84 Private@4.38 Gold@4.92 de@5.10 Lattafa.@5.30 Pas@6.40 de@6.48 pourcentage@6.62 magique_:@7.12 il@7.68 coûte@7.78 moins@8.16 de@8.42 vingt-cinq@8.76 euros.@9.04 Le@10.36 lien@10.46 est@10.66 juste@10.92 en@11.16 dessous,@11.30 sur@11.56 le@11.74 panier@11.88 orange.@12.08 Et@13.14 toi,@13.26 tu@13.64 crois@13.70 encore@13.82 aux@14.02 promos_?@14.20 Dis-le@14.76 en@14.94 commentaire.@15.06",
 'dp_david': "Black@0.00 Friday_!@0.56 Moins@1.76 90_%@2.16 sur@3.48 tout_!@3.86 Euh…@5.36 sur…@6.12 presque@6.88 tout_?@7.14 Bon,@8.06 d'accord…@8.82 c'était@9.52 le@9.84 prix@9.96 normal.@10.12",
}
CUTS = {
 'xp_i1': ('dp_ines', [(0.0, 1.95)], []),
 'xp_d1': ('dp_david', [(0.0, 4.25)], []),
 'xp_d2': ('dp_david', [(5.0, 7.75)], []),
 'xp_d3': ('dp_david', [(7.85, 10.6)], []),
 'xp_i2': ('dp_ines', [(2.28, 5.95)], []),
 'xp_i3': ('dp_ines', [(6.30, 9.55)], []),
 'xp_i4': ('dp_ines', [(10.25, 12.60)], []),
 'xp_i5': ('dp_ines', [(13.0, 15.6)], []),
}
PITCH = {'dp_ines': 1.05, 'dp_david': 1.0}; SPEED = 1.12
def parse(s):
    return [(w.replace('_', ' ').upper(), float(t)) for w, t in (tok.rsplit('@', 1) for tok in s.split(' '))]
def words_for(c):
    src, segs, gaps = CUTS[c]
    return [(w, t / SPEED) for w, t in sklib.map_words(parse(RAW[src]), segs, gaps)]
if __name__ == '__main__':
    for c, (src, segs, gaps) in CUTS.items():
        sklib.cut_clip(src, segs, gaps, c + '_raw'); r = PITCH[src]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'clips/{c}_raw.wav', '-af',
                        f'asetrate=24000*{r},aresample=24000,atempo={SPEED / r:.4f},highpass=f=110',
                        '-ar', '24000', '-ac', '1', f'clips/{c}.wav'], check=True)
    import scenes
    tot = 0
    for c in CUTS:
        L = scenes.clip_len(c); tot += L; print(c, round(L, 2), [w for w, _ in words_for(c)])
    print('total voix', round(tot, 2))
