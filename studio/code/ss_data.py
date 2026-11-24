# -*- coding: utf-8 -*-
"""Découpe des voix « Secret Santa au bureau » : David (Puck) et Sarah (Aoede), parfum Lattafa."""
import sklib, subprocess
RAW = {
 'ss_david': "Secret@0.00 Santa@0.82 au@1.28 bureau_:@1.50 vingt-cinq@2.18 euros@2.42 de@2.66 budget.@2.80 Tu@3.24 lui@3.30 offres@3.42 quoi_?@3.60 Des@4.70 chaussettes@4.86 de@5.10 Noël_?@5.18 Alors…@6.18 le@7.20 Confidential@7.58 Private@8.20 Gold@8.64 de@8.90 Lattafa.@9.14 Et@10.04 il@10.12 coûte@10.24 moins@10.60 de@10.88 vingt-cinq@11.10 euros.@11.36 Le@12.26 lien@12.32 est@12.50 juste@12.86 en@13.04 dessous,@13.24 sur@13.56 le@13.60 panier@13.72 orange.@13.88",
 'ss_sarah': "Pas@0.00 un@0.68 mug,@1.10 s'il@1.74 te@1.90 plaît.@2.06 J'en@2.54 ai@2.72 déjà@2.84 douze.@3.04 Elles@4.94 vont@5.10 finir@5.30 au@5.90 fond@6.18 du@6.28 tiroir.@6.46 Oh_!@8.56 Le@9.66 flacon@9.94 doré…@10.22 là,@11.26 tu@12.24 marques@12.32 des@12.50 points.@12.68 Parfum@13.90 au@14.30 Secret@14.60 Santa_:@14.96 bonne@15.96 idée@16.20 ou@16.54 trop@16.82 perso_?@16.96 Dis-le@17.88 en@18.06 commentaire.@18.22",
}
CUTS = {
 'xs_d1': ('ss_david', [(0, 3.95)], []),
 'xs_s1': ('ss_sarah', [(0, 3.72)], []),
 'xs_d2': ('ss_david', [(4.62, 5.72)], []),
 'xs_s2': ('ss_sarah', [(4.86, 7.15)], []),
 'xs_d3': ('ss_david', [(6.12, 6.56), (7.14, 9.88)], [0.22]),
 'xs_s3': ('ss_sarah', [(8.48, 9.2), (9.6, 10.78), (11.2, 13.05)], [0.12, 0.12]),
 'xs_d4': ('ss_david', [(9.98, 11.82)], []),
 'xs_s4': ('ss_sarah', [(13.84, 15.32), (15.9, 18.8)], [0.18]),
 'xs_d5': ('ss_david', [(12.2, 14.3)], []),
}
PITCH = {'ss_david': 1.08, 'ss_sarah': 1.05}; SPEED = 1.2
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
