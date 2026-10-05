#!/bin/bash
cd /Users/love/Documents/Claude/Amplify
T=content-bank/_model-tests/runs/2026-10-05_top-models; K=".venv/bin/python tools/kie.py"; C="--run $T --run-cap 6000"
P="$(cat $T/prompt_i2v.txt)"; F=$T/stills/gpt25s_t1.png
$K video --model seedance25 --prompt "$P" --first-frame $F --duration 6 --resolution 1080p --audio --out $T/i2v/seedance25.mp4 $C > $T/i2v/seedance25.log 2>&1 &
$K video --model wan3 --prompt "$P" --first-frame $F --duration 6 --resolution 1080P --audio --out $T/i2v/wan3.mp4 $C > $T/i2v/wan3.log 2>&1 &
$K video --model h3 --prompt "$P" --first-frame $F --duration 6 --resolution 2K --out $T/i2v/h3.mp4 $C > $T/i2v/h3.log 2>&1 &
$K video --model omni11 --prompt "$P" --first-frame $F --duration 6 --resolution 1080p --out $T/i2v/omni11.mp4 $C > $T/i2v/omni11.log 2>&1 &
$K video --model kling3 --prompt "$P" --first-frame $F --duration 6 --mode pro --out $T/i2v/kling3.mp4 $C > $T/i2v/kling3.log 2>&1 &
wait
for f in $T/i2v/*.log; do echo "== $f"; tail -2 $f; done
