import string
import hashlib
from pathlib import Path
import shutil
from PIL import Image
from threaded_cache import threaded_cache
from latex import render_latex_to_png


CACHE_DIR = Path("_latex_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def long_hash(latex: str) -> str:
    """
    A runtime-independent hash for LaTeX that hopefully will not have collisions
    """
    rv = "".join(c for c in latex if c in string.ascii_letters + string.digits)[::32]
    h = hashlib.sha256()
    h.update(latex.encode())
    rv += h.hexdigest()
    h.update((latex * 2).encode())
    rv += h.hexdigest()
    return rv


def image_from_file(path: Path) -> Image.Image:
    # this is needed because a file-based image
    # is lazy: it doesn't actually load the bitmap
    img = Image.open(path)
    img.load()
    return img.convert("RGBA")


@threaded_cache
def render_latex(latex: str) -> Image.Image:
    filename = CACHE_DIR / f"{long_hash(latex)}.png"
    if filename.exists():
        return image_from_file(filename)
    def on_render(p: Path):
        shutil.copy(p, filename)
        return image_from_file(filename)
    return render_latex_to_png(latex, on_render)


@threaded_cache
def _render_latex_scaled(_: tuple[str, float]) -> Image.Image:
    latex, scale_factor = _
    img = render_latex(latex)
    return img.resize((
        int(img.width * scale_factor),
        int(img.height * scale_factor)
    ))


def render_latex_scaled(latex: str, scale_factor: float) -> Image.Image:
    return _render_latex_scaled((latex, scale_factor))
