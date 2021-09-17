from lanim.core import const_a
from lanim.pil import appear, gbackground, move_by, Latex, Rect, Pair
from lanim.easings import in_out, sled

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = (
    appear(border) * 0.5
    + gbackground(appear(sign), [border]).ease(in_out)
    + const_a(pair) * 0.25
    + move_by(pair, dx=0, dy=10).ease(sled)
)
