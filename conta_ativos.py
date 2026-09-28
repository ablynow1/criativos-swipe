"""Reconta o total de anúncios ativos das páginas em que o total ficou igual ao de 30+ dias (atalho da varredura)."""
import asyncio, json, os, sys, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bib
from util import num_tot
PAUSA = float(os.environ.get("PAUSA", "9"))
M = {m["slug"] for m in json.load(open("marcas.json"))}
alvos = []
for f in sorted(glob.glob("paginas/*.json")):
    d = json.load(open(f))
    if d.get("slug") not in M or d.get("ativos_conferido"): continue
    n30 = num_tot(d.get("tot")); at = num_tot(d.get("tot_ativos"))
    if n30 >= 20 and at == n30: alvos.append(f)
print(len(alvos), "páginas pra recontar", flush=True)
async def main():
    ws, a = await bib.abre()
    for f in alvos:
        d = json.load(open(f)); t0 = time.time()
        try: r = await bib.coleta(a, bib.url_pagina(d["pid"], d.get("pais", "BR")), "", 0, espera=7)
        except Exception as e: print("ERRO", d["slug"], e, flush=True); continue
        if r["tot"]:
            d["tot_ativos"] = r["tot"]; d["ativos_conferido"] = True; json.dump(d, open(f, "w"), ensure_ascii=False)
        print(f"{d['slug']} | 30d+ {d['tot']} | ativos {r['tot'] or '??'} | {time.time()-t0:.0f}s", flush=True)
        await asyncio.sleep(PAUSA)
    print("FIM_CONTA", flush=True); await ws.close()
asyncio.run(main())
