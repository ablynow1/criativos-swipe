"""uso: python3 baixa.py ads.json midia_dir  (ads.json = lista de anúncios com poster/imgs/video)"""
import json, os, sys, subprocess, concurrent.futures as cf
ads = json.load(open(sys.argv[1])); D = sys.argv[2]; os.makedirs(D, exist_ok=True)
jobs = []
for a in ads:
    th = a.get("poster") or (a.get("imgs") or [""])[0]
    if th: jobs.append((th, f"{D}/{a['id']}.jpg"))
    for k, u in enumerate((a.get("imgs") or [])[1:6] if a.get("fmt") == "carrossel" else []):
        jobs.append((u, f"{D}/{a['id']}_{k+2}.jpg"))
    if a.get("video"): jobs.append((a["video"], f"{D}/{a['id']}.mp4"))
def get(j):
    u, p = j
    if os.path.exists(p) and os.path.getsize(p) > 2000: return 0
    r = subprocess.run(["curl", "-sL", "--max-time", "120", "-A", "Mozilla/5.0", "-o", p, u])
    return 1 if r.returncode == 0 and os.path.exists(p) and os.path.getsize(p) > 2000 else -1
with cf.ThreadPoolExecutor(8) as ex: res = list(ex.map(get, jobs))
print("baixados", res.count(1), "cache", res.count(0), "falhas", res.count(-1), "de", len(jobs))
