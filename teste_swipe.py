"""Teste do swipe (Chrome headless via CDP + servidor PHP local): carta, voto pro servidor, arrastar, desfazer, listas, recarregar.
uso: python3 teste_swipe.py [url]   (sem url sobe `php -S` em site/ e testa http://127.0.0.1:8765/swipe/)"""
import asyncio, json, os, subprocess, sys, time, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["CDP_PORTA"] = "9466"; os.environ["CDP_PERFIL"] = f"/tmp/swipe-teste-{int(time.time())}"
import cdp_base as C, websockets
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/swipe/"
LOG = "site/swipe/dados/votos.jsonl"
OUT = "/tmp/shots/out"

async def main():
    php = None
    if len(sys.argv) == 1:
        if os.path.exists(LOG): os.remove(LOG)
        php = subprocess.Popen(["php", "-S", "127.0.0.1:8765", "-t", "site"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    ch = C.sobe_chrome()
    try:
        ws = await websockets.connect(C.ws_url(), max_size=50 * 1024 * 1024, ping_interval=None)
        a = C.Aba(ws); await a.cmd("Page.enable"); await a.cmd("Runtime.enable")
        await a.cmd("Page.addScriptToEvaluateOnNewDocument", source="window.__E=[];addEventListener('error',e=>__E.push(String(e.message)));addEventListener('unhandledrejection',e=>__E.push('rej:'+String(e.reason)))")
        await a.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
        await a.cmd("Page.navigate", url=URL); await asyncio.sleep(3)
        r = {}
        r["inicio"] = json.loads(await a.js("""JSON.stringify({coach:!document.getElementById('coach').hidden, top:document.querySelector('.card:not(.next)')?.dataset.id, primeiro:D.items[0].id,
            cartas:document.querySelectorAll('.card').length, prog:document.getElementById('prog').textContent, chips:[...document.querySelectorAll('.chip')].map(b=>b.textContent),
            video:!!document.querySelector('.card:not(.next) video'), deck:[document.getElementById('deck').clientWidth,document.getElementById('deck').clientHeight]})"""))
        await a.cmd("Page.captureScreenshot", format="jpeg", quality=80)
        shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=82)
        open(f"{OUT}/swipe_coach.jpg", "wb").write(base64.b64decode(shot["data"]))
        await a.js("document.getElementById('bCoach').click()"); await asyncio.sleep(0.6)
        shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=82)
        open(f"{OUT}/swipe_carta.jpg", "wb").write(base64.b64decode(shot["data"]))
        # 1) botão Quero
        id1 = await a.js("document.querySelector('.card:not(.next):not(.leaving)').dataset.id")
        await a.js("document.getElementById('bYes').click()"); await asyncio.sleep(1.5)
        # 2) arrastar pra esquerda com o mouse
        id2 = await a.js("document.querySelector('.card:not(.next):not(.leaving)').dataset.id")
        box = json.loads(await a.js("JSON.stringify(document.querySelector('.card:not(.next):not(.leaving)').getBoundingClientRect())"))
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 3
        await a.cmd("Input.dispatchMouseEvent", type="mousePressed", x=cx, y=cy, button="left", clickCount=1)
        for k in range(1, 13):
            await a.cmd("Input.dispatchMouseEvent", type="mouseMoved", x=cx - k * 16, y=cy + k, button="left", buttons=1); await asyncio.sleep(0.016)
        meio = await a.js("document.querySelector('.card:not(.next):not(.leaving) .stamp.no').style.opacity")
        await a.cmd("Input.dispatchMouseEvent", type="mouseReleased", x=cx - 192, y=cy + 12, button="left", clickCount=1); await asyncio.sleep(1.5)
        r["votos_local"] = json.loads(await a.js(f"JSON.stringify({{q:vOf('{id1}'),n:vOf('{id2}'),sync:document.getElementById('sync').textContent,prog:document.getElementById('prog').textContent,nQ:document.getElementById('nQ').textContent,carimboNaoNoMeio:{json.dumps(meio)}}})"))
        # 3) desfazer (volta a carta arrastada)
        await a.js("document.getElementById('bUndo').click()"); await asyncio.sleep(1)
        r["desfez"] = json.loads(await a.js(f"JSON.stringify({{topo:document.querySelector('.card:not(.next):not(.leaving)').dataset.id==='{id2}', v:vOf('{id2}'), prog:document.getElementById('prog').textContent}})"))
        # 4) teclado → e ←
        await a.cmd("Input.dispatchKeyEvent", type="keyDown", key="ArrowRight", code="ArrowRight", windowsVirtualKeyCode=39); await a.cmd("Input.dispatchKeyEvent", type="keyUp", key="ArrowRight", code="ArrowRight", windowsVirtualKeyCode=39)
        await asyncio.sleep(1)
        # 5) ficha de detalhes
        await a.js("document.getElementById('bInfo').click()"); await asyncio.sleep(0.5)
        r["ficha"] = json.loads(await a.js("JSON.stringify({aberta:!document.getElementById('sheet').hidden, blocos:[...document.querySelectorAll('#shC .kv .k')].map(k=>k.textContent), links:document.querySelectorAll('#shC .lk a').length})"))
        shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=82)
        open(f"{OUT}/swipe_ficha.jpg", "wb").write(base64.b64decode(shot["data"]))
        await a.js("document.getElementById('scrim').click()"); await asyncio.sleep(0.3)
        # 6) lista "quero" → tirar um de volta pro swipe
        await a.js("document.getElementById('bMeus').click()"); await asyncio.sleep(0.5)
        r["lista"] = json.loads(await a.js("JSON.stringify({aberta:!document.getElementById('lst').hidden, itens:document.querySelectorAll('#g .gi').length, seg:[...document.querySelectorAll('#seg button')].map(b=>b.textContent), nota:document.getElementById('lstn').textContent})"))
        shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=82)
        open(f"{OUT}/swipe_lista.jpg", "wb").write(base64.b64decode(shot["data"]))
        await a.js("document.querySelector('#g .gi').click()"); await asyncio.sleep(0.3)
        await a.js("document.querySelector('#shA [data-v=\"0\"]').click()"); await asyncio.sleep(1.2)
        r["lista_depois"] = await a.js("document.querySelectorAll('#g .gi').length")
        await a.js("document.getElementById('lstV').click()"); await asyncio.sleep(0.3)
        # 7) filtro Mundo
        await a.js("document.querySelector('.chip[data-f=\"mu\"]').click()"); await asyncio.sleep(0.5)
        r["mundo"] = json.loads(await a.js("JSON.stringify({prog:document.getElementById('prog').textContent, topoMundo:byId[document.querySelector('.card:not(.next):not(.leaving)').dataset.id].r})"))
        await asyncio.sleep(1.5)
        r["servidor_linhas"] = sum(1 for _ in open(LOG)) if os.path.exists(LOG) else "remoto"
        # 8) recarregar com localStorage limpo: estado tem que vir do servidor
        await a.js("localStorage.clear()")
        await a.cmd("Page.navigate", url=URL); await asyncio.sleep(3)
        r["recarregou"] = json.loads(await a.js("JSON.stringify({nQ:document.getElementById('nQ').textContent, prog:document.getElementById('prog').textContent, sync:document.getElementById('sync').textContent})"))
        await a.js("document.getElementById('bMeus').click()"); await asyncio.sleep(0.5)
        shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=82)
        open(f"{OUT}/swipe_lista2.jpg", "wb").write(base64.b64decode(shot["data"]))
        await a.cmd("Emulation.setDeviceMetricsOverride", width=1280, height=820, deviceScaleFactor=1, mobile=False)
        await a.cmd("Page.navigate", url=URL + "?theme=light"); await asyncio.sleep(3)
        shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=82)
        open(f"{OUT}/swipe_desktop.jpg", "wb").write(base64.b64decode(shot["data"]))
        r["erros"] = json.loads(await a.js("JSON.stringify(window.__E)"))
        r["overflowX"] = await a.js("document.documentElement.scrollWidth>document.documentElement.clientWidth")
        print(json.dumps(r, ensure_ascii=False, indent=1))
        await ws.close()
    finally:
        if ch: ch.terminate()
        if php: php.terminate()

asyncio.run(main())
