"""Transcreve os vídeos de selecionados.json (pula os já feitos) -> transcricoes/<id>.json. Idioma automático."""
import json, os, subprocess, time
import mlx_whisper
S = json.load(open(os.environ.get("SEL", "selecionados.json"))); os.makedirs("transcricoes", exist_ok=True); os.makedirs("wav", exist_ok=True)
feitos = 0
for e in S:
    i = e["id"]; f = f"midia/{i}.mp4"; out = f"transcricoes/{i}.json"
    if not os.path.exists(f) or os.path.exists(out): continue
    if (e.get("dur_s") or 0) < 12: continue
    w = f"wav/{i}.wav"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", w])
    if r.returncode != 0 or not os.path.exists(w):
        json.dump({"id": i, "erro": "sem audio", "text": "", "segs": []}, open(out, "w")); continue
    t0 = time.time()
    try:
        res = mlx_whisper.transcribe(w, path_or_hf_repo=os.environ.get("WMODEL", "mlx-community/whisper-small-mlx"), verbose=None, condition_on_previous_text=False, no_speech_threshold=0.5, compression_ratio_threshold=2.0)
        segs = [{"s": round(s["start"], 2), "e": round(s["end"], 2), "t": s["text"].strip(), "nsp": round(s.get("no_speech_prob", 0), 3), "lp": round(s.get("avg_logprob", 0), 3)} for s in res.get("segments", [])]
        json.dump({"id": i, "lang": res.get("language"), "text": res.get("text", "").strip(), "segs": segs}, open(out, "w"), ensure_ascii=False)
    except Exception as ex:
        json.dump({"id": i, "erro": str(ex)[:200], "text": "", "segs": []}, open(out, "w"))
    try: os.remove(w)
    except OSError: pass
    feitos += 1
    print(f"{i} {time.time()-t0:.1f}s", flush=True)
print("TUDO PRONTO", feitos, flush=True)
