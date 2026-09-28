"""uso: CDP_PORTA=.. CDP_PERFIL=.. python3 acha_pid.py marcas_web.json -> pids_web.json
Para cada marca sem page_id: busca o nome na Biblioteca (anúncios ativos, BR) e escolhe a página cujo link aponta pro domínio da marca
(ou cujo nome bate). Sem DMAX: qualquer anúncio ativo serve pra achar a página."""
import asyncio, json, os, re, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bib
from util import dominio
W = json.load(open(sys.argv[1])); OUT = "pids_web.json"
R = json.load(open(OUT)) if os.path.exists(OUT) else {}
norm = lambda s: re.sub(r"[^a-z0-9]", "", "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn"))
async def main():
    ws, a = await bib.abre()
    for w in W:
        nome = w["nome"]; site = dominio("https://" + re.sub(r"^https?://", "", w.get("site", "")))
        if nome in R: continue
        t0 = time.time()
        try: d = await bib.coleta(a, bib.url_busca(nome, "BR"), "", 2)
        except Exception as e: print("ERRO", nome, e, flush=True); continue
        cands = {}
        for ad in d["ads"]:
            pid = ad.get("pid");
            if not pid: continue
            c = cands.setdefault(pid, {"page": ad["page"], "n": 0, "dom": 0, "nome": 0})
            c["n"] += 1
            if site and site.split(".")[0] in dominio(ad.get("url")): c["dom"] += 1
            if norm(nome) and (norm(nome) in norm(ad["page"]) or norm(ad["page"]) in norm(nome)): c["nome"] += 1
        best = sorted(cands.items(), key=lambda kv: (-(kv[1]["dom"] > 0), -(kv[1]["nome"] > 0), -kv[1]["dom"], -kv[1]["n"]))
        esc = best[0] if best and (best[0][1]["dom"] or best[0][1]["nome"]) else None
        R[nome] = {"pid": esc[0], "page": esc[1]["page"], "sinal": esc[1]} if esc else {"pid": "", "tot": d["tot"]}
        json.dump(R, open(OUT, "w"), ensure_ascii=False, indent=1)
        print(f"{nome} -> {R[nome].get('page','—')} {R[nome].get('pid','')} | {d['tot']} | {time.time()-t0:.0f}s", flush=True)
        await asyncio.sleep(2)
    await ws.close()
asyncio.run(main())
