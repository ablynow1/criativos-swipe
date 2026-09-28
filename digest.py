"""Resumo por loja pra escrever os textos (estilo, preço, oferta, leitura)."""
import json, os, collections, statistics
S = json.load(open("selecionados.json")); M = {m["slug"]: m for m in json.load(open("marcas_medidas.json"))}
V = json.load(open("validados.json"))
por = collections.defaultdict(list)
for e in S: por[e["m"]].append(e)
val = collections.Counter(e["m"] for e in V)
for s, L in por.items():
    m = M.get(s, {}); lj = json.load(open(f"lojas/{s}.json")) if os.path.exists(f"lojas/{s}.json") else {}
    fm = collections.Counter(e["fmt"] for e in [x for x in V if x["m"] == s])
    print(f"\n## {m.get('nome')} [{m.get('grupo')}] ativos={m.get('ativos')} 30d+={m.get('n30')} maxd={m.get('maxd')} val_coletados={val[s]} fmts={dict(fm)}")
    print(f"   site={lj.get('final','')} plat={lj.get('plataforma','')} precos={lj.get('precos',[])[:12]} ofertas={lj.get('ofertas',[])}")
    print(f"   title={lj.get('title','')[:80]} | desc={lj.get('desc','')[:140]}")
    for e in L[:6]:
        p = f"analise/out/{e['id']}.json"; x = json.load(open(p)) if os.path.exists(p) else {}
        print(f"   - {e['d']}d n={e.get('n',1)} {e['fmt']} | {x.get('formato','')} | {x.get('gancho','')[:80]} | of={x.get('oferta','')[:40]} | {(e.get('body') or '')[:80]!r}")
