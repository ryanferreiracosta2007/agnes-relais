# -*- coding: utf-8 -*-
"""Découpe des voix « Red flag / green flag : la salle de bain de ton date » : mini Inès (Leda), mini Hamza (Fenrir), dentifrice Miswak."""
import sklib, subprocess
RAW = {
 'rf_ines': "Tu@0.00 fouilles@0.38 la@0.66 salle@0.84 de@1.06 bain@1.20 de@1.28 ton@1.46 date_?@1.56 Le@3.14 tube@3.36 de@3.56 dentifrice@3.78 écrasé@4.24 au@4.82 milieu...@4.98 Red@5.88 flag.@6.18 La@7.44 brosse@7.68 à@7.90 dents@8.02 toute@8.20 écrabouillée...@8.40 Red@9.54 flag_!@9.82 Attends...@11.20 un@12.18 dentifrice@12.28 aux@12.78 plantes,@13.08 avec@13.84 de@14.08 l'extrait@14.26 pur@14.70 d'Al-Arak_?@14.92 Green@16.70 flag.@17.14 Et@18.66 toi,@18.88 ton@19.48 red@19.52 flag,@19.82 c'est@20.96 quoi_?@21.08 Dis-le@21.60 en@21.82 commentaire.@22.00",
 'rf_hamza': "Attends_!@0.00 Regarde@3.18 plutôt@3.32 ça_!@3.60 Sur@4.54 la@4.72 boîte,@4.88 c'est@5.44 écrit_:@5.58 des@6.40 dents@6.68 fortes,@7.04 des@7.98 gencives@8.12 saines@8.86 et@9.26 une@9.74 haleine@9.94 fraîche.@10.32",
 'rf_hprix': "Et@0.00 en@0.24 plus,@0.50 il@1.14 coûte@1.30 moins@1.56 de@1.78 cinq@2.14 euros.@2.36 Le@3.56 lien@3.70 est@3.96 juste@4.34 en@4.58 dessous,@4.76 sur@5.28 le@5.34 panier@5.52 orange.@5.72",
}
CUTS = {
 'fi_1': ('rf_ines', [(0.0, 2.0)], []),
 'fi_2': ('rf_ines', [(3.05, 5.35), (5.80, 6.55)], [0.12]),
 'fi_3': ('rf_ines', [(7.38, 9.20), (9.48, 10.20)], [0.08]),
 'fh_1': ('rf_hamza', [(0.0, 0.60), (2.80, 3.98)], [0.10]),
 'fi_4': ('rf_ines', [(12.05, 16.40)], []),
 'fi_5': ('rf_ines', [(16.60, 17.65)], []),
 'fh_2': ('rf_hamza', [(4.48, 5.80), (6.30, 10.90)], [0.10]),
 'fi_6': ('rf_ines', [(18.55, 19.98), (20.85, 22.42)], [0.06]),
 'fh_3': ('rf_hprix', [(1.0, 2.95), (3.40, 6.12)], [0.15]),
}
PITCH = {'rf_ines': 1.05, 'rf_hamza': 1.06, 'rf_hprix': 1.06}; SPEED = {'rf_ines': 1.22, 'rf_hamza': 1.25, 'rf_hprix': 1.2}
SPEED_C = {'fi_1': 1.12}  # accroche : un peu moins accélérée pour rester claire
def sp(c): return SPEED_C.get(c, SPEED[CUTS[c][0]])
def parse(s):
    return [(w.replace('_', ' ').upper(), float(t)) for w, t in (tok.rsplit('@', 1) for tok in s.split(' '))]
def words_for(c):
    src, segs, gaps = CUTS[c]
    return [(w, t / sp(c)) for w, t in sklib.map_words(parse(RAW[src]), segs, gaps)]
if __name__ == '__main__':
    for c, (src, segs, gaps) in CUTS.items():
        sklib.cut_clip(src, segs, gaps, c + '_raw'); r = PITCH[src]
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'clips/{c}_raw.wav', '-af',
                        f'asetrate=24000*{r},aresample=24000,atempo={sp(c) / r:.4f},highpass=f=110',
                        '-ar', '24000', '-ac', '1', f'clips/{c}.wav'], check=True)
    import scenes
    tot = 0
    for c in CUTS:
        L = scenes.clip_len(c); tot += L; print(c, round(L, 2), [w for w, _ in words_for(c)])
    print('total voix', round(tot, 2))
