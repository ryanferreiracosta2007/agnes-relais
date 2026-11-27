# -*- coding: utf-8 -*-
"""Découpe des voix « La météo de ta barbe » : Léa présentatrice météo (Zephyr) et Hamza (Fenrir), Philips OneBlade 360.
   Accroche régénérée (mb3_lea) : « Bulletin » de la 1re prise était mal entendu par Whisper, on garde « la météo de ta barbe ».
   Whisper entend « de l'affiche » pour « de la fiche » (homophones, déjà vu le 26/11)."""
import sklib, subprocess
RAW = {
 'mb3_lea': "La@1.00 météo@1.22 de@1.66 ta@1.90 barbe_!@2.04",
 'mb2_lea': "Alerte@3.26 orange_:@3.44 des@4.10 poils@4.28 partout@4.52 sur@4.88 le@5.12 cou.@5.28 Heureusement,@6.74 une@7.38 éclaircie@7.52 arrive_:@7.96 le@8.50 Philips@8.74 OneBlade@9.06 360.@9.54 Il@10.70 taille,@10.92 il@11.52 fait@11.62 les@11.74 contours@11.86 et@12.18 il@12.46 rase.@12.66 Il@13.98 est@14.08 à@14.24 50,99_€,@14.34 et@15.26 à@15.78 29,99_€@16.00 avec@16.96 les@17.36 coupons@17.56 de@17.72 la@17.82 fiche.@17.90 Le@19.48 lien@19.60 est@19.76 juste@19.96 en@20.20 dessous,@20.36 sur@20.60 le@20.78 panier@20.92 orange.@21.12 Et@22.06 chez@22.24 toi,@22.38 c'est@22.90 soleil,@23.06 nuages@23.60 ou@23.84 tempête_?@24.08 Dis-le@24.76 en@24.96 commentaire.@25.06",
 'mb2_hamza': "Eh_!@0.00 C'est@0.60 pas@0.82 une@0.92 tempête,@1.12 c'est@1.90 mon@2.06 style_!@2.24 Bon…@3.40 d'accord.@4.72 Ciel@5.74 dégagé.@5.88",
}
CUTS = {
 'xm_l1': ('mb3_lea', [(0.93, 2.62)], []),
 'xm_l2': ('mb2_lea', [(3.18, 6.10)], []),
 'xm_h1': ('mb2_hamza', [(0.0, 2.95)], []),
 'xm_l3': ('mb2_lea', [(6.62, 10.40)], []),
 'xm_l4': ('mb2_lea', [(10.62, 13.45)], []),
 'xm_h2': ('mb2_hamza', [(3.32, 3.85), (4.62, 6.55)], [0.22]),
 'xm_l5': ('mb2_lea', [(13.90, 18.60)], []),
 'xm_l6': ('mb2_lea', [(19.40, 21.70)], []),
 'xm_l7': ('mb2_lea', [(21.96, 25.76)], []),
}
PITCH = {'mb3_lea': 1.03, 'mb2_lea': 1.03, 'mb2_hamza': 1.0}; SPEED = 1.2
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
