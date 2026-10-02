#!/bin/bash
cd /Users/love/Documents/Claude/Amplify
R=content-bank/P009-animated-mascot-workout-reel/runs/run-01_2026-09-26_verde-upper-traps
for i in 2 3 4 5 6; do
  P=$(./.venv/bin/python -c "import json;print(json.load(open('$R/spec.json'))['shots'][$i-1]['prompt'])")
  echo "== shot $i"
  ./.venv/bin/python tools/kie.py video --model kling3 --mode std --duration 3 --first-frame $R/raw/frames/shot$i.png --prompt "$P" --out $R/raw/clip$i.mp4 --run $R --run-cap 900 2>&1 | tail -2
done
echo ALL DONE
