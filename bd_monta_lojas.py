"""Lojas parecidas com a Balddoria -> criativos pro swipe (até 15 por loja, ligados há 10+ dias).
Entra a loja com nota de loja (analise/lojas_bd/<slug>.json) mais alta, até N_LOJAS (sem a própria Balddoria).
Criativos: varredura de 10+ dias (paginas/<PAIS>-<slug>--10d.json) ou, se não houver, a de 30+ dias; fora outra peça, feminino, B2B e o que já está no swipe.
uso: N_LOJAS=30 K=15 NOTA_MIN=5 python3 bd_monta_lojas.py  -> balddoria/lojas_escolhidas.json + balddoria/lojas_sel.json"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio
N_LOJAS = int(os.environ.get("N_LOJAS", "30")); K = int(os.environ.get("K", "15")); NOTA_MIN = int(os.environ.get("NOTA_MIN", "5"))
MM = {m["slug"]: m for m in json.load(open("marcas_medidas.json"))}
EM = {m["slug"]: m for m in json.load(open("estampa/marcas.json"))}
NV = {m["slug"]: m for m in json.load(open("balddoria/novas_scan.json"))}
JA = set(json.load(open("site/swipe/ids.json"))) | set(json.load(open("curadoria.json"))["excluir"])
FEM = re.compile(r"\bwom[ae]n|\bladies\b|feminin|\bmulher|cropped|baby ?look|vestido|\bsaia\b|biqu", re.I)
NAO = re.compile(r"\bcal[çc]a|bermuda|\bshorts?\b|\bbon[ée]\b|t[êe]nis|\bmeias?\b|cueca|sand[áa]lia|chinelo|perfume|[óo]culos|bolsa|mochila|carteira|pants|\bcaps?\b|sneaker|socks|jaqueta|jeans", re.I)
B2B = re.compile(r"revenda|lojista|atacado|wholesale|revendedor", re.I)
notas = []
for f in glob.glob("analise/lojas_bd/*.json"):
    try: x = json.load(open(f))
    except Exception: continue
    s = x["slug"].replace("--10d", "")
    if s == "balddoria": continue
    notas.append((int(x.get("parecida") or 0), s, x))
notas.sort(key=lambda t: -t[0])
escolhidas, sel = [], []
for nota, s, x in notas:
    if nota < NOTA_MIN or len(escolhidas) >= N_LOJAS: break
    m = MM.get(s) or EM.get(s) or NV.get(s) or {}
    pais = m.get("pais") or "BR"
    f10 = [f for f in (f"paginas/{pais}-{s}--10d.json", f"paginas/BR-{s}--10d.json", f"paginas/ALL-{s}--10d.json") if os.path.exists(f)]
    f30 = [f for f in (f"paginas/{pais}-{s}.json", f"paginas/BR-{s}.json", f"paginas/ALL-{s}.json") if os.path.exists(f)]
    fonte = (f10 or f30 or [None])[0]
    if not fonte: continue
    cand, vistos = [], set()
    for f in f10 + f30:  # 10+ dias primeiro, depois completa com a varredura de 30+
        for pos, a in enumerate(json.load(open(f)).get("ads", [])):
            dd = dias(a.get("start"))
            if a["id"] in vistos or dd is None or dd < 10 or not a.get("ativo", True): continue
            vistos.add(a["id"])
            tit = (a.get("card") or ["", ""])[1] if len(a.get("card") or []) > 1 else ""
            t = " ".join([a.get("body") or "", *(a.get("card") or [])])
            if FEM.search(tit) or NAO.search(tit) or B2B.search(t): continue
            cand.append(dict(a, m=s, d=dd, pos=pos, dom=dominio(a.get("url")), score=dd + 12 * min(max(a.get("n", 1) - 1, 0), 10) + max(0, 60 - pos) * 2))
    ja = [a for a in cand if a["id"] in JA]
    novos = sorted([a for a in cand if a["id"] not in JA], key=lambda a: -a["score"])[:max(0, K + 4 - len(ja))]  # sobra pra dedupe
    sel += novos
    escolhidas.append(dict(slug=s, nome=m.get("nome") or x.get("slug"), nota=nota, motivo=x.get("motivo", ""), vende=x.get("o_que_vende", ""), pais=pais,
                           pid=m.get("pid", ""), site=m.get("site") or ("https://" + m["dom"] if m.get("dom") else ""), no_swipe=len(ja), novos=len(novos)))
json.dump(escolhidas, open("balddoria/lojas_escolhidas.json", "w"), ensure_ascii=False, indent=1)
json.dump(sel, open("balddoria/lojas_sel.json", "w"), ensure_ascii=False)
print(f"lojas escolhidas {len(escolhidas)} (nota >= {NOTA_MIN}) | criativos novos pra baixar {len(sel)}")
for e in escolhidas: print(f"  {e['nota']} {e['nome'][:28]:28} já no swipe {e['no_swipe']:3} · novos {e['novos']:3} · {e['motivo'][:60]}")
