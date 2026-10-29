# -*- coding: utf-8 -*-
"""
Relais voix Gemini (GitHub Actions) : génère les répliques d'un épisode avec les voix Gemini TTS.

- Demande : voix_attente/<nom>.json
    {"voices": {"H": "Fenrir", "C": "Leda"},
     "lines": [{"id": "line00", "sp": "H", "text": "Claude ! ...", "style": "très excité, rapide"}]}
- Résultat : voix/<nom>/<id>.wav (24 kHz mono) + STATUT.txt ; la demande passe dans voix_attente/traitees/
- La clé vient du secret GitHub GEMINI_API_KEY (jamais écrite dans le dépôt ni dans les logs).
"""
import base64, json, os, shutil, struct, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
REQ, OUT = os.path.join(ROOT, "voix_attente"), os.path.join(ROOT, "voix")
DONE = os.path.join(REQ, "traitees")
KEY = os.environ.get("GEMINI_API_KEY", "").strip()
BASE = "https://generativelanguage.googleapis.com/v1beta"
MODELS = [m for m in os.environ.get("GEMINI_TTS_MODELS", "gemini-3.8-flash-tts,gemini-3.1-flash-tts-preview,gemini-2.5-flash-preview-tts").split(",") if m]


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode())


def find_audio(obj):
    """cherche la plus longue chaîne base64 (l'audio) dans la réponse, avec son type mime éventuel"""
    best = [None, None]
    def walk(o, mime=None):
        if isinstance(o, dict):
            m = o.get("mime_type") or o.get("mimeType") or mime
            for v in o.values():
                walk(v, m)
        elif isinstance(o, list):
            for v in o:
                walk(v, mime)
        elif isinstance(o, str) and len(o) > 2000 and (best[0] is None or len(o) > len(best[0])):
            best[0], best[1] = o, mime
    walk(obj)
    return best


def to_wav(raw, mime):
    if raw[:4] == b"RIFF":
        return raw
    rate = 24000
    if mime and "rate=" in mime:
        try: rate = int(mime.split("rate=")[1].split(";")[0])
        except ValueError: pass
    hdr = b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16) \
        + b"data" + struct.pack("<I", len(raw))
    return hdr + raw


def tts(model, text, style, voice):
    if model.startswith("gemini-2.5"):
        prompt = f"Dis en français, sur ce ton : {style}. Texte : {text}" if style else text
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
        r = post(f"{BASE}/models/{model}:generateContent", body)
    else:
        content = {"type": "text", "text": text}
        if style:
            content["annotations"] = [{"type": "speech_metadata", "style": style}]
        body = {"model": model, "input": [{"type": "user_input", "content": [content]}],
                "response_format": {"type": "audio"},
                "generation_config": {"speech_config": [{"voice": voice}]}}
        r = post(f"{BASE}/interactions", body)
    b64, mime = find_audio(r)
    if not b64:
        raise RuntimeError("pas d'audio dans la réponse : " + json.dumps(r)[:300])
    return to_wav(base64.b64decode(b64), mime)


def main():
    if not KEY:
        sys.exit("Secret GEMINI_API_KEY manquant.")
    os.makedirs(DONE, exist_ok=True)
    reqs = sorted(f for f in os.listdir(REQ) if f.endswith(".json"))
    if not reqs:
        log("Aucune demande."); return
    model_ok = None
    for rf in reqs:
        name = os.path.splitext(rf)[0]; folder = os.path.join(OUT, name); os.makedirs(folder, exist_ok=True)
        spec = json.load(open(os.path.join(REQ, rf), encoding="utf-8-sig"))
        voices = spec.get("voices", {}); lines = spec["lines"]; done = 0; errors = []
        log(f"=== {rf} : {len(lines)} réplique(s) ===")
        for ln in lines:
            dest = os.path.join(folder, ln["id"] + ".wav")
            if os.path.exists(dest) and os.path.getsize(dest) > 2000:
                done += 1; continue
            voice = ln.get("voice") or voices.get(ln.get("sp"), "Puck")
            for attempt in range(6):
                models = [model_ok] if model_ok else MODELS
                err = None
                for m in models:
                    try:
                        wav = tts(m, ln["text"], ln.get("style", ""), voice)
                        open(dest, "wb").write(wav); model_ok = m; err = None; break
                    except urllib.error.HTTPError as e:
                        body = e.read().decode(errors="replace")[:300]
                        err = f"{m} {e.code} {body}"
                        if e.code == 401 or e.code == 403:
                            sys.exit(f"Clé refusée ({e.code}) : vérifie le secret GEMINI_API_KEY. {body}")
                        if e.code == 429:
                            break
                    except Exception as e:
                        err = f"{m} {e}"
                if err is None:
                    break
                log(f"[{ln['id']}] essai {attempt + 1} : {err}")
                time.sleep(35 if "429" in err else 5)
            if os.path.exists(dest):
                done += 1; log(f"✓ {ln['id']} ({voice}, {model_ok})")
            else:
                errors.append(ln["id"])
            time.sleep(4)
        with open(os.path.join(folder, "STATUT.txt"), "w", encoding="utf-8") as f:
            f.write(f"{'TERMINE' if done == len(lines) else 'EN COURS'} : {done}/{len(lines)} répliques, modèle {model_ok}\n")
            if errors: f.write("manquantes : " + ", ".join(errors) + "\n")
        if done == len(lines):
            shutil.move(os.path.join(REQ, rf), os.path.join(DONE, rf))


if __name__ == "__main__":
    main()
