"""Acha o page_id das gringas pelo nome (Biblioteca, mundo todo, só anúncios 30+ dias) -> mundo_descobertas2.json"""
import asyncio, json, os, re, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bib
from util import dominio
DMAX = os.environ.get("DMAX", "2026-08-27"); PAUSA = float(os.environ.get("PAUSA", "9"))
norm = lambda s: re.sub(r"[^a-z0-9]", "", "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn"))
W = json.load(open("mundo_web_pend.json")); R = json.load(open("pids_mundo.json")) if os.path.exists("pids_mundo.json") else {}
async def main():
    ws, a = await bib.abre()
    for w in W:
        if w["nome"] in R: continue
        base = w["site"].split(".")[0]; t0 = time.time()
        try: d = await bib.coleta(a, bib.url_busca(w["nome"], "ALL", dmax=DMAX), "", 2)
        except Exception as e: print("ERRO", w["nome"], e, flush=True); continue
        c = {}
        for ad in d["ads"]:
            pid = ad.get("pid")
            if not pid: continue
            x = c.setdefault(pid, {"page": ad["page"], "n": 0, "dom": 0, "nome": 0}); x["n"] += 1
            if base in dominio(ad.get("url")): x["dom"] += 1
            if norm(w["nome"]) == norm(ad["page"]) or norm(ad["page"]).startswith(norm(w["nome"])): x["nome"] += 1
        best = sorted(c.items(), key=lambda kv: (-(kv[1]["dom"] > 0), -kv[1]["dom"], -kv[1]["nome"], -kv[1]["n"]))
        esc = best[0] if best and best[0][1]["dom"] else None
        R[w["nome"]] = {"pid": esc[0], "page": esc[1]["page"]} if esc else {"pid": ""}
        json.dump(R, open("pids_mundo.json", "w"), ensure_ascii=False, indent=1)
        print(f"{w['nome']} -> {R[w['nome']].get('page','—')} {R[w['nome']].get('pid','')} | {d['tot']} | {time.time()-t0:.0f}s", flush=True)
        await asyncio.sleep(PAUSA)
    novos = [{"nome": w["nome"], "pid": R[w["nome"]]["pid"], "grupo": w["grupo"], "pais": "ALL", "site": "https://" + w["site"] + "/"} for w in W if R.get(w["nome"], {}).get("pid")]
    json.dump(novos, open("mundo_descobertas2.json", "w"), ensure_ascii=False, indent=0)
    print("FIM", len(novos), flush=True); await ws.close()
asyncio.run(main())
