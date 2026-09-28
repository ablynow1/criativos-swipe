"""Teste do render (Chrome headless via CDP): erros de JS, contagens, modal com vídeo, filtros, tema."""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("CDP_PORTA", "9464"); os.environ.setdefault("CDP_PERFIL", "/tmp/malta-teste")
import cdp_base as C, websockets
URL = sys.argv[1] if len(sys.argv) > 1 else "file://" + os.path.abspath("site/index.html")
async def main():
    C.sobe_chrome(); ws = await websockets.connect(C.ws_url(), max_size=50 * 1024 * 1024, ping_interval=None)
    a = C.Aba(ws); await a.cmd("Page.enable"); await a.cmd("Runtime.enable")
    erros = []
    await a.cmd("Emulation.setDeviceMetricsOverride", width=1280, height=900, deviceScaleFactor=1, mobile=False)
    await a.cmd("Page.navigate", url=URL); await asyncio.sleep(4)
    r = await a.js("""(async()=>{const o={};
      o.lojas=document.querySelectorAll('.loja').length; o.cards=document.querySelectorAll('#gal .ad').length; o.count=document.getElementById('count').textContent;
      o.top=document.querySelectorAll('#topL .long').length; o.pad=document.querySelectorAll('#padG .card').length; o.fr=document.querySelectorAll('#frG li').length; o.rep=document.querySelectorAll('#repG .idea').length;
      o.res=document.querySelectorAll('#resumoL li').length; o.imgsQuebradas=[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&i.src).map(i=>i.src.split('/').pop()).slice(0,10);
      const v=[...document.querySelectorAll('#gal .ad')].find(b=>b.querySelector('.play')); v.click(); await new Promise(r=>setTimeout(r,800));
      o.modalAberto=document.getElementById('scrim').classList.contains('open'); const vid=document.querySelector('#sheet video'); o.video=!!vid; o.videoSrc=vid?vid.getAttribute('src'):'';
      o.replicar=!!document.querySelector('#sheet .blk.ok');
      document.getElementById('xB').click(); o.fechou=!document.getElementById('scrim').classList.contains('open');
      const sel=document.getElementById('fLoja'); sel.value=sel.options[1].value; sel.dispatchEvent(new Event('change')); o.filtroLoja=document.getElementById('count').textContent+' ('+sel.options[1].text+')';
      sel.value=''; sel.dispatchEvent(new Event('change'));
      const d=document.getElementById('fDias'); d.value='90'; d.dispatchEvent(new Event('change')); o.filtro90=document.getElementById('count').textContent; d.value='30'; d.dispatchEvent(new Event('change'));
      document.getElementById('tema').click(); o.temaEscuro=getComputedStyle(document.body).backgroundColor;
      o.overflowX=document.documentElement.scrollWidth>document.documentElement.clientWidth;
      return JSON.stringify(o)})()""")
    print(r)
    await a.cmd("Emulation.setDeviceMetricsOverride", width=375, height=812, deviceScaleFactor=2, mobile=True)
    await a.cmd("Page.navigate", url=URL); await asyncio.sleep(3)
    print("mobile:", await a.js("JSON.stringify({overflowX:document.documentElement.scrollWidth>document.documentElement.clientWidth, sw:document.documentElement.scrollWidth, largos:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>376).slice(0,5).map(e=>e.tagName+'.'+e.className)})"))
    await ws.close()
asyncio.run(main())
