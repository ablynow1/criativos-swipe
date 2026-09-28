"""candidatos.json -> lojas_curl/<pid>.json (home via curl: plataforma, preços, ofertas) — sem Facebook."""
import json, os, re, sys, statistics, concurrent.futures as cf
sys.path.insert(0, ".")
from lojas import le_home
os.makedirs("lojas_curl", exist_ok=True)
C = json.load(open("candidatos.json"))
RUIM = re.compile(r"instagram|facebook|fb\.me|linktr|wa\.me|whatsapp|google|apple|youtube|tiktok|bit\.ly|cutt\.ly|doubleclick|hotmart|kiwify|shein|temu|alibaba|amazon|mercadolivre|shopee", re.I)
alvos = [c for c in C if c["dom"] and not RUIM.search(c["dom"]) and not os.path.exists(f"lojas_curl/{c['pid']}.json")]
def job(c):
    try: d = le_home("https://" + c["dom"] + "/")
    except Exception as e: d = {"erro": str(e)[:100]}
    d.update(pid=c["pid"], page=c["page"], dom=c["dom"])
    json.dump(d, open(f"lojas_curl/{c['pid']}.json", "w"), ensure_ascii=False)
    return c["page"]
with cf.ThreadPoolExecutor(10) as ex: list(ex.map(job, alvos))
print("feitos", len(alvos))
