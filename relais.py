# -*- coding: utf-8 -*-
"""
Relais Agnes (GitHub Actions) : transforme des images en clips vidéo avec l'API gratuite Agnes AI.

- Les demandes sont des fichiers texte dans file_attente/ :  une ligne par plan  "image.jpg | mouvement"
- Les images sont dans images/
- Les clips arrivent dans clips/<nom_demande>/NN_image.mp4 (+ STATUT.txt)
- La clé vient du secret GitHub AGNES_API_KEY (jamais écrite dans le dépôt ni dans les logs).

Chaque exécution :
  * reprend les vidéos déjà lancées (fichiers .pending) et télécharge celles qui sont prêtes ;
  * lance au plus 1 nouveau plan par minute ;
  * si la file Agnes est pleine, s'arrête proprement : la prochaine exécution réessaiera.
"""
import json, mimetypes, os, sys, time, uuid, urllib.request, urllib.error, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
REQ, IMG, OUT = (os.path.join(ROOT, d) for d in ("file_attente", "images", "clips"))
DONE = os.path.join(REQ, "traitees")
BASE = os.environ.get("AGNES_BASE", "https://apihub.agnes-ai.com")
MODEL = "agnes-video-2.5-flash"
STYLE = ("cinematic 2D anime illustration, same character and same set as the image, "
         "natural subtle motion, consistent lighting")
MAX_RUN = int(os.environ.get("MAX_RUN_SECONDS", "1080"))   # ~18 min par exécution
T0 = time.time()
KEY = os.environ.get("AGNES_API_KEY", "").strip()


def log(m):
    print(time.strftime("%H:%M:%S ") + m, flush=True)


def left():
    return MAX_RUN - (time.time() - T0)


class ApiError(Exception):
    def __init__(self, code, body):
        super().__init__(f"{code} - {body[:300]}")
        self.code, self.body = code, body


def api(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data else "GET",
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": "application/json",
                                          "User-Agent": "agnes-relais/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode(errors="replace"))


def upload(url, field, path, extra):
    b = uuid.uuid4().hex
    parts = []
    for k, v in extra.items():
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{field}"; filename="{os.path.basename(path)}"\r\n'
                 f'Content-Type: {mime}\r\n\r\n'.encode() + open(path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(url, data=b"".join(parts), method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}",
                                          "User-Agent": "agnes-relais/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode().strip()


def public_url(path):
    if os.environ.get("RELAIS_TEST_URL"):
        return os.environ["RELAIS_TEST_URL"]
    hosts = [("litterbox", "https://litterbox.catbox.moe/resources/internals/api.php", "fileToUpload",
              {"reqtype": "fileupload", "time": "72h"}),
             ("catbox", "https://catbox.moe/user/api.php", "fileToUpload", {"reqtype": "fileupload"}),
             ("0x0", "https://0x0.st", "file", {})]
    for name, url, field, extra in hosts:
        try:
            u = upload(url, field, path, extra)
            if u.startswith("http"):
                return u
            log(f"  hébergeur {name} : réponse inattendue")
        except Exception as e:
            log(f"  hébergeur {name} indisponible ({e})")
    raise RuntimeError("aucun hébergeur d'image disponible")


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "agnes-relais/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest + ".part", "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(dest + ".part", dest)


def poll(vid):
    r = api(f"/agnesapi?video_id={vid}&model_name={MODEL}")
    st = r.get("status")
    url = r.get("url") or (r.get("metadata") or {}).get("url")
    return st, url, r


def plans_of(req_path):
    out = []
    for line in open(req_path, encoding="utf-8-sig"):
        line = line.strip()
        if line and not line.startswith("#") and "|" in line:
            img, prompt = (p.strip() for p in line.split("|", 1))
            out.append((img, prompt))
    return out


def status(folder, text):
    with open(os.path.join(folder, "STATUT.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")


def main():
    if not KEY.startswith("sk-"):
        sys.exit("Secret AGNES_API_KEY manquant ou invalide.")
    os.makedirs(DONE, exist_ok=True)
    reqs = sorted(f for f in os.listdir(REQ) if f.endswith(".txt"))
    if not reqs:
        log("Aucune demande en attente.")
        return
    last_create = 0.0
    queue_full = False
    for rf in reqs:
        name = os.path.splitext(rf)[0]
        folder = os.path.join(OUT, name)
        os.makedirs(folder, exist_ok=True)
        plans = plans_of(os.path.join(REQ, rf))
        log(f"=== {rf} : {len(plans)} plan(s) ===")
        done = 0
        for i, (img, prompt) in enumerate(plans, 1):
            base = f"{i:02d}_{os.path.splitext(img)[0]}"
            dest = os.path.join(folder, base + ".mp4")
            pend = os.path.join(folder, base + ".pending")
            if os.path.exists(dest) and os.path.getsize(dest) > 10000:
                done += 1
                continue
            # 1) vidéo déjà lancée : on regarde si elle est prête
            if os.path.exists(pend):
                vid = open(pend).read().strip()
                try:
                    st, url, r = poll(vid)
                except ApiError as e:
                    log(f"[{i}] suivi impossible ({e}) : on relancera")
                    os.remove(pend)
                    continue
                if st == "completed" and url:
                    download(url, dest); os.remove(pend); done += 1
                    log(f"[{i}] ✓ {base}.mp4")
                elif st == "failed":
                    log(f"[{i}] échec côté Agnes : {json.dumps(r.get('error'))[:200]} : on relancera")
                    os.remove(pend)
                else:
                    log(f"[{i}] en cours ({st} {r.get('progress', '')}%)")
                continue
            # 2) nouveau plan
            if queue_full or left() < 120:
                continue
            path = os.path.join(IMG, img)
            if not os.path.exists(path):
                log(f"[{i}] image introuvable : images/{img}")
                continue
            wait = 62 - (time.time() - last_create)
            if last_create and wait > 0:
                time.sleep(wait)
            last_create = time.time()
            try:
                u = public_url(path)
                body = {"model": MODEL, "prompt": f"{prompt}. {STYLE}", "mode": "keyframe",
                        "first_frame": u, "seconds": "6", "size": "720P", "aspect_ratio": "9:16"}
                res = api("/v1/videos", body)
                vid = res.get("video_id") or res.get("id") or res.get("task_id")
                open(pend, "w").write(str(vid))
                log(f"[{i}] lancé ({img})")
            except ApiError as e:
                if "queue_full" in e.body or e.code in (429, 503):
                    log(f"[{i}] file Agnes pleine : on réessaiera à la prochaine exécution")
                    queue_full = True
                elif e.code == 401:
                    sys.exit("Clé refusée (401) : vérifie le secret AGNES_API_KEY.")
                elif "quota" in e.body:
                    sys.exit("Quota épuisé pour ce modèle.")
                else:
                    log(f"[{i}] refusé : {e}")
            except Exception as e:
                log(f"[{i}] erreur : {e}")
        # attendre les vidéos lancées tant qu'il reste du temps
        while left() > 60:
            pendings = [f for f in os.listdir(folder) if f.endswith(".pending")]
            if not pendings:
                break
            time.sleep(15)
            for pf in pendings:
                base = pf[:-8]
                vid = open(os.path.join(folder, pf)).read().strip()
                try:
                    st, url, r = poll(vid)
                except ApiError:
                    continue
                if st == "completed" and url:
                    download(url, os.path.join(folder, base + ".mp4"))
                    os.remove(os.path.join(folder, pf)); done += 1
                    log(f"✓ {base}.mp4")
                elif st == "failed":
                    os.remove(os.path.join(folder, pf))
                    log(f"✗ {base} : échec côté Agnes, relancé à la prochaine exécution")
        if done >= len(plans):
            status(folder, f"TERMINE : {done}/{len(plans)} clips")
            shutil.move(os.path.join(REQ, rf), os.path.join(DONE, rf))
            log(f"=== {rf} terminée ===")
        else:
            status(folder, f"EN COURS : {done}/{len(plans)} clips" + (" (file Agnes pleine)" if queue_full else ""))


if __name__ == "__main__":
    main()
