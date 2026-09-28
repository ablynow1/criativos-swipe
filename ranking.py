"""validados.json -> ranking.json: os criativos mais escalados, do mais pro menos.
Escala = dias no ar (tempo imprimindo) x bônus de variações (+15% por variação extra, até +150%).
Só entra anúncio que leva pro site da loja (home, coleção ou produto). Top N por região (Brasil / Mundo)."""
import json, os, re, subprocess, concurrent.futures as cf
from PIL import Image
from util import dominio
V = json.load(open("validados.json")); M = {m["slug"]: m for m in json.load(open("marcas.json"))}
CUR = json.load(open("curadoria.json")); EXC = set(CUR.get("excluir", []))
N = int(os.environ.get("RANK_N", "150")); CAP = int(os.environ.get("RANK_CAP", "8"))
RUIM = re.compile(r"instagram\.com|facebook\.com|fb\.com|fb\.me|wa\.me|whatsapp|linktr|l\.instagram|apps\.apple|play\.google", re.I)
FEM = re.compile(r"feminin|\bsaia\b|vestido|biqu[ií]ni|\bmai[ôo]\b|cropped|lingerie|suti[ãa]|calcinha|legging|women|womenswear|\bdonna\b|\bfemme\b|\bmujer\b|\bdress\b|\bskirt\b|bikini|\bher\b", re.I)
def an(i):
    p = f"analise/out/{i}.json"
    return json.load(open(p)) if os.path.exists(p) else None
def escala(a): return round(a["d"] * (1 + 0.15 * min(max(a.get("n", 1), 1) - 1, 10)), 1)
pool = {"br": [], "mundo": []}
for a in V:
    m = M.get(a["m"])
    if not m or a["id"] in EXC: continue
    u = a.get("url") or ""
    if not u or RUIM.search(u) or not dominio(u): continue
    x = an(a["id"])
    if x is not None:
        if x.get("publico") == "feminino" or (x.get("publico") not in ("masculino", "unissex") and FEM.search(x.get("peca", ""))): continue
    elif FEM.search((a.get("body") or "") + " " + " ".join(a.get("card") or [])): continue
    reg = "mundo" if m["grupo"].startswith("mundo") or m["grupo"] == "fora" else "br"
    pool[reg].append(dict(a, esc=escala(a), reg=reg))
os.makedirs("site/thumbs", exist_ok=True); os.makedirs("midia", exist_ok=True)
def baixa(a):
    t = f"midia/{a['id']}.jpg"
    if os.path.exists(t) and os.path.getsize(t) > 2000: return True
    u = a.get("poster") or (a.get("imgs") or [""])[0]
    if not u: return False
    r = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", "Mozilla/5.0", "-o", t, u])
    return r.returncode == 0 and os.path.exists(t) and os.path.getsize(t) > 2000
def ahash(p):
    try:
        im = Image.open(p).convert("L").resize((16, 16)); px = list(im.getdata()); mm = sum(px) / len(px)
        return int("".join("1" if x > mm else "0" for x in px), 2)
    except Exception: return None
out = []
for reg, L in pool.items():
    L.sort(key=lambda a: (-a["esc"], -a["d"]))
    fica, hashes, por = [], {}, {}
    fila = []
    for a in L:
        if por.get(a["m"], 0) + sum(1 for x in fila if x["m"] == a["m"]) >= CAP: continue
        fila.append(a)
        if len(fila) >= N * 1.4: break
    with cf.ThreadPoolExecutor(8) as ex: ok = list(ex.map(baixa, fila))
    for a, k in zip(fila, ok):
        if not k or por.get(a["m"], 0) >= CAP: continue
        h = ahash(f"midia/{a['id']}.jpg")
        if h is not None and any(bin(h ^ h2).count("1") <= 6 for h2 in hashes.get(a["m"], [])): continue
        hashes.setdefault(a["m"], []).append(h)
        th = f"site/thumbs/{a['id']}.jpg"
        if not os.path.exists(th):
            im = Image.open(f"midia/{a['id']}.jpg").convert("RGB"); im.thumbnail((520, 988)); im.save(th, quality=80, optimize=True)
        fica.append(a); por[a["m"]] = por.get(a["m"], 0) + 1
        if len(fica) == N: break
    for i, a in enumerate(fica):
        out.append(dict(id=a["id"], m=a["m"], reg=reg, pos=i + 1, esc=a["esc"], d=a["d"], n=a.get("n", 1), fmt=a["fmt"], dur=a.get("dur", ""),
                        ini=a.get("start", ""), body=a.get("body", ""), card=a.get("card") or [], cta=a.get("cta", ""), url=a.get("url", ""),
                        th=f"thumbs/{a['id']}.jpg"))
json.dump(out, open("ranking.json", "w"), ensure_ascii=False)
from collections import Counter
for reg in ("br", "mundo"):
    R = [r for r in out if r["reg"] == reg]
    print(reg, len(R), "| top5:", [(M[r["m"]]["nome"], r["d"], r["n"], r["esc"]) for r in R[:5]], "| lojas mais presentes:", Counter(M[r["m"]]["nome"] for r in R).most_common(5))
