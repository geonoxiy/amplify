#!/bin/bash
cd /Users/love/Documents/Claude/Amplify
T=content-bank/_model-tests/runs/2026-10-05_top-models; I=$T/inputs; K=".venv/bin/python tools/kie.py"; C="--run $T --run-cap 4500"
TAIL="Static locked-off phone camera, framed exactly like the image. Unretouched phone video, natural skin texture, true-to-life colour."
P_SD="@Image1 is the woman and the place: keep her face, hair, clothes, the background and the light exactly as in @Image1. @Video1 is the motion reference only: she performs exactly the body movement, timing, head movement, facial expressions and mouth movement of the person in @Video1, beat for beat. Do not copy the person, the clothes or the place from @Video1. $TAIL"
P_WAN="${P_SD//@Image1/Image1}"; P_WAN="${P_WAN//@Video1/Video1}"
P_H3="${P_SD//@Image1/Image 1}"; P_H3="${P_H3//@Video1/Video 1}"
P_OMNI="The uploaded image is the woman and the place: keep her face, hair, clothes, the background and the light exactly as in the image. The uploaded video is the motion reference only: she performs exactly the body movement, timing, head movement, facial expressions and mouth movement of the person in the video, beat for beat. Do not copy the person, the clothes or the place from the video. $TAIL"
$K motion --model kling3-mc --character $I/willow_p015_still.png --driver $I/driver10.mp4 --mode 1080p --prompt "No distortion, the character's movements are consistent with the video." --out $T/motion/kling3mc.mp4 $C > $T/motion/kling3mc.log 2>&1 &
$K video --model seedance25 --prompt "$P_SD" --ref $I/willow_p015_still.png --ref-video $I/driver10.mp4 --duration 10 --resolution 1080p --out $T/motion/seedance25.mp4 $C > $T/motion/seedance25.log 2>&1 &
$K video --model wan3 --prompt "$P_WAN" --ref $I/willow_p015_still.png --ref-video $I/driver10.mp4 --duration 10 --resolution 1080P --out $T/motion/wan3.mp4 $C > $T/motion/wan3.log 2>&1 &
$K video --model h3 --prompt "$P_H3" --ref $I/willow_p015_still.png --ref-video $I/driver10.mp4 --duration 10 --resolution 2K --out $T/motion/h3.mp4 $C > $T/motion/h3.log 2>&1 &
$K video --model omni11 --prompt "$P_OMNI" --ref $I/willow_p015_still.png --ref-video $I/driver10.mp4 --duration 10 --resolution 1080p --out $T/motion/omni11.mp4 $C > $T/motion/omni11.log 2>&1 &
wait
for f in $T/motion/*.log; do echo "== $f"; tail -2 $f; done
