"""Folha por loja (8 criativos 30d+ mais vistos, em grade 4x2 com o nome) pra nota de loja parecida com a Balddoria.
uso: python3 bd_folhas.py balddoria/cand_lojas.json  -> analise/folhas_lojas/<slug>.jpg"""
import json, os, re, sys, subprocess, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import dias
from PIL import Image, ImageDraw, ImageFont
C = json.load(open(sys.argv[1])); os.makedirs("analise/folhas_lojas", exist_ok=True); os.makedirs("midia/lojas_bd", exist_ok=True)
NAO = re.compile(r"\bcal[çc]a|bermuda|\bshorts?\b|\bbon[ée]\b|t[êe]nis|\bmeias?\b|cueca|sand[áa]lia|chinelo|perfume|[óo]culos|bolsa|mochila|pants|\bcaps?\b|sneaker|socks", re.I)
def pagina(c):
    for p in ([c.get("pais")] if c.get("pais") else []) + ["BR", "ALL"]:
        f = f"paginas/{p}-{c['slug']}.json"
        if os.path.exists(f): return json.load(open(f))
    return None
def get(u, p):
    if os.path.exists(p) and os.path.getsize(p) > 2000: return p
    subprocess.run(["curl", "-sL", "--max-time", "60", "-A", "Mozilla/5.0", "-o", p, u])
    return p if os.path.exists(p) and os.path.getsize(p) > 2000 else None
try: F = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
except Exception: F = ImageFont.load_default()
def folha(c):
    d = pagina(c)
    if not d: return c["slug"], 0
    ads = [a for a in d.get("ads", []) if (dias(a.get("start")) or 0) >= 30]
    ads = [a for a in ads if not NAO.search(" ".join((a.get("card") or [])[1:2]))][:8]
    ims = []
    for k, a in enumerate(ads):
        u = a.get("poster") or (a.get("imgs") or [""])[0]
        if u:
            p = get(u, f"midia/lojas_bd/{c['slug']}_{k}.jpg")
            if p:
                try: ims.append(Image.open(p).convert("RGB"))
                except Exception: pass
    if not ims: return c["slug"], 0
    W, H = 300, 375; out = Image.new("RGB", (W * 4 + 30, 60 + H * 2 + 10), (255, 255, 255)); dr = ImageDraw.Draw(out)
    dr.text((10, 14), f"{c.get('nome', c['slug'])}  ·  {c['slug']}", fill=(0, 0, 0), font=F)
    for i, im in enumerate(ims):
        im.thumbnail((W, H)); x = 10 + (i % 4) * (W + 3); y = 60 + (i // 4) * (H + 5)
        out.paste(im, (x + (W - im.width) // 2, y + (H - im.height) // 2))
    out.save(f"analise/folhas_lojas/{c['slug']}.jpg", quality=80)
    return c["slug"], len(ims)
with cf.ThreadPoolExecutor(6) as ex: res = list(ex.map(folha, C))
print("folhas:", sum(1 for _, n in res if n), "de", len(C), "| sem imagem:", [s for s, n in res if not n])
