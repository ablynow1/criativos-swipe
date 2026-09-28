# A LOJA é parecida com a Balddoria? (nota de loja, 0 a 10)

A Malta quer lojas parecidas com a BALDDORIA (balddoria.com.br) pra copiar os moldes de anúncio.
Balddoria: marca premium de streetwear; camiseta OVERSIZED (e moletom) com FRASE curta de atitude, ironia ou noite,
quase sempre NAS COSTAS, em inglês ('ONLY FOOLS ARE SATISFIED', 'POLITE AS FUCK', 'Porn Star Martini', '5AM is for clubbing, not for running').
Anúncios com modelo vestindo, turma de amigos, balada, beach club, flash estourado, editorial, preto e branco. Preço alto.

## Entrada
Uma lista de lojas. Pra cada loja há uma folha (imagem) com até 8 anúncios dela que estão no ar há 30+ dias, em grade.

## Nota "parecida" (0 a 10)
- 9–10: mesma proposta: oversized com frase de atitude/ironia/noite, clima de balada/flash/editorial, cara premium.
- 7–8: streetwear premium de camiseta com frase ou tipografia forte, clima jovem/noite, mesmo que com menos ironia.
- 5–6: camiseta estampada (arte, logo grande) com cara de marca, mas sem frase de atitude nem clima de noite.
- 3–4: básico, varejo de oferta, outra estética (surf, resort, alfaiataria), ou camiseta com frase genérica de presente.
- 0–2: não vende camiseta, loja feminina/infantil, B2B.

## Saída
Pra cada loja, grave `analise/lojas_bd/<slug>.json` com EXATAMENTE:
{ "slug": "...", "parecida": inteiro 0–10, "motivo": até 20 palavras, "o_que_vende": até 12 palavras }
JSON válido. Ao terminar, responda só: quantas lojas avaliou e quantas tiveram nota >= 6.
