#!/bin/bash
cd "$(dirname "$0")"
until grep -q FIM log_pg2.txt 2>/dev/null; do sleep 5; done
export CDP_PORTA=9463 CDP_PERFIL=/tmp/malta-cdp2 DMAX=2026-08-27
python3 paginas.py alvos_fora.json ALL 8 > log_pg4.txt 2>&1
echo FIM >> log_pg4.txt
