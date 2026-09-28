"""Junta páginas + buscas + transcrições -> dados.json (anúncios selecionados) + lista de mídia."""
import json, glob, re, os, datetime, collections
HOJE = datetime.date(2026, 9, 25)
MES = dict(jan=1, fev=2, mar=3, abr=4, mai=5, jun=6, jul=7, ago=8, set=9, out=10, nov=11, dez=12)
def data(s):
    m = re.match(r"(\d+) de (\w+) de (\d+)", (s or "").strip())
    return datetime.date(int(m[3]), MES[m[2]], int(m[1])) if m else None
M = json.load(open("marcas.json"))            # slug -> meta (grupo, cat, nome, pids, modo, ...)
OV = json.load(open("overrides.json"))        # {"fora": [ids], "dentro": [ids], "b2b2c": [ids]}
BARB = re.compile(r"barbear|barbeir|barber|barbería|barbero", re.I)
INT = re.compile(r"revend|distribu|atacado|tabela|fábrica|fabrica[çc]|fornecedor|representante|margem|lucr|faturament|estoque|prateleira|bancada|parceir|condições especiais|condições exclusivas|preço especial|preços especiais|catálogo|seja um|sua barbearia|seu negócio|para barbearias|barbearias d[eo]|donos? de barbearia|barbeiros?,|ticket|cadastr|abaste[çc]a|wholesale|stockist|stock |trade pricing|reseller|mayorist|tu barbería|su barbería|dueños|ganar|ingresos|your shop|your counter|business owners", re.I)
INTL = re.compile(r"wholesale|stockist|trade pric|reseller|mayorist|distribuid|business owners|dueños|revendedor|own a barbershop|beauty pros|salon owners|tu negocio|su negocio|tu barbería|tienes una barbería|your shop", re.I)
PERF = re.compile(r"perfum|body splash|colônia|\bfragrances?\b|\bscents?\b", re.I)
B2B2C = re.compile(r"reconhecida por barbeiros|nas melhores barbearias|barbearia parceira|encontre .{0,40}barbearia|disponível .{0,40}barbearias", re.I)
FIX = [(r"\bD(?:om|on|ual|uon|u)\s?(?:All\s?)?[Ss]eeds\b", "Don Alcides"), (r"\bCabaleiros\b", "Caballeros"), (r"\bBlack ?[Ww]ait\b", "Black White"),
       (r"\bAlpha ?look'?s?\b|\bAlphalux\b|\bAlfalook'?s?\b", "Alfa Look's"), (r"\bCOD Barber ?[Ss]hop\b", "QOD Barber Shop"), (r"\bYouman\b", "You Man"),
       (r"\bForce Man\b", "Force Men"), (r"\bbarbeirias\b", "barbearias"), (r"\bDon Alcid(?:e|ez)s?\b", "Don Alcides")]
def fala(i):
    p = f"transcricoes/{i}.json"
    if not os.path.exists(p): return "", ""
    d = json.load(open(p)); t = d.get("text", "")
    lp = [s["lp"] for s in d.get("segs", [])]
    if len(t.split()) < 12 or (lp and sum(lp) / len(lp) < -0.6): return "", ""
    for a, b in FIX: t = re.sub(a, b, t)
    g = " ".join(s["t"] for s in d["segs"] if s["s"] < 4.5).strip() or d["segs"][0]["t"]
    for a, b in FIX: g = re.sub(a, b, g)
    return t.strip(), g[:200]
TAGS = [
 ("Lucro e margem", r"lucr|faturament|margem|ganhar mais|ganha mais|ganhos|renda|receita|ticket|dinheiro|rentab|profit|margin|ingresos|ganar"),
 ("Seja distribuidor", r"distribuidor|revendedor|representante|exclusividade regional|sua cidade|sua região|stockist|reseller|distributor"),
 ("Tabela e condição", r"tabela|condiç(ão|ões) (especia|exclusiva)|preço especial|preços especiais|desconto|preço de fábrica|atacado|quanto mais compra|pedido mínimo|trade pricing|wholesale|mayorista|precios"),
 ("Fábrica e estoque", r"fábrica|fabricação|centros? (logístic|de distribui)|pronta entrega|estoque (sempre|abastecido)|ruptura|entrega rápida|anos de mercado|mil barbearias|países|fabricantes?"),
 ("Exclusividade", r"exclusiv|não está em farmácia|não (vende|vendemos) pra distribuidor|sem intermedi|sem distribuidor|direto com a marca|fale direto"),
 ("Produto em uso", r"aplica|finaliza|fixação|efeito (matte|seco|brilho|clássico)|textura|comparativo|como usar|passo a passo|antes e depois|procedimento|demonstr"),
 ("Educação e parceria", r"curso|mentoria|capacita|treinamento|suporte|parceir|consultor|ensina|training"),
 ("Bancada e vitrine", r"bancada|prateleira|vitrine|balcão|embalagem|apresentação|posicionamento|shelf|counter"),
 ("Chamada regional", r"(no|na|em|do|de) (paraná|são paulo|rio de janeiro|minas gerais|belo horizonte|curitiba|goiânia|manaus|londrina|maringá|piauí|montes claros|estado de são paulo|rio grande)|\bhouston\b|\bbolivia\b|\becuador\b"),
 ("Promoção", r"black friday|natal|promoç|% ?off|últimos dias|cupom|oferta|sale\b"),
 ("Marca própria", r"marca própria|sua (própria )?marca|rótulo|private label|nome da sua barbearia|maquila|fabrica tu marca"),
 ("Serviço novo", r"desondula|pigment|platin|selagem|cobre (os )?(fios )?brancos|luzes|progressiva|novo serviço|serviço rápido|mais serviços"),
]
TAGS = [(n, re.compile(r, re.I)) for n, r in TAGS]
def hook_txt(b):
    for l in b.split("\n"):
        l = re.sub(r"^[\W_]+", "", l).strip()
        if len(l) > 3: return l[:180]
    return ""
def dominio(u):
    m = re.match(r"https?://(?:www\.)?([^/?#]+)", u or ""); d = m[1] if m else ""
    return "" if d in ("fb.me", "l.facebook.com") else d

def carrega():
    ads = {}
    for f in glob.glob("paginas/*.json") + glob.glob("busca/*.json"):
        d = json.load(open(f))
        for a in d["ads"]:
            if a["id"] not in ads or len(a.get("imgs", [])) > len(ads[a["id"]].get("imgs", [])): ads[a["id"]] = a
    return ads

def main():
    ads = carrega()
    pid2, modo = {}, {}
    for s, m in M.items():
        for p, md in m["pids"].items(): pid2[p] = s; modo[p] = md
    out = []
    por = collections.defaultdict(list)
    for a in ads.values():
        s = pid2.get(a["pid"])
        if not s or a["id"] in OV["fora"]: continue
        m = M[s]; t_fala, g_fala = fala(a["id"])
        txt = a["body"] + " " + " ".join(a.get("card", [])) + " " + t_fala
        md = modo[a["pid"]]
        if md == "so_ov" and a["id"] not in OV["dentro"] + OV["b2b2c"]: continue
        if a["id"] in OV["b2b2c"] or md == "b2b2c" or (md == "regex" and B2B2C.search(txt) and not INT.search(a["body"])): pub = "b2b2c"
        elif md == "tudo" or a["id"] in OV["dentro"]: pub = "b2b"
        elif md == "barb" and BARB.search(txt): pub = "b2b"
        elif md == "intl" and INTL.search(txt): pub = "b2b"
        elif md == "regex" and BARB.search(txt) and INT.search(txt): pub = "b2b"
        else: continue
        dt = data(a["start"]); dd = (HOJE - dt).days if dt else 0
        tags = [n for n, r in TAGS if r.search(a["body"] + " " + t_fala)]
        if pub == "b2b2c": tags = ["Puxa pela barbearia"] + tags
        if PERF.search(a["body"]): tags.append("Perfume")
        e = dict(id=a["id"], m=s, g=m["grupo"], pub=pub, ini=dt.strftime("%d/%m/%y") if dt else "", d=dd, n=a.get("n", 1), multi=a.get("multi", False),
                 fmt=a["fmt"], dur=a.get("dur", ""), body=a["body"].strip(), card=[c for c in a.get("card", []) if len(c) > 2][:3], cta=a.get("cta", ""),
                 dom=dominio(a.get("url", "")), hookT=hook_txt(a["body"]), hookF=g_fala, fala=t_fala, tags=tags,
                 poster=a.get("poster", ""), video=a.get("video", ""), imgs=a.get("imgs", []))
        por[s].append(e)
    for s, L in por.items():
        L.sort(key=lambda e: (-e["d"], e["id"]))
        grupos = {}
        for e in L:
            mid = (e["poster"] or (e["imgs"] or [""])[0]).split("?")[0].rsplit("/", 1)[-1]
            k = (e["body"][:300], e["dur"]) if e["fmt"] == "video" and e["body"] else (e["body"][:300], e["fmt"], e["dur"], mid)
            if k in grupos:
                g = grupos[k]; g["irmaos"] = g.get("irmaos", []) + [e["id"]]; g["n"] = max(g["n"], e["n"], len(g["irmaos"]) + 1)
                if not g["fala"] and e["fala"]: g["fala"], g["hookF"] = e["fala"], e["hookF"]
            else: grupos[k] = e
        L[:] = list(grupos.values())
        cap = M[s].get("cap")
        if cap:  # vizinhos e lá fora: fica com os mais longevos, sem repetir o mesmo texto
            vist, keep = set(), []
            L.sort(key=lambda e: (e["id"] not in OV["dentro"] + OV["b2b2c"], -e["d"]))
            for e in L:
                k = e["hookT"][:60]
                if k in vist and e["id"] not in OV["dentro"]: continue
                vist.add(k); keep.append(e)
                if len(keep) >= cap: break
            L[:] = keep
        out += L
    json.dump(out, open("selecionados.json", "w"), ensure_ascii=False)
    c = collections.Counter((e["g"], e["pub"]) for e in out)
    print(len(out), dict(c))
    for s in M:
        L = por.get(s, [])
        print(f"  {s}: {len(L)} ({sum(1 for e in L if e['fmt']=='video')} vídeos) max {max([e['d'] for e in L], default=0)}d")
if __name__ == "__main__": main()
