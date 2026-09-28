#!/usr/bin/env python3
"""Print de seções do relatório com Chrome headless (Popen + espera o arquivo + killpg).
uso: shot.py <nome> <tema light|dark> <largura> <ids separados por vírgula | all | hero> [altura]
Gera <SP>/apple/out/<nome>.jpg (recortado na altura do conteúdo)."""
import subprocess, os, signal, time, sys, pathlib, shutil
from PIL import Image, ImageChops

SP = pathlib.Path(os.environ.get('SHOT_TMP', '/tmp/shot-apple')); SP.mkdir(parents=True, exist_ok=True)   # páginas temporárias e perfil do Chrome
OUT = SP / 'out'; OUT.mkdir(exist_ok=True)
SITE = pathlib.Path(os.environ.get('SITE', 'site'))   # SITE=/caminho/do/site python3 shot.py ...
CH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def chrome(url, png, w, h):
    png = pathlib.Path(png)
    if png.exists(): png.unlink()
    ud = SP / f"chr_{os.getpid()}_{int(time.time()*1000)}"
    p = subprocess.Popen([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                          "--allow-file-access-from-files", f"--user-data-dir={ud}", f"--window-size={w},{h}",
                          "--virtual-time-budget=9000", f"--screenshot={png}", url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    t0 = time.time(); last = -1; stable = 0
    while time.time() - t0 < 90:
        time.sleep(0.4)
        if png.exists():
            sz = png.stat().st_size
            stable = stable + 1 if (sz == last and sz > 0) else 0
            last = sz
            if stable >= 3: break
    try: os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError: pass
    time.sleep(0.2); shutil.rmtree(ud, ignore_errors=True)
    return png.exists()

def main():
    nome, tema, largura, ids = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    altura = int(sys.argv[5]) if len(sys.argv) > 5 else 9000
    html = (SITE / 'index.html').read_text()
    css = ''
    if ids == 'hero':
        css = 'main,footer{display:none!important}'
    elif ids != 'all':
        keep = ','.join('#' + i for i in ids.split(','))
        css = f'main>section:not({keep}),.hero,footer{{display:none!important}}'
    html = html.replace('</head>', f'<style>{css}</style></head>', 1)
    html = html.replace('loading="lazy"', '')
    page = SITE / f'_p_{nome}.html'; page.write_text(html)
    url = f'file://{page}?theme={tema}'
    if largura < 500:
        wrap = SP / f'_w_{nome}.html'
        bg = '#000' if tema == 'dark' else '#f5f5f7'
        wrap.write_text(f'<!doctype html><html><body style="margin:0;background:{bg};width:520px"><iframe src="{url}" style="border:0;width:{largura}px;height:{altura}px;display:block"></iframe></body></html>')
        url = f'file://{wrap}'; win = 520
    else:
        win = largura
    png = OUT / f'{nome}.png'
    ok = chrome(url, png, win, altura)
    if not ok: print('FALHOU', nome); sys.exit(1)
    im = Image.open(png).convert('RGB')
    if largura < 500: im = im.crop((0, 0, largura * (im.width // 520 or 1), im.height))
    bgc = im.getpixel((im.width - 2, im.height - 2))
    diff = ImageChops.difference(im, Image.new('RGB', im.size, bgc)).getbbox()
    if diff: im = im.crop((0, 0, im.width, min(im.height, diff[3] + 24)))
    # fatias de no máx. 2200 px de altura para leitura
    n = 0; H = im.height; step = 2200
    for y in range(0, H, step):
        part = im.crop((0, y, im.width, min(H, y + step)))
        f = OUT / (f'{nome}.jpg' if H <= step else f'{nome}_{n}.jpg')
        part.save(f, quality=88); n += 1
        print(f, part.size)
    png.unlink()

main()
