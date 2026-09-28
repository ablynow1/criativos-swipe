# Análise de criativos validados de CAMISETA ESTAMPADA (Meta Ads · mundo todo)

Você é um diretor de criação de performance analisando anúncios que estão NO AR há 30+ dias (sinal de que se pagam).
Contexto: a Malta vende camiseta masculina estampada premium (oversized, frase de atitude, arte, R$190–330) e quer
copiar os MOLDES de anúncio de camiseta estampada que duram no ar pelo mundo.

## Entrada
Um arquivo JSON (lote) com uma lista de criativos. Cada item tem: id, loja, grupo, dias (no ar), variacoes,
formato (video/imagem/carrossel), duracao, texto_anuncio, cartao (linhas do cartão do link), botao, destino (URL),
fala (transcrição automática do áudio; pode estar vazia) e folha (caminho de uma imagem).
A `folha` é uma tira com os quadros do criativo: em VÍDEO são 5 quadros em ordem (início → fim, o 1º é o gancho);
em IMAGEM é a própria peça; em CARROSSEL são os primeiros cards lado a lado.

## O que fazer
Para CADA item: abra a `folha` com a ferramenta Read (é imagem), leia os campos de texto e preencha a análise.
Descreva só o que dá pra ver/ler. Nada de inventar. Se algo não dá pra saber, deixe "".
Se a `fala` parecer letra de música ou lixo de transcrição, ignore a fala.
O texto do anúncio pode estar em qualquer língua: escreva a análise em português do Brasil, e no campo `estampa`
mantenha a frase da estampa na língua original, entre aspas simples.

PRIMEIRO decida `estampada` com rigor:
- true  = o produto anunciado é camiseta (manga curta ou longa, regata não) COM ESTAMPA visível: frase, tipografia,
          arte, ilustração, foto, logo grande, estampa de costas. Várias camisetas estampadas num carrossel também vale.
- false = camiseta lisa ou só com logo pequeno/bordado discreto; polo; camisa de botão; moletom/hoodie; calça,
          short, boné, tênis, acessório; peça feminina (cropped, baby look, vestido); anúncio que não mostra a camiseta
          (só marca, evento, desconto genérico, app); impressão sob demanda de caneca/pôster.
Se `estampada` for false, preencha o resto do jeito mais curto possível (pode deixar "" e []).

## Saída
Para cada item, grave um arquivo `analise/out/<id>.json` (pasta ao lado desta instrução) com EXATAMENTE estas chaves:
{
 "id": "...",
 "estampada": true | false,
 "estampa": o que está estampado, até 14 palavras (ex.: "frase 'Stay Hungry' em serifa nas costas", "ilustração vintage de carro de corrida no peito"),
 "tipo_estampa": uma destas, exatamente como escrita:
   "Frase/tipografia" | "Ilustração/arte" | "Logo grande" | "Foto/colagem" | "Vintage/desbotada" | "Humor/meme" | "Cultura pop/licenciada" | "Esporte/clube" | "Outra",
 "lugar_estampa": "frente" | "costas" | "frente e costas" | "manga/detalhe" | "",
 "formato": uma destas opções, exatamente como escrita:
   "Vídeo de clima (lifestyle)" | "Vídeo da peça no corpo" | "Vídeo do produto (sem modelo)" | "Vídeo POV/unboxing" | "Vídeo com fala (creator/UGC)" | "Vídeo de bastidor/produção" |
   "Vídeo de oferta (banner animado)" | "Foto editorial (campanha)" | "Foto da peça no corpo" | "Foto still/packshot" |
   "Banner de oferta" | "Carrossel de peças" | "Carrossel editorial" | "Catálogo automático" | "Meme/texto na tela" | "Collab/evento",
 "gancho": o que prende nos primeiros 3 segundos (vídeo) ou no primeiro olhar (imagem). Até 14 palavras, concreto,
 "texto": texto escrito NA PEÇA do anúncio (sobreposto ou na arte), literal e curto; "" se não houver,
 "cena": onde se passa, até 8 palavras,
 "peca": o que está sendo vendido, até 10 palavras (ex.: "camiseta oversized preta com arte nas costas"),
 "oferta": oferta explícita na peça ou no texto ("3 por 2", "frete grátis", "20% OFF", "$29") ou "",
 "angulos": lista de 1 a 3 destes rótulos, exatamente como escritos:
   "Oferta" | "Lançamento/drop" | "Verão & viagem" | "Noite & drink" | "Clube & esporte" | "Frase/atitude" |
   "Peça & detalhe" | "Tecido & qualidade" | "Prova social" | "Creator/UGC" | "Marca/manifesto" | "Kit/combinação",
 "porque": por que esse criativo se sustenta no ar, 1 frase até 25 palavras, ancorada no que se vê,
 "publico": "masculino" | "feminino" | "unissex",
 "fala_util": true se a `fala` é fala de verdade que ajuda a entender o anúncio; false se vazia, música ou ruído,
 "replicar": como a Malta replica o MOLDE com uma camiseta estampada dela (não a marca), 1 frase até 30 palavras,
             direção de produção concreta: quem aparece, onde, qual plano, onde a estampa aparece, qual texto/oferta.
}
Português do Brasil. JSON válido (aspas duplas, sem comentários). Um arquivo por id.
Ao terminar, responda só: quantos arquivos gravou, quantos deram estampada=true e quais ids ficaram com dúvida (se houver).
