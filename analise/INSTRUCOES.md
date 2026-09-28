# Análise de criativos validados (Meta Ads · moda masculina premium)

Você é um diretor de criação de performance analisando anúncios de moda que estão NO AR há 30+ dias (sinal de que se pagam).
Contexto: a Malta vai lançar/escalar uma marca de roupa masculina no universo da Ermos e da Balddoria
(camiseta oversized premium R$190–330 com frase de atitude, verão europeu, noite/drinks, clube, linho, "3 por 2").

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

## Saída
Para cada item, grave um arquivo `analise/out/<id>.json` (pasta ao lado desta instrução) com EXATAMENTE estas chaves:
{
 "id": "...",
 "formato": uma destas opções, exatamente como escrita:
   "Vídeo de clima (lifestyle)" | "Vídeo da peça no corpo" | "Vídeo do produto (sem modelo)" | "Vídeo POV/unboxing" | "Vídeo com fala (creator/UGC)" | "Vídeo de bastidor/produção" |
   "Vídeo de oferta (banner animado)" | "Foto editorial (campanha)" | "Foto da peça no corpo" | "Foto still/packshot" |
   "Banner de oferta" | "Carrossel de peças" | "Carrossel editorial" | "Catálogo automático" | "Meme/texto na tela" | "Collab/evento",
 "gancho": o que prende nos primeiros 3 segundos (vídeo) ou no primeiro olhar (imagem). Até 14 palavras, concreto
           (ex.: "Close da estampa 'It's 9pm' nas costas, luz de fim de tarde"),
 "texto": texto escrito NA PEÇA (sobreposto ou na arte), literal e curto; "" se não houver,
 "cena": onde se passa, até 8 palavras (ex.: "bar à noite, balcão com drink"),
 "peca": o que está sendo vendido, até 10 palavras (ex.: "camiseta oversized off-white com frase nas costas"),
 "oferta": oferta explícita na peça ou no texto ("3 por 2", "frete grátis", "20% OFF", "R$ 189") ou "",
 "angulos": lista de 1 a 3 destes rótulos, exatamente como escritos:
   "Oferta" | "Lançamento/drop" | "Verão & viagem" | "Noite & drink" | "Clube & esporte" | "Frase/atitude" |
   "Peça & detalhe" | "Tecido & qualidade" | "Prova social" | "Creator/UGC" | "Marca/manifesto" | "Kit/combinação",
 "porque": por que esse criativo se sustenta no ar, 1 frase até 25 palavras, ancorada no que se vê,
 "publico": "masculino" se a peça anunciada é de homem, "feminino" se é de mulher (saia, vestido, top, conjunto feminino…), "unissex" se serve aos dois ou não dá pra saber,
 "fala_util": true se a `fala` é fala de verdade (narração, depoimento, diálogo) que ajuda a entender o anúncio; false se estiver vazia, for letra de música, ruído ou transcrição sem sentido,
 "replicar": como a Malta replica o MOLDE (não a marca), 1 frase até 30 palavras, direção de produção concreta:
             quem aparece, onde, qual plano, qual texto/oferta. Ex.: "Modelo de costas no balcão de um bar à noite,
             câmera fechada na frase da camiseta, drink na mão; legenda com a frase e '3 por 2'."
}
Português do Brasil. JSON válido (aspas duplas, sem comentários). Um arquivo por id.
Ao terminar, responda só: quantos arquivos gravou e quais ids ficaram com dúvida (se houver).
