"""selecionados.json + transcricoes -> analise/lotes/lote_XX.json (entrada dos analistas)"""
import json, os, math, sys
S = json.load(open(os.environ.get("SEL", "selecionados.json"))); M = {m["slug"]: m for m in json.load(open(os.environ.get("MARCAS", "marcas_medidas.json")))}
TAM = int(sys.argv[1]) if len(sys.argv) > 1 else 18
LD = os.environ.get("LOTES_DIR", "analise/lotes"); os.makedirs(LD, exist_ok=True); os.makedirs("analise/out", exist_ok=True)
BASE = os.path.abspath(".")
def fala(i):
    p = f"transcricoes/{i}.json"
    if not os.path.exists(p): return ""
    t = json.load(open(p)); segs = [s for s in t.get("segs", []) if s.get("nsp", 0) < 0.5 and s.get("lp", -9) > -1.0]
    txt = " ".join(s["t"] for s in segs).strip()
    return txt if len(txt.split()) >= 10 else ""
recs = []
for e in S:
    if os.path.exists(os.path.join(os.environ.get("OUT_DIR", "analise/out"), e["id"] + ".json")): continue
    m = M[e["m"]]
    recs.append(dict(id=e["id"], loja=m["nome"], grupo=m["grupo"], dias=e["d"], variacoes=e.get("n", 1), formato=e["fmt"], duracao=e.get("dur", ""),
                     texto_anuncio=(e.get("body") or "")[:900], cartao=e.get("card") or [], botao=e.get("cta", ""), destino=e.get("url", ""),
                     fala=fala(e["id"])[:900], folha=os.path.join(BASE, e["folha"]) if e.get("folha") else ""))
n = math.ceil(len(recs) / TAM) if recs else 0
for k in range(n):
    json.dump(recs[k * TAM:(k + 1) * TAM], open(f"{LD}/lote_{k+1:02d}.json", "w"), ensure_ascii=False, indent=1)
print(len(recs), "criativos em", n, "lotes")
