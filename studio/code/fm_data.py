# -*- coding: utf-8 -*-
"""Découpe des voix « Fin de Movember » : Inès (Leda) et Hamza (Fenrir), tondeuse Philips OneBlade 360."""
import sklib, subprocess
RAW = {
 'fm_ines2': "Movember,@0.00 c'est@1.36 fini@1.56 dans@1.80 six@2.18 jours.@2.52 Ta@3.34 moustache,@3.46 tu@4.30 la@4.40 rases@4.52 quand_?@4.66",
 'fm_ines': "Bernard,@5.38 il@5.58 ressemble@5.74 à@6.02 un@6.16 vieux@6.54 balai_!@6.76 Ah_!@8.88 Là,@10.02 il@10.62 est@10.76 propre_!@11.00 Et@11.96 toi_:@12.16 après@12.78 Movember,@12.88 tu@13.70 gardes@13.78 la@13.96 moustache@14.04 ou@14.38 tu@14.50 rases@14.62 tout_?@14.78 Dis-le@15.50 en@15.74 commentaire.@15.86",
 'fm_hamza': "Jamais_!@0.66 Elle@1.22 a@1.36 un@1.48 nom_:@1.62 elle@2.00 s'appelle@2.10 Bernard.@2.42 Avec@7.10 le@7.26 Philips@7.54 OneBlade@7.88 360,@8.40 je@9.44 taille,@9.62 je@10.50 fais@10.66 les@10.76 contours,@10.94 et@11.50 je@11.88 garde@12.06 Bernard.@12.22 Il@13.38 est@13.52 à@13.68 50,99_€@13.86 et@15.22 à@15.80 29,99_€@16.02 avec@17.08 les@17.32 coupons@17.48 de@17.68 la@17.80 fiche.@17.86 Le@19.84 lien@20.00 est@20.20 juste@20.46 en@20.64 dessous,@20.82 sur@21.78 le@21.80 panier@21.94 orange.@22.10",
}
CUTS = {
 'xm_i1': ('fm_ines2', [(0, 3.05), (3.3, 5.1)], [0.12]),
 'xm_h1': ('fm_hamza', [(0.4, 3.3)], []),
 'xm_i2': ('fm_ines', [(5.3, 7.35)], []),
 'xm_h2': ('fm_hamza', [(7.0, 9.1), (9.4, 10.1), (10.45, 12.8)], [0.1, 0.1]),
 'xm_i3': ('fm_ines', [(8.8, 9.45), (10.0, 11.5)], [0.1]),
 'xm_h3': ('fm_hamza', [(13.3, 15.3), (15.75, 18.45)], [0.1]),
 'xm_i4': ('fm_ines', [(11.9, 12.5), (12.6, 16.6)], [0.08]),
 'xm_h4': ('fm_hamza', [(19.75, 22.5)], []),
}
PITCH = {'fm_ines': 1.04, 'fm_ines2': 1.04, 'fm_hamza': 1.04}; SPEED = 1.25
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
