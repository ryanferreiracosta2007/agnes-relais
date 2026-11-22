# -*- coding: utf-8 -*-
"""Découpe des voix des mini vendeurs : Hamza (dentifrice) et Léa (parfum)."""
import sklib, subprocess
from ras_data import parse
RAW = {
 'mini_dent': "Non,@0.00 non,@0.84 non_!@1.30 Il@1.96 me@2.14 tombe@2.30 dessus_!@2.44 Ouh@4.85 là…@5.05 ça@5.30 va,@5.45 je@5.66 suis@5.76 vivant_!@5.86 Je@7.68 vous@7.84 présente@8.02 le@8.62 dentifrice@9.04 Miswak@9.74 de@10.52 Dabur.@10.88 C'est@11.82 un@12.00 dentifrice@12.12 aux@12.52 plantes,@12.72 avec@13.28 de@13.58 l'extrait@13.76 pur@14.24 d'Al-Arak,@14.54 le@15.56 bâton@15.72 de@15.94 miswak.@16.10 Sur@17.14 la@17.30 boîte,@17.44 c'est@17.86 écrit_:@17.98 des@18.26 dents@18.66 fortes,@18.92 des@19.72 gencives@19.88 saines@20.32 et@20.60 une@21.12 haleine@21.36 fraîche.@21.72 Mmh…@22.60 ça@23.08 sent@23.58 la@23.70 fraîcheur_!@23.90 Et@24.72 il@24.88 coûte@24.96 moins@25.18 de@25.42 cinq@25.64 euros_!@25.80 Le@26.66 lien@26.84 est@27.06 juste@27.32 en@27.56 dessous,@27.72 sur@27.92 le@28.12 panier@28.26 orange.@28.46",
 'mini_parf': "Non,@0.00 non,@1.10 n'appuie@1.44 pas@1.74 là-dessus_!@1.92 Mmh…@2.80 il@3.96 sent@4.12 trop@4.40 bon,@4.90 ce@5.18 parfum_!@5.46 C'est@6.62 le@6.78 Confidential@7.14 Private@7.88 Gold@8.36 de@8.70 Lattafa.@9.04 Hé_!@10.32 Doucement,@11.14 je@11.70 suis@11.78 dessus_!@11.88 Pour@13.18 Noël,@13.40 c'est@14.06 l'idée@14.16 cadeau@14.42 parfaite,@14.76 avec@15.62 son@15.74 flacon@15.98 doré@16.34 qui@16.78 brille.@17.02 Et@17.72 il@17.86 coûte@17.94 moins@18.20 de@18.40 vingt-cinq@18.60 euros_!@18.86 Le@20.12 lien@20.30 est@20.50 juste@20.82 en@21.06 dessous,@21.22 sur@21.50 le@21.66 panier@21.82 orange.@22.02",
}
CUTS = {
 'xh_1': ('mini_dent', [(0, 3.05)]), 'xh_2': ('mini_dent', [(4.75, 6.5)]), 'xh_3': ('mini_dent', [(7.05, 11.28)]),
 'xh_4': ('mini_dent', [(11.66, 16.47)]), 'xh_5': ('mini_dent', [(16.93, 22.09)]), 'xh_6': ('mini_dent', [(22.5, 24.62)]),
 'xh_7': ('mini_dent', [(24.62, 25.97)]), 'xh_8': ('mini_dent', [(26.52, 29.08)]),
 'xl_1': ('mini_parf', [(0, 2.62)]), 'xl_2': ('mini_parf', [(2.72, 6.55)]), 'xl_3': ('mini_parf', [(6.55, 9.45)]),
 'xl_4': ('mini_parf', [(10.24, 12.22)]), 'xl_5': ('mini_parf', [(12.78, 17.45)]), 'xl_6': ('mini_parf', [(17.5, 19.1)]),
 'xl_7': ('mini_parf', [(19.74, 22.6)]),
}
PITCH = {'mini_dent': (1.22, 0.82), 'mini_parf': (1.14, 0.88)}
def words_for(c):
    src, segs = CUTS[c]; return sklib.map_words(parse(RAW[src]), segs, [])
if __name__ == '__main__':
    for c, (src, segs) in CUTS.items():
        sklib.cut_clip(src, segs, [], c + '_raw'); r, tp = PITCH[src]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'clips/{c}_raw.wav', '-af', f'asetrate=24000*{r},aresample=24000,atempo={tp},highpass=f=120',
                        '-ar', '24000', '-ac', '1', f'clips/{c}.wav'], check=True)
    for c in CUTS: print(c, [w for w, _ in words_for(c)])
