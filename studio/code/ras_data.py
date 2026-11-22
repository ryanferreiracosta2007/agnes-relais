# -*- coding: utf-8 -*-
import sklib
RAW = {
'ras_s': "Franchement,@0.00 je@1.40 sais@1.45 même@1.58 pas@1.80 quelle@1.96 barbe@2.08 me@2.38 va.@2.46 Une@3.90 application@4.02 ?@4.52 Pour@5.06 un@5.22 rasoir@5.44 ?@5.78 Ah@6.94 non@7.22 !@7.44 Pas@7.94 la@8.06 moustache@8.22 !@8.64 Wow…@9.62 J'ai@11.12 rajeuni@11.42 de@11.78 10@11.92 ans@12.08 !@12.28",
'ras_m': "Prends@0.00 mon@0.48 rasoir,@0.56 il@1.48 a@1.60 une@1.70 application@1.82 gratuite.@2.28 Tu@4.38 essaies@4.50 les@4.64 styles@4.82 de@4.96 barbe@5.18 en@5.36 réalité@5.60 augmentée,@5.94 avant@6.84 de@6.96 raser.@7.14 Et@8.18 après,@8.32 il@8.64 taille,@8.86 il@9.38 fait@9.48 les@9.56 contours@9.74 et@10.02 il@10.32 rase,@10.52 quelle@10.92 que@11.22 soit@11.38 la@11.44 longueur.@11.58 C'est@12.60 le@12.76 Philips@13.00 OneBlade@13.30 360.@13.86 Il@15.14 est@15.28 affiché@15.48 à@15.80 50,99_€@16.02 et@17.6 à@17.82 29,99_€@18.16 avec@19.32 les@19.60 coupons@19.76 de@19.92 la@20.04 fiche.@20.12 Le@20.88 Black@21.04 Friday@21.22 dure@21.42 jusqu'au@21.70 30@21.98 novembre.@22.16 Le@23.08 lien@23.22 est@23.36 juste@23.54 en@23.72 dessous,@23.88 sur@24.42 le@24.50 panier@24.62 orange.@24.78",
'ras_p': "Ce@0.00 rasoir@0.48 Philips@0.84 taille,@1.38 fait@2.18 les@2.26 contours@2.50 et@2.90 rase,@3.22 quelle@4.02 que@4.14 soit@4.30 la@4.40 longueur@4.56 de@4.78 tes@4.92 poils.@5.02 Sa@6.00 lame@6.10 360@6.26 suit@6.96 les@7.28 courbes@7.46 du@7.64 visage,@7.82 et@8.20 il@8.38 s'utilise@8.52 sur@8.84 le@9.00 visage@9.12 comme@9.42 sur@9.64 le@9.84 corps.@9.98 Il@10.94 est@11.04 étanche,@11.14 tu@11.74 peux@11.86 l'utiliser@12.00 à@12.48 sec@12.76 ou@12.92 avec@13.20 de@13.32 la@13.48 mousse,@13.58 et@14.32 l'application@14.44 gratuite@15.02 te@15.48 fait@15.68 essayer@15.86 des@16.08 styles@16.40 de@16.56 barbe.@16.84 Il@17.68 est@17.84 affiché@18.02 à@18.42 50,99_€@18.74 et@20.04 jusqu'à@20.60 29,99_€@21.20 avec@22.60 les@22.82 coupons@23.04 de@23.20 la@23.32 fiche.@23.44 Un@24.16 rasoir@24.26 Philips@24.54 à@24.86 moins@25.02 de@25.16 30_€@25.28 ?@26.10 Attends,@26.28 regarde@27.14 la@27.20 fiche.@27.30 Avec@28.00 les@28.22 coupons,@28.38 tu@28.72 le@28.80 paies@28.92 29,99_€@29.30 au@30.46 lieu@30.76 de@30.86 50,99_€.@31.10",
}
def parse(s):
    out = []
    for tok in s.split(' '):
        w, t = tok.rsplit('@', 1)
        if w in ('?', '!', '…') and out: out[-1] = (out[-1][0] + ' ' + w, out[-1][1]); continue
        out.append((w.replace('_', ' ').upper(), float(t)))
    return out
CUTS = {
 'xr_s1': ('ras_s', [(0, 2.57)], []),
 'xr_s2': ('ras_s', [(3.84, 4.52), (5.06, 5.82)], [0.1]),
 'xr_s3': ('ras_s', [(6.94, 8.69)], []),
 'xr_s4': ('ras_s', [(9.59, 10.64), (11.06, 12.22)], [0.1]),
 'xr_m1': ('ras_m', [(0, 2.83)], []),
 'xr_m2': ('ras_m', [(4.32, 7.29)], []),
 'xr_m3': ('ras_m', [(8.12, 11.80)], []),
 'xr_m4': ('ras_m', [(12.53, 14.52), (15.12, 20.27)], [0.15]),
 'xr_m5': ('ras_m', [(20.86, 22.45), (22.99, 25.40)], [0.12]),
 'xr_p1': ('ras_p', [(0, 5.17)], []),
 'xr_p2': ('ras_p', [(5.86, 10.07)], []),
 'xr_p3': ('ras_p', [(10.88, 17.07)], []),
 'xr_p4': ('ras_p', [(17.66, 23.58)], []),
 'xr_c1': ('ras_p', [(24.06, 25.48), (26.24, 27.49)], [0.15]),
 'xr_c2': ('ras_p', [(28.0, 32.48)], []),
}
def words_for(c):
    src, segs, gaps = CUTS[c]; return sklib.map_words(parse(RAW[src]), segs, gaps)
if __name__ == '__main__':
    for c, (src, segs, gaps) in CUTS.items(): sklib.cut_clip(src, segs, gaps, c)
    for c in CUTS: print(c, [w for w, _ in words_for(c)])
