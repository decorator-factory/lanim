# Requirements

1. Python 3.9+
2. Everything from `requirements.txt`
3. `pdflatex`
4. ffmpeg
5. dvipng

# Usage

```bash
rm -rf _out \
    && python pil_graphics.py
    && (yes | ffmpeg -framerate 30 -start_number 0 -i _out/frame_%d.png -vcodec mpeg4 out.mp4)
    && rm -rf _out
```
