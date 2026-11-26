# -*- coding: utf-8 -*-
"""Découpe des voix « Micro-trottoir : j'interviewe une tondeuse » : Inès (Leda) et la tondeuse (Algenib), Philips OneBlade 360.
   Coupés pour tenir en 25 s : « Aujourd'hui », la question 2 (contre-sens), « Question 3 », « quelle que soit la longueur » et
   « Je suis le Philips OneBlade 360 » (la marque reste à l'écran). Whisper entend « de l'affiche » pour « de la fiche » (homophones)."""
import sklib, subprocess
RAW = {
 'it_ines': "Micro-trottoir_!@0.00 Aujourd'hui,@1.32 j'interviewe@1.96 une@2.64 tondeuse.@2.84 Question@4.10 une,@4.42 tu@5.12 sers@5.30 à@5.52 quoi_?@5.70 Question@10.14 trois,@10.46 tu@11.12 coupes@11.28 la@11.50 peau_?@11.58 Dernière@12.56 question,@13.06 tu@13.78 coûtes@13.92 combien_?@14.22 Et@15.30 toi,@15.64 tu@16.14 lui@16.20 poserais@16.36 quelle@16.68 question_?@16.76 Écris-la@17.70 en@18.06 commentaire.@18.28 Le@19.42 lien@19.62 est@19.80 juste@20.04 en@20.30 dessous,@20.52 sur@20.88 le@21.04 panier@21.22 orange.@21.44",
 'it_ob': "Je@0.00 taille,@0.50 je@1.48 fais@1.62 les@1.78 contours@1.96 et@2.60 je@3.00 rase.@3.42 Non.@11.40 Je@12.26 suis@12.52 conçu@12.80 pour@13.12 couper@13.36 les@13.72 poils,@13.98 pas@14.68 la@14.78 peau.@14.98 50,99_€@19.04 et@20.40 29,99_€@21.24 avec@22.70 les@23.04 coupons@23.24 de@23.48 la@23.62 fiche.@23.70",
}
CUTS = {
 'xi_i1': ('it_ines', [(0.0, 1.20), (1.92, 3.38)], [0.08]),
 'xi_i2': ('it_ines', [(4.02, 5.9)], []),
 'xi_o1': ('it_ob', [(0.0, 4.18)], []),
 'xi_i3': ('it_ines', [(11.05, 12.02)], []),
 'xi_o2': ('it_ob', [(11.34, 11.74), (12.2, 15.5)], [0.18]),
 'xi_i4': ('it_ines', [(12.5, 14.58)], []),
 'xi_o3': ('it_ob', [(18.98, 24.08)], []),
 'xi_i5': ('it_ines', [(15.1, 18.68)], []),
 'xi_i6': ('it_ines', [(19.32, 21.78)], []),
}
PITCH = {'it_ines': 1.04, 'it_ob': 1.0}; SPEED = 1.25
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
