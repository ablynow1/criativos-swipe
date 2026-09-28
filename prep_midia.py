"""selecionados.json -> site/thumbs, site/cards, site/videos (540p leve) + analise/folhas/<id>.jpg (folha de quadros pra análise)"""
import json, os, subprocess, shutil, sys
from PIL import Image, ImageStat
S = json.load(open(os.environ.get("SEL", "selecionados.json")))
for d in ("site/thumbs", "site/cards", "site/videos", "analise/folhas", "midia/q"): os.makedirs(d, exist_ok=True)
def escuro(p):
    try: return ImageStat.Stat(Image.open(p).convert("L")).mean[0] < 22
    except Exception: return True
def frame(v, dst, t):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", v, "-frames:v", "1", "-q:v", "3", dst])
    return os.path.exists(dst) and os.path.getsize(dst) > 1000
def dur(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except Exception: return 0
def reduz(src, dst, w=520):
    im = Image.open(src).convert("RGB"); im.thumbnail((w, int(w * 1.9))); im.save(dst, quality=80, optimize=True)
def folha(paths, dst, h=520):
    ims = [Image.open(p).convert("RGB") for p in paths if os.path.exists(p)]
    if not ims: return False
    ims = [im.resize((max(1, int(im.width * h / im.height)), h)) for im in ims]
    W = sum(im.width for im in ims) + 8 * (len(ims) - 1)
    out = Image.new("RGB", (W, h), (255, 255, 255)); x = 0
    for im in ims: out.paste(im, (x, 0)); x += im.width + 8
    if out.width > 2400: out.thumbnail((2400, h))
    out.save(dst, quality=82); return True
st = {"thumb": 0, "frame": 0, "card": 0, "video": 0, "sem": 0, "folha": 0}
for e in S:
    i = e["id"]; src = f"midia/{i}.jpg"; v = f"midia/{i}.mp4"
    tem_v = os.path.exists(v) and os.path.getsize(v) > 20000
    if tem_v and (not os.path.exists(src) or escuro(src)):
        for t in ("1.5", "3", "0.5"):
            if frame(v, f"midia/q/{i}_f.jpg", t) and not escuro(f"midia/q/{i}_f.jpg"): src = f"midia/q/{i}_f.jpg"; st["frame"] += 1; break
    if os.path.exists(src):
        reduz(src, f"site/thumbs/{i}.jpg"); e["th"] = f"thumbs/{i}.jpg"; st["thumb"] += 1
    else: e["th"] = ""; st["sem"] += 1
    e["car"] = []
    for k in range(2, 7):
        c = f"midia/{i}_{k}.jpg"
        if os.path.exists(c): reduz(c, f"site/cards/{i}_{k}.jpg", 380); e["car"].append(f"cards/{i}_{k}.jpg"); st["card"] += 1
    quadros = []
    if tem_v:
        D = dur(v) or 10; e["dur_s"] = round(D, 1)
        for k, frac in enumerate((0.03, 0.18, 0.4, 0.62, 0.85)):
            p = f"midia/q/{i}_{k}.jpg"
            if os.path.exists(p) or frame(v, p, round(max(0.3, D * frac), 2)): quadros.append(p)
        out = f"site/videos/{i}.mp4"
        if not os.path.exists(out):
            r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-vf", "scale='min(540,iw)':-2", "-c:v", "libx264", "-crf", "27", "-preset", "veryfast",
                                "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out])
            if r.returncode != 0 or not os.path.exists(out): shutil.copy(v, out)
        e["vid"] = f"videos/{i}.mp4"; st["video"] += 1
    else:
        e["vid"] = ""
        quadros = ([src] if os.path.exists(src) else []) + [f"midia/{i}_{k}.jpg" for k in range(2, 5) if os.path.exists(f"midia/{i}_{k}.jpg")]
    if quadros and folha(quadros, f"analise/folhas/{i}.jpg", 520 if tem_v else 900): e["folha"] = f"analise/folhas/{i}.jpg"; st["folha"] += 1
json.dump(S, open(os.environ.get("SEL", "selecionados.json"), "w"), ensure_ascii=False)
print(st)
