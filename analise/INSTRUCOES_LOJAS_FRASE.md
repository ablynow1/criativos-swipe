# A LOJA é parecida com FRASED e BY SOMEONE'S DIARY? (nota de loja, 0 a 10)

Referências (o Vitor mandou): frased.com (@frased.unfiltered) e bysomeonesdiary.com (@bysomeonesdiary).
- Produto: camiseta (e moletom) com FRASE engraçada, irônica ou ousada em destaque, quase sempre NAS COSTAS.
  Frases reais: 'CEO OF BAD DECISIONS', 'DO WHATEVER THE FUCK MAKES YOU HAPPY', 'IF YOU NEED A PROBLEM I'M HERE',
  'ESPRESSO MARTINI CLUB', 'EVERYTHING I LOVE IS ILLEGAL, EXPENSIVE OR BLONDE', 'EXERCISING JUST ENOUGH TO F*CK & FIGHT',
  'UNDIAGNOSED BUT SOMETHING AIN'T RIGHT', 'I TOLD CHATGPT ABOUT U', 'PASTA SEX WINE'. Tipografia grande ou letra à mão colorida.
- Anúncios: creator/UGC vestindo, de costas pra frase aparecer, no dia a dia (cozinha, mercado, praia, piscina, festival, balada);
  closes da frase; arte simples com oferta "compre 2, leve 3" / "mix & match".
- Tom: humor sobre beber, festa, namoro, decisões ruins; jovem; unissex.

## Entrada
Lista de lojas; pra cada uma, uma folha (imagem) com até 8 anúncios dela ligados há 10+ dias.

## Nota "parecida" (0 a 10)
- 9–10: mesma proposta: camiseta/moletom com frase engraçada/irônica/ousada nas costas + creator/UGC ou lifestyle.
- 7–8: camiseta com frase de humor/atitude em destaque, mas anúncio mais de produto (flat/mockup) ou frase menos ousada.
- 5–6: camiseta com frase genérica (motivacional, fofa, de presente) ou estampa de arte com um pouco de texto.
- 3–4: camiseta estampada sem frase (arte, logo), básico, ou outra estética.
- 0–2: não vende camiseta, loja só feminina/infantil, personalizada por encomenda, B2B.

## Saída
Pra cada loja, grave `analise/lojas_fr/<slug>.json` com EXATAMENTE:
{ "slug": "...", "parecida": inteiro 0–10, "motivo": até 20 palavras, "o_que_vende": até 12 palavras }
JSON válido. Ao terminar, responda só: quantas lojas avaliou e quantas tiveram nota >= 6.
