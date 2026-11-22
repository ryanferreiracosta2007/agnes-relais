# -*- coding: utf-8 -*-
import sklib
from ras_data import parse
RAW = {
'noel_ines': "Joyeux@0.30 Noël,@0.76 mon@1.16 cœur !@1.22 Ouvre@1.88 vite@2.08 ton@2.22 cadeau.@2.36 Non…@4.38 je@5.46 veux@5.54 dire@5.66 qu'elle@5.78 ressemble@6.00 à@6.28 un@6.40 buisson.@6.54 C'est@7.82 le@7.94 Philips@8.18 OneBlade@8.54 360.@9.08 Il@10.08 taille,@10.28 il@10.92 fait@11.06 les@11.16 contours@11.38 et@11.68 il@11.92 rase.@12.10 Et@12.90 regarde,@13.08 l'application@13.72 gratuite@14.24 te@14.54 fait@14.72 essayer@14.80 les@15.08 styles@15.28 de@15.42 barbe.@15.62 Et@16.74 avec@16.90 les@17.04 coupons@17.22 de@17.42 la@17.56 fiche,@17.68 il@18.00 est@18.04 à@18.16 29,99_€.@18.34 Le@20.50 Black@20.66 Friday@20.84 dure@21.08 jusqu'au@21.26 30@21.52 novembre.@21.70 Le@22.50 lien@22.62 est@22.78 juste@23.00 en@23.18 dessous,@23.34 sur@23.76 le@23.82 panier@23.96 orange.@24.16",
'noel_sarah': "Les@0.00 cadeaux@0.56 de@0.92 Noël@1.04 pour@1.28 ton@1.50 copain :@1.64 un@2.54 seul@2.62 que@2.74 je@2.86 garde.@3.04 Numéro@4.28 3 :@4.42 les@5.14 chaussettes@5.30 de@5.56 Noël.@5.74 Il@6.42 les@6.50 met@6.68 une@6.78 fois,@7.16 et@7.42 c'est@7.64 fini.@7.84 Numéro@8.70 2 :@8.98 le@9.52 pull@9.72 moche.@9.84 Il@10.46 va@10.58 le@10.70 cacher@10.86 au@11.14 fond@11.44 du@11.52 placard.@11.70 Et@12.82 numéro@13.02 1 :@13.36 le@13.96 Philips@14.28 OneBlade@14.58 360.@15.08 Il@16.32 taille,@16.52 il@17.14 fait@17.28 les@17.38 contours@17.60 et@17.92 il@18.18 rase,@18.38 et@19.24 il@19.40 a@19.52 une@19.56 application@19.72 pour@20.18 essayer@20.40 les@20.68 styles@20.86 de@21.00 barbe.@21.22 Il@21.78 est@21.90 affiché@22.10 à@22.46 50,99_€@22.72 et@23.80 à@24.16 29,99_€@24.46 avec@25.68 les@25.94 coupons@26.14 de@26.32 la@26.44 fiche.@26.52 Le@27.10 Black@27.44 Friday@27.70 dure@27.98 jusqu'au@28.20 30@28.56 novembre.@28.80 Le@29.76 lien@29.84 est@30.02 juste@30.34 en@30.54 dessous,@30.66 sur@30.82 le@30.94 panier@31.08 orange.@31.28",
}
RAW['noel_sarah'] = RAW['noel_sarah'].replace('copain :', 'copain_:').replace('3 :', '3_:').replace('2 :', '2_:').replace('1 :', '1_:')
RAW['noel_ines'] = RAW['noel_ines'].replace('cœur !', 'cœur_!')
CUTS = {
 'xn_i1': ('noel_ines', [(0, 2.64)], []),
 'xn_i2': ('noel_ines', [(3.67, 6.94)], []),
 'xn_i3': ('noel_ines', [(7.74, 12.30)], []),
 'xn_i4': ('noel_ines', [(12.89, 15.82)], []),
 'xn_i5': ('noel_ines', [(16.74, 19.61)], []),
 'xn_i6': ('noel_ines', [(20.39, 24.72)], []),
 'xn_h1': ('noel_hamza', [(0, 1.08), (1.77, 3.20)], [0.12]),
 'xn_h2': ('noel_hamza', [(4.03, 4.52), (5.10, 6.23), (6.65, 7.80)], [0.25, 0.1]),
 'xn_h3': ('noel_hamza', [(8.82, 9.50), (10.12, 11.28)], [0.15]),
 'xn_s1': ('noel_sarah', [(0, 3.27)], []),
 'xn_s3': ('noel_sarah', [(3.99, 7.99)], []),
 'xn_s2': ('noel_sarah', [(8.57, 12.03)], []),
 'xn_s0': ('noel_sarah', [(12.76, 15.88)], []),
 'xn_s4': ('noel_sarah', [(16.34, 21.62)], []),
 'xn_s5': ('noel_sarah', [(21.70, 26.78)], []),
 'xn_s6': ('noel_sarah', [(27.22, 31.84)], []),
}
MANUAL = {
 'xn_h1': [('UN', 0.0), ('RASOIR ?', 0.4), ('TU', 1.2), ('VEUX', 1.4), ('DIRE', 1.55), ('QUE', 1.7), ('MA', 1.85), ('BARBE', 2.0), ('EST', 2.3), ('MOCHE ?', 2.45)],
 'xn_h2': [('BON…', 0.0), ("D'ACCORD.", 0.74), ('IL', 1.97), ('FAIT', 2.15), ('QUOI,', 2.3), ('CE', 2.55), ('RASOIR ?', 2.7)],
 'xn_h3': [('FRANCHEMENT…', 0.0), ('JE', 0.83), ('SUIS', 0.98), ('BEAU', 1.15), ('GOSSE,', 1.35), ('NON ?', 1.7)],
}
def words_for(c):
    if c in MANUAL: return MANUAL[c]
    src, segs, gaps = CUTS[c]; w = sklib.map_words(parse(RAW[src]), segs, gaps)
    if c == 'xn_s6': w = [('LE', 0.0)] + w
    return w
if __name__ == '__main__':
    for c, (src, segs, gaps) in CUTS.items(): sklib.cut_clip(src, segs, gaps, c)
    for c in CUTS: print(c, [w for w, _ in words_for(c)][:14])
