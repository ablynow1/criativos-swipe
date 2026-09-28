"""Fila única (1 Chrome, devagar) depois do bloqueio:
 A) acha o page_id das marcas da pesquisa web (busca pelo nome, só anúncios com 30+ dias) -> descobertas5.json
 B) varre as páginas que faltam (prioridade na ordem de marcas.json + fora no fim)
Freio: 3 vazios seguidos -> busca de controle ("camiseta oversized"); se o controle vier vazio, para (bloqueio)."""
import asyncio, json, os, re, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bib
from util import num_tot, dominio
DMAX = os.environ.get("DMAX", "2026-08-27"); PAUSA = float(os.environ.get("PAUSA", "9"))
norm = lambda s: re.sub(r"[^a-z0-9]", "", "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn"))
def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
GRUPO_WEB = {"ermos": "verao", "balddoria": "street", "ambas": "street", "universo amplo": "street"}
class Freio:
    def __init__(s): s.n = 0
    async def checa(s, a, vazio):
        if not vazio: s.n = 0; return True
        s.n += 1
        if s.n < 3: return True
        await asyncio.sleep(PAUSA)
        c = await bib.coleta(a, bib.url_busca("camiseta oversized", "BR", dmax=DMAX), "", 0)
        s.n = 0
        if not c["ads"]: print("BLOQUEIO confirmado pelo controle: parando", flush=True); return False
        print("controle ok (os vazios são reais)", flush=True); return True
async def fase_a(a, fr):
    W = json.load(open("web_pend.json")); web = {w["nome"]: w for w in json.load(open("marcas_web.json"))}
    R = json.load(open("pids_web.json")) if os.path.exists("pids_web.json") else {}
    for w in W:
        nome = w["nome"]
        if nome in R: continue
        site = dominio("https://" + re.sub(r"^https?://", "", w["site"]).strip("/")); base = site.split(".")[0]
        t0 = time.time()
        try: d = await bib.coleta(a, bib.url_busca(nome, "BR", dmax=DMAX), "", 2)
        except Exception as e: print("ERRO", nome, e, flush=True); continue
        cands = {}
        for ad in d["ads"]:
            pid = ad.get("pid")
            if not pid: continue
            c = cands.setdefault(pid, {"page": ad["page"], "n": 0, "dom": 0, "nome": 0})
            c["n"] += 1; dm = dominio(ad.get("url"))
            if dm and (dm == site or (len(base) > 3 and dm.split(".")[0] == base)): c["dom"] += 1
            if norm(nome) and (norm(nome) in norm(ad["page"]) or (len(norm(ad["page"])) > 3 and norm(ad["page"]) in norm(nome))): c["nome"] += 1
        best = sorted(cands.items(), key=lambda kv: (-(kv[1]["dom"] > 0), -(kv[1]["nome"] > 0), -kv[1]["dom"], -kv[1]["n"]))
        esc = best[0] if best and (best[0][1]["dom"] or best[0][1]["nome"]) else None
        R[nome] = {"pid": esc[0], "page": esc[1]["page"], "sinal": esc[1], "site": site} if esc else {"pid": "", "tot": d["tot"]}
        json.dump(R, open("pids_web.json", "w"), ensure_ascii=False, indent=1)
        print(f"A {nome} -> {R[nome].get('page','—')} {R[nome].get('pid','')} | {d['tot']} | {time.time()-t0:.0f}s", flush=True)
        if not await fr.checa(a, not d["ads"]): return False
        await asyncio.sleep(PAUSA)
    novos = []
    for nome, r in R.items():
        if r.get("pid"):
            pw = next((x for x in web.values() if x["nome"].split(" (")[0] == nome), {})
            novos.append({"nome": nome, "pid": r["pid"], "grupo": GRUPO_WEB.get(pw.get("parecida_com", ""), "street"), "site": "https://" + r.get("site", "") + "/"})
    json.dump(novos, open("descobertas5.json", "w"), ensure_ascii=False, indent=0)
    return True
async def varre(a, pid, pais, maxs=10):
    d = await bib.coleta(a, bib.url_pagina(pid, pais, dmax=DMAX), "", maxs)
    n30 = num_tot(d["tot"]); tot = ""
    if 0 < n30 < 20:
        await asyncio.sleep(PAUSA / 2)
        tot = (await bib.coleta(a, bib.url_pagina(pid, pais), "", 0, espera=7))["tot"]
    d["tot_ativos"] = tot or (d["tot"] if n30 >= 20 else ""); return d
async def fase_b(a, fr):
    os.system("python3 monta_marcas.py > /dev/null")
    M = {m["pid"]: m for m in json.load(open("marcas.json"))}
    ordem = []
    for arq in ["descobertas5.json", "descobertas3.json", "descobertas2.json", "descobertas4.json", "fora.json", "descobertas.json", "seeds.json"]:
        if os.path.exists(arq):
            for x in json.load(open(arq)):
                if x["pid"] in M and M[x["pid"]] not in ordem: ordem.append(M[x["pid"]])
    fila = ordem
    ult = []
    for m in fila:
        pais = m.get("pais", "BR"); f = f"paginas/{pais}-{m['slug']}.json"
        if os.path.exists(f): continue
        t0 = time.time()
        try: d = await varre(a, m["pid"], pais, 8 if pais == "ALL" else 10)
        except Exception as e: print("ERRO", m["slug"], e, flush=True); continue
        vazio = not d["tot"] and not d["ads"]
        ok = await fr.checa(a, vazio)
        if not ok:
            for g in ult: 
                if os.path.exists(g): os.remove(g)
            return False
        ult = (ult + [f])[-2:] if vazio else []
        d.update(slug=m["slug"], pid=m["pid"], pais=pais, dmax=DMAX)
        json.dump(d, open(f, "w"), ensure_ascii=False)
        print(f"B {m['slug']} | ativos {d['tot_ativos']} | 30d+ {d['tot']} | {d['count']} cards | {time.time()-t0:.0f}s", flush=True)
        await asyncio.sleep(PAUSA)
    return True
async def main():
    ws, a = await bib.abre(); fr = Freio()
    ok = await fase_a(a, fr)
    if ok: ok = await fase_b(a, fr)
    print("FIM_FILA" if ok else "PAROU", flush=True)
    await ws.close()
asyncio.run(main())
