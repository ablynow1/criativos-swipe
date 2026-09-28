#!/bin/bash
cd "$(dirname "$0")"
while kill -0 93423 2>/dev/null; do sleep 5; done
export CDP_PORTA=9461 CDP_PERFIL=/tmp/malta-cdp DMAX=2026-08-27 PAUSA=9
python3 acha_mundo.py > log_achamundo.txt 2>&1
python3 monta_marcas.py > /dev/null
python3 -c "
import json,os
M=json.load(open('marcas.json'))
al=[{'slug':m['slug'],'pid':m['pid']} for m in M if m['grupo'].startswith('mundo') and not os.path.exists('paginas/ALL-'+m['slug']+'.json')]
json.dump(al,open('alvos_mundo2.json','w'))"
python3 paginas.py alvos_mundo2.json ALL 8 > log_pgmundo2.txt 2>&1
echo FIM >> log_pgmundo2.txt
