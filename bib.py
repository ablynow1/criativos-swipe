"""Coletor da Biblioteca de Anúncios (CDP headless). Uma aba, rola até estabilizar,
lê os cards do DOM + page_id/collation do estado React (adCardsResults)."""
import asyncio, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp_base as C, websockets

JS = r"""(async (RX, MAXS) => {
const sleep = ms => new Promise(r => setTimeout(r, ms));
const cnt = () => (document.body.innerText.match(/Identificação da biblioteca: \d+/g) || []).length;
let last = -1, stable = 0;
for (let i = 0; i < MAXS; i++) {
  window.scrollTo(0, document.body.scrollHeight); await sleep(2300);
  const n = cnt(); if (n === last) { if (++stable >= 2) break; } else { stable = 0; last = n; }
}
const T = document.body.innerText;
const tot = (T.match(/~?[\d.]+ resultados?/) || [''])[0];
const empty = /Nenhum anúncio corresponde/.test(T);
const nodes = [...document.querySelectorAll('span,div')].filter(e => e.childElementCount === 0 && /^Identificação da biblioteca: \d+/.test(e.textContent));
const metaOf = (n, id) => { try { const fk = Object.keys(n).find(k => k.startsWith('__reactFiber')); let f = n[fk], d = 0;
  while (f && d < 80) { const p = f.memoizedProps; if (p && p.adCardsResults) { const res = p.adCardsResults; const arr = Array.isArray(res) ? res : (res.toArray ? res.toArray() : []);
    const flat = []; for (const g of arr) { if (!g) continue; if (Array.isArray(g)) flat.push(...g); else if (g.toArray) flat.push(...g.toArray()); else flat.push(g); }
    const r = flat.find(x => x && x.ad_archive_id === id) || flat[0]; if (r) return {pid: r.page_id, n: r.collation_count, act: r.is_active}; }
    f = f.return; d++; } } catch (e) {} return {}; };
const CTA = /^(Enviar mensagem pelo WhatsApp|Send WhatsApp Message|Enviar mensagem|Send message|Saiba mais|Learn [Mm]ore|Cadastre-se|Sign [Uu]p|Comprar agora|Shop [Nn]ow|Ver detalhes|Fale conosco|Pedir agora|Order [Nn]ow|Acessar o perfil do Instagram|Visitar perfil|Receber promoções|Get [Pp]romotions|Inscreva-se|Ligar|Obter oferta|Get [Oo]ffer|Solicitar agora|Apply [Nn]ow|Candidate-se agora|Assistir mais|Watch [Mm]ore|Baixar|Download|Reservar|Book [Nn]ow|Obter cotação|Get [Qq]uote|Contact [Uu]s|Subscribe|Assinar)$/;
const NOISE = /^(0:00( \/ [\d:]+)?|Ativo|Inativo|Baixo volume de impressões|Impressões:?|<100|Patrocinado|Status do sistema|Português \(Brasil\)|API da Biblioteca de Anúncios.*)$/;
const out = [], seen = new Set();
for (const n of nodes) {
  let c = n; while (c.parentElement && (c.parentElement.innerText.match(/Identificação da biblioteca/g) || []).length === 1) c = c.parentElement;
  const t = c.innerText; const id = (t.match(/biblioteca: (\d+)/) || [])[1]; if (!id || seen.has(id)) continue; seen.add(id);
  const after = (t.split(/Ver detalhes do anúncio|Ver resumo/)[1] || '');
  const lines = after.split('\n').map(s => s.trim()).filter(s => s && s !== '​');
  const page = lines[0] || '';
  if (RX && !(new RegExp(RX, 'i')).test(page)) continue;
  const anchors = [...c.querySelectorAll('a[href*="l.facebook.com/l.php"]')];
  let url = ''; if (anchors[0]) { try { url = new URL(anchors[0].href).searchParams.get('u') || '' } catch (e) {} }
  const rest = lines.slice(2).filter(s => !NOISE.test(s));
  let ix = rest.findIndex(s => /^(?:[A-Z0-9-]+\.)+[A-Z]{2,}(?:\/\S*)?$/.test(s) || /^(WHATSAPP|FACEBOOK|INSTAGRAM|WWW\.[A-Z0-9.-]+)$/.test(s));
  if (ix < 0) ix = rest.length;
  const cta = [...rest].reverse().find(s => CTA.test(s)) || '';
  const body = rest.slice(0, ix).filter(s => !CTA.test(s)).join('\n');
  const card0 = rest.slice(ix, ix + 5);
  const pa = [...c.querySelectorAll('a[href^="https://www.facebook.com/"]')].find(a => a.innerText.trim() === page);
  const v = c.querySelector('video');
  const imgs = [...c.querySelectorAll('img')].map(i => i.src).filter(s => s && !/s60x60|p60x60|emoji|rsrc\.php/.test(s));
  const m = metaOf(n, id);
  out.push({id, page, pid: m.pid || '', page_url: pa ? pa.href : '', ativo: m.act !== undefined ? m.act : !/Inativo/.test(t.slice(0, 200)),
    start: (t.match(/Veiculação iniciada em ([^\n·]+)/) || [])[1] || '', n: m.n || +((t.match(/(\d+) anúncios usam/) || [])[1] || 1),
    multi: /várias versões/.test(t), fmt: v ? 'video' : (imgs.length > 1 ? 'carrossel' : 'imagem'), dur: (t.match(/0:00 \/ ([\d:]+)/) || [])[1] || '',
    body, card: card0, cta, url, poster: v ? v.poster : '', video: v ? v.src : '', imgs: imgs.slice(0, 6)});
}
return JSON.stringify({tot, empty, count: out.length, seen: seen.size, ads: out});
})(%s, %s)"""

async def abre():
    C.sobe_chrome()
    ws = await websockets.connect(C.ws_url(), max_size=300 * 1024 * 1024, ping_interval=None)
    a = C.Aba(ws); await a.cmd("Page.enable"); await a.cmd("Runtime.enable")
    return ws, a

async def coleta(a, url, rx="", maxs=12, espera=8):
    await a.cmd("Page.navigate", url=url); await asyncio.sleep(espera)
    r = await a.js(JS % (json.dumps(rx), maxs))
    return json.loads(r or '{"ads":[],"tot":"","empty":false,"count":0}')

SORT = "&sort_data%5Bmode%5D=total_impressions&sort_data%5Bdirection%5D=desc"

def _desde(dmax):
    return f"&start_date%5Bmax%5D={dmax}" if dmax else ""

def url_busca(q, pais="BR", status="active", dmax=None, tipo="keyword_unordered"):
    import urllib.parse
    return (f"https://www.facebook.com/ads/library/?active_status={status}&ad_type=all&country={pais}"
            f"&media_type=all&q={urllib.parse.quote(q)}&search_type={tipo}{_desde(dmax)}{SORT}")

def url_pagina(pid, pais="BR", status="active", dmax=None):
    return (f"https://www.facebook.com/ads/library/?active_status={status}&ad_type=all&country={pais}"
            f"&media_type=all&search_type=page&view_all_page_id={pid}{_desde(dmax)}{SORT}")
