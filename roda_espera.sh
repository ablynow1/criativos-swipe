#!/bin/bash
cd "$(dirname "$0")"
until grep -q FIM log_q2.txt 2>/dev/null; do sleep 10; done
echo "q2 terminou: $(grep -c resultados log_q2.txt) buscas"
