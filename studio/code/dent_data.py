# -*- coding: utf-8 -*-
import json, sklib
RAW = {
'dent_david': "Salut@0.00 toi…@0.56 tu@1.66 fais@1.70 quoi@1.84 ce@2.02 soir@2.18 ?@2.42 Sérieux@3.10 ?@3.64 C'est@3.96 si@4.14 grave@4.30 que@4.44 ça@4.62 ?@4.88 Et@5.44 maintenant,@5.60 ça@6.66 va@6.74 mieux@6.84 ?@7.00 Moins@7.90 de@8.14 5@8.32 euros.@8.48 Le@9.36 lien@9.44 est@9.56 juste@9.70 en@9.84 dessous,@9.98 sur@10.48 le@10.54 panier@10.68 orange.@10.86",
'dent_ines': "Oh@0.00 là@0.54 là…@0.76 Recule@1.76 un@1.96 peu,@2.12 s'il@2.28 te@2.42 plaît.@2.58 Ton@3.24 haleine,@3.40 c'est@3.76 une@4.12 catastrophe !@4.44 Tiens,@5.82 prends@6.28 ça.@6.32 C'est@7.02 le@7.16 dentifrice@7.26 Miswak@7.70 de@8.24 chez@8.40 Dabur,@8.50 à@9.20 base@9.32 de@9.44 plantes.@9.78 Mmh…@11.72 là,@12.36 on@12.64 peut@12.82 parler !@12.98 Il@13.84 t'a@13.96 coûté@14.12 combien,@14.30 ton@14.56 dentifrice ?@14.74",
'dent_promo': "Ce@0.00 dentifrice@0.46 à@0.96 moins@1.12 de@1.22 5 €,@1.42 il@1.94 faut@1.98 absolument@2.18 que@2.68 je@2.74 t'en@2.80 parle.@2.98 C'est@4.36 le@4.48 Miswak@4.64 de@5.06 chez@5.26 Dabur,@5.38 un@6.10 dentifrice@6.28 à@6.80 base@6.94 de@7.04 plantes,@7.28 avec@7.66 de@7.80 l'extrait@7.94 de@8.22 miswak.@8.30 Sur@9.24 la@9.38 boîte,@9.52 ils@9.78 annoncent@9.94 des@10.14 dents@10.28 solides,@10.46 des@11.02 gencives@11.12 saines@11.46 et@11.70 une@12.02 haleine@12.16 fraîche.@12.76 Le@13.38 lien@13.48 est@13.62 juste@13.80 en@14.00 dessous,@14.16 sur@14.30 le@14.44 panier@14.56 orange.@14.72",
}
def parse(s):
    out = []
    for tok in s.split(' '):
        w, t = tok.rsplit('@', 1)
        if w in ('?', '!', '…') and out: out[-1] = (out[-1][0] + ' ' + w, out[-1][1]); continue
        out.append((w.replace('_', ' ').upper(), float(t)))
    return out
# (source, segments, silences entre segments)
CUTS = {
 'xd_d1': ('dent_david', [(0, 0.99), (1.55, 2.33)], [0.15]),
 'xd_d2': ('dent_david', [(2.94, 3.36), (3.88, 4.77)], [0.12]),
 'xd_d3': ('dent_david', [(5.42, 5.99), (6.60, 6.98)], [0.1]),
 'xd_d4': ('dent_david', [(7.77, 8.71)], []),
 'xd_d5': ('dent_david', [(9.25, 11.4)], []),
 'xd_i1': ('dent_ines', [(0, 5.08)], []),
 'xd_i2': ('dent_ines', [(5.63, 10.03)], []),
 'xd_i3': ('dent_ines', [(11.16, 13.23), (13.73, 15.56)], [0.15]),
 'xd_p1': ('dent_promo', [(0, 3.12)], []),
 'xd_p2': ('dent_promo', [(4.22, 8.59)], []),
 'xd_p3': ('dent_promo', [(9.18, 12.57)], []),
 'xd_p4': ('dent_promo', [(13.3, 15.28)], []),
}
def words_for(clip):
    src, segs, gaps = CUTS[clip]
    return sklib.map_words(parse(RAW[src].replace('5 €,', '5_€,').replace('catastrophe !', 'catastrophe_!').replace('parler !', 'parler_!').replace('dentifrice ?', 'dentifrice_?')), segs, gaps)
if __name__ == '__main__':
    for c, (src, segs, gaps) in CUTS.items(): sklib.cut_clip(src, segs, gaps, c)
    for c in CUTS: print(c, words_for(c))
