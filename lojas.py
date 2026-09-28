"""uso: CDP_PORTA=9462 CDP_PERFIL=... python3 lojas.py lojas_alvo.json
lojas_alvo.json = [{"slug":..,"site":"https://.."}] -> lojas/<slug>.json + site/lojas/<slug>.jpg (print do celular)
Lê a home com curl (título, plataforma, preços, ofertas, redes) e tira print 390px via CDP."""
import asyncio, base64, json, os, re, subprocess, sys, time, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp_base as C, websockets
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
PLAT = [("Nuvemshop", r"nuvemshop|mitiendanube|lojavirtualnuvem"), ("Shopify", r"cdn\.shopify|shopify\.com|Shopify\.theme"),
        ("VTEX", r"vtex(commercestable|img|assets)|vteximg"), ("Tray", r"tray\.com\.br|traycorp"), ("Loja Integrada", r"lojaintegrada"),
        ("Yampi", r"yampi"), ("WooCommerce", r"woocommerce|wp-content"), ("Wix", r"wix\.com|wixstatic"), ("Magento", r"Magento_|mage-init|magento")]
OFERTAS = [("3 por 2", r"\b3\s*por\s*2\b|(compre|leve)\s*3\s*[\w\s]{0,25}?pague\s*(apenas\s*|s[oó]\s*)?2|compre\s*2\s*[\w\s]{0,15}?leve\s*3"),
           ("Frete grátis", r"frete\s*gr[aá]tis"), ("Cupom", r"cupom|c[oó]digo\s+[A-Z0-9]{4,}"), ("Pix com desconto", r"\d+\s*%\s*(off\s*)?(de desconto\s*)?no\s*pix|pix\s*com\s*\d+"),
           ("Parcelamento", r"\d+\s*x\s*sem\s*juros"), ("Sale", r"\bsale\b|liquida|black\s*friday|% ?off")]
os.makedirs("lojas", exist_ok=True); os.makedirs("site/lojas", exist_ok=True)
def le_home(url):
    r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30", "-w", "\n__FIM__%{http_code} %{url_effective}", url], capture_output=True)
    s = r.stdout.decode("utf-8", "ignore"); code, final = "000", url
    if "__FIM__" in s:
        s, tail = s.rsplit("__FIM__", 1); code, final = (tail.split(" ", 1) + [url])[:2]
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", s); t = H.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"\s+", " ", t)
    title = H.unescape((re.search(r"(?is)<title[^>]*>(.*?)</title>", s) or [None, ""])[1]).strip()
    desc = H.unescape((re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', s) or [None, ""])[1]).strip()
    plat = next((n for n, rx in PLAT if re.search(rx, s, re.I)), "")
    precos = []
    for p in re.findall(r"R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})", t):
        v = float(p.replace(".", "").replace(",", "."))
        if 29 <= v <= 3000: precos.append(v)
    ofs = [n for n, rx in OFERTAS if re.search(rx, t, re.I)]
    ig = sorted(set(m.lower() for m in re.findall(r"instagram\.com/([A-Za-z0-9_.]{2,40})", s) if m.lower() not in ("p", "explore", "reel", "stories")))
    return dict(code=code.strip(), final=final.strip(), title=title[:140], desc=desc[:300], plataforma=plat,
                precos=sorted(set(precos))[:40], ofertas=ofs, instagram=ig[:3], texto=t[:4000])
async def main():
    alvos = json.load(open(sys.argv[1]))
    C.sobe_chrome(); ws = await websockets.connect(C.ws_url(), max_size=200 * 1024 * 1024, ping_interval=None)
    a = C.Aba(ws); await a.cmd("Page.enable"); await a.cmd("Runtime.enable")
    await a.cmd("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    await a.cmd("Emulation.setUserAgentOverride", userAgent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1")
    for al in alvos:
        f = f"lojas/{al['slug']}.json"
        if os.path.exists(f): print("cache", al["slug"], flush=True); continue
        t0 = time.time(); d = le_home(al["site"]); d.update(al)
        try:
            await a.cmd("Page.navigate", url="about:blank"); await asyncio.sleep(0.5)
            await a.cmd("Page.navigate", url=al["site"]); await asyncio.sleep(10)
            base = re.sub(r"^www\.", "", re.sub(r"^https?://", "", al["site"]).split("/")[0]).split(".")[0]
            for _ in range(3):
                host = await a.js("location.hostname") or ""
                pronto = await a.js("document.readyState") or ""
                if base in host and pronto == "complete": break
                await asyncio.sleep(4)
            d["host_print"] = await a.js("location.hostname") or ""
            # fecha pop-ups comuns (cookies/newsletter) sem clicar em nada que compre
            if not os.environ.get("NOHIDE"): await a.js("""(()=>{
  const W=innerWidth,H=innerHeight;
  document.querySelectorAll('[class*=cookie] button,[id*=cookie] button,[aria-label*=Fechar],[aria-label*=fechar],[aria-label*=Close],[aria-label*=close],.modal .close,.js-modal-close,[class*=popup] [class*=close],[class*=newsletter] [class*=close]').forEach(b=>{try{b.click()}catch(e){}});
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  for(const el of document.querySelectorAll('body *')){const cs=getComputedStyle(el);if(cs.position!=='fixed'&&!(cs.position==='absolute'&&+cs.zIndex>999))continue;const r=el.getBoundingClientRect();
    if(r.width*r.height>W*H*0.28&&r.height>H*0.3){const t=(el.innerText||'').slice(0,600);const bg=cs.backgroundColor;const a=(bg.match(/rgba\([^)]*,\s*([\d.]+)\)/)||[])[1];
      const modal=/cupom|desconto|% ?off|newsletter|cadastr|e-?mail|primeira compra|inscrev|assine|whats|ganhe|cookies|pol[ií]tica de privacidade/i.test(t)||el.querySelector('input[type=email],input[type=tel],form')||(a!==undefined&&+a>0.15&&+a<0.97);
      if(modal)el.style.setProperty('display','none','important')}}
  document.documentElement.style.overflow='auto';document.body.style.overflow='auto';return 1})()""")
            await asyncio.sleep(1.2)
            if not d.get("precos") or not d.get("plataforma"):
                txt = await a.js("document.body.innerText.slice(0,6000)") or ""
                htm = await a.js("document.documentElement.outerHTML.slice(0,400000)") or ""
                if not d.get("plataforma"): d["plataforma"] = next((n for n, rx in PLAT if re.search(rx, htm, re.I)), "")
                if not d.get("precos"):
                    pr = []
                    for p in re.findall(r"R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})", txt):
                        v = float(p.replace(".", "").replace(",", "."))
                        if 29 <= v <= 3000: pr.append(v)
                    d["precos"] = sorted(set(pr))[:40]
                d["ofertas"] = sorted(set(d.get("ofertas", [])) | {n for n, rx in OFERTAS if re.search(rx, txt, re.I)})
                if not d.get("instagram"): d["instagram"] = sorted(set(m.lower() for m in re.findall(r"instagram\.com/([A-Za-z0-9_.]{2,40})", htm)))[:3]
            shot = await a.cmd("Page.captureScreenshot", format="jpeg", quality=72)
            p = f"site/lojas/{al['slug']}.jpg"; open(p, "wb").write(base64.b64decode(shot["data"])); d["print"] = f"lojas/{al['slug']}.jpg"
        except Exception as e: d["print"] = ""; d["erro_print"] = str(e)[:120]
        json.dump(d, open(f, "w"), ensure_ascii=False)
        print(f"{al['slug']} | {d['code']} | {d['plataforma']} | {d['ofertas']} | {len(d['precos'])} preços | {time.time()-t0:.0f}s", flush=True)
    await ws.close()
if __name__ == "__main__": asyncio.run(main())
