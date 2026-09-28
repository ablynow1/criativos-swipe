"""uso: CDP_PORTA=.. CDP_PERFIL=.. DMAX=2026-08-27 PAUSA=8 python3 paginas.py alvos.json [PAIS] [MAXS]
alvos.json = [{"slug":..,"pid":..}] -> paginas/<PAIS>-<slug>.json
Por página: 1) anúncios ativos que já rodavam em DMAX (ordenados por impressões)
            2) só se vierem entre 1 e 19: o total de ativos (pra saber se a loja passa de 20).
Freio anti-bloqueio: página vazia sem contagem não é gravada na hora (vai pra repescagem no fim);
3 vazias seguidas = para tudo (bloqueio silencioso da Biblioteca)."""
import asyncio, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bib
from util import num_tot
ALVOS = json.load(open(sys.argv[1])); PAIS = sys.argv[2] if len(sys.argv) > 2 else "BR"
MAXS = int(sys.argv[3]) if len(sys.argv) > 3 else 10
DMAX = os.environ.get("DMAX") or None
PAUSA = float(os.environ.get("PAUSA", "8"))
async def varre(a, al):
    d = await bib.coleta(a, bib.url_pagina(al["pid"], PAIS, dmax=DMAX), "", MAXS)
    n30 = num_tot(d["tot"]); tot = {"tot": "", "empty": d["empty"]}
    if 0 < n30 < 20:
        await asyncio.sleep(PAUSA / 2)
        tot = await bib.coleta(a, bib.url_pagina(al["pid"], PAIS), "", 0, espera=7)
    d.update(al); d["pais"] = PAIS; d["dmax"] = DMAX
    d["tot_ativos"] = tot["tot"] or (d["tot"] if n30 >= 20 else "")
    return d
def grava(d, t0):
    json.dump(d, open(f"paginas/{PAIS}-{d['slug']}.json", "w"), ensure_ascii=False)
    print(f"{d['slug']} | ativos {d['tot_ativos']} | 30d+ {d['tot']} | {d['count']} cards | vazio={d['empty']} | {time.time()-t0:.0f}s", flush=True)
async def main():
    ws, a = await bib.abre(); seguidos = 0; pend = []
    fila = [al for al in ALVOS if not os.path.exists(f"paginas/{PAIS}-{al['slug']}.json")]
    for al in fila:
        t0 = time.time()
        try: d = await varre(a, al)
        except Exception as e: print("ERRO", al["slug"], e, flush=True); continue
        if not d["tot"] and not d["ads"]:
            seguidos += 1; pend.append(al); print(f"{al['slug']} | vazia (repescagem)", flush=True)
            if seguidos >= 3:
                await asyncio.sleep(PAUSA)
                c = await bib.coleta(a, bib.url_busca("oversized", PAIS, dmax=DMAX), "", 0)
                if not c["ads"]: print("BLOQUEIO: parando", flush=True); await ws.close(); return
                print("controle ok: vazias são reais", flush=True); seguidos = 0
        else: seguidos = 0; grava(d, t0)
        await asyncio.sleep(PAUSA)
    for al in pend:
        t0 = time.time()
        try: grava(await varre(a, al), t0)
        except Exception as e: print("ERRO", al["slug"], e, flush=True)
        await asyncio.sleep(PAUSA)
    print("FIM_VARREDURA", flush=True)
    await ws.close()
asyncio.run(main())
