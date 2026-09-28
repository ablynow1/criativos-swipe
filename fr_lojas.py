"""Lojas tipo Frased / By Someone's Diary: buscas de q_frase.txt (10+ dias) -> balddoria/fr_cand.json (lojas novas, pelo domínio, com os anúncios achados)
e analise/folhas_lojas/fr_<slug>.jpg (grade com até 8 anúncios de cada, direto da busca) pra nota de loja."""
import json, os, re, sys, glob, collections, subprocess, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio
from PIL import Image, ImageDraw, ImageFont
src = open("estampa_monta.py").read().split("lojas = collections.defaultdict")[0]
ns = {"__file__": os.path.abspath("estampa_monta.py")}; exec(src, ns)
MARKET, B2B, FORA, slug = ns["MARKET"], ns["B2B"], ns["FORA"], ns["slug"]
arq = lambda q: re.sub(r"[^a-z0-9]+", "-", q.lower().replace('"', ''))[:60].strip("-")
Q = [l.strip() for l in open(os.environ.get("QFILE", "q_frase.txt")) if l.strip()]
OUT = os.environ.get("OUT", "balddoria/fr_cand.json")
MM = json.load(open("marcas_medidas.json")); EM = json.load(open("estampa/marcas.json")); NV = json.load(open("balddoria/novas_scan.json"))
conhecidos = {dominio(m.get("site") or "") for m in MM + EM} | {m["slug"] for m in MM + EM + NV} | {m.get("dom", "") for m in NV}
conhecidos |= {os.path.basename(f)[:-5].replace("--10d", "") for f in glob.glob("analise/lojas_bd/*.json")} | {"frased-com", "bysomeonesdiary-com"}
conhecidos |= {c["slug"] for f in glob.glob("balddoria/fr_cand*.json") if f != OUT for c in json.load(open(f))}
TEE = re.compile(r"t-?shirts?|\btees?\b|hoodie|camiset|remera|playera|shirt|spruch|sweat", re.I)
L = collections.defaultdict(lambda: {"ads": {}, "nomes": collections.Counter(), "pids": collections.Counter()})
for q in Q:
    f = f"busca/ALL-{arq(q)}.json"
    if not os.path.exists(f): continue
    for pos, a in enumerate(json.load(open(f)).get("ads", [])):
        dd = dias(a.get("start")); u = a.get("url") or ""; dom = re.sub(r"^(www\d?|shop|store|loja|m|checkout)\.", "", dominio(u))
        if dd is None or dd < 10 or not dom or re.search(r"instagram|facebook|fb\.|wa\.me|whatsapp|linktr|apple\.com|play\.google|tiktok|flashshort", u, re.I): continue
        t = " ".join([a.get("body") or "", *(a.get("card") or [])])
        if MARKET.search(a.get("page", "") + " " + dom) or FORA.search(a.get("page", "") + " " + dom) or B2B.search(t) or not TEE.search(t): continue
        s = slug(dom)
        if dom in conhecidos or s in conhecidos: continue
        x = L[s]; x["ads"][a["id"]] = dict(a, d=dd, pos=pos); x["nomes"][a.get("page", "")] += 1; x["pids"][a.get("pid", "")] += 1; x["dom"] = dom
rank = sorted(({"slug": s, "nome": x["nomes"].most_common(1)[0][0], "pid": x["pids"].most_common(1)[0][0], "dom": x["dom"], "n": len(x["ads"]),
                "ads": sorted(x["ads"].values(), key=lambda a: a["pos"])[:8]} for s, x in L.items()), key=lambda r: -r["n"])
os.makedirs("midia/lojas_fr", exist_ok=True)
try: F = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
except Exception: F = ImageFont.load_default()
def get(u, p):
    if not (os.path.exists(p) and os.path.getsize(p) > 2000): subprocess.run(["curl", "-sL", "--max-time", "60", "-A", "Mozilla/5.0", "-o", p, u])
    return p if os.path.exists(p) and os.path.getsize(p) > 2000 else None
def folha(r):
    ims = []
    for k, a in enumerate(r["ads"]):
        u = a.get("poster") or (a.get("imgs") or [""])[0]
        p = get(u, f"midia/lojas_fr/{r['slug']}_{k}.jpg") if u else None
        if p:
            try: ims.append(Image.open(p).convert("RGB"))
            except Exception: pass
    if not ims: return 0
    W, H = 300, 375; out = Image.new("RGB", (W * 4 + 30, 60 + H * 2 + 10), (255, 255, 255)); dr = ImageDraw.Draw(out)
    dr.text((10, 14), f"{r['nome']}  ·  {r['dom']}", fill=(0, 0, 0), font=F)
    for i, im in enumerate(ims[:8]):
        im.thumbnail((W, H)); x = 10 + (i % 4) * (W + 3); y = 60 + (i // 4) * (H + 5); out.paste(im, (x + (W - im.width) // 2, y + (H - im.height) // 2))
    out.save(f"analise/folhas_lojas/fr_{r['slug']}.jpg", quality=80); return len(ims)
with cf.ThreadPoolExecutor(8) as ex: n = list(ex.map(folha, rank))
for r, k in zip(rank, n): r["folha_n"] = k
json.dump([{k: v for k, v in r.items() if k != "ads"} for r in rank], open(OUT, "w"), ensure_ascii=False, indent=1)
print("lojas novas:", len(rank), "| com folha:", sum(1 for k in n if k), "| com 2+ anúncios:", sum(1 for r in rank if r["n"] >= 2))
