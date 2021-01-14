import sys
width, height, fps = map(int, sys.argv[1:])

from pathlib import Path
from easings import *
from anim import *
from pil_graphics import *
from pil_types import *



def slider(x1: float, x2: float, y: float, t: float):
    x = x1*(1-t) + x2*t
    return Pair(
        Rect((x1 + x2)/2, y + 0.4, x2 - x1, 0.05, line_width=1.5),
        Latex(x, y, f"${t:.02f}$", 0.5),
    )

def slider_and_rect(t: float):
    return Pair(
        slider(x1=-4.0, x2=4.0, y=-3.0, t=t),

        Rect(0, 0, 2, 2, line_width=2)
        .morph_into(Rect(0, 0, 4, 1.5, line_width=2))
        .projector(t)
    )

base = Animation(duration=1.5, projector=slider_and_rect) @ in_out
here_and_there = seq_a(
    base >> (pause_after, 1.0),
    base @ invert >> (pause_after, 0.5)
)
animation = seq_a(
    here_and_there >> (pause_after, 0.5),
    here_and_there * 0.2,
    here_and_there * 0.2,
    here_and_there * 0.2
)


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


#animation = easing_generalization >> (pause_before, 0.5) >> (pause_after, 2.0)
animation = animation >> (pause_before, 0.75) >> (pause_after, 1.25)

render_pil(width, height, animation, Path("./out"), fps, workers=4)
