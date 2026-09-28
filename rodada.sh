#!/bin/bash
# seleção -> mídia -> dedupe -> prep -> transcrição -> lotes de análise
cd "$(dirname "$0")"
python3 monta_marcas.py
python3 seleciona.py | tail -1
python3 baixa.py selecionados.json midia | tail -1
python3 dedupe.py
python3 prep_midia.py | tail -1
python3 transcreve.py 2>&1 | grep -v Fetching | tail -1
LD=${LOTES_DIR:-analise/lotes}; mkdir -p $LD; rm -f $LD/*.json
LOTES_DIR=$LD python3 lotes.py ${1:-15}
