"""Agrega as buscas por palavra-chave -> candidatos.json (uma linha por página anunciante)."""
import json, glob, collections, re
from util import dias, dominio
LIXO = re.compile(r"shein|alibaba|artlist|aliexpress|temu|shopee|mercadolivre|amazon|magalu|netshort|play\.google|apps\.apple|hotmart|kiwify|canva|capcut", re.I)
P = {}
import sys
PREF = sys.argv[1] if len(sys.argv) > 1 else "BR"
for f in sorted(glob.glob(f"busca/{PREF}-*.json")):
    d = json.load(open(f)); q = d.get("q", f)
    for pos, a in enumerate(d["ads"]):
        pid = a.get("pid") or ""
        if not pid: continue
        e = P.setdefault(pid, dict(pid=pid, page=a["page"], q=set(), n=0, doms=collections.Counter(), maxd=0, ex=[], fmts=collections.Counter(), best_pos=999))
        e["q"].add(q); e["n"] += 1; e["fmts"][a["fmt"]] += 1; e["best_pos"] = min(e["best_pos"], pos)
        dm = dominio(a.get("url"))
        if dm: e["doms"][dm] += 1
        dd = dias(a.get("start")) or 0; e["maxd"] = max(e["maxd"], dd)
        if len(e["ex"]) < 3: e["ex"].append((a.get("body") or " ".join(a.get("card") or []))[:140].replace("\n", " "))
out = []
for e in P.values():
    dom = e["doms"].most_common(1)[0][0] if e["doms"] else ""
    if LIXO.search(dom) or LIXO.search(e["page"]): continue
    out.append(dict(pid=e["pid"], page=e["page"], dom=dom, n=e["n"], nq=len(e["q"]), q=sorted(e["q"])[:8], maxd=e["maxd"], best_pos=e["best_pos"], fmts=dict(e["fmts"]), ex=e["ex"]))
out.sort(key=lambda x: (-x["nq"], -x["n"]))
json.dump(out, open("candidatos.json" if PREF == "BR" else f"candidatos_{PREF}.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "páginas")
for x in out[:400]:
    print(f"{x['nq']:2d} {x['n']:3d} {x['maxd']:4d}d {x['page'][:28]:28s} {x['pid']:17s} {x['dom'][:30]:30s} | {' ; '.join(x['q'][:4])[:60]} | {x['ex'][0][:70] if x['ex'] else ''}")
