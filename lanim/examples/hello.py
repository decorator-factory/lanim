from lanim.core import pause_after, seq_a
from lanim.pil_graphics import appear, gbackground, move_by
from lanim.pil_types import Latex, Pair, Rect
from lanim.easings import in_out, sled

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(x=0, y=-0.1, width=sign.width() + 0.5, height=sign.height() + 0.5)

export = seq_a(
    appear(border) * 0.5,
    pause_after(
        gbackground(appear(sign), [border]).ease(in_out),
        0.25,
    ),
    move_by(Pair(sign, border), dx=0, dy=10).ease(sled),
)
