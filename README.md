# Criativos → Swipe (Tinder de anúncios)

Puxa criativos **validados** (rodando há 30+ dias) da Biblioteca de Anúncios da Meta, analisa cada um e joga tudo num **swipe estilo Tinder**: direita = quero replicar, esquerda = não.

## Precisa ter
- macOS com Google Chrome em `/Applications`
- Python 3 + `pip install websockets pillow mlx-whisper` (mlx-whisper só pra transcrever vídeo, Apple Silicon)
- `ffmpeg` (`brew install ffmpeg`)
- PHP (só pra testar o swipe local / servidor com PHP pra gravar votos)

## Fluxo
1. **Termos de busca** → `q*.txt` (um termo por linha)
2. **Buscar lojas** → `busca.py` / `bib.py` (coletor via CDP, 1 Chrome só)
3. **Varrer páginas das lojas** → `paginas.py` (quantos anúncios ativos, desde quando)
4. **Rodada completa** → `bash rodada.sh` (seleciona → baixa mídia → dedupe → prepara → transcreve → lotes de análise)
5. **Analisar** → lotes em `analise/lotes/`, régua em `analise/INSTRUCOES*.md` (feito por agentes do Claude Code)
6. **Ranking** → `python3 ranking.py` (escala = dias × variações)
7. **Montar site + swipe** → `python3 build.py` → gera `site/` e `site/swipe/`
8. **Testar local** → `python3 teste_swipe.py` (sobe `php -S` em `site/`)
9. **Publicar** → subir a pasta `site/` num host com PHP
10. **Ler as escolhas** → `SWIPE_BASE=https://seu-site.com/criativos/ python3 escolhas.py` → `escolhas.json`

## Variáveis úteis
- `DMAX=2026-08-27` → só anúncios que já rodavam nessa data (= 30+ dias)
- `PAUSA=9` → segundos entre páginas
- `CDP_PORTA` / `CDP_PERFIL` → porta e perfil do Chrome

## Cuidados (aprendidos na marra)
- **Nunca 2 Chromes em paralelo** na Biblioteca: bloqueia em ~30 min. 1 Chrome + 9s de pausa roda 100+ páginas.
- Playwright recebe a Biblioteca **vazia**; o coletor CDP próprio (`cdp_base.py`) funciona.
- Match de page_id por nome dá falso positivo: aceitar só se o link do anúncio bate com o domínio da marca.
- Mesma arte com id diferente: dedupe por md5 do vídeo + aHash da thumb.
- Não subir `votos.jsonl` de teste pro servidor.

Mídia, dados coletados e resultados **não estão no repo** (pesados). Rodando o fluxo, tudo é gerado de novo.
