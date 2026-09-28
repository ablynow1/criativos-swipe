#!/bin/bash
cd "$(dirname "$0")"
alvo=$(date -j -f "%H:%M" "11:38" +%s); agora=$(date +%s)
[ $alvo -gt $agora ] && sleep $((alvo-agora))
export CDP_PORTA=9461 CDP_PERFIL=/tmp/malta-cdp DMAX=2026-08-27 PAUSA=9
python3 fila.py > log_fila.txt 2>&1
