# -*- coding: utf-8 -*-
import sklib, subprocess, os
from ras_data import parse
RAW = "Hé !@0.00 Toi,@0.74 là !@1.14 Oui,@1.48 toi@1.72 qui@1.94 scrolles !@2.14 Regarde@2.80 ce@3.12 que@3.24 j'ai@3.28 trouvé.@3.48 C'est@4.38 le@4.58 Philips@4.86 OneBlade@5.26 360.@5.96 Il@7.06 taille,@7.28 il@7.84 fait@7.98 les@8.08 contours@8.26 et@8.58 il@8.90 rase.@9.08 Attention,@9.96 il@10.50 arrive !@10.70 Et@11.76 il@11.92 a@12.02 même@12.20 une@12.36 application@12.52 gratuite@12.98 pour@13.34 essayer@13.52 les@13.80 styles@14.00 de@14.12 barbe.@14.32 Il@15.22 est@15.34 affiché@15.52 à@15.80 50,99_€@16.04 et@17.16 à@17.70 29,99_€@17.96 avec@19.32 les@19.72 coupons@19.90 de@20.08 la@20.18 fiche.@20.26 Le@21.38 Black@21.56 Friday@21.74 dure@22.08 jusqu'au@22.46 30@22.80 novembre.@23.02 Le@23.80 lien@23.96 est@24.12 juste@24.44 en@24.66 dessous,@24.80 sur@25.26 le@25.32 panier@25.46 orange.@25.62"
RAW = RAW.replace('Hé !', 'Hé_!').replace('là !', 'là_!').replace('scrolles !', 'scrolles_!').replace('arrive !', 'arrive_!')
CUTS = {'xm_1': [(0, 3.71)], 'xm_2': [(4.14, 9.35)], 'xm_3': [(9.93, 11.07)], 'xm_4': [(11.76, 14.50)], 'xm_5': [(15.0, 20.51)], 'xm_6': [(21.19, 26.28)]}
def words_for(c): return sklib.map_words(parse(RAW), CUTS[c], [])
if __name__ == '__main__':
    for c, segs in CUTS.items():
        sklib.cut_clip('mini', segs, [], c + '_raw')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'clips/{c}_raw.wav', '-af', 'asetrate=24000*1.22,aresample=24000,atempo=0.82,highpass=f=120',
                        '-ar', '24000', '-ac', '1', f'clips/{c}.wav'], check=True)
    for c in CUTS: print(c, [w for w, _ in words_for(c)])
