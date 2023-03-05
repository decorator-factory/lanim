# Inspired by https://reibitto.github.io/hadoukenify/
# TODO: add the dude

from lanim.core import Animation, pause_after, pause_before
from lanim.easings import in_out
from lanim.pil_types import Align, Group, Latex

lines = [
    "function1(args, function() {",
    "    functiosn2(args, function() {",
    "        function3(args, function() {",
    "            function4(args, function() {",
    "                function5(args, function() {",
    "                    function6(args, function() {",
    "                        function7(args, function() {",
    "                            function8(args, function() {",
    "                                console.log('Done!');",
    "                            });",
    "                        });",
    "                    });",
    "                });",
    "            });",
    "        });",
    "    });",
    "});",
]


rendered_lines = [
    Latex(
        x = -6,
        y = -4 + i * 0.45,
        source=fr"\verb|{line.lstrip()}|",
        scale_factor=0.3,
        align=Align.LU
    )
    for i, line in enumerate(lines)
]

indents = [
    len(line) - len(line.lstrip())
    for line in lines
]


def projector(t: float) -> Group[Latex]:
    return Group([
        rendered.moved(dx=indent * 0.2 * t, dy=0)
        for indent, rendered in zip(indents, rendered_lines)
    ])


export = (
    Animation(1.5, projector)
    .ease(in_out)
    >> (pause_after, 1.0)
    >> (pause_before, 2.0)
)
