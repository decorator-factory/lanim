from lanim.core import pause_after, pause_before
from lanim.pil_types import Group, Latex, Pair, Opacity
from lanim.pil_graphics import appear, gbackground, morph_into, move_by, scene_any, ThenAny
from lanim.easings import linear, in_out, sled


promises = [
    Latex(0, 0, "animation library"),
    Group([
        Latex(0, -0.5, "inspired by"),
        Latex(0, 0.8, "reanimate (Haskell)").scaled(0.8),
        Latex(0, 2.1, "and manim (Python)").scaled(0.8),
    ]),
    Pair(
        Latex(0, -0.5, "uses ideas from"),
        Latex(0, 0.8, "functional programming").scaled(0.8),
    ),
    Pair(
        Latex(0, -0.5, r"simple $\land$ small"),
        Latex(0, 0.8, "design"),
    ),
    Pair(
        Latex(0, -0.5, "multithreaded"),
        Latex(0, 0.8, "rendering"),
    ),
    Pair(
        Latex(0, -0.5, r"high-quality"),
        Latex(0, 0.8, "type annotations"),
    ),
    Pair(
        Latex(0, -0.5, "comprehensive tutorials").scaled(0.8),
        Latex(0, 0.8, "and how-to guides").scaled(0.8),
    ),
    Group([
        Latex(0, -0.5, "good choice for"),
        Latex(0, 0.8, "simple visualizations"),
        Latex(0, 2.1, "(like this one)").scaled(0.5)
    ]),
]


@scene_any(linear)
def export(then: ThenAny):
    sign = Latex(0, 0, r"$\lambda$anim").scaled(2)
    sign = then(morph_into(sign, sign.scaled(0.6)).ease(in_out) >> (pause_before, 2))
    sign = then((move_by(sign, dx=-5, dy=-3.4) * 0.7).ease(in_out) >> (pause_after, 1))

    for promise in promises:
        then(gbackground(appear(promise), [sign]).ease(sled) * 0.5 >> (pause_after, 1.8))
        then(
            gbackground(
                Opacity(promise).fade(), [sign]
            )
            .ease(in_out)
            * 0.4
            >> (pause_after, 0.5)
        )

    call_to_action = Pair(
        Latex(0, 2.1, r"\texttt{pip install lanim}").scaled(0.7),
        Latex(0, 3.4, r"\texttt{decorator-factory.github.io/lanim}").scaled(0.55),
    )

    logo = Latex(0, 10, r"\textit{$\lambda$anim}").scaled(2.3)
    logo = then(move_by(logo, dx=0, dy=-11).ease(in_out) * 2 >> (pause_after, 0.5))
    logo = then(gbackground(Opacity(call_to_action, 0).fade(1), [logo]) * 2 >> (pause_after, 5))
    logo = then(Opacity(logo).fade() >> (pause_after, 0.5))
