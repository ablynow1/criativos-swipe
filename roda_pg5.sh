#!/bin/bash
cd "$(dirname "$0")"
until grep -q FIM log_pg3.txt 2>/dev/null; do sleep 5; done
export CDP_PORTA=9461 CDP_PERFIL=/tmp/malta-cdp DMAX=2026-08-27
python3 paginas.py alvos_desc3.json BR 10 > log_pg5.txt 2>&1
echo FIM >> log_pg5.txt
