# -*- coding: utf-8 -*-
"""Tondeuse, saison 2 : faux documentaire animalier (narrateur + poils) et Gérard la barbe."""
import sklib, subprocess
from ras_data import parse
RAW = {
 'docu': "Chut…@0.00 Ne@1.64 faites@1.94 aucun@2.12 bruit.@2.46 Ici,@3.54 dans@4.42 la@4.52 salle@4.70 de@4.92 bain,@5.14 vit@6.16 une@6.30 créature@6.54 redoutée@7.34 de@8.18 tous@8.52 les@8.66 poils_:@8.90 le@10.80 Philips@11.20 OneBlade@11.66 360.@12.30 Le@14.24 voilà@14.42 qui@14.62 sort@14.96 de@15.10 sa@15.28 tanière.@15.42 Il@16.64 chasse@16.98 de@17.30 trois@17.62 façons_:@17.80 il@18.86 taille,@19.10 il@19.94 fait@20.16 les@20.26 contours,@20.46 et@20.98 il@21.36 rase,@21.68 quelle@23.04 que@23.16 soit@23.32 la@23.46 longueur.@23.64 Sa@24.72 lame@24.86 360@25.10 suit@26.06 les@26.42 courbes@26.70 du@27.06 visage.@27.26 Aucun@28.36 poil@28.64 ne@28.88 lui@29.00 échappe.@29.20 Il@30.08 chasse@30.26 même@30.54 sous@30.88 l'eau,@31.06 car@31.50 il@31.84 est@31.98 étanche.@32.20 On@33.50 peut@33.60 l'observer@33.76 à@34.38 50,99_€@34.76 et@36.22 à@37.16 29,99_€@37.46 avec@39.04 les@39.34 coupons@39.58 de@39.82 la@39.98 fiche.@40.12 Le@41.56 lien@41.76 est@41.96 juste@42.20 en@42.38 dessous,@42.60 sur@43.14 le@43.20 panier@43.38 orange.@43.64",
 'poils': "Au@0.00 secours_!@0.60 Il@1.30 arrive_!@1.40 Cours,@3.06 Kevin,@3.50 cours_!@4.22 Nooooon_!@5.56 On@6.84 est@7.26 fichus_!@7.48",
 'barbe': "Au@0.00 secours_!@1.06 Il@1.84 veut@2.12 me@2.24 raser_!@2.44 Bonjour.@4.14 Moi,@4.86 c'est@5.16 Gérard,@5.52 la@6.36 barbe@6.54 de@6.72 Hamza.@6.88 Et@7.80 lui,@7.92 là,@8.10 c'est@8.72 mon@8.94 pire@9.10 ennemi_:@9.34 le@10.04 Philips@10.28 OneBlade@10.66 360.@11.06 Il@12.34 taille,@12.62 il@13.40 fait@13.58 les@13.68 contours,@13.86 et@14.22 il@14.58 rase,@14.88 quelle@15.32 que@15.66 soit@15.88 ma@16.00 longueur_!@16.16 Et@17.22 il@17.40 a@17.54 une@17.60 application@17.76 gratuite@18.24 pour@18.68 choisir@19.06 mon@19.50 style.@19.66 Il@20.52 décide@20.86 de@21.16 ma@21.36 coupe,@21.48 maintenant_!@21.62 Le@22.86 pire,@23.18 c'est@23.86 son@24.06 prix_:@24.30 29,99_€@24.64 avec@26.52 les@27.04 coupons@27.30 de@27.54 la@27.70 fiche,@27.78 au@28.10 lieu@28.36 de@28.46 50,99_€.@28.78 Le@31.52 lien@31.90 est@32.18 juste@32.40 en@32.60 dessous,@32.76 sur@33.60 le@33.64 panier@33.84 orange…@34.06 Surtout,@35.24 n'appuie@36.00 pas@36.42 dessus_!@36.62",
}
CUTS = {
 'xn_1': ('docu', [(0, 2.72)]), 'xn_2': ('docu', [(3.45, 9.45)]), 'xn_3': ('docu', [(10.6, 13.6)]), 'xn_4': ('docu', [(14.1, 15.95)]),
 'xn_5': ('docu', [(16.45, 18.3)]), 'xn_6': ('docu', [(18.8, 24.15)]), 'xn_7': ('docu', [(24.45, 27.85)]), 'xn_8': ('docu', [(28.15, 29.65)]),
 'xn_9': ('docu', [(29.95, 32.8)]), 'xn_10': ('docu', [(33.4, 40.5)]), 'xn_11': ('docu', [(41.45, 44.2)]),
 'xq_1': ('poils', [(0, 2.2)]), 'xq_2': ('poils', [(2.8, 4.7)]), 'xq_3': ('poils', [(5.3, 6.72)]), 'xq_4': ('poils', [(6.72, 8.24)]),
 'xb_1': ('barbe', [(0, 3.35)]), 'xb_2': ('barbe', [(3.65, 7.55)]), 'xb_3': ('barbe', [(7.6, 11.9)]), 'xb_4': ('barbe', [(12.3, 16.65)]),
 'xb_5': ('barbe', [(16.9, 20.0)]), 'xb_6': ('barbe', [(20.5, 22.1)]), 'xb_7': ('barbe', [(22.75, 30.25)]), 'xb_8': ('barbe', [(31.1, 34.75)]),
 'xb_9': ('barbe', [(34.85, 37.12)]),
}
PITCH = {'poils': (1.45, 0.78)}
def words_for(c):
    src, segs = CUTS[c]; return sklib.map_words(parse(RAW[src]), segs, [])
if __name__ == '__main__':
    for c, (src, segs) in CUTS.items():
        if src in PITCH:
            sklib.cut_clip(src, segs, [], c + '_raw'); r, tp = PITCH[src]
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'clips/{c}_raw.wav', '-af', f'asetrate=24000*{r},aresample=24000,atempo={tp},highpass=f=150',
                            '-ar', '24000', '-ac', '1', f'clips/{c}.wav'], check=True)
        else:
            sklib.cut_clip(src, segs, [], c)
    for c in CUTS: print(c, round(float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'clips/{c}.wav'],capture_output=True,text=True).stdout),2), [w for w, _ in words_for(c)])
