#!/bin/bash
cd "$(dirname "$0")"
until grep -q FIM log_q2.txt 2>/dev/null; do sleep 5; done
export CDP_PORTA=9461 CDP_PERFIL=/tmp/malta-cdp DMAX=2026-08-27
python3 paginas.py alvos_desc2.json BR 10 > log_pg3.txt 2>&1
echo FIM >> log_pg3.txt
