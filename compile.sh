#!/bin/bash
rm -rf out
python bob.py $1 \
&& time (yes | ffmpeg -framerate $1 -start_number 0 -i out/frame_%d.png -c:v libx264 -crf 5 -preset ultrafast out.mp4)
