#!/bin/bash
cd /Users/love/Documents/Claude/Amplify
T=content-bank/_model-tests/runs/2026-10-05_top-models; F=personas/willow/refs; P="$(cat $T/prompt_still.txt)"
run() { .venv/bin/python tools/kie.py image --model $1 --resolution $2 --prompt "$P" --ref $F/real_face.png $F/sheet_real.png $F/rooms/kitchen.jpg --aspect 9:16 --out $T/stills/$1_t$3.png --take $3 --run $T --run-cap 4500 > $T/stills/$1_t$3.log 2>&1; echo "$1 t$3: $(tail -1 $T/stills/$1_t$3.log)"; }
for m in nbp:4K gpt25s:4K gpt25f:4K gpt2:4K nb2:4K sd5:2K; do run ${m%%:*} ${m##*:} 1 & run ${m%%:*} ${m##*:} 2 & done; wait
