"""
Rendering-agnostic tools for animations.

Conceptually, an animation on type A consists of two parts:
- a duration (float)
- a projector (float -> A)

A projector is a function from [0; 1] to an element of type A. It transforms
the "progress" (a number from 0 to 1 inclusively) of the animation to a still
frame of type A.

Example:

>>> def projector(t: float) -> str
...     greeting = "Hello, world!"
...     return greeting[:round(t * (len(greeting) + 1))]
>>> duration = 1.0
>>> animation = Animation(duration, projector)
>>> for frame in frames(animation, fps=6):
...     print(frame)

He
Hello
Hello,
Hello, wo
Hello, world
Hello, world!
"""


from __future__ import annotations
from dataclasses import dataclass, replace as dataclass_replace
from typing import Callable, Generic, Iterable, Iterator, TypeVar, Union, overload
from lanim.easings import Easing


A = TypeVar("A", covariant=True)
B = TypeVar("B", covariant=True)
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")


__all__ = [
    "Projector",
    "Animation",
    "const_p",
    "map_p",
    "join_p",
    "flatmap_p",
    "par_p",
    "ease_p",
    "const_a",
    "seq_a",
    "flatmap_a",
    "par_a_longest",
    "par_a_shortest",
    "pause_after",
    "pause_before",
    "frames",
]


Projector = Callable[[float], A]


@dataclass(frozen=True)
class Animation(Generic[A]):
    """
    Animation with a given duration on a set A of still frames
    """

    duration: float
    "How long the animation lasts, in seconds"

    projector: Projector[A]
    "Strategy to get a still frame from a progress in [0; 1]"

    def __post_init__(self):
        if self.duration < 0.0:
            raise ValueError(f"{self!r}: duration is negative")

    def with_duration(self, duration: float) -> Animation[A]:
        """
        Return the same animatino, but with a new duration
        """
        return dataclass_replace(self, duration=duration)

    def with_projector(self, projector: Projector[B]) -> Animation[B]:
        """
        Return the same animation, but with a new projector
        """
        return Animation(self.duration, projector)

    def map(self, f: Callable[[A], B]) -> Animation[B]:
        """
        Apply a function to each frame of an animation
        """
        return self.map_projector(lambda p: map_p(p, f))

    def progress_map(self, f: Callable[[A, float], B]) -> Animation[B]:
        """
        Similar to [`map`][lanim.core.Animation.map], but also passes the `t`
        parameter to the provided function `f`.
        """
        return self.map_projector(lambda p: lambda t: f(p(t), t))

    def ease(self, easing: Easing) -> Animation[A]:
        """
        Apply an easing to an animation
        """
        return self.map_projector(lambda p: ease_p(p, easing))

    def map_projector(self, f: Callable[[Projector[A]], Projector[B]]) -> Animation[B]:
        """
        Apply a function to the projector
        """
        return self.with_projector(f(self.projector))

    def map_duration(self, f: Callable[[float], float]) -> Animation[A]:
        """
        Apply a function to the duration
        """
        return self.with_duration(f(self.duration))

    def __mul__(self, factor: float) -> Animation[A]:
        """
        Overloading of `self * factor`.

        Stretch the duration of the animation by `factor`
        """
        return self.with_duration(self.duration * factor)

    def __add__(self, other: Animation[B]) -> Animation[Union[A, B]]:
        """
        Overloading of `self + other`.

        Put one animation after the other
        """
        return seq_a(self, other)  # type: ignore

    @overload
    def __rshift__(self, other: Callable[[Animation[A]], B]) -> B: ...
    @overload
    def __rshift__(self, other: tuple[Callable[[Animation[A], C], D], C]) -> D: ...
    @overload
    def __rshift__(self, other: tuple[Callable[[Animation[A], B, C], D], B, C]) -> D: ...
    @overload
    def __rshift__(self, other: tuple[Callable[[Animation[A], B, C, D], E], B, C, D]) -> E: ...
    def __rshift__(self, other):
        """
        Overloading of `self >> other`.

        Apply a function in a pipes-and-filters style:

        - `self >> fn` means `fn(self)`
        - `self >> (fn, arg)` means `fn(self, arg)`
        - `self >> (fn, arg1, arg2)` means `fn(self, arg1, arg2)`
        - etc.
        """
        if hasattr(other, "__call__"):
            return other(self)
        if not isinstance(other, tuple):
            return NotImplemented
        fn, *args = other
        return fn(self, *args)


def const_p(a: C) -> Projector[C]:
    """
    Make a projector that always returns the same still frame
    """
    return lambda _: a


def map_p(proj: Projector[A], f: Callable[[A], B]) -> Projector[B]:
    """
    Apply a function to the result of a projector
    """
    return lambda t: f(proj(t))


def join_p(proj: Projector[Projector[A]]) -> Projector[A]:
    """
    Flatten a projector of projectors into just a projector
    """
    return lambda t: proj(t)(t)


def flatmap_p(proj: Projector[A], f: Callable[[A], Projector[B]]) -> Projector[B]:
    """
    Composition of `map_p` and `join_p`
    """
    return lambda t: f(proj(t))(t)


def par_p(pa: Projector[A], pb: Projector[B]) -> Projector[tuple[A, B]]:
    """
    Combine two projectors to create a projector of a tuple
    """
    return lambda t: (pa(t), pb(t))


def ease_p(proj: Projector[A], e: Easing) -> Projector[A]:
    """
    Apply an easing to a projector
    ```py
    >>> from lanim.easings import in_out
    >>> projector1 = lambda t: (3*t, 4*t)
    >>> projector2 = ease_p(projector1, in_out)
    >>> projector1(0.54)
    (1.62, 2.16)
    >>> projector2(0.54)
    (1.832, 2.443)
    ```
    """
    return lambda t: proj(e(t))


def const_a(a: C) -> Animation[C]:
    """
    Create a second-long animation consisting of a still frame
    """
    return Animation(1.0, const_p(a))


def seq_a(*animations: Animation[A]) -> Animation[A]:
    """
    Put animations in sequence, one after another.
    """
    if animations == ():
        raise ValueError("No animations")

    total = 0.0
    steps: list[tuple[float, float, Animation[A]]] = []
    for a in animations:
        dur = a.duration * 512
        steps.append((total, total+dur, a))
        total += dur

    # 100__________500________________1200
    #       +400             +700
    # (0, 100, ...), (400, 500, ...), (500, 1200, ...)

    def projector(t: float) -> A:
        for (begin, end, a) in reversed(steps):
            if begin <= t * total <= end:
                break
        t_offset = begin / total  # type: ignore
        t_delta = t - t_offset
        t_scale = total / (end - begin) # type: ignore

        # this is required to account for floating-point errors:
        t = max(0, min(1, t_scale * t_delta))
        return a.projector(t)  # type: ignore

    return Animation(sum(a.duration for a in animations), projector)


def _it_flatmap(it: Iterable[A], f: Callable[[A], Iterable[B]]) -> Iterator[B]:
    for a in it:
        yield from f(a)


def flatmap_a(
    animations: Iterable[Animation[A]],
    f: Callable[[Animation[A]], Iterable[Animation[B]]],
) -> Animation[B]:
    """
    For each animation `animations`, apply `f` to get a list of
    animations which in turn will be concatenated.
    """
    return seq_a(*_it_flatmap(animations, f))


def par_a_longest(anim1: Animation[A], anim2: Animation[B]) -> Animation[tuple[A, B]]:
    """
    Run two animations side by side.

    If one animation is longer than the other, the last frame of
    the shorter animation will be kept hanging.
    """
    duration = max(anim1.duration, anim2.duration)
    def projector(t: float) -> tuple[A, B]:
        t1 = t * min(1.0, duration / anim1.duration)
        t2 = t * min(1.0, duration / anim2.duration)
        return (anim1.projector(t1), anim2.projector(t2))
    return Animation(duration, projector)


def par_a_shortest(anim1: Animation[A], anim2: Animation[B]) -> Animation[tuple[A, B]]:
    """
    Run two animations side by side.

    If one animation is longer animation, the longer animation
    will be cut off when the short one ends.
    """
    duration = min(anim1.duration, anim2.duration)
    def projector(t: float) -> tuple[A, B]:
        t1 = t * duration / anim1.duration
        t2 = t * duration / anim2.duration
        return (anim1.projector(t1), anim2.projector(t2))
    return Animation(duration, projector)


def pause_after(anim: Animation[A], duration: float) -> Animation[A]:
    """
    Stretch the last frame for `duration` seconds after the
    animation is over.
    """
    last_frame = anim.projector(1.0)
    total_duration = duration + anim.duration
    def projector(t: float) -> A:
        if t < anim.duration / total_duration:
            return anim.projector(t * total_duration / anim.duration)
        else:
            return last_frame
    return Animation(total_duration, projector)


def pause_before(anim: Animation[A], duration: float) -> Animation[A]:
    """
    Stretch the first frame for `duration` seconds before the
    animation starts.
    """
    first_frame = anim.projector(0.0)
    total_duration = duration + anim.duration
    def projector(t: float) -> A:
        if t > duration / total_duration:
            return anim.projector((t - duration / total_duration) * total_duration / anim.duration)
        else:
            return first_frame
    return Animation(total_duration, projector)


def crop_by_range(anim: Animation[A], start: float, finish: float) -> Animation[A]:
    """
    Render a range of an animation.
    `start` and `finish` should be floats from 0 to 1.
    """
    if not (0 <= start < finish <= 1):
        raise ValueError(
            "Invalid range ({}, {}). Expected 0 <= start <= finish < 1"
            .format(start, finish)
        )
    scale_factor = finish - start
    new_duration = anim.duration * scale_factor

    def projector(t: float) -> A:
        return anim.projector(t * scale_factor + start)

    return Animation(new_duration, projector)


def frames(animation: Animation[A], fps: float) -> Iterator[A]:
    """
    Generate a series of discrete frames from an animation given
    the frames per second.
    """
    total_steps = round(fps * animation.duration)
    for step in range(total_steps + 1):
        yield animation.projector(step / total_steps)
