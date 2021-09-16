import pathlib
import importlib
import subprocess
from typing import Protocol

from lanim.core import Animation, crop_by_range
from lanim.pil_types import PilRenderable
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
    range: tuple[int, int]


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


def _crop_animation(
    anim: Animation[PilRenderable],
    start: int,
    finish: int
) -> Animation[PilRenderable]:
    return crop_by_range(anim, start / 100, (finish + 1) / 100)


def _find_animation(module_name: str, export_name: str) -> Animation[PilRenderable]:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ImportError("Module {!r} not found".format(module_name)) from None

    try:
        animation = getattr(module, export_name)
    except AttributeError:
        raise ImportError(
            "Module {!r} doesn't export {!r}".format(module, export_name)
        ) from None

    if not isinstance(animation, Animation):
        raise TypeError(
            "{}.{} should be an animation, but I got {1.__class__!r}: {1!r}"
            .format(module_name, export_name, animation)
        )

    return animation


def _purge_temp_dir(path: pathlib.Path):
    path.mkdir(parents=True, exist_ok=True)
    for file in path.glob("*.png"):
        file.unlink()


def entry_point(options: Options) -> None:
    _purge_temp_dir(options.temp_dir)

    _ensure_dependencies_exist()

    animation = _find_animation(options.module, options.export_name)
    animation = _crop_animation(animation, *options.range)

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