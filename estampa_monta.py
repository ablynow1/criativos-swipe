"""Camiseta estampada no mundo: busca/ALL-*.json (termos de q_estampa.txt, só anúncio ativo que já rodava em 27/08)
-> estampa/sel.json (criativos pra baixar e analisar) + estampa/marcas.json (lojas) + estampa/lojas_rank.json (diagnóstico).
Loja entra pela soma dos melhores criativos (dias no ar, variações, posição por impressões) e por quantas buscas diferentes ela aparece.
uso: N_LOJAS=70 K=8 python3 estampa_monta.py"""
import json, os, re, sys, unicodedata, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias, dominio
N_LOJAS = int(os.environ.get("N_LOJAS", "70")); K = int(os.environ.get("K", "8"))
os.makedirs("estampa", exist_ok=True)
def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "loja"
arq = lambda q: re.sub(r"[^a-z0-9]+", "-", q.lower().replace('"', ''))[:60].strip("-")
Q = [l.strip() for l in open("q_estampa.txt") if l.strip() and not l.startswith("#")]
JA = set(json.load(open("site/swipe/ids.json"))) | set(json.load(open("curadoria.json")).get("excluir", []))
MARKET = re.compile(r"amazon|temu|shein|aliexpress|alibaba|etsy|ebay|mercado ?livre|mercado ?libre|shopee|walmart|target|redbubble|teepublic|"
                    r"spreadshirt|printful|printify|teespring|spring\.com|bonfire|gelato|placeit|canva|zazzle|cafepress|society6|threadless|tiktok shop|wish\b|"
                    r"whatnot|lightinthebox|\blitb\b|ajio|myntra|flipkart|meesho|tatacliq|nykaa|zalando|asos|boohoo|costco|kohls|macys|nordstrom|dhgate|joom|lazada|tokopedia|rakuten|zozo", re.I)
B2B = re.compile(r"custom (t-?shirts?|tees?|print|apparel)|print on demand|\bpod\b|\bdtf\b|wholesale|blank (t-?shirts?|tees?)|bulk order|your (own )?(design|logo)|"
                 r"personaliz|atacado|revenda|lojista|sublima|estamparia|serigraf|print shop|printing (service|company)|heat press|screen printing (service|business|equipment)|"
                 r"start (your|a) (clothing|t-?shirt) (brand|business)|clothing brand course|mockup", re.I)
FEM = re.compile(r"\bwom[ae]n'?s?\b|\bladies\b|\bmujer(es)?\b|\bdamen\b|\bfemme\b|\bdonna\b|feminin|\bgirls?\b|\bbaby ?look\b|cropped", re.I)
OUTRO = re.compile(r"\bhoodies?\b|sweatshirt|moletom|\bmugs?\b|\bposters?\b|stickers?|\bcaps?\b|\bhats?\b|sneakers?|\bshoes?\b|\bdress(es)?\b|leggings?|\bsocks?\b|jewel|\brings?\b", re.I)
FORA = re.compile(r"personali|prezent|g[åa]vor|\bgifts?\b|geschenk|regalo|cadeau|name ?wear|design f[öo]r dig|aquilase|gekketee|eprezenty|tinkigift|market ?sale|"
                  r"\bkids?\b|\bbaby\b|infant|[çc]ocuk|firstcry|enfant|kinder|toddler|crian[çc]a|"
                  r"jolies|floral|kitten|bosom|zizzi|anthropologie|farm ?rio|adoro farm|\bwomen|ladies|\bgirls?\b|mujer|femme|donna|damen|"
                  r"h&m|hm\.com|primark|lefties|jumia|\bn11\b|new ?era|eddie bauer|school|academy|business|equipment|supplement|muscleblaze|discounter|"
                  r"cod24|form\.id|shp\.ee|app\.link|\bpresent\b|lingerie|trendyol|university|vistaprint|amaframe", re.I)
TEE = re.compile(r"t-?shirts?|\btees?\b|camiset|remera|playera|maglie|koszul|ti[sş][oö]rt|\bkaos\b|tシャツ|티셔츠|tr[oö]ja|\btryck|\bshirts?\b", re.I)
lojas = collections.defaultdict(lambda: {"ads": {}, "qs": set(), "doms": collections.Counter(), "nomes": collections.Counter(), "pids": collections.Counter()})
vistos = 0
for q in Q:
    f = f"busca/ALL-{arq(q)}.json"
    if not os.path.exists(f): continue
    d = json.load(open(f))
    for pos, a in enumerate(d.get("ads", [])):
        vistos += 1
        dd = dias(a.get("start"))
        if not a.get("ativo", True) or dd is None or dd < 30 or a["id"] in JA: continue
        texto = " ".join([a.get("body") or "", *(a.get("card") or [])])
        titulo = (a.get("card") or ["", ""])[1] if len(a.get("card") or []) > 1 else ""
        if MARKET.search(a.get("page", "")) or MARKET.search(dominio(a.get("url"))) or B2B.search(texto): continue
        if FORA.search(a.get("page", "")) or FORA.search(dominio(a.get("url"))): continue
        if not dominio(a.get("url")) or re.search(r"instagram\.com|facebook\.com|fb\.(com|me)|wa\.me|whatsapp|linktr|apple\.com|play\.google|apps\.apple|t\.me|tiktok\.com", a.get("url") or "", re.I): continue
        if FEM.search(titulo) or (FEM.search(a.get("body") or "") and not re.search(r"\bm[ae]n'?s?\b|hombre|herren|homme|uomo|masculin", texto, re.I)): continue
        if OUTRO.search(titulo) and not TEE.search(titulo): continue
        s = slug(re.sub(r"^(www\d?|shop|store|loja|tienda|m)\.", "", dominio(a.get("url"))))  # a mesma loja roda várias páginas: agrupa pelo domínio
        L = lojas[s]; L["nomes"][a.get("page", "")] += 1; L["pids"][a.get("pid", "")] += 1; L["qs"].add(q)
        if dominio(a.get("url")): L["doms"][dominio(a.get("url"))] += 1
        sc = dd + 12 * min(max(a.get("n", 1) - 1, 0), 10) + max(0, 60 - pos) + (15 if TEE.search(texto) else 0)
        velho = L["ads"].get(a["id"])
        if not velho or sc > velho["score"]:
            L["ads"][a["id"]] = dict(a, m=s, d=dd, pos=pos, dom=dominio(a.get("url")), score=sc, q=q)
rank = []
for s, L in lojas.items():
    ads = sorted(L["ads"].values(), key=lambda a: -a["score"])
    if not ads: continue
    ls = sum(a["score"] for a in ads[:3]) + 15 * len(L["qs"]) + 5 * min(len(ads), 10)
    rank.append(dict(slug=s, nome=L["nomes"].most_common(1)[0][0], pid=L["pids"].most_common(1)[0][0], paginas=len(L["nomes"]), n=len(ads), qs=sorted(L["qs"]), dom=(L["doms"].most_common(1) or [("", 0)])[0][0], score=ls, maxd=max(a["d"] for a in ads)))
rank.sort(key=lambda r: -r["score"])
json.dump(rank, open("estampa/lojas_rank.json", "w"), ensure_ascii=False, indent=1)
top = rank[:N_LOJAS]
sel = [a for r in top for a in sorted(lojas[r["slug"]]["ads"].values(), key=lambda a: -a["score"])[:K]]
marcas = [dict(slug=r["slug"], nome=r["nome"], pid=r["pid"], grupo="estampa", pais="ALL", site=("https://" + r["dom"]) if r["dom"] else "", n_busca=r["n"], maxd=r["maxd"], buscas=r["qs"]) for r in top]
json.dump(sel, open("estampa/sel.json", "w"), ensure_ascii=False)
json.dump(marcas, open("estampa/marcas.json", "w"), ensure_ascii=False, indent=1)
print(f"cards lidos {vistos} | lojas com criativo 30d+ {len(rank)} | escolhidas {len(top)} | criativos pra baixar {len(sel)} "
      f"({sum(1 for a in sel if a['fmt']=='video')} vídeos)")
for r in top[:25]: print(f"  {r['nome'][:28]:28} {r['dom'][:26]:26} {r['n']:3} criativos · {len(r['qs'])} buscas · {r['maxd']}d")
