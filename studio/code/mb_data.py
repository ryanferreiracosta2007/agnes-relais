# -*- coding: utf-8 -*-
"""Découpe des voix « le miswak, c'est d'abord un bâton ? » : mini Sarah (Aoede) et mini Léa (Zephyr), dentifrice Miswak.
   « de Dabur » est retiré de la réplique de Léa (prononciation douteuse à la transcription) : la marque est écrite à l'écran."""
import sklib, subprocess
RAW = {
 'mb_sarah': "Tu@0.00 savais@0.50 que@0.88 le@1.00 Miswak,@1.26 c'est@2.00 d'abord@2.14 un@2.34 bâton_?@2.54 Regarde,@3.36 je@3.88 te@3.98 montre_!@4.14 Bon,@5.26 il@5.80 est@5.90 un@6.04 peu@6.12 trop@6.32 grand@6.58 pour@6.74 moi.@6.94 Sur@7.94 la@8.10 boîte,@8.26 c'est@8.60 écrit_:@8.78 des@8.96 dents@9.54 fortes,@9.88 des@10.56 gencives@10.72 saines@11.22 et@11.44 une@11.78 haleine@11.98 fraîche.@12.32 Et@13.34 toi,@13.52 tu@14.04 as@14.06 déjà@14.20 essayé@14.44 le@14.78 vrai@14.96 bâton_?@15.10 Dis-le@15.84 en@16.08 commentaire_!@16.30",
 'mb_lea': "Sarah...@0.66 le@1.58 Miswak,@1.78 il@2.46 existe@2.46 aussi@2.64 en@2.86 dentifrice_!@3.02 Le@4.14 Miswak,@4.38 c'est@6.46 un@6.58 dentifrice@6.68 aux@7.12 plantes,@7.46 avec@8.18 de@8.26 l'extrait@8.42 pur@8.90 d'Al-Arak.@9.18 Et@10.38 il@10.56 coûte@10.68 moins@11.00 de@11.28 cinq@11.68 euros_!@11.86 Le@13.12 lien@13.24 est@13.38 juste@13.66 en@13.88 dessous,@14.06 sur@14.44 le@14.46 panier@14.62 orange.@14.82",
}
CUTS = {
 'mbs_1': ('mb_sarah', [(0.0, 3.05)], []),
 'mbs_2': ('mb_sarah', [(3.30, 4.62)], []),
 'mbs_3': ('mb_sarah', [(5.20, 7.35)], []),
 'mbl_1': ('mb_lea', [(0.3, 3.75)], []),
 'mbl_2': ('mb_lea', [(4.08, 4.88), (6.36, 10.05)], [0.12]),
 'mbs_4': ('mb_sarah', [(7.88, 12.95)], []),
 'mbs_5': ('mb_sarah', [(13.28, 17.00)], []),
 'mbl_3': ('mb_lea', [(10.32, 12.40)], []),
 'mbl_4': ('mb_lea', [(13.05, 15.30)], []),
}
PITCH = {'mb_sarah': 1.07, 'mb_lea': 1.06}; SPEED = 1.2
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
