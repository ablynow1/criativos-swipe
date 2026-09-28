"""uso: CDP_PORTA=9461 CDP_PERFIL=... DMAX=2026-08-27 python3 busca.py consultas.txt [PAIS] [MAXS]
Busca por palavra-chave (anúncios ativos, ordenados por impressões; DMAX = só quem já rodava nessa data)."""
import asyncio, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bib
Q = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
PAIS = sys.argv[2] if len(sys.argv) > 2 else "BR"; MAXS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
DMAX = os.environ.get("DMAX") or None
slug = lambda q: re.sub(r"[^a-z0-9]+", "-", q.lower().replace('"', ''))[:60].strip("-")
async def main():
    ws, a = await bib.abre()
    for q in Q:
        f = f"busca/{PAIS}-{slug(q)}.json"
        if os.path.exists(f): print("cache", q, flush=True); continue
        t0 = time.time()
        tipo = "keyword_exact_phrase" if q.startswith('"') else "keyword_unordered"
        try: d = await bib.coleta(a, bib.url_busca(q.strip('"'), PAIS, dmax=DMAX, tipo=tipo), "", MAXS)
        except Exception as e: print("ERRO", q, e, flush=True); continue
        d["q"] = q; d["pais"] = PAIS; d["dmax"] = DMAX
        json.dump(d, open(f, "w"), ensure_ascii=False)
        print(f"{q} | {d['tot']} | {d['count']} cards | vazio={d['empty']} | {time.time()-t0:.0f}s", flush=True)
        await asyncio.sleep(float(os.environ.get("PAUSA", "3")))
    await ws.close()
asyncio.run(main())
