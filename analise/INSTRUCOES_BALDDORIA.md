# Análise: o criativo é "igual a Balddoria"? (Meta Ads · 30+ dias no ar)

Você é um diretor de criação de performance. A Malta quer mais criativos no estilo da BALDDORIA (balddoria.com.br).
Todos os anúncios do lote estão no ar há 30+ dias (sinal de que se pagam).

## Como é o estilo Balddoria (a régua)
- Peça: camiseta OVERSIZED (às vezes moletom) com FRASE de atitude, ironia ou noite em destaque, quase sempre NAS COSTAS.
  Exemplos reais dela: 'I'M YOUR BIGGEST DREAM', 'ONLY FOOLS ARE SATISFIED', 'POLITE AS FUCK', 'ALLERGIC TO IDIOTS',
  'Heartless but cool', 'Porn Star Martini', '5AM is for clubbing, not for running'. Frase em inglês, curta, com humor seco.
- Cena: modelo VESTINDO a peça, muitas vezes de costas pra frase aparecer; noite, balada, beach club, turma de amigos,
  foto com FLASH estourado, editorial de campanha, vídeo em preto e branco; também close da frase nas costas.
- Tom: marca premium de streetwear com atitude, não varejo de oferta. Preço alto (~R$ 290).

## Nota "parecido" (0 a 10)
- 9–10: camiseta/moletom oversized com frase de atitude/ironia/noite em destaque, modelo vestindo, clima noite/balada/flash/editorial ou P&B.
- 7–8: camiseta com frase ou tipografia forte e cara premium, mas cena diferente (estúdio, rua de dia, close da peça) ou frase menos irônica.
- 4–6: camiseta estampada com arte/ilustração (sem frase), ou estética de varejo/oferta com banner, ou peça boa mas sem estampa marcante.
- 0–3: outra peça (calça, short, boné, tênis), camiseta lisa, peça feminina, anúncio de oferta genérica sem mostrar a peça.

## Entrada
Um arquivo JSON (lote) com criativos. Cada item tem: id, loja, dias, variacoes, formato (video/imagem/carrossel), duracao,
texto_anuncio, cartao, botao, destino, fala (pode estar vazia) e folha (caminho de uma imagem).
A `folha` é uma tira com os quadros: em VÍDEO são 5 quadros em ordem (o 1º é o gancho); em IMAGEM é a peça; em CARROSSEL, os primeiros cards.

## O que fazer
Para CADA item: abra a `folha` com a ferramenta Read (é imagem), leia os textos e dê a nota com rigor. Descreva só o que dá pra ver/ler.

## Saída
Para cada item, grave `analise/out_b/<id>.json` (pasta ao lado desta instrução) com EXATAMENTE estas chaves:
{
 "id": "...",
 "parecido": número inteiro de 0 a 10,
 "motivo": por que essa nota, até 20 palavras, concreto (ex.: "frase irônica nas costas, amigos na balada com flash"),
 "estampa": o que está estampado (frase literal entre aspas simples, ou descrição da arte), até 14 palavras, ou "",
 "formato": uma destas, exatamente como escrita:
   "Vídeo de clima (lifestyle)" | "Vídeo da peça no corpo" | "Vídeo do produto (sem modelo)" | "Vídeo POV/unboxing" | "Vídeo com fala (creator/UGC)" | "Vídeo de bastidor/produção" |
   "Vídeo de oferta (banner animado)" | "Foto editorial (campanha)" | "Foto da peça no corpo" | "Foto still/packshot" |
   "Banner de oferta" | "Carrossel de peças" | "Carrossel editorial" | "Catálogo automático" | "Meme/texto na tela" | "Collab/evento",
 "gancho": o que prende no 1º olhar/3 segundos, até 14 palavras,
 "texto": texto escrito NA PEÇA do anúncio (sobreposto ou na arte), literal e curto, ou "",
 "cena": onde se passa, até 8 palavras,
 "peca": o que está sendo vendido, até 10 palavras,
 "oferta": oferta explícita ("3 por 2", "frete grátis", "20% OFF", "R$ 189") ou "",
 "angulos": 1 a 3 destes rótulos, exatamente como escritos:
   "Oferta" | "Lançamento/drop" | "Verão & viagem" | "Noite & drink" | "Clube & esporte" | "Frase/atitude" |
   "Peça & detalhe" | "Tecido & qualidade" | "Prova social" | "Creator/UGC" | "Marca/manifesto" | "Kit/combinação",
 "porque": por que se sustenta no ar, 1 frase até 25 palavras,
 "publico": "masculino" | "feminino" | "unissex",
 "replicar": como a Malta replica o MOLDE com uma camiseta dela, 1 frase até 30 palavras: quem aparece, onde, plano, onde a frase aparece, texto/oferta.
}
Português do Brasil (a frase da estampa fica na língua original). JSON válido. Um arquivo por id.
Ao terminar, responda só: quantos arquivos gravou, quantos tiveram parecido >= 7 e quais ids ficaram com dúvida.
