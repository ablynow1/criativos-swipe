#!/usr/bin/env python3
"""Coletor da Biblioteca de Anúncios via CDP (Chrome DevTools Protocol).

Por que não `--dump-dom`: o headless do Chrome 151 ignora --virtual-time-budget e
fica preso no polling da Biblioteca — o dump nunca sai. Via CDP eu navego, espero
um tempo fixo, rolo a página e leio o DOM na hora que eu quiser.

Uma instância só de Chrome para todas as marcas (lançar/matar por marca era o
que custava 90-150s cada).
"""
import asyncio, json, os, subprocess, sys, time, urllib.request, socket

import websockets

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
PORTA = int(os.environ.get("CDP_PORTA", "9333"))
PERFIL = os.environ.get("CDP_PERFIL", "/tmp/anama-cdp")


def porta_livre(p):
    s = socket.socket()
    try:
        s.connect(("127.0.0.1", p)); s.close(); return False
    except Exception:
        return True


def sobe_chrome():
    if not porta_livre(PORTA):
        return None
    os.makedirs(PERFIL, exist_ok=True)
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--remote-debugging-port={PORTA}", f"--user-data-dir={PERFIL}",
         f"--user-agent={UA}", "--window-size=1500,3200",
         "--no-first-run", "--no-default-browser-check",
         "--disable-blink-features=AutomationControlled",
         "--disable-background-timer-throttling", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        if not porta_livre(PORTA):
            return p
        time.sleep(0.5)
    raise RuntimeError("Chrome nao subiu na porta CDP")


def ws_url():
    for _ in range(30):
        try:
            d = json.load(urllib.request.urlopen(
                f"http://127.0.0.1:{PORTA}/json/list", timeout=5))
            paginas = [t for t in d if t.get("type") == "page"]
            if paginas:
                return paginas[0]["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("sem alvo CDP")


class Aba:
    def __init__(self, ws):
        self.ws = ws
        self.i = 0

    async def cmd(self, metodo, **params):
        self.i += 1
        await self.ws.send(json.dumps({"id": self.i, "method": metodo, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == self.i:
                if "error" in msg:
                    raise RuntimeError(f"{metodo}: {msg['error']}")
                return msg.get("result", {})

    async def js(self, expr):
        r = await self.cmd("Runtime.evaluate", expression=expr,
                           returnByValue=True, awaitPromise=True)
        return (r.get("result") or {}).get("value")


async def coleta(aba, url, espera=9.0, rolagens=6):
    await aba.cmd("Page.navigate", url=url)
    await asyncio.sleep(espera)
    # a Biblioteca carrega por scroll infinito — cada rolagem traz mais uma leva
    for _ in range(rolagens):
        await aba.js("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2.2)
    await asyncio.sleep(1.5)
    return await aba.js("document.documentElement.outerHTML")


async def main():
    alvos = json.load(open(sys.argv[1], encoding="utf-8"))
    destino = sys.argv[2]
    os.makedirs(destino, exist_ok=True)
    proc = sobe_chrome()
    try:
        async with websockets.connect(ws_url(), max_size=200 * 1024 * 1024,
                                      ping_interval=None) as ws:
            aba = Aba(ws)
            await aba.cmd("Page.enable")
            await aba.cmd("Runtime.enable")
            for i, a in enumerate(alvos):
                arq = os.path.join(destino, f"{a['slug']}.html")
                if os.path.exists(arq) and os.path.getsize(arq) > 300_000:
                    print(f"[{i+1}/{len(alvos)}] {a['slug']}: cache", flush=True)
                    continue
                t0 = time.time()
                try:
                    h = await coleta(aba, a["url"], a.get("espera", 9.0), a.get("rolagens", 6))
                except Exception as e:
                    print(f"[{i+1}/{len(alvos)}] {a['slug']}: ERRO {e}", flush=True)
                    continue
                open(arq, "w", errors="ignore").write(h or "")
                n = (h or "").count('"ad_archive_id"')
                print(f"[{i+1}/{len(alvos)}] {a['slug']}: {len(h or '')//1024}kb "
                      f"| {n} ads | {time.time()-t0:.0f}s", flush=True)
    finally:
        if proc:
            proc.terminate()


if __name__ == "__main__":
    asyncio.run(main())
