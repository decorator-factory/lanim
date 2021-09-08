#!/bin/bash
rm -rf out
python example.py $1 $2 $3 \
&& time (yes | ffmpeg -framerate $3 -start_number 0 -i out/frame_%d.png out.mp4)
