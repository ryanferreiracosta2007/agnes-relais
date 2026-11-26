# -*- coding: utf-8 -*-
"""Découpe des voix « ASMR dentifrice raté » : mini Léa (Zephyr, chuchote) et mini Hamza (Fenrir, crie), dentifrice Miswak.
   Le mot « dentifrice » chuchoté par Léa (mal compris à la transcription) est coupé : il est écrit à l'écran."""
import sklib, subprocess
RAW = {
 'ar_lea': "Chut_!@0.00 Mets@1.20 le@1.40 son,@1.66 je@2.38 te@2.56 fais@2.90 un@3.12 ASMR.@3.48 Écoute@6.26 le@6.64 petit@6.86 bouchon...@7.10 Et@9.04 maintenant...@9.24 la@10.14 pâte.@10.36 Hamza...@15.80 on@16.66 chuchote.@16.98 Et@18.82 toi,@19.02 l'ASMR,@19.58 ça@20.36 te@20.48 détend@20.66 ou@21.06 ça@21.26 t'énerve_?@21.50 Dis-le@22.56 en@22.86 commentaire.@23.12",
 'ar_hamza': "OH_!@0.00 C'est@0.98 le@1.20 Miswak_?!@1.40 Pardon...@2.44 Il@3.36 est@3.50 aux@3.54 plantes,@3.78 avec@4.78 de@4.88 l'extrait@5.02 pur@5.48 d'Al-Arak.@5.78 Sur@7.36 la@7.52 boîte,@7.64 c'est@8.12 écrit_:@8.30 des@8.56 dents@9.12 fortes,@9.46 des@10.42 gencives@10.62 saines@11.14 et@11.56 une@12.04 haleine@12.22 fraîche_!@12.56 Il@14.40 coûte@14.58 moins@14.88 de@15.02 cinq@15.20 euros_!@15.32 Le@16.04 lien@16.16 est@16.36 juste@16.62 en@16.84 dessous,@17.00 sur@17.60 le@17.66 panier@17.80 orange.@18.00",
}
CUTS = {
 'arl_1': ('ar_lea', [(0.0, 0.65), (1.05, 1.80), (1.98, 3.94)], [0.0, 0.0]),
 'arl_2': ('ar_lea', [(6.10, 7.42)], []),
 'arl_3': ('ar_lea', [(8.98, 10.78)], []),
 'arh_1': ('ar_hamza', [(0.0, 0.62), (0.88, 1.98)], [0.04]),
 'arl_4': ('ar_lea', [(15.65, 17.62)], []),
 'arh_2': ('ar_hamza', [(2.40, 4.15), (4.48, 6.45)], [0.0]),
 'arh_3': ('ar_hamza', [(7.25, 13.10)], []),
 'arl_5': ('ar_lea', [(18.70, 21.90), (22.42, 23.62)], [0.0]),
 'arh_4': ('ar_hamza', [(14.30, 18.40)], []),
}
PITCH = {'ar_lea': 1.05, 'ar_hamza': 1.06}; SPEED = {'ar_lea': 1.15, 'ar_hamza': 1.25}
SPEED_C = {'arl_1': 1.04, 'arh_1': 1.08}  # accroche et « Miswak » : moins accélérés pour rester clairs
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
