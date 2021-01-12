from pathlib import Path
from contextlib import contextmanager
import subprocess
import random
import shutil
from typing import Callable, TypeVar


A = TypeVar("A")


def run_latex_process(input_file: Path, output_dir: Path) -> Path:
    cmd_pdflatex = [
        "pdflatex",
        "-draftmode", # lower quality + produces only DVI, not PDF
        "-output-format=dvi",
        "-halt-on-error",
        "-output-directory", str(output_dir.absolute()),
        str(input_file.absolute()) # input filename
    ]
    p1 = subprocess.run(cmd_pdflatex, stdout=subprocess.PIPE)
    if p1.returncode != 0:
        raise RuntimeError(p1.stderr)

    output_png_file = output_dir / "output.png"

    cmd_dvipng = [
        "dvipng",
        str(output_dir / input_file.name.replace(".tex", ".dvi")),
        "-fg", "rgb 1.0 1.0 1.0",
        "-bg", "Transparent",
        "-D", "720", # DPI
        "-o", str(output_png_file.absolute())
    ]
    p2 = subprocess.run(cmd_dvipng, stdout=subprocess.PIPE)
    if p2.returncode != 0:
        raise RuntimeError(p2.stderr)

    return output_png_file


TEMPLATE = \
R"""
\documentclass[preview]{standalone}

\usepackage{amsmath}
\usepackage{amssymb}

\begin{document}
%s
\end{document}
"""


def render_latex_to_png(source: str, callback: Callable[[Path], A]) -> A:
    with mktempdir(Path("./_latex_cache/"), "_latex") as tempdir:
        in_path = tempdir / "input.tex"
        out_path = tempdir / "out"
        content = TEMPLATE % source
        in_path.write_text(content, "utf-8")
        out_path.mkdir()
        output_file_path = run_latex_process(in_path, out_path)
        a = callback(output_file_path)
    return a


@contextmanager
def mktempdir(dir: Path, prefix: str):
    filename = f"{prefix}_{random.randint(0, 2**32-1):020x}"
    filepath = dir / filename
    filepath.mkdir(parents=True, exist_ok=True)
    try:
        yield filepath
    finally:
        shutil.rmtree(filepath, ignore_errors=True)
