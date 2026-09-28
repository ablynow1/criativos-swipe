"""2ª rodada da camiseta estampada: página de cada loja (paginas/ALL-<slug>.json, anúncios ativos que já rodavam em 27/08, por impressões)
-> estampa/sel2.json com os criativos novos das lojas em que a 1ª análise achou camiseta estampada, e o total de anúncios ativos em estampa/marcas.json.
uso: K2=6 python3 estampa_monta2.py"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio, num_tot
src = open("estampa_monta.py").read().split("lojas = collections.defaultdict")[0]  # só os filtros (regex) do 1º passo
ns = {"__file__": os.path.abspath("estampa_monta.py")}; exec(src, ns)
MARKET, B2B, FEM, OUTRO, TEE, FORA, JA = ns["MARKET"], ns["B2B"], ns["FEM"], ns["OUTRO"], ns["TEE"], ns["FORA"], ns["JA"]
K2 = int(os.environ.get("K2", "6"))
M = json.load(open("estampa/marcas.json")); S1 = json.load(open("estampa/sel.json"))
ja = JA | {a["id"] for a in S1} | {d for a in S1 for d in a.get("dups", [])}
def an(i):
    p = f"analise/out/{i}.json"
    return json.load(open(p)) if os.path.exists(p) else None
tem_estampa = {a["m"] for a in S1 if (an(a["id"]) or {}).get("estampada") is True}
sel2 = []
for m in M:
    f = f"paginas/ALL-{m['slug']}.json"
    if not os.path.exists(f): continue
    d = json.load(open(f))
    m["ativos"] = num_tot(d.get("tot_ativos") or d.get("tot")) or m.get("ativos", 0)
    m["n30"] = num_tot(d.get("tot"))
    if m["slug"] not in tem_estampa: continue
    novos = []
    for pos, a in enumerate(d.get("ads", [])):
        dd = dias(a.get("start"))
        if not a.get("ativo", True) or dd is None or dd < 30 or a["id"] in ja: continue
        texto = " ".join([a.get("body") or "", *(a.get("card") or [])])
        titulo = (a.get("card") or ["", ""])[1] if len(a.get("card") or []) > 1 else ""
        if B2B.search(texto) or FEM.search(titulo) or (OUTRO.search(titulo) and not TEE.search(titulo)): continue
        u = a.get("url") or ""
        if not dominio(u) or re.search(r"instagram\.com|facebook\.com|fb\.(com|me)|wa\.me|whatsapp|linktr|apple\.com|play\.google|t\.me|tiktok\.com", u, re.I): continue
        sc = dd + 12 * min(max(a.get("n", 1) - 1, 0), 10) + max(0, 60 - pos) + (15 if TEE.search(texto) else 0)
        novos.append(dict(a, m=m["slug"], d=dd, pos=pos, dom=dominio(u), score=sc, q="página da loja"))
    sel2 += sorted(novos, key=lambda a: -a["score"])[:K2]
json.dump(M, open("estampa/marcas.json", "w"), ensure_ascii=False, indent=1)
json.dump(sel2, open("estampa/sel2.json", "w"), ensure_ascii=False)
print(f"lojas com estampa confirmada {len(tem_estampa)} | criativos novos pela página {len(sel2)} ({sum(1 for a in sel2 if a['fmt']=='video')} vídeos) | "
      f"lojas medidas {sum(1 for m in M if m.get('n30') is not None)} | 20+ ativos: {sum(1 for m in M if (m.get('ativos') or 0) >= 20)}")
