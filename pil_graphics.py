from __future__ import annotations

from pil_machinery import render_pil
from pil_types import *

from typing import Any, Callable, Protocol, TYPE_CHECKING, Union
import anim
from anim import Animation, map_a
import easings


__all__ = [
    "render_pil",
    "partition",
    "background",
    "gbackground",
    "group_join",
    "mixed_group_join",
    "merge_group_animations",
    "group",
    "parallel",
    "appear",
    "par_and_bg",
    "appear_from",
    "Then",
    "ThenAny",
    "scene",
    "scene_any",
]



N = TypeVar("N", bound=PilRenderable, covariant=True)
M = TypeVar("M", bound=PilRenderable, covariant=True)


def partition(anim: Animation[A]) -> tuple[Animation[A], A]:
    return anim, anim.projector(1.0)


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


def appear(p: PSX) -> Animation[PSX]:
    return morph_into(p.scaled(0.0), (p))


def appear_from(p: PSX, x: float, y: float) -> Animation[PSX]:
    return morph_into(p.scaled_about(0.0, x, y), p)


class ThenAny(Protocol):
    def __call__(self, a: Animation[P]) -> P: ...


class Then(Protocol[P]):
    def __call__(self, a: Animation[P]) -> P: ...


def group(*ps: P) -> Group[P]:
    return Group(ps)


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
