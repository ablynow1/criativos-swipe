"""paginas/*.json + marcas.json -> validados.json (todos os criativos 30+ dias das lojas) e selecionados.json (os que entram na página)
Critérios: loja escalada = 20+ anúncios ativos no BR (referências entram sempre); criativo validado = ativo e no ar há 30+ dias."""
import json, re, collections, os, sys
B2B = re.compile(r"revend|lojista|atacado|homologa|seja (um )?parceiro|franquia|\bb2b\b", re.I)
EXTRA = int(os.environ.get("EXTRA", "4"))
from util import dias, num_tot, dominio
MARCAS = json.load(open("marcas.json"))
EXC = set(json.load(open("curadoria.json")).get("excluir", [])) if os.path.exists("curadoria.json") else set()
CAP = {"ref": 14, "street": 7, "verao": 7, "basicos": 5, "fora": 4, "mundo-resort": 4, "mundo-street": 4, "mundo-casual": 4}
MIN_ATIVOS = 20
def chave_midia(a):
    u = a.get("poster") or (a.get("imgs") or [""])[0] or ""
    m = re.search(r"/([0-9]+_[0-9]+_[0-9]+_n\.\w+)", u)
    return m.group(1) if m else (a.get("body", "")[:80] + "|" + " ".join(a.get("card") or [])[:60])
val, sel, resumo = [], [], []
for m in MARCAS:
    f = f"paginas/{m.get('pais','BR')}-{m['slug']}.json"
    if not os.path.exists(f): print("sem página", m["slug"]); continue
    d = json.load(open(f))
    n30 = num_tot(d.get("tot")); ativos = max(num_tot(d.get("tot_ativos")), n30)
    vistos = set(); ads = []
    for pos, a in enumerate(d.get("ads", [])):
        if a.get("pid") and a["pid"] != m["pid"]: continue
        if a.get("ativo") is False or a.get("id") in EXC: continue
        dd = dias(a.get("start"))
        if dd is None or dd < 30: continue
        if B2B.search((a.get("body") or "") + " " + (a.get("url") or "") + " " + " ".join(a.get("card") or [])): continue
        k = chave_midia(a)
        if k in vistos: continue
        vistos.add(k)
        a = dict(a, m=m["slug"], d=dd, pos=pos, dom=dominio(a.get("url")))
        a["score"] = round(min(dd, 240) + 12 * min(a.get("n", 1) - 1, 10) + max(0, 25 - pos) * 2, 1)
        ads.append(a)
    m.update(ativos=ativos, n30=n30, n_val=len(ads), maxd=max([a["d"] for a in ads] or [0]))
    escalada = (m["grupo"] == "ref" or ativos >= MIN_ATIVOS) and len(ads) > 0
    m["escalada"] = escalada
    resumo.append((m["slug"], m["grupo"], ativos, n30, len(ads), m["maxd"], escalada))
    if not escalada: continue
    val += ads
    ads.sort(key=lambda a: -a["score"])
    sel += ads[:CAP.get(m["grupo"], 6) + EXTRA]
MAX_MUNDO = int(os.environ.get("MAX_MUNDO", "51"))
mundo = sorted([m for m in MARCAS if m.get("escalada") and m["grupo"].startswith("mundo")], key=lambda m: (-m.get("n30", 0), -m.get("ativos", 0)))
fora_corte = {m["slug"] for m in mundo[MAX_MUNDO:]}
if fora_corte:
    for m in MARCAS:
        if m["slug"] in fora_corte: m["escalada"] = False; m["corte"] = "limite de 51 lojas do mundo"
    val = [a for a in val if a["m"] not in fora_corte]; sel = [a for a in sel if a["m"] not in fora_corte]
print("mundo escaladas:", len(mundo), "| ficam", min(len(mundo), MAX_MUNDO))
json.dump(val, open("validados.json", "w"), ensure_ascii=False)
json.dump(sel, open("selecionados.json", "w"), ensure_ascii=False)
json.dump(MARCAS, open("marcas_medidas.json", "w"), ensure_ascii=False, indent=1)
for r in sorted(resumo, key=lambda r: (-r[6], r[1], -r[2])):
    print(f"{r[0][:22]:22s} {r[1]:6s} ativos={r[2]:5d} 30d+={r[3]:4d} coletados={r[4]:3d} maxd={r[5]:4d} {'ESCALADA' if r[6] else '-'}")
print("validados", len(val), "selecionados", len(sel), "lojas na página", len({a['m'] for a in sel}))
