# Relais Agnes

Génère des clips vidéo à partir d'images avec l'API gratuite Agnes AI, sur GitHub Actions (PC éteint).

- `images/` : les images de départ (jpg/png, 9:16 conseillé)
- `file_attente/<nom>.txt` : une demande = une ligne par plan, `image.jpg | mouvement`
- `clips/<nom>/` : les clips générés + `STATUT.txt`

Le relais tourne toutes les heures et à chaque nouvelle demande. Si la file gratuite d'Agnes est pleine, il réessaie à l'exécution suivante.
La clé API est dans le secret `AGNES_API_KEY` (Settings › Secrets and variables › Actions).
