"""Resumo por loja do mundo (dados + análises dos criativos) -> analise/digest_mundo.json, pra escrever os textos das lojas."""
import json, os, collections
S = json.load(open("selecionados.json")); M = {m["slug"]: m for m in json.load(open("marcas_medidas.json"))}
TL = json.load(open("textos_lojas.json"))
por = collections.defaultdict(list)
for e in S: por[e["m"]].append(e)
out = []
for s, L in por.items():
    m = M.get(s, {})
    if not m.get("grupo", "").startswith("mundo") or s in TL: continue
    lj = json.load(open(f"lojas/{s}.json")) if os.path.exists(f"lojas/{s}.json") else {}
    cr = []
    for e in L:
        p = f"analise/out/{e['id']}.json"; x = json.load(open(p)) if os.path.exists(p) else {}
        cr.append(dict(dias=e["d"], variacoes=e.get("n", 1), formato=x.get("formato", e["fmt"]), gancho=x.get("gancho", ""), texto=x.get("texto", ""),
                       oferta=x.get("oferta", ""), peca=x.get("peca", ""), copy=(e.get("body") or "")[:220]))
    out.append(dict(slug=s, nome=m["nome"], grupo=m["grupo"], anuncios_ativos_mundo=m.get("ativos"), com_30_dias=m.get("n30"), mais_antigo_dias=m.get("maxd"),
                    site=lj.get("final", ""), titulo_site=lj.get("title", ""), descricao_site=lj.get("desc", ""), precos_site=lj.get("precos", [])[:12],
                    ofertas_site=lj.get("ofertas", []), criativos=cr))
json.dump(out, open("analise/digest_mundo.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "lojas")
