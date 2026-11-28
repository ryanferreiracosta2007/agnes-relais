# -*- coding: utf-8 -*-
"""Découpe des voix « Calendrier de l'Avent » (parfum Lattafa) : Sarah (Aoede) et Hamza (Fenrir).
   Transcription de contrôle faster-whisper OK (« en dessous », « panier orange »). « de l'ATFA » = Lattafa (son correct)."""
import sklib, subprocess
RAW = {
 'ca_sarah': "POV_:@0.00 tu@0.90 ouvres@1.14 ton@1.32 calendrier@1.56 de@2.14 l'Avent.@2.32 Case@3.70 un_:@3.92 un@4.92 tout@5.20 petit@5.38 chocolat.@5.56 Case@7.08 deux…@7.28 encore@8.36 un@8.50 tout@8.72 petit@8.84 chocolat.@9.02 Quoi_?!@10.42 Le@11.28 Confidential@11.70 Private@12.42 Gold@12.70 de@12.96 Lattafa_?!@13.20 Et@14.38 toi,@14.60 tu@15.12 préfères@15.30 vingt-quatre@15.70 petits@16.02 chocolats,@16.36 ou@16.90 un@17.16 seul@17.46 vrai@17.68 cadeau_?@17.92 Dis-le@18.68 en@18.90 commentaire.@19.10 Le@20.08 lien@20.28 est@20.50 juste@20.78 en@21.00 dessous,@21.20 sur@21.48 le@21.62 panier@21.82 orange.@22.04",
 'ca_hamza': "Attends_!@0.00 Saute@0.94 direct@1.28 à@1.72 la@1.94 case@2.10 vingt-quatre_!@2.28 Un@3.86 vrai@4.24 cadeau,@4.48 tout@5.34 doré…@5.54 et@6.34 il@6.50 coûte@6.60 moins@6.96 de@7.26 vingt-cinq@7.52 euros_!@7.92",
}
CUTS = {
 'xc_s1': ('ca_sarah', [(0.0, 0.34), (0.62, 2.62)], [0.1]),
 'xc_s2': ('ca_sarah', [(3.58, 4.30), (4.82, 6.15)], [0.15]),
 'xc_s3': ('ca_sarah', [(6.98, 7.58), (8.05, 9.88)], [0.3]),
 'xc_h1': ('ca_hamza', [(0.0, 2.90)], []),
 'xc_s4': ('ca_sarah', [(10.22, 10.78), (11.15, 13.78)], [0.12]),
 'xc_h2': ('ca_hamza', [(3.72, 8.56)], []),
 'xc_s5': ('ca_sarah', [(14.28, 19.60)], []),
 'xc_s6': ('ca_sarah', [(19.95, 22.60)], []),
}
PITCH = {'ca_sarah': 1.04, 'ca_hamza': 1.0}; SPEED = 1.15
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
