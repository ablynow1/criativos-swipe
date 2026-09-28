"""Estilo Balddoria: criativos validados (30+ dias) que ainda não estão no swipe, das lojas do universo dela
(referências, streetwear BR, streetwear mundo), tirados das páginas já varridas (paginas/*.json).
-> balddoria/sel.json + balddoria/marcas.json, pra baixar e analisar com analise/INSTRUCOES_BALDDORIA.md."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio
MM = {m["slug"]: m for m in json.load(open("marcas_medidas.json"))}
GR = {"ref": 14, "street": 6, "mundo-street": 4}   # candidatos por loja
CAPS = {"balddoria": 32, "ermos": 14, "chico-rei": 0}
JA = set(json.load(open("site/swipe/ids.json"))) | set(json.load(open("curadoria.json"))["excluir"])
FEM = re.compile(r"\bwom[ae]n|\bladies\b|feminin|\bmulher|cropped|baby ?look|vestido|\bsaia\b|biqu", re.I)
NAO = re.compile(r"\bcal[çc]a|bermuda|\bshorts?\b|\bbon[ée]\b|t[êe]nis|\bmeias?\b|cueca|jaqueta|jeans|sand[áa]lia|chinelo|perfume|[óo]culos|bolsa|mochila|carteira|pants|\bcaps?\b|sneaker|socks", re.I)
TEE = re.compile(r"camiset|oversized|\btees?\b|t-?shirt|moletom|hoodie|frase|estampa", re.I)
sel, marcas = [], []
for s, m in MM.items():
    g = m.get("grupo")
    if g not in GR: continue
    f = f"paginas/{m.get('pais', 'BR')}-{s}.json"
    if not os.path.exists(f): continue
    cand = []
    for pos, a in enumerate(json.load(open(f)).get("ads", [])):
        dd = dias(a.get("start"))
        if dd is None or dd < 30 or a["id"] in JA or not a.get("ativo", True): continue
        t = " ".join([a.get("body") or "", *(a.get("card") or [])])
        tit = (a.get("card") or ["", ""])[1] if len(a.get("card") or []) > 1 else ""
        if FEM.search(tit) or (NAO.search(tit) and not TEE.search(tit)): continue
        sc = dd + 12 * min(max(a.get("n", 1) - 1, 0), 10) + max(0, 60 - pos) + (20 if TEE.search(t) else 0)
        cand.append(dict(a, m=s, d=dd, pos=pos, dom=dominio(a.get("url")), score=sc))
    esc = sorted(cand, key=lambda a: -a["score"])[:CAPS.get(s, GR[g])]
    if esc:
        sel += esc
        marcas.append(dict(slug=s, nome=m["nome"], grupo="estampa", grupo_real=g, pais=m.get("pais", "BR"), pid=m.get("pid", ""), site=m.get("site", "")))
os.makedirs("balddoria", exist_ok=True)
json.dump(sel, open("balddoria/sel.json", "w"), ensure_ascii=False)
json.dump(marcas, open("balddoria/marcas.json", "w"), ensure_ascii=False, indent=1)
print(f"candidatos {len(sel)} de {len(marcas)} lojas ({sum(1 for a in sel if a['fmt']=='video')} vídeos) | balddoria {sum(1 for a in sel if a['m']=='balddoria')}")
