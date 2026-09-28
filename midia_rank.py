"""Vídeos dos anúncios que só estão no ranking (sem análise) -> midia/<id>.mp4 -> site/videos/<id>.mp4 (540p leve), pro swipe e pro modal."""
import json, os, subprocess, shutil, concurrent.futures as cf
R = json.load(open("ranking.json")); V = json.load(open("validados.json"))
vi = {a["id"]: a for a in V}
sel = {a["id"] for a in json.load(open("selecionados.json"))}
alvo = [r["id"] for r in R if r["id"] not in sel and r["fmt"] == "video" and vi.get(r["id"], {}).get("video")]
def um(i):
    src, out = f"midia/{i}.mp4", f"site/videos/{i}.mp4"
    if os.path.exists(out): return "cache"
    if not (os.path.exists(src) and os.path.getsize(src) > 2000):
        subprocess.run(["curl", "-sL", "--max-time", "120", "-A", "Mozilla/5.0", "-o", src, vi[i]["video"]])
        if not (os.path.exists(src) and os.path.getsize(src) > 2000): return "falha"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", "scale='min(540,iw)':-2", "-c:v", "libx264", "-crf", "27", "-preset", "veryfast",
                        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out])
    if r.returncode != 0 or not os.path.exists(out): shutil.copy(src, out)
    return "ok"
with cf.ThreadPoolExecutor(4) as ex: res = list(ex.map(um, alvo))
print("vídeos só-ranking:", len(alvo), {k: res.count(k) for k in set(res)})
