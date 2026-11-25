# -*- coding: utf-8 -*-
"""Découpe des voix « Soft launch » : Léa (Zephyr) et Inès (Leda), parfum Lattafa.
   Le début chuchoté « Petit soft launch » de Léa est mal articulé (transcrit « Tissots flanches ») : coupé, le mot reste à l'écran."""
import sklib, subprocess
RAW = {
 'sl_lea': "Je@1.45 te@1.62 présente@1.80 quelqu'un.@2.30 Il@3.72 est@3.88 tout@4.24 doré…@4.54 et@5.16 un@5.66 peu@5.84 mystérieux.@6.02 Je@7.42 te@7.48 présente@7.70 le@8.20 Confidential@8.76 Private@9.50 Gold@9.86 de@10.12 Lattafa.@10.44 Et@11.72 en@11.80 plus,@11.98 il@12.60 coûte@12.68 moins@13.02 de@13.34 vingt-cinq@13.60 euros.@13.86 Le@14.84 lien@15.02 est@15.34 juste@15.72 en@15.94 dessous,@16.10 sur@16.92 le@16.98 panier@17.14 orange.@17.36",
 'sl_ines': "Attends,@0.00 c'est@0.44 qui_?@0.54 Montre-moi@1.06 son@1.36 visage_!@1.48 Quoi_?@2.85 C'est@3.56 un@3.72 parfum_?!@3.86 Et@5.30 toi,@5.42 tu@5.62 ferais@5.66 le@5.76 soft@5.88 launch@6.06 de@6.24 quoi_?@6.42 Dis-le@6.84 en@7.04 commentaire.@7.12",
}
CUTS = {
 'xl_l1': ('sl_lea', [(1.36, 2.98)], []),
 'xl_i1': ('sl_ines', [(0.0, 2.32)], []),
 'xl_l2': ('sl_lea', [(3.64, 7.08)], []),
 'xl_l3': ('sl_lea', [(7.36, 11.1)], []),
 'xl_i2': ('sl_ines', [(2.74, 5.2)], []),
 'xl_l4': ('sl_lea', [(11.64, 14.32)], []),
 'xl_i3': ('sl_ines', [(5.24, 7.73)], []),
 'xl_l5': ('sl_lea', [(14.76, 17.9)], []),
}
PITCH = {'sl_lea': 1.05, 'sl_ines': 1.05}; SPEED = 1.15
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
