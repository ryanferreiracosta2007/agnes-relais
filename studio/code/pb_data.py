# -*- coding: utf-8 -*-
"""Tondeuse, saison 3 : vrais problèmes du rasage. 1) « les 3 galères » (David) 2) POV rendez-vous dans 5 minutes (Hamza + Inès)."""
import sklib, subprocess
from ras_data import parse
RAW = {
 'galeres': "Toi@0.00 aussi,@0.46 tu@0.64 ressembles@0.76 à@1.04 ça@1.10 après@1.48 t'être@1.56 rasé_?@1.78 Problème@3.08 numéro@3.26 un_:@3.62 les@4.12 coupures.@4.36 Le@5.88 Philips@6.04 OneBlade@6.36 360@6.80 est@7.36 conçu@7.66 pour@7.88 couper@8.06 les@8.34 poils,@8.66 et@9.18 pas@9.44 la@9.66 peau.@9.82 Son@10.76 double@10.92 système@11.22 de@11.48 protection,@11.72 avec@12.26 un@12.34 revêtement@12.48 lisse@12.80 et@13.04 des@13.16 bords@13.30 arrondis,@13.42 aide@14.24 la@14.34 lame@14.54 à@14.70 glisser@14.82 en@15.16 douceur,@15.44 même@16.16 à@16.32 contre-sens.@16.46 Problème@17.98 numéro@18.28 deux_:@18.66 les@19.26 contours@19.58 ratés.@19.92 Sa@21.16 lame@21.32 double@21.52 sens@21.82 te@21.98 permet@22.12 de@22.30 tracer@22.50 des@22.70 lignes@22.92 nettes,@23.16 dans@23.64 n'importe@23.86 quelle@24.20 direction.@24.30 Problème@25.88 numéro@26.10 trois_:@26.50 la@26.98 peau@27.18 qui@27.30 chauffe.@27.56 Il@27.96 ne@28.52 rase@28.68 pas@28.90 d'aussi@28.98 près@29.24 qu'une@29.32 lame@29.50 classique,@29.62 et@30.18 ça@30.44 préserve@30.62 ta@30.86 peau.@31.00 Il@32.04 est@32.10 à@32.20 50,99_€@32.32 et@33.34 à@33.84 29,99_€@34.04 avec@35.16 les@35.36 coupons@35.50 de@35.68 la@35.80 fiche.@35.84 Fini@37.02 le@37.16 papier@37.30 toilette@37.48 sur@37.80 le@37.96 visage_!@38.08",
 'date_h': "Cinq@0.00 minutes_?!@0.64 Mais@1.78 je@1.86 ne@1.98 suis@2.14 même@2.20 pas@2.30 rasé_!@2.52 Avant,@4.80 dès@5.26 que@5.38 je@5.44 me@5.54 rasais@5.68 trop@5.84 vite,@6.06 je@6.30 me@6.40 coupais.@6.56 Mais@7.48 le@7.60 Philips@7.84 OneBlade@8.12 360@8.62 est@9.24 conçu@9.56 pour@9.88 couper@10.04 les@10.24 poils,@10.40 et@10.62 pas@10.74 la@10.86 peau.@10.98 Alors@11.68 j'y@11.86 vais,@12.04 sans@12.36 stress.@12.42 Je@13.50 taille,@13.66 je@15.12 fais@15.32 mes@15.46 contours@15.60 avec@15.86 la@16.04 lame@16.16 double@16.28 sens,@16.54 et@17.80 je@17.94 rase,@18.12 même@18.48 à@18.60 contre-sens.@18.76 Et@20.62 voilà,@20.78 je@21.32 suis@21.40 prêt_!@21.52 Il@22.90 est@23.04 à@23.18 29,99_€@23.36 avec@24.42 les@24.78 coupons@24.96 de@25.16 la@25.28 fiche,@25.40 au@25.76 lieu@25.84 de@25.94 50,99_€.@26.12 Le@27.62 lien@28.06 est@28.32 juste@28.62 en@28.88 dessous,@29.06 sur@29.40 le@29.46 panier@29.56 orange.@29.74",
 'galeres_cta': "Le@0.00 lien@0.38 est@0.58 juste@0.98 en@1.24 dessous,@1.42 sur@1.84 le@1.86 panier@2.04 orange.@2.24",
 'date_i': "J'arrive@0.00 dans@0.58 cinq@0.76 minutes_!@0.90 C'est@3.24 moi,@3.36 je@3.54 suis@3.66 en@3.68 bas_!@3.80 Oh…@5.86 t'es@6.90 tout@7.20 beau,@7.42 toi_!@7.60",
}
CUTS = {
 'xg_1': ('galeres', [(0, 2.05)]), 'xg_2': ('galeres', [(2.7, 4.88)]), 'xg_3': ('galeres', [(5.6, 9.98)]), 'xg_4': ('galeres', [(10.55, 16.95)]),
 'xg_5': ('galeres', [(17.75, 20.32)]), 'xg_6': ('galeres', [(21.05, 24.67)]), 'xg_7': ('galeres', [(25.7, 27.87)]), 'xg_8': ('galeres', [(27.9, 31.12)]),
 'xg_9': ('galeres', [(31.9, 36.08)]), 'xg_10': ('galeres', [(36.65, 38.42)]),
 'xh_d1': ('date_h', [(0, 3.08)]), 'xh_d2': ('date_h', [(4.05, 7.15)]), 'xh_d3': ('date_h', [(7.3, 12.78)]), 'xh_d4': ('date_h', [(13.45, 14.08)]),
 'xh_d5': ('date_h', [(15.1, 16.87)]), 'xh_d6': ('date_h', [(17.8, 19.27)]), 'xh_d7': ('date_h', [(20.55, 21.82)]), 'xh_d8': ('date_h', [(22.35, 27.32)]),
 'xh_d9': ('date_h', [(27.55, 30.32)]),
 'xg_11': ('galeres_cta', [(0, 2.84)]),
 'xi_d1': ('date_i', [(0, 1.25)]), 'xi_d2': ('date_i', [(3.05, 3.92)]), 'xi_d3': ('date_i', [(5.7, 8.25)]),
}
def words_for(c):
    src, segs = CUTS[c]; return sklib.map_words(parse(RAW[src]), segs, [])
if __name__ == '__main__':
    for c, (src, segs) in CUTS.items(): sklib.cut_clip(src, segs, [], c)
    for c in CUTS: print(c, round(float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'clips/{c}.wav'],capture_output=True,text=True).stdout),2), ' '.join(w for w, _ in words_for(c)))
