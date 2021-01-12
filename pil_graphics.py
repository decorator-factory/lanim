from __future__ import annotations

from dataclasses import dataclass, field
from itertools import repeat
from typing import Any, Callable, ClassVar, Generic, Iterable, Iterator, Literal, NoReturn, Optional, Protocol, Sequence, TYPE_CHECKING, TypeVar, Union, Generator, overload
from PIL import Image, ImageDraw
from pathlib import Path
from threading import Thread
from queue import Queue
from pil_utils import render_latex_scaled
import time
import anim
from anim import Animation, const_a
import easings


@dataclass(frozen=True)
class Style:
    fill: Optional[Union[str, int]]
    outline: Optional[Union[str, int]]
    line_width: int

    default: ClassVar[Style]

Style.default = Style(fill=None, outline=0xffffff, line_width=4)  # type: ignore


@dataclass(frozen=True)
class PilSettings:
    width: int
    height: int
    center_x: int
    center_y: int
    unit: int

    def make_ctx(self) -> PilContext:
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.ImageDraw(img) # type: ignore
        return PilContext(self, img, draw)


@dataclass(frozen=True)
class PilContext:
    settings: PilSettings
    img: Image.Image
    draw: ImageDraw.ImageDraw

    def coord(self, x: float, y: float) -> tuple[int, int]:
        pixels_x = self.settings.center_x + self.settings.unit * x
        pixels_y = self.settings.center_y + self.settings.unit * y
        return round(pixels_x), round(pixels_y)

    def rectangle_wh(self, cx: float, cy: float, width: float, height: float, style: Style = Style.default):
        self.rectangle(cx - width/2, cy - height/2, cx + width/2, cy + height/2, style)

    def rectangle(self, x1: float, y1: float, x2: float, y2: float, style: Style = Style.default):
        self.draw.rectangle(
            (self.coord(x1, y1), self.coord(x2, y2) ),
            fill=style.fill,
            outline=style.outline,
            width=style.line_width,
        )


class PilRenderable(Protocol):
    def render_pil(self, ctx: PilContext) -> None: ...

A = TypeVar("A")
B = TypeVar("B")
P = TypeVar("P", bound=PilRenderable)
P_co = TypeVar("P_co", bound=PilRenderable, covariant=True)
P_contra = TypeVar("P_contra", bound=PilRenderable, contravariant=True)
Q = TypeVar("Q", bound=PilRenderable)
R = TypeVar("R", bound=PilRenderable)


class HasPosition(PilRenderable, Protocol):
    x: float
    y: float


class Movable(HasPosition, Protocol):
    def moved(self: A, dx: float, dy: float) -> A: ...


class Scalable(HasPosition, Protocol):
    def scaled(self: A, factor: float) -> A: ...
    def scaled_about(self: A, factor: float, cx: float, cy: float) -> A: ...

class Morphable(PilRenderable, Protocol):
    def morph_into(self: A, other: A) -> Animation[A]: ...

class ScalableMovable(Scalable, Movable, Protocol):
    pass

class ScalableMorphable(Scalable, Morphable, Protocol):
    pass

class MovableMorphable(Movable, Morphable, Protocol):
    pass

class ScalableMovableMorphable(Scalable, Movable, Morphable, Protocol):
    pass

PP = TypeVar("PP", bound=HasPosition)
PS = TypeVar("PS", bound=Scalable)
PM = TypeVar("PM", bound=Movable)
PX = TypeVar("PX", bound=Morphable)
PSM = TypeVar("PSM", bound=ScalableMovable)
PMX = TypeVar("PMX", bound=MovableMorphable)
PSX = TypeVar("PSX", bound=ScalableMorphable)
PSMX = TypeVar("PSMX", bound=ScalableMovableMorphable)


def move_by(obj: PMX, dx: float, dy: float) -> Animation[PMX]:
    return obj.morph_into(obj.moved(dx, dy))


def scale(obj: PSX, factor: float) -> Animation[PSX]:
    return obj.morph_into(obj.scaled(factor))


def scale_about(obj: PSX, factor: float) -> Animation[PSX]:
    return obj.morph_into(obj.scaled(factor))


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    def scaled(self, factor: float) -> Rect:
        return Rect(self.x, self.y, self.width * factor, self.height * factor)

    def moved(self, dx: float, dy: float) -> Rect:
        return Rect(self.x + dx, self.y + dy, self.width, self.height)

    def scaled_about(self, factor: float, cx: float, cy: float) -> Rect:
        dx = self.x - cx
        dy = self.y - cy
        new_x = cx + dx*factor
        new_y = cy + dy*factor
        return Rect(new_x, new_y, self.width*factor, self.height*factor)

    def move_by(self, dx: float, dy: float) -> Animation[Rect]:
        return self.morph_into(self.moved(dx, dy))

    def move_to(self, x: float, y: float) -> Animation[Rect]:
        return self.move_by(x - self.x, y - self.y)

    def morph_into(self, other: Rect) -> Animation[Rect]:
        def projector(t: float):
            return Rect(
                self.x * (1 - t) + other.x * t,
                self.y * (1 - t) + other.y * t,
                self.width * (1 - t) + other.width * t,
                self.height * (1 - t) + other.height * t,
            )
        return Animation(1.0, projector)

    def render_pil(self, ctx: PilContext) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        ctx.rectangle_wh(
            self.x, self.y, self.width, self.height,
            style=Style(fill=None, outline=0xffffff, line_width=4),
        )


@dataclass(frozen=True)
class Group(Generic[P]):
    items: Sequence[P]

    if TYPE_CHECKING:
        x: float = field(init = False)
        y: float = field(init = False)
    else:
        @property
        def x(self) -> float:
            return self.center()[0]

        @property
        def y(self) -> float:
            return self.center()[1]

    def morph_into(self: Group[PX], other: Group[PX]) -> Animation[Group[PX]]:
        if len(self.items) != len(other.items):
            raise NotImplementedError("Morphing groups with different lengths isn't implemented yet")
        animations = [
            item_a.morph_into(item_b)
            for (item_a, item_b) in zip(self.items, other.items)
        ]
        def projector(t: float) -> Group[PX]:
            return Group([a.projector(t) for a in animations])
        return Animation(1.0, projector)

    def __iter__(self) -> Iterator[P]:
        return iter(self.items)

    def center(self) -> tuple[float, float]:
        if len(self.items) == 0:
            raise ValueError(f"Cannot find a center of an empty group, items: {self.items!r}")
        cx = sum(item.x for item in self.items)/len(self.items)  # type: ignore
        cy = sum(item.y for item in self.items)/len(self.items)  # type: ignore
        return (cx, cy)

    def moved(self: Group[PM], dx: float, dy: float) -> Group[PM]:
        return Group([item.moved(dx, dy) for item in self.items])

    def scaled_about(self: Group[PS], factor: float, cx: float, cy: float) -> Group[PS]:
        return Group([item.scaled_about(factor, cx, cy) for item in self.items])

    def scaled(self: Group[PS], factor: float) -> Group[PS]:
        return self.scaled_about(factor, *self.center())

    def add(self: Group[P], new_item: Q) -> Group[Union[P, Q]]:
        return Group([*self.items, new_item])

    def concat(self: Group[P], other: Group[Q]) -> Group[Union[P, Q]]:
        return Group([*self.items, *other.items])

    def render_pil(self, ctx: PilContext) -> None:
        for item in self.items:
            item.render_pil(ctx)


@dataclass(frozen=True)
class Latex:
    x: float
    y: float
    source: str
    scale_factor: float = 1.0

    def morph_into(self, other: Latex) -> Animation[Latex]:
        if other.source != self.source:
            raise NotImplementedError("Morphing of Latex with different source isn't implemented yet")
        def projector(t: float) -> Latex:
            return Latex(
                self.x * (1 - t) + other.x * t,
                self.y * (1 - t) + other.y * t,
                other.source,
                self.scale_factor * (1 - t) + other.scale_factor * t
            )
        return Animation(1.0, projector)

    def scale_upto(self, factor: float) -> Animation[Latex]:
        return self.morph_into(Latex(self.x, self.y, self.source, factor))

    def scaled(self, factor: float) -> Latex:
        return Latex(self.x, self.y, self.source, self.scale_factor * factor)

    def scaled_about(self, factor: float, cx: float, cy: float) -> Latex:
        dx = self.x - cx
        dy = self.y - cy
        new_x = cx + dx*factor
        new_y = cy + dy*factor
        return Latex(new_x, new_y, self.source, self.scale_factor * factor)

    def moved(self, dx: float, dy: float) -> Latex:
        return Latex(self.x + dx, self.y + dy, self.source, self.scale_factor)

    def render_pil(self, ctx: PilContext) -> None:
        scale_factor = self.scale_factor * (ctx.settings.width / 1920)
        if scale_factor <= 0.025:
            return
        img = render_latex_scaled(self.source, scale_factor)
        x, y = ctx.coord(self.x, self.y)
        ctx.draw.bitmap((x - img.width//2, y - img.height//2), img)


ImageQ = Queue[Union[Literal["stop"], tuple[int, Image.Image]]]


def render_pil(animation: Animation[PilRenderable], path: Path, fps: float, workers: int):
    path.mkdir(parents=True, exist_ok=True)

    WIDTH = 864
    HEIGHT = round(WIDTH * 9 / 16)

    settings = PilSettings(
        width=WIDTH, height=HEIGHT,
        center_x=WIDTH//2, center_y=HEIGHT//2,
        unit=WIDTH//16
    )

    print(f"Rendering animation {WIDTH}x{HEIGHT} {animation.duration}s @{fps}FPS")

    jobs = [[] for _ in range(workers)]

    for (i, frame) in enumerate(anim.frames(animation, fps)):
        jobs[i % workers].append((i, frame))

    queue: ImageQ = Queue()
    frame_rendering_threads: list[Thread] = []
    png_rendering_threads: list[Thread] = []

    t1 = time.time()
    for (n, job) in enumerate(jobs):
        print(f"Starting job {n} with {len(job)} frames...")
        thread = Thread(target=_render_frames, args=(job, settings, queue), daemon=True)
        thread.start()
        frame_rendering_threads.append(thread)

    for n in range(workers):
        thread = Thread(target=_save_frame_to_file, args=(path, queue), daemon=True)
        thread.start()
        png_rendering_threads.append(thread)

    for (n, thread) in enumerate(frame_rendering_threads):
        print(f"Waiting for frame-job {n}...")
        thread.join()

    for n in range(workers):
        queue.put("stop", block=True)

    for (n, thread) in enumerate(png_rendering_threads):
        print(f"Waiting for png-job {n}...")
        thread.join()

    t2 = time.time()
    print(f"Time taken: {t2 - t1:.2f}s")
    return t2 - t1


def _save_frame_to_file(path: Path, queue: ImageQ):
    while True:
        item = queue.get()
        if item == "stop":
            break
        i, image = item
        image.copy().save(path / f"frame_{i}.png", format="PNG")


def _render_frames(frames: Iterable[tuple[int, PilRenderable]], settings: PilSettings, queue: ImageQ):
    ctx = settings.make_ctx()
    for (i, frame) in frames:
        ctx.draw.rectangle((0, 0) + ctx.img.size, fill=(0, 0, 0, 255))
        frame.render_pil(ctx)
        queue.put((i, ctx.img.copy()), block=True)


def partition(anim: Animation[A]) -> tuple[Animation[A], A]:
    return anim, anim.projector(1.0)


def background(a: Animation[P], group: Group[Q]) -> Animation[Group[Union[P, Q]]]:
    return anim.map_a(a, group.add)


def parallel(*animations: Animation[P]) -> Animation[Group[P]]:
    if animations == ():
        raise ValueError("No animations!")
    duration = max(animation.duration for animation in animations)
    factors = [duration / animation.duration for animation in animations]
    def projector(t: float) -> Group[P]:
        return Group([a.projector(t * f if t < 1/f else 1.0) for (a, f) in zip(animations, factors)])

    return Animation(duration, projector)


def appear(p: PSX) -> Animation[PSX]:
    return p.scaled(0.0).morph_into(p)


def appear_from(p: PSX, x: float, y: float) -> Animation[PSX]:
    return p.scaled_about(0.0, x, y).morph_into(p)


class ThenAny(Protocol):
    def __call__(self, a: Animation[P]) -> P: ...


class Then(Protocol[P]):
    def __call__(self, a: Animation[P]) -> P: ...


def scene_any(easing: easings.Easing = easings.linear, duration: float = 1.0): # type: ignore
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


if __name__ == "__main__":
    import sys

    @scene()
    def base(then: Then[Group[Latex]]):
        @scene(easings.in_out)
        def a_to_b__appears(then: Then[Latex]):
            a_to_b1 = then(appear(Latex(-2.0, 0.5, R"$A \implies B$", 0.75)) * 2)
            a_to_b2 = then(move_by(a_to_b1, -2.0, 0.0))
            a_to_b3 = then(move_by(a_to_b2, -1.0, -2.5))

        @scene(easings.in_out)
        def b_to_a__appears(then: Then[Latex]):
            b_to_a1 = then(appear(Latex(2.0, -0.5, R"$B \implies A$", 0.75)) * 2)
            b_to_a2 = then(move_by(b_to_a1, 2.0, 0.0))
            b_to_a3 = then(move_by(b_to_a2, 1.0, 2.5))

        two_equations = then(parallel(a_to_b__appears, b_to_a__appears))
        then(const_a(two_equations) * 0.5)
        then(scale(two_equations, 0.0) @ easings.in_out)

    animation = base >> (anim.pause_before, 0.5) >> (anim.pause_after, 0.5)

    render_pil(
        anim.seq_a(animation, animation, animation),
        Path("./out"),
        fps=int(sys.argv[1]),
        workers=4
    )
