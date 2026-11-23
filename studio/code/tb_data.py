# -*- coding: utf-8 -*-
"""Découpe des voix « team brosse mouillée ou sèche » : Hamza (Fenrir) et Inès (Leda), dentifrice Miswak."""
import sklib, subprocess
RAW = {
 'tb_hamza': "Attends,@0.00 tu@1.32 mets@1.48 le@1.72 dentifrice@1.96 sur@2.58 une@2.86 brosse@3.14 sèche_?@3.50 N'importe@5.16 quoi_!@5.58 C'est@6.52 toi,@6.74 n'importe@7.12 quoi_!@7.38 Le@8.28 Miswak@8.54 de@9.12 Dabur.@9.38 C'est@10.18 un@10.28 dentifrice@10.38 aux@10.86 plantes,@11.12 avec@11.80 de@11.90 l'extrait@12.04 pur@12.50 d'Al-Arak.@12.72 Et@13.78 il@13.92 coûte@14.08 moins@14.40 de@14.58 cinq@14.82 euros_!@14.98",
 'tb_ines': "Bah@0.00 oui,@0.64 mouiller@1.42 la@1.74 brosse@2.04 avant,@2.28 c'est@2.88 n'importe@3.04 quoi.@3.32 Bon,@4.56 au@5.46 moins@5.50 on@5.68 est@5.78 d'accord@5.96 sur@6.16 le@6.30 dentifrice.@6.42 Sur@7.54 la@7.72 boîte,@7.90 c'est@8.42 écrit_:@8.60 des@8.88 dents@9.28 fortes,@9.56 des@10.26 gencives@10.38 saines@10.88 et@11.16 une@11.48 haleine@11.70 fraîche.@12.00 Et@12.96 toi,@13.12 t'es@13.74 team@13.92 brosse@14.12 mouillée@14.40 ou@14.72 team@14.96 brosse@15.26 sèche_?@15.56 Dis-le@16.40 en@16.60 commentaire.@16.78 Le@17.66 lien@17.82 est@17.98 juste@18.14 en@18.32 dessous,@18.46 sur@18.98 le@19.04 panier@19.18 orange.@19.40",
}
CUTS = {
 'xb_h1': ('tb_hamza', [(0, 0.92), (1.28, 4.42)], [0.08]),
 'xb_i1': ('tb_ines', [(1.36, 3.76)], []),
 'xb_i2': ('tb_ines', [(4.50, 4.90), (5.40, 6.98)], [0.12]),
 'xb_h2': ('tb_hamza', [(8.22, 13.45)], []),
 'xb_i3': ('tb_ines', [(7.48, 12.56)], []),
 'xb_i4': ('tb_ines', [(12.90, 17.42)], []),
 'xb_h3': ('tb_hamza', [(13.72, 15.42)], []),
 'xb_i5': ('tb_ines', [(17.60, 19.78)], []),
}
# (hauteur, vitesse finale) : voix de mini personnages un peu plus aiguës et plus rapides
PITCH = {'tb_hamza': 1.12, 'tb_ines': 1.07}; SPEED = 1.18
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
