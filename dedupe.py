"""Depois do baixa.py: tira criativo repetido (mesmo vídeo ou mesma imagem) dentro da loja e corta no teto por grupo.
Mantém o de maior score e soma as variações."""
import json, os, hashlib, collections
from PIL import Image
S = json.load(open(os.environ.get("SEL", "selecionados.json"))); M = {m["slug"]: m for m in json.load(open(os.environ.get("MARCAS", "marcas.json")))}
CAP = {"ref": 14, "street": 7, "verao": 7, "basicos": 5, "fora": 4, "mundo-resort": 4, "mundo-street": 4, "mundo-casual": 4, "estampa": int(os.environ.get("CAP_ESTAMPA", "6"))}
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def ahash(p):
    try:
        im = Image.open(p).convert("L").resize((16, 16)); px = list(im.getdata()); m = sum(px) / len(px)
        return int("".join("1" if x > m else "0" for x in px), 2)
    except Exception: return None
por = collections.defaultdict(list)
for e in sorted(S, key=lambda e: -e["score"]): por[e["m"]].append(e)
out, cortados = [], 0
for s, L in por.items():
    fica = []
    for e in L:
        v = f"midia/{e['id']}.mp4"; t = f"midia/{e['id']}.jpg"
        e["_md5"] = md5(v) if os.path.exists(v) else None; e["_ah"] = ahash(t) if os.path.exists(t) else None
        dup = None
        for f in fica:
            if e["_md5"] and e["_md5"] == f["_md5"]: dup = f; break
            if e["_ah"] is not None and f["_ah"] is not None and bin(e["_ah"] ^ f["_ah"]).count("1") <= 6 and (e["fmt"] == f["fmt"]): dup = f; break
        if dup: dup["n"] = dup.get("n", 1) + e.get("n", 1); dup.setdefault("dups", []).append(e["id"]); cortados += 1; continue
        fica.append(e)
    out += fica[:CAP.get(M.get(s, {}).get("grupo", ""), 6)]
for e in out: e.pop("_md5", None); e.pop("_ah", None)
json.dump(out, open(os.environ.get("SEL", "selecionados.json"), "w"), ensure_ascii=False)
print("repetidos cortados:", cortados, "| ficam", len(out), "em", len({e['m'] for e in out}), "lojas")
