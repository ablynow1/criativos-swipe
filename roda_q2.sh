#!/bin/bash
cd "$(dirname "$0")"
while kill -0 39009 2>/dev/null; do sleep 5; done
export CDP_PORTA=9461 CDP_PERFIL=/tmp/malta-cdp DMAX=2026-08-27
python3 busca.py q2.txt BR 6 > log_q2.txt 2>&1
echo FIM >> log_q2.txt
