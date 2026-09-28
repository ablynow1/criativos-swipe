"""Lojas parecidas com a Balddoria — descoberta: buscas por termo (busca/BR-*.json e as de camiseta com frase no mundo)
-> balddoria/lojas_novas.json (lojas que ainda não estão no acervo nem nas estampadas, pelo domínio, com os anúncios 30d+ achados)."""
import json, os, re, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio
src = open("estampa_monta.py").read().split("lojas = collections.defaultdict")[0]
ns = {"__file__": os.path.abspath("estampa_monta.py")}; exec(src, ns)
MARKET, B2B, FEM, FORA, slug = ns["MARKET"], ns["B2B"], ns["FEM"], ns["FORA"], ns["slug"]
arq = lambda q: re.sub(r"[^a-z0-9]+", "-", q.lower().replace('"', ''))[:60].strip("-")
qs_all = [l.strip() for f in ("q_bd_all.txt", "q_estampa.txt") for l in open(f) if l.strip() and not l.startswith("#")]
files = glob.glob("busca/BR-*.json") + [f"busca/ALL-{arq(q)}.json" for q in qs_all]
MM = json.load(open("marcas_medidas.json")); EM = json.load(open("estampa/marcas.json"))
conhecidos = {dominio(m.get("site") or m.get("url") or "") for m in MM + EM} | {m["slug"] for m in MM + EM} | {str(m.get("pid")) for m in MM + EM}
FRASE = re.compile(r"frase|slogan|statement|costas|back ?print|oversized|drop|cole[çc][ãa]o|collection|camiset|\btees?\b|t-?shirt", re.I)
L = collections.defaultdict(lambda: {"ads": {}, "nomes": collections.Counter(), "pids": collections.Counter(), "paises": collections.Counter()})
for f in files:
    if not os.path.exists(f): continue
    d = json.load(open(f)); pais = d.get("pais", "BR")
    for a in d.get("ads", []):
        dd = dias(a.get("start")); u = a.get("url") or ""; dom = re.sub(r"^(www\d?|shop|store|loja|m)\.", "", dominio(u))
        if dd is None or dd < 30 or not dom or re.search(r"instagram|facebook|fb\.|wa\.me|whatsapp|linktr|apple\.com|play\.google|tiktok", u, re.I): continue
        t = " ".join([a.get("body") or "", *(a.get("card") or [])])
        if MARKET.search(a.get("page", "") + " " + dom) or FORA.search(a.get("page", "") + " " + dom) or B2B.search(t) or not FRASE.search(t): continue
        s = slug(dom)
        if dom in conhecidos or s in conhecidos or str(a.get("pid")) in conhecidos: continue
        x = L[s]; x["ads"][a["id"]] = dict(d=dd, t=t[:140]); x["nomes"][a.get("page", "")] += 1; x["pids"][a.get("pid", "")] += 1; x["paises"][pais] += 1; x["dom"] = dom
rank = sorted(({"slug": s, "nome": x["nomes"].most_common(1)[0][0], "pid": x["pids"].most_common(1)[0][0], "dom": x["dom"], "pais": x["paises"].most_common(1)[0][0],
                "n": len(x["ads"]), "maxd": max(v["d"] for v in x["ads"].values()), "ex": [v["t"] for v in list(x["ads"].values())[:2]]} for s, x in L.items()),
              key=lambda r: (-r["n"], -r["maxd"]))
json.dump(rank, open("balddoria/lojas_novas.json", "w"), ensure_ascii=False, indent=1)
print("lojas novas com anúncio 30d+:", len(rank))
for r in rank[:45]: print(f"  {r['nome'][:26]:26} {r['dom'][:26]:26} {r['pais']} {r['n']:3} · {r['maxd']}d · {r['ex'][0][:60]!r}")
