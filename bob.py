import sys
width, height, fps = map(int, sys.argv[1:])

from pathlib import Path
from easings import *
from anim import *
from pil_graphics import *
from pil_types import *



# Trajectories:


@scene(linear)
def moving_rectangle(then: Then[Rect]):
    r0 = then(const_a(Rect(-2, -2, 1, 1)) * 0.1)
    r1 = then(move_t(r0, dest_x=3, dest_y=1, traj=halfcircle_traj) >> (pause_after, 0.5))
    r2 = then(move_t(r1, dest_x=-2, dest_y=-2, traj=low_arc_traj) >> (pause_after, 0.5))

traj_markers = Pair(Rect(-2, -2, 0.1, 0.1), Rect(3, 1, 0.1, 0.1))
traj_animations = lpair(moving_rectangle, traj_markers)


# Slider:

def slider(x1: float, x2: float, y: float, t: float):
    x = x1*(1-t) + x2*t
    return Pair(
        Rect((x1 + x2)/2, y + 0.6, x2 - x1, 0.05, line_width=1.5),
        Pair(
            Triangle(x, y + 0.4, *(-0.2, 0, +0.2, 0, 0, 0.2)),
            Latex(x, y, f"${t:.02f}$", 0.5),
        ),
    )

def slider_and_tri(t: float):
    return Pair(
        slider(x1=-4.0, x2=4.0, y=-3.0, t=t),

        Triangle(0, 0, *(1, 0, -1, -1, -0.5, 1.25), line_width=2)
        .morphed(Triangle(0, 0, *(2, 0, -2.5, -0.5, -0.25, 3), line_width=6), t)
    )

base = Animation(duration=1.5, projector=slider_and_tri) @ in_out
here_and_there = seq_a(
    base >> (pause_after, 1.0),
    base @ invert >> (pause_after, 0.5)
)
slider_animation = seq_a(
    here_and_there >> (pause_after, 0.5),
    here_and_there * 0.2,
    here_and_there * 0.2,
    here_and_there * 0.2
)


# Easing definition:

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
                morph_into(generalization1, generalization1.aligned(Align.RC).moved(-0.5, 0.0)),
                df6
            )*0.35 >> (pause_after, 1.0)
        )
    df8 = then(gbackground(appear(generalization2), df7) >> (pause_after, 1.0))


animation = traj_animations * 2 >> (pause_before, 0.75) >> (pause_after, 1.25)


render_pil(width, height, animation, Path("./out"), fps, workers=4)
