"""Lojas tipo Frased / By Someone's Diary -> criativos pro swipe (até K por loja, ligados há 10+ dias).
Passo 1 (FASE=alvos): escolhe as lojas (nota de loja em analise/lojas_fr >= NOTA_MIN, mais as duas referências) e grava os alvos da varredura.
Passo 2 (FASE=sel):   lê paginas/ALL-<slug>--10d.json e grava balddoria/fr_sel.json + balddoria/fr_lojas.json.
uso: FASE=alvos NOTA_MIN=5 N_LOJAS=60 python3 fr_monta.py ; (varre) ; FASE=sel K=10 python3 fr_monta.py"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio
FASE = os.environ.get("FASE", "sel"); NOTA_MIN = int(os.environ.get("NOTA_MIN", "5")); N_LOJAS = int(os.environ.get("N_LOJAS", "60")); K = int(os.environ.get("K", "10"))
C = {c["slug"]: c for f in ("balddoria/fr_cand.json", "balddoria/fr_cand2.json") if os.path.exists(f) for c in json.load(open(f))}
REFS = {"frased-com": dict(slug="frased-com", nome="Frased", dom="frased.com", nota=10, motivo="referência que você mandou (@frased.unfiltered)"),
        "bysomeonesdiary-com": dict(slug="bysomeonesdiary-com", nome="By Someone's Diary", dom="bysomeonesdiary.com", nota=10, motivo="referência que você mandou (@bysomeonesdiary)")}
if FASE == "alvos":
    # pid das referências: a página mais comum nos anúncios que levam pro domínio delas
    import collections
    arq = lambda q: re.sub(r"[^a-z0-9]+", "-", q.lower().replace('"', ''))[:60].strip("-")
    for r in REFS.values():
        cnt = collections.Counter()
        for q in ['frased unfiltered', '"frased"', 'someones diary', "\"someone's diary\"", 'bysomeonesdiary']:
            f = f"busca/ALL-{arq(q)}.json"
            if os.path.exists(f):
                for a in json.load(open(f))["ads"]:
                    if r["dom"] in dominio(a.get("url")) and " com " not in a.get("page", ""): cnt[a.get("pid")] += 1
        r["pid"] = cnt.most_common(1)[0][0] if cnt else ""
    notas = []
    for f in glob.glob("analise/lojas_fr/*.json"):
        try: x = json.load(open(f))
        except Exception: continue
        c = C.get(x["slug"])
        if c and int(x.get("parecida") or 0) >= NOTA_MIN: notas.append(dict(c, nota=int(x["parecida"]), motivo=x.get("motivo", ""), vende=x.get("o_que_vende", "")))
    notas.sort(key=lambda c: (-c["nota"], -c["n"]))
    lojas = list(REFS.values()) + notas[:N_LOJAS]
    json.dump(lojas, open("balddoria/fr_lojas.json", "w"), ensure_ascii=False, indent=1)
    json.dump([dict(slug=l["slug"] + "--10d", pid=l["pid"]) for l in lojas if l.get("pid")], open("balddoria/fr_alvos.json", "w"))
    print("lojas escolhidas:", len(lojas), "| notas:", [l["nota"] for l in lojas])
    sys.exit()
JA = set(json.load(open("site/swipe/ids.json"))) | set(json.load(open("curadoria.json"))["excluir"])
FEM = re.compile(r"\bwom[ae]n'?s?\b|\bladies\b|feminin|damen|femme|mujer|cropped|baby ?tee|\bdress\b|\bkids?\b|toddler|infant|baby\b", re.I)
NAO = re.compile(r"\bpants\b|shorts\b|\bcaps?\b|\bhats?\b|sneaker|socks|\bmugs?\b|poster|sticker|necklace|bracelet|\brings?\b|jewel|bag\b|\bcal[çc]a|\bbon[ée]", re.I)
B2B = re.compile(r"wholesale|bulk|print on demand|start your|reseller|atacado|revenda", re.I)
lojas = json.load(open("balddoria/fr_lojas.json")); sel = []
for l in lojas:
    f = f"paginas/ALL-{l['slug']}--10d.json"
    if not os.path.exists(f): l["novos"] = 0; continue
    cand = []
    for pos, a in enumerate(json.load(open(f)).get("ads", [])):
        dd = dias(a.get("start"))
        if dd is None or dd < 10 or a["id"] in JA or not a.get("ativo", True): continue
        tit = (a.get("card") or ["", ""])[1] if len(a.get("card") or []) > 1 else ""
        t = " ".join([a.get("body") or "", *(a.get("card") or [])])
        if FEM.search(tit) or NAO.search(tit) or B2B.search(t): continue
        cand.append(dict(a, m=l["slug"], d=dd, pos=pos, dom=dominio(a.get("url")), score=dd + 12 * min(max(a.get("n", 1) - 1, 0), 10) + max(0, 60 - pos) * 2))
    esc = sorted(cand, key=lambda a: -a["score"])[:K + 4]  # sobra pra dedupe
    l["novos"] = len(esc); sel += esc
json.dump(lojas, open("balddoria/fr_lojas.json", "w"), ensure_ascii=False, indent=1)
json.dump(sel, open("balddoria/fr_sel.json", "w"), ensure_ascii=False)
print("criativos pra baixar:", len(sel), "| lojas com 10+:", sum(1 for l in lojas if l.get("novos", 0) >= K), "de", len(lojas))
