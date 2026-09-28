"""Apaga de site/ a mídia que não está mais na página (thumbs, cards, vídeos, prints de loja)."""
import json, os, re, sys
html = open("site/index.html").read() + (open("site/swipe/index.html").read() if os.path.exists("site/swipe/index.html") else "")  # o swipe tem criativos que só existem nele
usados = set(re.findall(r'(?:thumbs|cards|videos|lojas)/[\w.-]+\.(?:jpg|mp4)', html))
apagados = 0
for pasta in (sys.argv[1:] or ["thumbs", "cards", "videos", "lojas"]):
    for f in os.listdir(f"site/{pasta}"):
        p = f"{pasta}/{f}"
        if p not in usados: os.remove(f"site/{p}"); apagados += 1
print("apagados", apagados, "| em uso", len(usados))
