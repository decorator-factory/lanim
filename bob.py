import sys
width, height, fps = map(int, sys.argv[1:])

from pathlib import Path
from easings import *
from anim import *
from pil_graphics import *
from pil_types import *


@scene()
def easing_generalization(then: Then[Group[Latex]]):
    square1 = Latex(-0.5, -2.0, R"($D$, $\tau \mapsto f(\tau^2)$)", 0.5, align=Align.RC)
    invert1 = Latex(+0.5, -2.0, R"($D$, $\tau \mapsto f(1 - \tau)$)", 0.5, align=Align.LC)

    square2 = Latex(-0.5, -2.0, R"($D$, $f \circ (\tau \mapsto \tau^2)$)", 0.5, align=Align.RC)
    invert2 = Latex(+0.5, -2.0, R"($D$, $f \circ (\tau \mapsto 1 - \tau)$)", 0.5, align=Align.LC)

    generalization1 = Latex(0.0, -2.0, R"($D$, $f \circ \text{easing}$)", 0.66)
    generalization2 = Latex(0.5, -2.0, R"($D$, $f$) $ @ $ easing", 0.66, align=Align.LC)

    df1 = then(appear(group(square1)))
    df2 = then(gbackground(appear(invert1), df1) >> (pause_after, 1.0))
    df3 = then(move_by(df2, 0.0, 2.0))
    df4 = then(gbackground(appear(square2), df3))
    df5 = then(gbackground(appear(invert2), df4) >> (pause_after, 1.0))
    df6 = then(move_by(df5, 0.0, 2.0))
    _   = then(gbackground(appear(generalization1), df6) * 0.35)
    df7 = then(
            gbackground(
                generalization1.morph_into(generalization1.aligned(Align.RC).moved(-0.5, 0.0)),
                df6
            )*0.35 >> (pause_after, 1.0)
        )
    df8 = then(gbackground(appear(generalization2), df7) >> (pause_after, 1.0))


animation = easing_generalization >> (pause_before, 0.5) >> (pause_after, 2.0)

render_pil(width, height, animation, Path("./out"), fps, workers=4)
