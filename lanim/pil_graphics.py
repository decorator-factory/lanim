from __future__ import annotations

from lanim.pil_types import *

import math
from typing import Any, Callable, Iterable, Protocol, TYPE_CHECKING, Union, TypeVar
from lanim.core import Animation, Projector, ease_p, par_a_longest, par_a_shortest, seq_a
from lanim import easings

__all__ = (
    "moved_to",
    "morph_into",
    "move_by",
    "scale",
    "align",
    "Trajectory",
    "ease_t",
    "move_t",
    "proj_t",
    "linear_traj",
    "make_arc_traj",
    "halfcircle_traj",
    "low_arc_traj",
    "lift_traj",
    "lpair",
    "rpair",
    "lrpair_longest",
    "lrpair_shortest",
    "gbackground",
    "gforeground",
    "group_join",
    "mixed_group_join",
    "merge_group_animations",
    "parallel",
    "group",
    "with_last_frame",
    "swap",
    "Maybe",
    "m_just",
    "m_none",
    "appear",
    "appear_from",
    "disappear",
    "disappear_from",
    "disappear_into_nil",
    "appear_from_nil",
    "ThenAny",
    "Then",
    "scene_any",
    "scene",
    "progression",
)


N = TypeVar("N", bound=PilRenderable, covariant=True)
M = TypeVar("M", bound=PilRenderable, covariant=True)


def moved_to(p: P, x: float, y: float) -> P:
    """
    Return the object moved to a particular point.
    """
    return p.moved(x - p.x, y - p.y)


# Fundamental animation constructions:

def morph_into(source: PX, destination: PX) -> Animation[PX]:
    """
    Create a second-long animation of one object morphing into the other
    """
    return Animation(1.0, lambda t: source.morphed(destination, t))


def move_by(obj: PX, dx: float, dy: float) -> Animation[PX]:
    """
    Create a second-long animation of an object moving by (`dx`, `dy`)
    """
    return morph_into(obj, obj.moved(dx, dy))


def scale(obj: PSX, factor: float) -> Animation[PSX]:
    """
    Create a second-long animation of an object scaling `factor` times
    """
    return morph_into(obj, obj.scaled(factor))


def align(obj: PAX, new_align: Align) -> Animation[PAX]:
    """
    Create a second-long animation of an object changing alignment
    """
    return morph_into(obj, obj.aligned(new_align))


# Movement:

class Trajectory(Protocol):
    """
    A trajectory is a way of interpolating between two points
    """
    def __call__(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        t: float
    ) -> tuple[float, float]:
        ...


def ease_t(traj: Trajectory, easing: easings.Easing) -> Trajectory:
    """
    Apply an easing to a trajectory
    """
    return lambda x1, y1, x2, y2, t: traj(x1, y1, x2, y2, easing(t))


def move_t(obj: PX, dest_x: float, dest_y: float, traj: Trajectory) -> Animation[PX]:
    """
    Create a second-long animation of an object moving along a trajectory
    from `dest_x` to `dest_y`
    """
    return Animation(1.0, proj_t(obj, dest_x, dest_y, traj))


def proj_t(obj: PX, dest_x: float, dest_y: float, traj: Trajectory) -> Projector[PX]:
    def projector(t: float) -> PX:
        x, y  = traj(obj.x, obj.y, dest_x, dest_y, t)
        return obj.moved(x - obj.x, y - obj.y)
    return projector


linear_traj: Trajectory = \
    lambda x1, y1, x2, y2, t: (
        x1 * (1 - t) + x2 * t,
        y1 * (1 - t) + y2 * t,
    )


def normal(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
    """
    Compute the normal vector given two points
    """
    phi = math.atan2(y2 - y1, x2 - x1) + math.pi/2
    return (math.cos(phi), math.sin(phi))


def make_arc_traj(distancing_function: Callable[[float], float]) -> Trajectory:
    """
    Make an arc trajectory using a distancing function.

    ```
            ^^^^^^^^^^^^       _
         ^^^            ^^^    | distancing_function(t)
        ^                  ^   _
       A--------------------B
    (x1,y1)              (x2,y2)
      t=0       t=0.5      t=1
    ```
    """
    def _traj(x1: float, y1: float, x2: float, y2: float, t: float) -> tuple[float, float]:
        nx, ny = normal(x1, y1, x2, y2)
        lx, ly = linear_traj(x1, y1, x2, y2, t)
        arm = distancing_function(t) * math.sqrt((x2 - x1)**2 + (y2 - y1)**2) / 2
        mx, my = lx + arm*nx, ly + arm*ny
        return (mx, my)
    return _traj
halfcircle_traj: Trajectory = make_arc_traj(lambda t: math.sqrt(1 - (2*t - 1)**2))
low_arc_traj: Trajectory = make_arc_traj(lambda t: t*(1 - t)*2)


def lift_traj(height: float) -> Trajectory:
    """
    Lift the trajectory up by `height` units
    """
    def traj(x1: float, y1: float, x2: float, y2: float, t: float):
        if t < 0.25:
            k = t * 4
            return (x1, y1 - height * k)
        elif t < 0.75:
            k = 2 * (t - 0.25)
            return (x1 * (1 - k) + x2 * k, y1 - height)
        else:
            k = 4 * (t - 0.75)
            return (x2, (y1 - height) * (1 - k) + y2 * k)
    return traj


# Pair-related functions:

def lpair(ap: Animation[P], q: Q) -> Animation[Pair[P, Q]]:
    """
    Add `Q` as a still image to an animation of P
    """
    return ap.map(lambda p: Pair(p, q))


def rpair(p: P, aq: Animation[Q]) -> Animation[Pair[P, Q]]:
    """
    Add `P` as a still image to an animation of Q
    """
    return aq.map(lambda q: Pair(p, q))


def lrpair_longest(ap: Animation[P], aq: Animation[Q]) -> Animation[Pair[P, Q]]:
    """
    Combine two animations into an animation of a pair.

    If one animation is longer, the other animation is extended.
    """
    return par_a_longest(ap, aq).map(lambda pq: Pair(*pq))


def lrpair_shortest(ap: Animation[P], aq: Animation[Q]) -> Animation[Pair[P, Q]]:
    """
    Combine two animations into an animation of a pair.

    If one animation is longer, it's cut off.
    """
    return par_a_shortest(ap, aq).map(lambda pq: Pair(*pq))


# Group-relatd functions:

def gbackground(fg: Animation[P], bg: Iterable[Q]) -> Animation[Pair[Group[Q], P]]:
    bg_list = list(bg)
    return fg.map(lambda p: Pair(Group(bg_list), p))


def gforeground(bg: Animation[P], fg: Iterable[Q]) -> Animation[Pair[P, Group[Q]]]:
    fg_list = list(fg)
    return bg.map(lambda q: Pair(q, Group(fg_list)))


def group_join(g: Group[Group[N]]) -> Group[N]:
    items: list[N] = []
    for subg in g.items:
        items.extend(subg.items)
    return Group(items)


def mixed_group_join(g: Group[Union[N, Group[N]]]) -> Group[N]:
    items: list[N] = []
    for item in g.items:
        if isinstance(item, Group):
            items.extend(item.items)
        else:
            items.append(item)
    return Group(items)


def merge_group_animations(*animations: Animation[Group[N]]) -> Animation[Group[N]]:
    return parallel(*animations).map(group_join)


def parallel(*animations: Animation[P]) -> Animation[Group[P]]:
    if animations == ():
        raise ValueError("No animations!")
    duration = max(animation.duration for animation in animations)
    factors = [duration / animation.duration for animation in animations]
    def projector(t: float) -> Group[P]:
        return Group([a.projector(t * f if t < 1/f else 1.0) for (a, f) in zip(animations, factors)])

    return Animation(duration, projector)

def group(*ps: P) -> Group[P]:
    return Group(ps)


def with_last_frame(animation: Animation[A], last_frame: A) -> Animation[A]:
    """
    Return the same animation but with the very last frame replaced
    """
    def projector(t: float):
        if t < 1.0:
            return animation.projector(t)
        else:
            return last_frame
    return animation.with_projector(projector)


def swap(
    group: Group[PX],
    index1: int,
    index2: int,
    traj1: Trajectory = linear_traj,
    traj2: Trajectory = linear_traj
) -> Animation[Group[PX]]:
    """
    Swap two items in a group, one being at index `index1` and another at `index2`.
    The resulting animation lasts one second.

    By default the objects will move towards each other in a straight line,
    but you can customize this behaviour by providing the `traj1` and `traj2`
    parameters for the first and second object respectively
    """
    items = list(group.items)
    items[index1], items[index2] = (
        moved_to(items[index2], items[index1].x, items[index1].y),
        moved_to(items[index1], items[index2].x, items[index2].y),
    )
    final_group = Group(items)

    proj1 = proj_t(group.items[index1], group.items[index2].x, group.items[index2].y, traj1)
    proj2 = proj_t(group.items[index2], group.items[index1].x, group.items[index1].y, traj2)

    def projector(t: float) -> Group[PX]:
        items = list(group.items)
        items[index1] = proj1(t)
        items[index2] = proj2(t)
        return Group(items)

    return with_last_frame(Animation(1.0, projector), final_group)



# Sum-related functions:


Maybe = Sum[PSX, Nil]


def m_just(p: PSX) -> Maybe[PSX]:
    return Sum(("p", p), disappear_into_nil)


def m_none(x: float, y: float) -> Maybe[PSX]:
    return Sum(("q", Nil(x, y)), disappear_into_nil)


# Appearing and disappearing:

def appear(p: PSX) -> Animation[PSX]:
    return morph_into(p.scaled(0.0), p)


def disappear(p: PSX) -> Animation[PSX]:
    return appear(p).ease(easings.invert)


def appear_from(p: PSX, x: float, y: float) -> Animation[PSX]:
    return morph_into(p.scaled_about(0.0, x, y), p)


def disappear_from(p: PSX, x: float, y: float) -> Animation[PSX]:
    return appear_from(p, x, y).ease(easings.invert)


def disappear_into_nil(p: PSX, nil: Nil) -> Projector[Select[PSX, Nil]]:
    def projector(t: float) -> Select[PSX, Nil]:
        if t == 1.0:
            return ("q", nil)
        else:
            return ("p", p.morphed(p.scaled_about(0.0, nil.x, nil.y), t))
    return projector


def appear_from_nil(p: PSX, nil: Nil) -> Projector[Select[PSX, Nil]]:
    return ease_p(disappear_into_nil(p, nil), easings.invert)



# Imperative API:

class ThenAny(Protocol):
    def __call__(self, a: Animation[P]) -> P: ...


class Then(Protocol[P]):
    def __call__(self, a: Animation[P]) -> P: ...


def scene_any(easing: easings.Easing = easings.linear, duration: float = 1.0):
    """
    Decorator used for making an imperative-feeling scene.

    The decorated function should accept a single argument --- a function ---
    which it can call with an animation. That function will return the last
    frame of the animation and add it to an internal animation list, which
    will be rendered using [lanim.core.seq_a][].

    The decorated function will be replaced with the generated animation.
    """
    def _(f: Callable[[ThenAny], Any]) -> Animation[PilRenderable]:
        animations: list[Animation[PilRenderable]] = []
        def on_animate(a: Animation[Q]) -> Q:
            animations.append(a.ease(easing) * duration)
            return a.projector(1.0)
        f(on_animate)
        return seq_a(*animations)
    return _


def scene(
    easing: easings.Easing = ...,
    duration: float = ...
) -> Callable[[Callable[[Then[P]], Any]], Animation[P]]: ...

if not TYPE_CHECKING:
    scene = scene_any


T = TypeVar("T")


def progression(
    step: Callable[[P, T], Animation[P]],
    initial: P,
    items: Iterable[T],
    then: Union[Then[P], ThenAny],
) -> P:
    """
    Given a step function and a sequence of element, produce an sequence
    of animations produced by the step function on each step. The step
    function will receive the current state (of type `P`) and an element
    (of type `T`).

    This essentially implements the 'reduce' pattern, but also calls `then`.

    This is similar to `foldM` in Haskell/Scala.
    """
    acc = initial
    for item in items:
        acc = then(step(acc, item))
    return acc
