# Installing `lanim`

## External dependencies

`lanim` requires some external programs to function.

### FFmpeg

We use _FFmpeg_ to turn a series of images into a video.

You should find out how to instll FFmpeg on the [official website](https://www.ffmpeg.org/).

### LaTeX

[_LaTeX_](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes) is the engine behind text and equations.

Besides LaTeX itself, you'll need three packages: `standalone`, `amsmath` and `amssymb`.

- Ubuntu:

    ```
    sudo apt-get install texlive-latex-extra
    ```

- Arch:

    ```
    pamac install texlive-latexextra
    ```

- Windows & Mac:

    Download MikTeX here: [https://miktex.org/download](https://miktex.org/download)

(If you know a better way of doing this on Windows and Mac, let me know!)

## Python

You need Python 3.9 or higher to use `lanim`.

We recommend using a [virtual environment](https://docs.python.org/3/tutorial/venv.html).
Run `pip install lanim` when you're inside the venv.


## Verify the installation

To make sure you installed `lanim` correctly, render the smoke test animation.

```bash
python -m lanim -o smoke_test.mp4 lanim.examples.hello
```

You should have a video called `smoke_test.mp4` in your current folder:

!["Hello, lanim" GIF](hello.gif)


The default settings are: `--width 1280 --height 720 --fps 30`. Let's try better ones:
```bash
python -m lanim -w 1920 -h 1080 --fps 60 -o smoke_test.mp4 lanim.examples.hello
```


## Performance

To see how fast animations will render on your machine, render the showcase animation.
It's about a minute long.
```bash
python -m lanim -o showcase.mp4 lanim.examples.showcase
```

Then render the animation again to see how the cache speeds up the rendering.
