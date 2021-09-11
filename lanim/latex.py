"""
Utility module for invoking `pdflatex` and `dvipng` to render
LaTeX documents as images.
"""


from pathlib import Path
from contextlib import contextmanager
import subprocess
import random
import shutil
from typing import Callable, Iterable, TypeVar


A = TypeVar("A")


def run_latex_process(input_file: Path, output_dir: Path) -> Path:
    """
    Invoke `pdflatex` and `dvipng` on a LaTeX document
    and return the path of the resulting PNG file.

    - `input_file`: path to a LaTeX document to render
    - `output_dir`: directory where to place the output
    """
    cmd_pdflatex = [
        "pdflatex",
        "-draftmode", # lower quality + produces only DVI, not PDF
        "-output-format=dvi",
        "-halt-on-error",
        "-output-directory", str(output_dir.absolute()),
        str(input_file.absolute()) # input filename
    ]
    p1 = subprocess.run(cmd_pdflatex, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p1.returncode != 0:
        raise RuntimeError(p1.stdout.decode())

    output_png_file = output_dir / "output.png"

    cmd_dvipng = [
        "dvipng",
        str(output_dir / input_file.name.replace(".tex", ".dvi")),
        "-fg", "rgb 1.0 1.0 1.0",
        "-bg", "Transparent",
        "-D", "1280", # DPI
        "-o", str(output_png_file.absolute())
    ]
    p2 = subprocess.run(cmd_dvipng, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p2.returncode != 0:
        raise RuntimeError(p2.stdout.decode())

    return output_png_file


TEMPLATE = \
R"""
\documentclass[varwidth, preview, border=1pt]{standalone}

%s

\begin{document}
%s
\end{document}
"""


def render_latex_to_png(source: str, packages: Iterable[str], callback: Callable[[Path], A]) -> A:
    r"""
    - `source`: LaTeX content to put between \begin{document} and \end{document}
    - `packages`: Packages to include with \usepackage{...}
    - `callback`: Function to call when the PNG file is ready

    After `callback` is called, the file will not be accessible.
    """

    usepackage_clauses = "\n".join([r"\usepackage{%s}" % package for package in packages])
    content = TEMPLATE % (usepackage_clauses, source)

    with mktempdir(Path("./_latex_cache/"), "_latex") as tempdir:
        in_path = tempdir / "input.tex"
        out_path = tempdir / "out"
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
