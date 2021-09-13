import pathlib
import importlib
import subprocess
from typing import Protocol

from lanim.anim import Animation
from lanim.pil_machinery import render_pil


class Options(Protocol):
    module: str
    export_name: str
    width: int
    height: int
    fps: int
    temp_dir: pathlib.Path
    output: pathlib.Path
    threads: int


def _is_present(*cmd: str):
    try:
        proc =subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.kill()
    except FileNotFoundError:
        return False
    else:
        return True


def _ensure_dependencies_exist():
    for command, reason in (
        ("pdflatex", "render LaTex to DVI"),
        ("ffmpeg", "compile a series of images into a video"),
        ("dvipng", "convert DVI to PNG")
    ):
        if not _is_present(command, "--help"):
            raise RuntimeError(
                "The `{}` program is not found. It's needed to {}."
                .format(command, reason)
            )


def entry_point(options: Options) -> None:
    _ensure_dependencies_exist()

    try:
        module = importlib.import_module(options.module)
    except ImportError:
        raise ImportError("Module {0.module!r} not found".format(options)) from None

    try:
        animation = getattr(module, options.export_name)
    except AttributeError:
        raise ImportError("Module {0.module!r} doesn't export {0.export_name!r}".format(options)) from None

    if not isinstance(animation, Animation):
        raise TypeError(
            "{0.module}.{0.export_name} should be an animation, but I got {1.__class__!r}: {1!r}"
            .format(options, animation)
        )

    render_pil(
        width=options.width,
        height=options.height,
        animation=animation,
        path=options.temp_dir,
        fps=options.fps,
        workers=options.threads,
    )

    ffmpeg_process = subprocess.Popen([
        "ffmpeg",
        "-y",  # overwrite the output file
        "-framerate", str(options.fps),
        "-start_number", "0",  # signal that frame_0.png is the
                               # first file and not frame_1.png
        "-i", str(options.temp_dir / "frame_%d.png"),
        str(options.output),
    ])
    ffmpeg_process.wait()