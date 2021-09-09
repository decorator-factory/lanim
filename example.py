import multiprocessing
from lanim.pil_machinery import render_pil
import sys
width, height, fps = map(int, sys.argv[1:])

from pathlib import Path
from lanim.easings import *
from lanim.anim import *
from lanim.pil_graphics import *
from lanim.pil_types import *


# Sum example


@scene_any()
def sum_example(then: ThenAny):
    n0: Maybe[Rect] = m_none(0.0, 0.0)
    n1 = then(morph_into(n0, n0.with_left(Rect(0, 0, 5, 3))))
    n2 = then(morph_into(n1, n1.with_left(Rect(0, 0, 2, 4))))
    n3 = then(morph_into(n2, n2.with_right(Nil(2, 2))))
    n4 = then(morph_into(n3, n3.with_left(Rect(1, -1, 3, 1))) * 2)




# Swapping


def swap_numbers(items: Sequence[int], swappings: Sequence[tuple[bool, int, int]]):
    Cell = Pair[Rect, Latex]

    lx = -len(items)/2
    cells = [
        Pair(
            Rect(lx+i, 0, 1, 1),
            Latex(lx+i, 0, f"${item}$", scale_factor=0.5)
        ) for (i, item) in enumerate(items)
    ]

    @scene()
    def _swap(then: Then[Group[Cell]]):
        g = Group(cells)
        for (should_swap, i1, i2) in swappings:
            if should_swap:
                g = then(swap(g, i1, i2, lift_traj(1), lift_traj(-1)))
            else:
                a = map_a(
                    par_a_longest(
                        swap(g, i1, i1, lift_traj(1), lift_traj(1)),
                        swap(g, i2, i2, lift_traj(-1), lift_traj(-1))
                    ),
                    lambda ab: ab[0].morphed(ab[1], 0.5)
                )
                g = then(a * 0.75)

    return _swap


def bubble_sort_swaps(items: Sequence[int]) -> Iterator[tuple[bool, int, int]]:
    arr = list(items)
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                yield (True, j, j+1)
            else:
                yield (False, j, j+1)


xs = [7, 15, 3, 8, 30, 10, 20, 1, 70, 25, 14]
animation = (
    swap_numbers(xs, list(bubble_sort_swaps(xs)))
    >> (pause_before, 0.75)
    >> (pause_after, 1.25)
)


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


animation = easing_generalization >> (pause_before, 0.75) >> (pause_after, 1.25)


render_pil(width, height, animation, Path("./out"), fps, workers=multiprocessing.cpu_count())
