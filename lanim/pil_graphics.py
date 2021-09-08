from __future__ import annotations
from functools import reduce

from lanim.pil_machinery import render_pil
from lanim.pil_types import *

import random
from immutables import Map
import math
from typing import Any, Callable, Protocol, TYPE_CHECKING, Union, TypeVar
from lanim import anim
from lanim.anim import Animation, Projector, ease_p, map_a
from lanim import easings


N = TypeVar("N", bound=PilRenderable, covariant=True)
M = TypeVar("M", bound=PilRenderable, covariant=True)


def moved_to(p: P, x: float, y: float) -> P:
    return p.moved(x - p.x, y - p.y)


# Fundamental animation constructions:

def morph_into(source: PX, destination: PX) -> Animation[PX]:
    return Animation(1.0, lambda t: source.morphed(destination, t))


def move_by(obj: PX, dx: float, dy: float) -> Animation[PX]:
    return morph_into(obj, obj.moved(dx, dy))


def scale(obj: PSX, factor: float) -> Animation[PSX]:
    return morph_into(obj, obj.scaled(factor))


def scale_about(obj: PSX, factor: float) -> Animation[PSX]:
    return morph_into(obj, obj.scaled(factor))


def align(obj: PAX, new_align: Align) -> Animation[PAX]:
    return morph_into(obj, obj.aligned(new_align))


def partition(anim: Animation[A]) -> tuple[Animation[A], A]:
    return anim, anim.projector(1.0)



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
    return lambda x1, y1, x2, y2, t: traj(x1, y1, x2, y2, easing(t))


def move_t(obj: PX, dest_x: float, dest_y: float, traj: Trajectory) -> Animation[PX]:
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
    phi = math.atan2(y2 - y1, x2 - x1) + math.pi/2
    return (math.cos(phi), math.sin(phi))


def make_arc_traj(distancing_function: Callable[[float], float]) -> Trajectory:
    """
    Make an arc trajectory using a distancing function.

            ^^^^^^^^^^^^       _
         ^^^            ^^^    | distancing_function(t)
        ^                  ^   _
       A--------------------B
    (x1,y1)              (x2,y2)
      t=0       t=0.5      t=1
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
    return map_a(ap, lambda p: Pair(p, q))


def rpair(p: P, aq: Animation[Q]) -> Animation[Pair[P, Q]]:
    return map_a(aq, lambda q: Pair(p, q))


def lrpair(ap: Animation[P], aq: Animation[Q]) -> Animation[Pair[P, Q]]:
    return map_a(par_a_longest(ap, aq), lambda pq: Pair(*pq))


# Group-relatd functions:


def gbackground(a: Animation[P], group: Group[Q]) -> Animation[Group[Union[P, Q]]]:
    return anim.map_a(a, group.add)


def background(fg: Animation[P], *bg: Q) -> Animation[Group[Union[P, Q]]]:
    return anim.map_a(fg, lambda p: Group((p, *bg)))


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
    return map_a(parallel(*animations), group_join)


def par_and_bg(fg: Sequence[Animation[N]], bg: Sequence[N]) -> Animation[Group[N]]:
    return map_a(background(parallel(*fg), Group(bg)), group_join)


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


def with_last_frame(animation: Animation[A], a: A) -> Animation[A]:
    def projector(t: float):
        if t < 1.0:
            return animation.projector(t)
        else:
            return a
    return animation.with_projector(projector)


def swap(g: Group[PX], index1: int, index2: int, traj1: Trajectory = linear_traj, traj2: Trajectory = linear_traj) -> Animation[Group[PX]]:
    items = list(g.items)
    items[index1], items[index2] = (
        moved_to(items[index2], items[index1].x, items[index1].y),
        moved_to(items[index1], items[index2].x, items[index2].y),
    )
    final_group = Group(items)

    proj1 = proj_t(g.items[index1], g.items[index2].x, g.items[index2].y, traj1)
    proj2 = proj_t(g.items[index2], g.items[index1].x, g.items[index1].y, traj2)

    def projector(t: float) -> Group[PX]:
        items = list(g.items)
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
    return appear(p) @ easings.invert


def appear_from(p: PSX, x: float, y: float) -> Animation[PSX]:
    return morph_into(p.scaled_about(0.0, x, y), p)


def disappear_from(p: PSX, x: float, y: float) -> Animation[PSX]:
    return appear_from(p, x, y) @ easings.invert


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


def scene_any(easing: easings.Easing = easings.in_out, duration: float = 1.0):
    def _(f: Callable[[ThenAny], Any]) -> Animation[PilRenderable]:
        animations: list[Animation[PilRenderable]] = []
        def on_animate(a: Animation[Q]) -> Q:
            animations.append((a @ easing) * duration)
            return a.projector(1.0)
        f(on_animate)
        return anim.seq_a(*animations)
    return _


def scene(
    easing: easings.Easing = ...,
    duration: float = ...
) -> Callable[[Callable[[Then[P]], Any]], Animation[P]]: ...

if not TYPE_CHECKING:
    scene = scene_any
