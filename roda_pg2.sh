#!/bin/bash
cd "$(dirname "$0")"
while kill -0 43323 2>/dev/null; do sleep 5; done
export CDP_PORTA=9463 CDP_PERFIL=/tmp/malta-cdp2 DMAX=2026-08-27
python3 paginas.py alvos_desc.json BR 10 > log_pg2.txt 2>&1
echo FIM >> log_pg2.txt
