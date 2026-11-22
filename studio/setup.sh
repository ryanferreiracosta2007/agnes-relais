#!/usr/bin/env bash
# Prépare l'atelier vidéo Rayplav dans une session neuve.
# Usage : bash studio/setup.sh   (depuis la racine du dépôt agnes-relais)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
W="${ATELIER:-$HOME/atelier}"
mkdir -p "$W" ~/.fonts
cp "$HERE"/fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null 2>&1 || true
python3 -c "import cairo, numpy, PIL" 2>/dev/null || pip install --break-system-packages -q pycairo numpy pillow
python3 -c "import faster_whisper" 2>/dev/null || pip install --break-system-packages -q faster-whisper
cp -r "$HERE"/code/. "$W"/
mkdir -p "$W"/seg "$W"/clips "$W"/voix "$W"/voix "$W"/frames "$W"/final "$W"/out
cp "$HERE"/clips/*.wav "$W"/clips/ 2>/dev/null || true
cp "$W"/fiche_kit.png "$W"/fiche_prix_band.png "$W"/seg/ 2>/dev/null || true
for f in "$HERE"/seg_mp4/*.mp4; do
  n=$(basename "$f" .mp4)
  if [ ! -d "$W/seg/$n" ]; then
    mkdir -p "$W/seg/$n"
    ffmpeg -v error -i "$f" -q:v 2 "$W/seg/$n/%04d.jpg"
  fi
done
echo "Atelier prêt dans $W"
