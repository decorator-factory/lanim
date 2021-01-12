import time

from easings import *
from anim import *


def backspace(size: int):
    print("\r" + size*" " + "\r", end="", flush=True)


def appear(text: str) -> Animation[str]:
    def _appear(t: float) -> str:
        if t == 0.0:
            return ""
        elif t == 1.0:
            return text
        else:
            return text[:int((len(text) + 1) * t)]
    return Animation(1.0, _appear)


def run_terminal_animation(animation: Animation[str], fps: float) -> None:
    # time.sleep(1)
    last_output = ""
    total_steps = math.ceil(fps * animation.duration)
    for step in range(total_steps ):
        backspace(len(last_output))
        last_output = animation.projector(step / total_steps)
        print(last_output, end="", flush=True)
        time.sleep(1/fps)
    # time.sleep(1)
    print()


if __name__ == "__main__":
    run_terminal_animation(
        seq_a(
            appear("Hello, world! Hello, world!")@compose(back_and_forth, in_out),
            appear("Never gonna give you up...")@in_out >> (pause_after, 0.5) >> (pause_after, 0.5),
        ) * 2.0,
        fps=60.0
    )

a = appear("Never gonna give you up...") @ quadratic >> (pause_after, 0.5)
