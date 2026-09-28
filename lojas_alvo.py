"""paginas/*.json + marcas.json -> lojas_alvo.json (site = domínio mais comum nos links dos anúncios)"""
import json, glob, collections, os, re
from util import dominio
M = {m["slug"]: m for m in json.load(open("marcas.json"))}
RUIM = re.compile(r"instagram|facebook|^fb\.|linktr|wa\.me|whatsapp|bit\.ly|google|youtube|tiktok|revendedor|atacado")
out = []
for f in glob.glob("paginas/*.json"):
    d = json.load(open(f)); s = d["slug"]
    if s not in M or not d.get("ads"): continue
    c = collections.Counter(x for x in (dominio(a.get("url")) for a in d["ads"]) if x and not RUIM.search(x))
    if not c: continue
    dom = c.most_common(1)[0][0]
    site = M[s].get("site") or f"https://{dom}/"
    out.append({"slug": s, "site": site})
json.dump(out, open("lojas_alvo.json", "w"), ensure_ascii=False, indent=0)
print(len(out)); print([o["site"] for o in out])
