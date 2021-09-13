# Requirements

1. Python 3.9+
2. Everything from `requirements.txt`
3. `pdflatex`
4. ffmpeg
5. dvipng

# Usage

Compile the example
```bash
python -m lanim -o out.mp4 lanim.examples.showcase
```

Compile the example in lower quality
```bash
python -m lanim -o out.mp4 -w 480 -h 270 --fps 15 lanim.examples.showcase
```

Compile the example but use tmpfs for temporary directory
```bash
python -m lanim -o out.mp4 -p /tmp/.lanim lanim.examples.showcase
```

See full list of options:
```bash
python -m lanim --help
```
