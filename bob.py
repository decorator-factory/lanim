import sys
fps = int(sys.argv[1])

from easings import *
from anim import *
from pil_graphics import *
from pil_types import *

# @scene(easings.in_out)
# def a_to_b__appears(then: Then[Latex]):
#     a_to_b1 = then(appear(Latex(-2.0, 0.5, R"$A \implies B$", 0.75)) * 2)
#     a_to_b2 = then(move_by(a_to_b1, -2.0, 0.0))
#     a_to_b3 = then(move_by(a_to_b2, -1.0, -2.5))

# @scene(easings.in_out)
# def b_to_a__appears(then: Then[Latex]):
#     b_to_a1 = then(appear(Latex(2.0, -0.5, R"$B \implies A$", 0.75)) * 2)
#     b_to_a2 = then(move_by(b_to_a1, 2.0, 0.0))
#     b_to_a3 = then(move_by(b_to_a2, 1.0, 2.5))

# @scene(easings.linear)
# def base(then: Then[Group[Latex]]):
#     two_equations = then(parallel(a_to_b__appears, b_to_a__appears))
#     then(const_a(two_equations) * 0.5)
#     then(scale(two_equations, 0.0) @ easings.in_out)


@scene()
def d_f__appears(then: Then[Latex]):
    df1 = then(appear(Latex(-4, 0.0, R"($D$, $f$)")))
    df2 = then(const_a(df1))


base = d_f__appears


animation = base >> (anim.pause_before, 0.5) >> (anim.pause_after, 0.5)

render_pil(
    animation,
    Path("./out"),
    fps,
    workers=4
)
