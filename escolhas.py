"""Lê os votos do swipe no servidor e separa as escolhas do Vitor.
uso: python3 escolhas.py  -> imprime o resumo e grava escolhas.json (quero / nao, com loja, dias, formato, gancho e links)"""
import json, re, subprocess
import os
BASE = os.environ.get("SWIPE_BASE", "https://SEU-SITE.com/criativos/")  # onde o site/ foi publicado
URL = BASE + "swipe/voto.php?estado=1"
votos = json.loads(subprocess.run(["curl", "-s", "--max-time", "30", URL], capture_output=True, text=True).stdout)["votos"]  # urllib leva 406 do mod_security
h = open("site/swipe/index.html").read()
D = json.loads(re.search(r"const D=(\{.*?\});\n", h, re.S).group(1).replace("<\\/", "</"))
by = {x["id"]: x for x in D["items"]}
def linha(x):
    an = x.get("an") or {}
    return dict(id=x["id"], loja=D["lojas"].get(x["m"], {}).get("n", x["m"]), regiao="Brasil" if x["r"] == "br" else "Mundo", dias=x["d"], variacoes=x["n"],
                formato=an.get("formato") or x["f"], gancho=an.get("gancho") or (x.get("b") or "").split("\n")[0][:160], replicar=an.get("replicar", ""),
                midia=(BASE + (x["v"] or x["th"])), biblioteca=f"https://www.facebook.com/ads/library/?id={x['id']}", destino=x.get("url", ""))
out = {"quero": [], "nao": []}
for id_, (v, t) in sorted(votos.items(), key=lambda kv: kv[1][1]):
    if id_ in by and v in (1, -1): out["quero" if v == 1 else "nao"].append(dict(linha(by[id_]), t=t))
json.dump(out, open("escolhas.json", "w"), ensure_ascii=False, indent=1)
print(f"quero {len(out['quero'])} · não {len(out['nao'])} · faltam {len(by) - len(out['quero']) - len(out['nao'])} de {len(by)}")
for e in out["quero"]: print(f"  ♥ {e['loja']} ({e['regiao']}) · {e['dias']}d · {e['formato']} · {e['gancho'][:90]}")
