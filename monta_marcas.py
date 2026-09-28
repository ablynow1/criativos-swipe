"""seeds.json + descobertas*.json + fora.json + web (pids_web.json/marcas_web.json) -> marcas.json"""
import json, os, re, unicodedata
def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
GRP = {"par": "street", "escala": "basicos"}  # seeds antigos
FORA_DO_UNIVERSO = {"youccie", "sacudido-s", "gangster", "colcci", "youcom", "ellus", "cavalera", "john-john", "quadro-creations", "011", "hausport", "alpha-co", "andre-ferran", "pano", "business-pleasure-co"}  # + tênis/multimarca, fitness, dropshipping gringo  # infantil, sertanejo, feminino/massa, liquidação
GRUPO_FIXO = {"oriba": "verao", "jouse": "basicos", "minimal-club": "basicos", "urban-basics": "basicos", "alpha-co": "basicos",
              "insider": "basicos", "handred": "verao", "eayz-basic": "basicos", "wolfield-rio": "basicos", "richards": "verao", "foxton": "verao", "sage-brazil": "verao", "chico-rei": "street", "cava": "basicos", "origgo": "basicos", "oka-basics": "basicos"}
out, vistos = [], set()
for f in ["seeds.json", "descobertas.json", "descobertas2.json", "descobertas3.json", "descobertas4.json", "descobertas5.json", "mundo_conhecidas.json", "mundo_descobertas.json", "mundo_descobertas2.json"]:
    if not os.path.exists(f): continue
    for m in json.load(open(f)):
        if m["pid"] in vistos: continue
        vistos.add(m["pid"]); g = GRP.get(m["grupo"], m["grupo"])
        if slug(m["nome"]) in FORA_DO_UNIVERSO: continue
        g = GRUPO_FIXO.get(slug(m["nome"]), g)
        out.append(dict(nome=m["nome"], slug=slug(m["nome"]), pid=m["pid"], grupo=g, pais=m.get("pais", "BR"), site=m.get("site", "")))
json.dump(out, open("marcas.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "marcas")
