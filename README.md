# Requirements

1. Python 3.9+
2. Poetry
3. Some external dependencies, see "External dependencies"

# External dependencies

## LaTeX
LaTeX is needed to render text and equations.

### Arch Linux
```bash
sudo pacman -S texlive-latexextra
```

### Ubuntu
```
sudo apt-get install texlive-latex-extra
```

### Windows
You should be good to go if you install MiKTeX (https://miktex.org/download)

## FFmpeg
FFmpeg is used to render a video from frames. You can get it here: https://www.ffmpeg.org/download.html


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
