# Production quotidienne Rayplav : mode d'emploi pour la session automatique

But : produire 1 vidéo TikTok Shop originale, drôle, courte et vendeuse, la livrer à Ryan, et apprendre de chaque essai. Ryan a donné son accord pour tester des idées nouvelles.

## 0. Préparer (5 min)
```
cd ~ && git clone https://github.com/ryanferreiracosta2007/agnes-relais.git 2>/dev/null || (cd agnes-relais && git pull -q)
bash ~/agnes-relais/studio/setup.sh        # atelier dans ~/atelier
cd ~/atelier
```
Lire : studio/REGLES.md, studio/PRODUITS.md, studio/RECHERCHE.md, studio/JOURNAL.md. La date du jour (`date`) compte : voir les règles de prix après le 30/11 dans PRODUITS.md.

## 1. Rechercher (toujours, 3 à 5 recherches web)
Se poser soi-même 3 questions avant d'écrire, et y répondre avec la recherche :
- Pourquoi quelqu'un s'arrêterait de scroller dans la première seconde ?
- Quel vrai problème ou quelle vraie envie du spectateur ce produit règle-t-il ?
- Pourquoi on partagerait ou commenterait cette vidéo ?
Chercher : une tendance d'accroche ou de format qui marche en ce moment (France de préférence), une technique d'animation ou de montage pour la rétention, un angle sur le produit. Ajouter 3 à 5 lignes datées dans studio/RECHERCHE.md (ce qu'on a appris + la source).

## 2. Choisir
- Produit : alterner (ne pas faire le même produit que la vidéo précédente du JOURNAL).
- Concept : nouveau, absent du JOURNAL. Oser : parodie, défi, question au spectateur, faux tuto raté, « avant/après », « réponse à un commentaire » fictif assumé, ASMR, mini-série avec un personnage récurrent… Écrire en une phrase l'hypothèse testée (ex. « une question directe au spectateur en accroche augmente la rétention à 3 s »).

## 3. Écrire (15 à 25 s, appliquer les décisions de RECHERCHE.md)
- 0 à 1 s : image RÉELLE du produit + personnage ou effet dessiné par-dessus + phrase parlée courte en « tu » + titre écrit (bandeau sklib.banner).
- Changement visuel au moins toutes les 2 s. Le produit utilisé à l'écran. Prix + appel à l'action ensemble à la fin.
- Phrases complètes. Appel à l'action : « Le lien est juste en dessous, sur le panier orange. »

## 4. Voix (relais Gemini, quota environ 10 répliques par jour et par modèle : 3 répliques maximum par session)
- Écrire `~/agnes-relais/voix_attente/<nom>.json` (même format que voix_attente/traitees/*.json : voices {}, models [...], lines [{id, sp, voice, text avec « <long pause> » entre phrases, style}]), commit + push sur main.
- Attendre `voix/<nom>/STATUT.txt` = « TERMINE » (git pull toutes les 30 s, 5 min max), copier les .wav dans ~/atelier/voix/.
- Voix : Puck = David (présentateur), Achird = David sceptique, Leda = Inès, Fenrir = Hamza (accent du sud), Aoede = Sarah, Zephyr = Léa, Charon = narrateur grave, Algenib = voix rocailleuse.
- Transcrire avec faster-whisper (medium, int8, language='fr', word_timestamps) : chaque phrase doit être juste, surtout « en dessous » et « panier orange ». Si faux : régénérer seulement la réplique fautive.

## 5. Monter (s'inspirer des fichiers existants)
- Modèles : mini2.py (mini personnages dans les vraies images), rf_videos.py (Gérard la barbe, faux documentaire), pb_videos.py (problèmes réels, POV chrono, incrustation pip(), écran partagé), dm_data.py / pb_data.py (découpe des voix).
- Outils : sklib.Timeline (ordre des répliques, sous-titres), sklib.banner, sklib.cta, sklib.cut_clip / map_words, scenes.footage(ctx, seg, t, zoom0, zoom1, dur, cx, cy, offset) pour les vraies images, chars.draw_char (personnages, yeux : open/wide/closed/happy/heart/wink/half/tiny ; bras : down/hip/point_side/point_down/face/cheer/run/grab/drink/wave/phone/chin/lips…), props, fx (spring, sweat, vein, shock_lines, dust, sniff_marks), rasoir_videos (oneblade, beard, fiche_band, coupon_note, phone_ar), audio.sfx (whoosh, pop, ding, boing, stamp, buzz, pschht, sniff, coins, bells, heart, sparkle, scratch, swipe, drumroll, wah…).
- Ajouter la vidéo dans make_mini2.py (dict VIDS) ; `python3 make_mini2.py <clé> stills` puis regarder frames/new_<clé>.jpg avec l'outil de lecture d'image et corriger (visages coupés, textes hors zone, personnages trop petits, chevauchements avec les sous-titres) ; puis `python3 make_mini2.py <clé> render` → final/<nom>.mp4.
- Contrôles finaux : volume intégré vers -14 LUFS (ffmpeg ebur128), transcription complète du fichier final, planche d'images (ffmpeg fps=1/2, tile) relue.

## 6. Livrer
- Envoyer la vidéo à Ryan avec SendUserFile + la description prête à coller (avec #pub, sans promesse interdite), le créneau conseillé pour poster (au moins 3 h après la dernière publication, jamais deux fois le même produit d'affilée) et, si besoin, « vérifie le prix avant de poster ».
- Dire en une ligne l'hypothèse testée et ce qu'il faudra regarder dans TikTok Studio (rétention à 3 s, vues complètes, clics panier).
- Ajouter une ligne dans studio/JOURNAL.md, sauvegarder le nouveau code dans studio/code/ (pas les vidéos), commit + push.

## 7. Ne jamais
- Publier sur TikTok, saisir un mot de passe ou une clé, inventer un prix ou un argument, refaire un concept du JOURNAL.
