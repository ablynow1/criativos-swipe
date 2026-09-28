"""selecionados.json + marcas_medidas.json + lojas/*.json + analise/out/*.json + textos.json -> site/index.html"""
import json, os, re, statistics, collections
from util import dominio
S = json.load(open("selecionados.json")); MM = {m["slug"]: m for m in json.load(open("marcas_medidas.json"))}
T = json.load(open("textos.json"))
TL = json.load(open("textos_lojas.json")) if os.path.exists("textos_lojas.json") else {}
GRUPOS = {"ref": {"nome": "Referências", "cor": "var(--pink)"}, "street": {"nome": "Streetwear premium", "cor": "var(--purple)"},
          "verao": {"nome": "Verão, linho e old money", "cor": "var(--orange)"}, "basicos": {"nome": "Básico premium e escala", "cor": "var(--blue)"},
          "mundo-resort": {"nome": "Mundo · resort e verão", "cor": "var(--teal)"}, "mundo-street": {"nome": "Mundo · streetwear e frase", "cor": "var(--indigo)"},
          "mundo-casual": {"nome": "Mundo · casual e básico", "cor": "var(--good)"}, "fora": {"nome": "Lá fora", "cor": "var(--teal)"}}
def regiao(g): return "mundo" if g.startswith("mundo") or g == "fora" else "br"
FORMATOS = {"video": "Vídeo", "imagem": "Imagem", "carrossel": "Carrossel"}
def an(i):
    p = f"analise/out/{i}.json"
    return json.load(open(p)) if os.path.exists(p) else {}
def fala(i):
    p = f"transcricoes/{i}.json"
    if not os.path.exists(p): return ""
    t = json.load(open(p)); segs = [s for s in t.get("segs", []) if s.get("nsp", 0) < 0.5 and s.get("lp", -9) > -1.0]
    txt = " ".join(s["t"] for s in segs).strip()
    return txt if len(txt.split()) >= 10 else ""
def limpa(t):
    t = re.sub(r"\s*\((?:[^)]*(?:legend|fala|estampa|na tela|sobreposto|rodapé|logo)[^)]*)\)", "", t or "")
    return t.strip(" ·/")
def dest(u):
    u = (u or "").lower()
    if not u: return ""
    if re.search(r"instagram\.com|facebook\.com|fb\.com|fb\.me|wa\.me|whatsapp|linktr", u): return "Instagram ou WhatsApp"
    if re.search(r"/products?/|/produtos?/|/p$|/p\?|/p/|-p\d|/item/", u): return "Página do produto"
    if re.search(r"/pages/|/lp\b|/lp/|landing|/kit|/oferta", u): return "Página de oferta ou kit"
    if re.match(r"https?://[^/]+/?(\?.*)?(#.*)?$", u): return "Home"
    return "Coleção ou categoria"
FAMILIA = {"Foto da peça no corpo": "Foto com modelo", "Foto editorial (campanha)": "Foto com modelo",
           "Foto still/packshot": "Foto só da peça (packshot)",
           "Vídeo da peça no corpo": "Vídeo com modelo", "Vídeo de clima (lifestyle)": "Vídeo com modelo",
           "Vídeo com fala (creator/UGC)": "Vídeo com fala (creator)",
           "Vídeo do produto (sem modelo)": "Vídeo sem modelo (peça, unboxing, bastidor)", "Vídeo POV/unboxing": "Vídeo sem modelo (peça, unboxing, bastidor)",
           "Vídeo de bastidor/produção": "Vídeo sem modelo (peça, unboxing, bastidor)",
           "Banner de oferta": "Arte de oferta ou texto", "Vídeo de oferta (banner animado)": "Arte de oferta ou texto", "Meme/texto na tela": "Arte de oferta ou texto",
           "Catálogo automático": "Catálogo e carrossel", "Carrossel de peças": "Catálogo e carrossel", "Carrossel editorial": "Catálogo e carrossel",
           "Collab/evento": "Collab ou evento"}
CUR = json.load(open("curadoria.json")) if os.path.exists("curadoria.json") else {}
EXC = set(CUR.get("excluir", []))
FEM = re.compile(r"feminin|\bsaia\b|vestido|biqu[ií]ni|\bmai[ôo]\b|cropped|lingerie|suti[ãa]|\bbody\b feminino|conjunto fitness|legging", re.I)
def feminino(x):
    if x.get("publico") == "feminino": return True
    if x.get("publico") in ("masculino", "unissex"): return False
    return bool(FEM.search(x.get("peca", "")))
ads = []
for e in S:
    if e["id"] in EXC: continue
    x = an(e["id"])
    if not x: continue  # sem análise (reposição de última hora) fica fora do acervo
    if feminino(x): continue
    fl = fala(e["id"]) if x.get("fala_util") else ""
    hook = (e.get("body") or "").strip().split("\n")[0][:160]
    ads.append(dict(id=e["id"], m=e["m"], d=e["d"], ini=e.get("start", ""), n=e.get("n", 1), fmt=e["fmt"], dur=e.get("dur", ""),
                    body=e.get("body", ""), card=e.get("card") or [], cta=e.get("cta", ""), url=e.get("url", ""), dom=e.get("dom", ""),
                    dest=dest(e.get("url")), th=e.get("th", ""), car=e.get("car") or [], vid=e.get("vid", ""), fala=fl, hook=hook,
                    score=e["score"], tags=x.get("angulos", []),
                    an={k: limpa(x.get(k, "")) if k == "texto" else x.get(k, "") for k in ("formato", "gancho", "texto", "cena", "peca", "oferta", "porque", "replicar")}))
RANK = json.load(open("ranking.json")) if os.path.exists("ranking.json") else []
ja = {a["id"] for a in ads}
for r in RANK:
    if r["id"] in ja or r["id"] in EXC: continue
    x = an(r["id"])
    if x and feminino(x): continue
    ads.append(dict(id=r["id"], m=r["m"], d=r["d"], ini=r.get("ini", ""), n=r.get("n", 1), fmt=r["fmt"], dur=r.get("dur", ""),
                    body=r.get("body", ""), card=r.get("card") or [], cta=r.get("cta", ""), url=r.get("url", ""), dom=dominio(r.get("url")),
                    dest=dest(r.get("url")), th=r.get("th", ""), car=[], vid=f"videos/{r['id']}.mp4" if os.path.exists(f"site/videos/{r['id']}.mp4") else "", fala="", hook=(r.get("body") or "").strip().split("\n")[0][:160],
                    score=r["esc"], tags=x.get("angulos", []) if x else [], so_rank=True,
                    an={k: limpa(x.get(k, "")) if k == "texto" else x.get(k, "") for k in ("formato", "gancho", "texto", "cena", "peca", "oferta", "porque", "replicar")} if x else {}))
ranking = [dict(id=r["id"], m=r["m"], reg=r["reg"], esc=r["esc"], d=r["d"], n=r.get("n", 1), fmt=r["fmt"], th=r.get("th", ""), body=(r.get("body") or "")[:200], card=(r.get("card") or [])[:3])
           for r in RANK if r["id"] not in EXC and any(a["id"] == r["id"] for a in ads)]
usadas = {a["m"] for a in ads}
VOLRX = re.compile(r"3 por 2|compre\s*\d|leve\s*\d|pague\s*\d|\bkit\b|\d\s*(overs|lisas|camisetas|peças)\s*por|pelo preço de 1|progressivo|a partir de 3|ganhe a 3", re.I)
VOLJ = set()
lojas = {}
for s, m in MM.items():
    if s not in usadas: continue
    lj = json.load(open(f"lojas/{s}.json")) if os.path.exists(f"lojas/{s}.json") else {}
    t = TL.get(s, {})
    if VOLRX.search(t.get("oferta", "")) or "3 por 2" in lj.get("ofertas", []): VOLJ.add(s)
    lojas[s] = dict(nome=m["nome"], grupo=m["grupo"], pid=m["pid"], pais=m.get("pais", "BR"), url=lj.get("final") or m.get("site", ""), dom=dominio(lj.get("final") or m.get("site", "")),
                    plataforma=lj.get("plataforma", ""), ig=(lj.get("instagram") or [""])[0], ativos=m.get("ativos", 0),
                    validados=m.get("n30", 0), maxd=m.get("maxd", 0), estilo=t.get("estilo", ""), preco=t.get("preco", ""),
                    oferta=t.get("oferta", ""), leitura=t.get("leitura", ""), print=lj.get("print", ""))
ordem = sorted(lojas, key=lambda s: (list(GRUPOS).index(lojas[s]["grupo"]), -lojas[s]["ativos"]))
lojas = {s: lojas[s] for s in ordem}
# top 12: maior score, no máx. 2 por loja, só BR
top, cnt = [], collections.Counter()
for a in sorted(ads, key=lambda a: -a["score"]):
    if regiao(lojas[a["m"]]["grupo"]) == "mundo" or a.get("so_rank") or cnt[a["m"]] >= 2: continue
    top.append(a["id"]); cnt[a["m"]] += 1
    if len(top) == 12: break
if CUR.get("top"): top = [i for i in CUR["top"] if any(a["id"] == i for a in ads)]
# top mundo: maior score, 1 por loja (ou curadoria top_mundo)
top_mu, vistos_mu = [], set()
for a in sorted([a for a in ads if not a.get("so_rank") and regiao(lojas[a["m"]]["grupo"]) == "mundo"], key=lambda a: -a["score"]):
    if a["m"] in vistos_mu: continue
    top_mu.append(a["id"]); vistos_mu.add(a["m"])
    if len(top_mu) == 12: break
if CUR.get("top_mundo"): top_mu = [i for i in CUR["top_mundo"] if any(a["id"] == i for a in ads)]
top = {"br": top, "mundo": top_mu}
# padrões e números por região (só criativos do acervo, não os que entram só no ranking)
def barra(t, d, pares, leitura, cor, N):
    itens = []
    for l, L in pares:
        if not L: continue
        md = int(statistics.median([a["d"] for a in L]))
        itens.append(dict(l=l, s=f"mediana de {md} dias no ar", n=len(L), pct=round(100 * len(L) / N), c=cor))
    return dict(t=t, d=d, itens=sorted(itens, key=lambda i: -i["n"]), leitura=leitura)
def ofertas(a):
    s = (a["body"] + " " + " ".join(a["card"]) + " " + a["an"].get("oferta", "") + " " + a["an"].get("texto", "")).lower()
    r = []
    if re.search(r"\b3\s*por\s*2\b|(compre|leve)\s*3\s*[\w\s]{0,25}?pague\s*(apenas\s*|s[oó]\s*)?2|compre\s*2\s*[\w\s]{0,15}?leve\s*3|leve\s*\d\s*pague\s*\d|\bkit\b|bundle|buy\s*\d|\d\s*for\s*[$£€]", s): r.append("Leve mais, pague menos (3 por 2, kit)")
    if re.search(r"frete\s*gr[aá]tis|free\s*(shipping|delivery)", s): r.append("Frete grátis")
    if re.search(r"\d{1,2}\s*%\s*(off|de desconto|desc)", s): r.append("Desconto em %")
    if re.search(r"cupom|c[oó]digo|\bcode\b|\buse\s+[A-Z0-9]{4,}", s): r.append("Cupom")
    if re.search(r"r\$\s?\d|[$£€]\s?\d", s): r.append("Preço à mostra")
    return r or ["Sem oferta"]
def med(L): return int(statistics.median([a["d"] for a in L])) if L else 0
def analisa(br, P):
    N = len(br) or 1
    pct = lambda n: round(100 * n / N)
    fm = collections.defaultdict(list)
    for a in br: fm[FAMILIA.get(a["an"].get("formato", ""), a["an"].get("formato") or FORMATOS[a["fmt"]])].append(a)
    ang = collections.defaultdict(list)
    for a in br:
        for t in a["tags"]: ang[t].append(a)
    of = collections.defaultdict(list)
    for a in br:
        for o in ofertas(a): of[o].append(a)
    de = collections.defaultdict(list)
    for a in br: de[a["dest"] or "Sem link"].append(a)
    dias = sorted(a["d"] for a in br) or [0]
    uni = [a for a in br if set(a["tags"]) & {"Verão & viagem", "Noite & drink", "Frase/atitude"}]
    NUM = dict(n_ads=len(br), med=med(br), max=max(dias),
               n_video=sum(1 for a in br if a["fmt"] == "video"), pct_video=pct(sum(1 for a in br if a["fmt"] == "video")),
               n_sem_oferta=len(of.get("Sem oferta", [])), pct_sem_oferta=pct(len(of.get("Sem oferta", []))), med_sem_oferta=med(of.get("Sem oferta", [])),
               n_volume=len(of.get("Leve mais, pague menos (3 por 2, kit)", [])), med_volume=med(of.get("Leve mais, pague menos (3 por 2, kit)", [])),
               pct_volume=pct(len(of.get("Leve mais, pague menos (3 por 2, kit)", []))),
               n_cupom=len(of.get("Cupom", [])), med_cupom=med(of.get("Cupom", [])), n_pct=len(of.get("Desconto em %", [])), med_pct=med(of.get("Desconto em %", [])),
               n_creator=len(fm.get("Vídeo com fala (creator)", [])), med_creator=med(fm.get("Vídeo com fala (creator)", [])),
               n_fotomod=len(fm.get("Foto com modelo", [])), med_fotomod=med(fm.get("Foto com modelo", [])),
               n_pack=len(fm.get("Foto só da peça (packshot)", [])), med_pack=med(fm.get("Foto só da peça (packshot)", [])),
               n_semmod=len(fm.get("Vídeo sem modelo (peça, unboxing, bastidor)", [])), med_semmod=med(fm.get("Vídeo sem modelo (peça, unboxing, bastidor)", [])),
               n_vidmod=len(fm.get("Vídeo com modelo", [])), med_vidmod=med(fm.get("Vídeo com modelo", [])),
               n_arte=len(fm.get("Arte de oferta ou texto", [])), med_arte=med(fm.get("Arte de oferta ou texto", [])),
               n_cat=len(fm.get("Catálogo e carrossel", [])), med_cat=med(fm.get("Catálogo e carrossel", [])),
               n_frase=len(ang.get("Frase/atitude", [])), med_frase=med(ang.get("Frase/atitude", [])),
               n_verao=len(ang.get("Verão & viagem", [])), med_verao=med(ang.get("Verão & viagem", [])),
               n_noite=len(ang.get("Noite & drink", [])), med_noite=med(ang.get("Noite & drink", [])),
               n_lanc=len(ang.get("Lançamento/drop", [])), med_lanc=med(ang.get("Lançamento/drop", [])),
               n_tecido=len(ang.get("Tecido & qualidade", [])), med_tecido=med(ang.get("Tecido & qualidade", [])),
               n_prova=len(ang.get("Prova social", [])), med_prova=med(ang.get("Prova social", [])),
               n_oferta_ang=len(ang.get("Oferta", [])), med_oferta_ang=med(ang.get("Oferta", [])),
               n_cria=len(ang.get("Creator/UGC", [])), med_cria=med(ang.get("Creator/UGC", [])),
               med_universo=med(uni), n_universo=len(uni),
               pct_produto=pct(len(de.get("Página do produto", []))), pct_colecao=pct(len(de.get("Coleção ou categoria", []))),
               pct_home=pct(len(de.get("Home", []))), pct_ig=pct(len(de.get("Instagram ou WhatsApp", []))))
    pad = [barra("Formato", "Como a peça é feita, agrupado em famílias.", fm.items(), P.get("formato", ""), "var(--blue)", N),
           barra("Ângulo", "Sobre o que o criativo fala. Um criativo pode ter mais de um.", ang.items(), P.get("angulo", ""), "var(--purple)", N),
           barra("Oferta", "Mecanismo comercial no texto ou na peça.", of.items(), P.get("oferta", ""), "var(--good)", N),
           barra("Destino do clique", "Pra onde o anúncio leva.", de.items(), P.get("destino", ""), "var(--warn)", N)]
    return pad, NUM
acervo = [a for a in ads if not a.get("so_rank")]
br = [a for a in acervo if regiao(lojas[a["m"]]["grupo"]) == "br"]
mu = [a for a in acervo if regiao(lojas[a["m"]]["grupo"]) == "mundo"]
pad_br, NUM = analisa(br, T.get("padroes", {}))
pad_mu, NUMM = analisa(mu, T.get("padroes_mundo", {}))
lojas_br = [s for s in lojas if regiao(lojas[s]["grupo"]) == "br"]; lojas_mu = [s for s in lojas if regiao(lojas[s]["grupo"]) == "mundo"]
NUM.update(n_lojas=len(lojas_br), n_lojas_mundo=len(lojas_mu), n_lojas_volume=len([s for s in VOLJ if s in lojas_br]))
NUM.update({"m_" + k: v for k, v in NUMM.items()})
NUM.update(n_rank=len(ranking), n_rank_br=len([r for r in ranking if r["reg"] == "br"]), n_rank_mu=len([r for r in ranking if r["reg"] == "mundo"]))
json.dump(NUM, open("numeros.json", "w"), ensure_ascii=False, indent=1)
fill = lambda s: s.format(**NUM) if isinstance(s, str) else s
for p in pad_br + pad_mu: p["leitura"] = fill(p["leitura"])
padroes = {"br": pad_br, "mundo": pad_mu}
meta = {k: fill(v) for k, v in T["meta"].items()}
todos = sorted(a["d"] for a in acervo) or [0]
meta["stats"] = [[str(len(lojas_br)), "lojas no Brasil"], [str(len(lojas_mu)), "lojas no mundo"],
                 [str(len(acervo)), "criativos validados e analisados"], [str(max(todos)), "dias, o mais antigo ainda no ar"]]
# ---- camiseta estampada · mundo: busca por termo em várias línguas; só entra o que a análise confirmou como camiseta estampada
EST_SEL = [a for f in ("estampa/sel.json", "estampa/sel2.json") if os.path.exists(f) for a in json.load(open(f))]
EST_M = {m["slug"]: m for m in json.load(open("estampa/marcas.json"))} if os.path.exists("estampa/marcas.json") else {}
EST_Q = [l.strip() for l in open("q_estampa.txt") if l.strip() and not l.startswith("#")] if os.path.exists("q_estampa.txt") else []
EST_CAP = 6
ja_ids = {a["id"] for a in ads}
est_ads, est_cnt = [], collections.Counter()
from PIL import Image
def ahash_th(p):
    try:
        im = Image.open("site/" + p).convert("L").resize((16, 16)); px = list(im.getdata()); m = sum(px) / len(px)
        return int("".join("1" if x > m else "0" for x in px), 2)
    except Exception: return None
est_hash = collections.defaultdict(list)  # mesma arte com outro id (1ª e 2ª rodada) entra uma vez só
for e in sorted(EST_SEL, key=lambda e: -e["score"]):
    if e["id"] in EXC or e["id"] in ja_ids or est_cnt[e["m"]] >= EST_CAP or not e.get("th") or not os.path.exists("site/" + e["th"]): continue
    x = an(e["id"])
    if not x or x.get("estampada") is not True or feminino(x): continue
    h = ahash_th(e["th"])
    if h is not None and any(bin(h ^ o).count("1") <= 6 for o in est_hash[e["m"]]): continue
    if h is not None: est_hash[e["m"]].append(h)
    est_cnt[e["m"]] += 1
    est_ads.append(dict(id=e["id"], m=e["m"], d=e["d"], ini=e.get("start", ""), n=e.get("n", 1), fmt=e["fmt"], dur=e.get("dur", ""),
                        body=e.get("body", ""), card=e.get("card") or [], cta=e.get("cta", ""), url=e.get("url", ""), dom=e.get("dom", ""),
                        dest=dest(e.get("url")), th=e.get("th", ""), car=e.get("car") or [], vid=e.get("vid", ""), fala=fala(e["id"]) if x.get("fala_util") else "",
                        hook=(e.get("body") or "").strip().split("\n")[0][:160], score=e["score"], tags=x.get("angulos", []), est=1,
                        an={k: limpa(x.get(k, "")) if k == "texto" else x.get(k, "") for k in ("formato", "gancho", "texto", "cena", "peca", "oferta", "porque", "replicar", "estampa", "tipo_estampa", "lugar_estampa")}))
nome_loja = lambda n: re.sub(r"^.+? com (?=\S)", "", n) if " com " in n else n  # anúncio em parceria: "Criador com Marca"
est_lojas = {s: dict(nome=nome_loja(m["nome"]), grupo="estampa", pid=m["pid"], pais="ALL", url=m.get("site", ""), dom=dominio(m.get("site", "")), ativos=m.get("ativos") or 0) for s, m in EST_M.items() if est_cnt[s]}
def leitura_mais(pares, minimo=5):
    ok = [(l, int(statistics.median([a["d"] for a in L])), len(L)) for l, L in pares if len(L) >= minimo]
    if not ok: return ""
    l, md, n = max(ok, key=lambda t: t[1])
    return f"Dura mais: {l.lower()}, mediana de {md} dias no ar ({n} criativos)."
est = None
if est_ads:
    NE = len(est_ads)
    tipo, lugar, fam = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
    for a in est_ads:
        tipo[a["an"].get("tipo_estampa") or "Outra"].append(a)
        if a["an"].get("lugar_estampa"): lugar[a["an"]["lugar_estampa"].capitalize()].append(a)
        fam[FAMILIA.get(a["an"].get("formato"), a["an"].get("formato") or "Outro")].append(a)
    est_pad = [barra("Tipo de estampa", "O que está estampado na camiseta.", tipo.items(), leitura_mais(tipo.items()), "var(--orange)", NE),
               barra("Onde fica a estampa", "Frente, costas ou os dois.", lugar.items(), leitura_mais(lugar.items()), "var(--blue)", NE),
               barra("Formato do anúncio", "Como a camiseta aparece, agrupado em famílias.", fam.items(), leitura_mais(fam.items()), "var(--purple)", NE)]
    est = dict(sub=f"Busca por {len(EST_Q)} termos em 13 línguas na Biblioteca de Anúncios, só anúncio ativo que já rodava em 27/08. "
                   f"Cada criativo foi conferido um a um: só entra camiseta com estampa (frase, arte, logo grande), peça masculina ou unissex, "
                   f"levando pro site da loja. No máximo {EST_CAP} por loja.",
               stats=[[str(len(est_lojas)), "lojas no mundo"], [str(NE), "criativos de camiseta estampada"],
                      [str(max(a["d"] for a in est_ads)), "dias, o mais antigo ainda no ar"], [str(int(statistics.median([a["d"] for a in est_ads]))), "dias no ar, a mediana"]],
               padroes=est_pad, lojas=est_lojas,
               lista=sorted([dict(k=s, nome=l["nome"], dom=l["dom"], ativos=l["ativos"], n=est_cnt[s], maxd=max(a["d"] for a in est_ads if a["m"] == s)) for s, l in est_lojas.items()],
                            key=lambda l: (-l["n"], -l["maxd"])))
est_resumo = []
if est_ads:
    t_tipo = max([(l, int(statistics.median([a["d"] for a in L])), len(L)) for l, L in tipo.items() if len(L) >= 5] or [("", 0, 0)], key=lambda t: t[1])
    velhos = [a["id"] for a in sorted(est_ads, key=lambda a: -a["d"])[:3]]
    est_resumo = [dict(t=f"<b>Camiseta estampada no mundo:</b> {len(est_ads)} criativos de {len(est_lojas)} lojas, todos há 30+ dias no ar (mediana de {int(statistics.median([a['d'] for a in est_ads]))} dias)."
                         + (f" A estampa que mais dura é {t_tipo[0].lower()}: mediana de {t_tipo[1]} dias." if t_tipo[0] else "") + " Os 3 mais antigos:", refs=velhos)]
data = dict(meta=meta, grupos=dict(GRUPOS, estampa={"nome": "Camiseta estampada · mundo", "cor": "var(--orange)"}), formatos=FORMATOS, lojas=lojas, ads=ads + est_ads, top=top, padroes=padroes, ranking=ranking, est=est,
            resumo=[dict(r, t=fill(r["t"])) for r in T.get("resumo", [])] + est_resumo, replicar=T.get("replicar", []), frases=T.get("frases", []), metodo=T.get("metodo", []), video=True)
html = open("template.html").read().replace("/*DATA*/", "const DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")
open("site/index.html", "w").write(html)
print("ok", len(acervo), "no acervo +", len(ads) - len(acervo), "só no ranking |", len(lojas_br), "lojas BR,", len(lojas_mu), "mundo |", os.path.getsize("site/index.html") // 1024, "kb")

# ---- swipe (aba estilo Tinder): acervo + ranking, do mais escalado pro menos, sem a mesma loja em sequência
def escala(d, n): return round(d * (1 + 0.15 * min(max(n - 1, 0), 10)), 1)
# ---- estilo Balddoria (só no swipe): criativos validados das lojas do universo dela com nota de parecido >= 7
bd_ads = []
if os.path.exists("balddoria/sel.json"):
    ja_sw = {a["id"] for a in ads + est_ads}
    hs = collections.defaultdict(list)
    for a in ads + est_ads:
        h = ahash_th(a["th"]) if a.get("th") else None
        if h is not None: hs[a["m"]].append(h)
    for e in sorted(json.load(open("balddoria/sel.json")), key=lambda e: -e["score"]):
        p = f"analise/out_b/{e['id']}.json"
        if e["id"] in EXC or e["id"] in ja_sw or not os.path.exists(p) or not e.get("th") or not os.path.exists("site/" + e["th"]): continue
        try: x = json.load(open(p))
        except Exception: continue
        if int(x.get("parecido") or 0) < 7 or x.get("publico") == "feminino": continue
        h = ahash_th(e["th"])
        if h is not None and any(bin(h ^ o).count("1") <= 6 for o in hs[e["m"]]): continue
        if h is not None: hs[e["m"]].append(h)
        bd_ads.append(dict(id=e["id"], m=e["m"], d=e["d"], n=e.get("n", 1), fmt=e["fmt"], th=e["th"], vid=e.get("vid", ""), car=e.get("car") or [],
                           dest=dest(e.get("url")), url=e.get("url", ""), body=e.get("body", ""), bd=1, pais=MM.get(e["m"], {}).get("pais", "BR"),
                           an={k: x.get(k, "") for k in ("formato", "gancho", "texto", "cena", "peca", "oferta", "porque", "replicar", "estampa", "motivo") if x.get(k)}))
    print("estilo Balddoria:", len(bd_ads), "criativos com parecido >= 7 de", len({a["m"] for a in bd_ads}), "lojas")
# ---- lojas parecidas com a Balddoria (só no swipe): até 15 criativos por loja, ligados há 10+ dias
lb_lojas = {l["slug"]: l for l in json.load(open("balddoria/lojas_escolhidas.json"))} if os.path.exists("balddoria/lojas_escolhidas.json") else {}
lb_ads = []
if lb_lojas and os.path.exists("balddoria/lojas_sel.json"):
    ja_sw = {a["id"] for a in ads + est_ads + bd_ads}
    hs = collections.defaultdict(list); cnt = collections.Counter()
    for a in ads + est_ads + bd_ads:
        if a["m"] in lb_lojas:
            cnt[a["m"]] += 1
            h = ahash_th(a["th"]) if a.get("th") else None
            if h is not None: hs[a["m"]].append(h)
    for e in sorted(json.load(open("balddoria/lojas_sel.json")), key=lambda e: -e["score"]):
        if e["id"] in EXC or e["id"] in ja_sw or cnt[e["m"]] >= 15 or not e.get("th") or not os.path.exists("site/" + e["th"]): continue
        h = ahash_th(e["th"])
        if h is not None and any(bin(h ^ o).count("1") <= 6 for o in hs[e["m"]]): continue
        if h is not None: hs[e["m"]].append(h)
        cnt[e["m"]] += 1; ja_sw.add(e["id"])
        lb_ads.append(dict(id=e["id"], m=e["m"], d=e["d"], n=e.get("n", 1), fmt=e["fmt"], th=e["th"], vid=e.get("vid", ""), car=e.get("car") or [],
                           dest=dest(e.get("url")), url=e.get("url", ""), body=e.get("body", ""), lb=1, pais=lb_lojas[e["m"]].get("pais", "BR"), an={}))
    print("lojas tipo Balddoria:", len(lb_lojas), "lojas |", len(lb_ads), "criativos novos no swipe |", sum(1 for s in lb_lojas if cnt[s] >= 10), "lojas com 10+ criativos")
# ---- lojas tipo Frased / By Someone's Diary (só no swipe): até 10 criativos por loja, ligados há 10+ dias
fr_lojas = {l["slug"]: l for l in json.load(open("balddoria/fr_lojas.json"))} if os.path.exists("balddoria/fr_lojas.json") else {}
fr_ads = []
if fr_lojas and os.path.exists("balddoria/fr_sel.json"):
    ja_sw = {a["id"] for a in ads + est_ads + bd_ads + lb_ads}
    hs = collections.defaultdict(list); cnt = collections.Counter()
    for e in sorted(json.load(open("balddoria/fr_sel.json")), key=lambda e: -e["score"]):
        if e["id"] in EXC or e["id"] in ja_sw or cnt[e["m"]] >= 10 or not e.get("th") or not os.path.exists("site/" + e["th"]): continue
        h = ahash_th(e["th"])
        if h is not None and any(bin(h ^ o).count("1") <= 6 for o in hs[e["m"]]): continue
        if h is not None: hs[e["m"]].append(h)
        cnt[e["m"]] += 1; ja_sw.add(e["id"])
        fr_ads.append(dict(id=e["id"], m=e["m"], d=e["d"], n=e.get("n", 1), fmt=e["fmt"], th=e["th"], vid=e.get("vid", ""), car=e.get("car") or [],
                           dest=dest(e.get("url")), url=e.get("url", ""), dom=e.get("dom", ""), body=e.get("body", ""), fr=1, an={}))
    print("lojas tipo Frased:", sum(1 for s in fr_lojas if cnt[s]), "lojas com criativo |", len(fr_ads), "criativos |", sum(1 for s in fr_lojas if cnt[s] >= 10), "lojas com 10")
pool = sorted(ads + est_ads + bd_ads + lb_ads + fr_ads, key=lambda a: (-escala(a["d"], a["n"]), a["id"]))
ordem = []
while pool:
    rec = [o["m"] for o in ordem[-2:]]
    k = next((i for i, a in enumerate(pool[:15]) if a["m"] not in rec), 0)
    ordem.append(pool.pop(k))
reg_sw = lambda a: ("br" if a.get("dom", "").endswith(".br") else "mu") if a.get("fr") else ("mu" if a.get("pais") == "ALL" else "br") if (a.get("bd") or a.get("lb")) else ("br" if a.get("dom", "").endswith(".br") else "mu") if a.get("est") else ("br" if regiao(lojas[a["m"]]["grupo"]) == "br" else "mu")
def nota_b(i):  # nota de parecido com a Balddoria (analise/out_b), também pros criativos que já estavam no swipe
    p = f"analise/out_b/{i}.json"
    if not os.path.exists(p): return None
    try: x = json.load(open(p))
    except Exception: return None
    return x if int(x.get("parecido") or 0) >= 7 and x.get("publico") != "feminino" else None
def an_sw(a):
    d = {k: v for k, v in (a.get("an") or {}).items() if v}
    x = nota_b(a["id"])
    if x and x.get("motivo"): d["motivo"] = x["motivo"]
    return d
itens = [dict(id=a["id"], m=a["m"], r=reg_sw(a), e=1 if a.get("est") else 0, bd=1 if (a.get("bd") or nota_b(a["id"])) else 0, lb=1 if (a.get("lb") or a["m"] in lb_lojas) else 0, fr=1 if a.get("fr") else 0, d=a["d"], n=a["n"], f=a["fmt"], th=a["th"], v=a["vid"],
              c=a["car"], dest=a["dest"], url=a["url"], b=(a["body"] or "").strip()[:500], an=an_sw(a)) for a in ordem]
print("filtro Estilo Balddoria no swipe:", sum(1 for x in itens if x["bd"]), "criativos (", sum(1 for x in itens if x["bd"] and not any(a["id"] == x["id"] for a in bd_ads)), "já estavam no swipe )")
lj = {s: dict(n=l["nome"], u=l.get("url", "")) for s, l in list(lojas.items()) + list(est_lojas.items())}
for s, l in fr_lojas.items():
    if s not in lj: lj[s] = dict(n=l["nome"], u="https://" + l.get("dom", "") if l.get("dom") else "")
for s, l in lb_lojas.items():
    if s not in lj: lj[s] = dict(n=l["nome"], u=l.get("site", ""))
for a in bd_ads:
    if a["m"] not in lj: lj[a["m"]] = dict(n=MM.get(a["m"], {}).get("nome", a["m"]), u=MM.get(a["m"], {}).get("site", ""))
os.makedirs("site/swipe", exist_ok=True)
blob = json.dumps(dict(items=itens, lojas=lj), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
open("site/swipe/index.html", "w").write(open("template_swipe.html").read().replace("/*DATA*/", "const D=" + blob + ";"))
json.dump([a["id"] for a in itens], open("site/swipe/ids.json", "w"))
print("swipe", len(itens), "criativos (", sum(1 for a in itens if a["r"] == "br"), "BR ) |", sum(1 for a in itens if a["v"]), "vídeos |", os.path.getsize("site/swipe/index.html") // 1024, "kb")
