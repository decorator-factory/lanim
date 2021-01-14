from __future__ import annotations

from dataclasses import dataclass, field
from itertools import repeat
from typing import Callable, ClassVar, Generic, Iterator, Literal, Optional, Protocol, Sequence, TYPE_CHECKING, TypeVar, Union, overload
from PIL import Image, ImageDraw
from pil_utils import render_latex_scaled
from anim import Animation, map_a, par_a_longest, par_a_shortest

@dataclass
class Align:
    dx: float
    dy: float

    CC: ClassVar[Align]
    LC: ClassVar[Align]
    RC: ClassVar[Align]
    CU: ClassVar[Align]
    LU: ClassVar[Align]
    RU: ClassVar[Align]
    CD: ClassVar[Align]
    LD: ClassVar[Align]
    RD: ClassVar[Align]

    def blend(self, other: Align, t: float) -> Align:
        return Align(self.dx * (1 - t) + other.dx * t, self.dy * (1 - t) + other.dy * t)

    def apply(self, x: float, y: float, width: float, height: float) -> tuple[float, float]:
        return x + self.dx * width, y + self.dy * height


Align.CC = Align(-1/2, -1/2)
Align.LC = Align(   0, -1/2)
Align.RC = Align(  -1, -1/2)
Align.CU = Align(-1/2,    0)
Align.LU = Align(   0,    0)
Align.RU = Align(  -1,    0)
Align.CD = Align(-1/2,   -1)
Align.LD = Align(   0,   -1)
Align.RD = Align(  -1,   -1)


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
    x: float
    y: float

    def moved(self: A, dx: float, dy: float) -> A: ...
    def render_pil(self, ctx: PilContext) -> None: ...

A = TypeVar("A")
B = TypeVar("B")
P = TypeVar("P", bound=PilRenderable)
Q = TypeVar("Q", bound=PilRenderable)
R = TypeVar("R", bound=PilRenderable)
R2 = TypeVar("R2", bound=PilRenderable)
R3 = TypeVar("R3", bound=PilRenderable)

class Scalable(PilRenderable, Protocol):
    def scaled(self: A, factor: float) -> A: ...
    def scaled_about(self: A, factor: float, cx: float, cy: float) -> A: ...

class Morphable(PilRenderable, Protocol):
    def morph_into(self: A, other: A) -> Animation[A]: ...

class Alignable(PilRenderable, Protocol):
    def aligned(self: A, new_align: Align) -> A: ...

class AlignableMorphable(Alignable, Morphable, Protocol):
    pass

class ScalableMorphable(Scalable, Morphable, Protocol):
    pass


PA = TypeVar("PA", bound=Alignable)
PS = TypeVar("PS", bound=Scalable)
QS = TypeVar("QS", bound=Scalable)
RS = TypeVar("RS", bound=Scalable)
RS2 = TypeVar("RS2", bound=Scalable)
RS3 = TypeVar("RS3", bound=Scalable)
PX = TypeVar("PX", bound=Morphable)
QX = TypeVar("QX", bound=Morphable)
RX = TypeVar("RX", bound=Morphable)
RX2 = TypeVar("RX2", bound=Morphable)
RX3 = TypeVar("RX3", bound=Morphable)
PSX = TypeVar("PSX", bound=ScalableMorphable)
QSX = TypeVar("QSX", bound=ScalableMorphable)
RSX = TypeVar("RSX", bound=ScalableMorphable)
RSX2 = TypeVar("RSX2", bound=ScalableMorphable)
RSX3 = TypeVar("RSX3", bound=ScalableMorphable)
PAX = TypeVar("PAX", bound=AlignableMorphable)
QAX = TypeVar("QAX", bound=AlignableMorphable)
RAX = TypeVar("RAX", bound=AlignableMorphable)
RAX2 = TypeVar("RAX2", bound=AlignableMorphable)
RAX3 = TypeVar("RAX3", bound=AlignableMorphable)


def move_by(obj: PX, dx: float, dy: float) -> Animation[PX]:
    return obj.morph_into(obj.moved(dx, dy))


def scale(obj: PSX, factor: float) -> Animation[PSX]:
    return obj.morph_into(obj.scaled(factor))


def scale_about(obj: PSX, factor: float) -> Animation[PSX]:
    return obj.morph_into(obj.scaled(factor))


def align(obj: PAX, new_align: Align) -> Animation[PAX]:
    return obj.morph_into(obj.aligned(new_align))


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float
    line_width: float = 1

    def scaled(self, factor: float) -> Rect:
        return Rect(self.x, self.y, self.width * factor, self.height * factor, self.line_width)

    def moved(self, dx: float, dy: float) -> Rect:
        return Rect(self.x + dx, self.y + dy, self.width, self.height, self.line_width)

    def scaled_about(self, factor: float, cx: float, cy: float) -> Rect:
        dx = self.x - cx
        dy = self.y - cy
        new_x = cx + dx*factor
        new_y = cy + dy*factor
        return Rect(new_x, new_y, self.width*factor, self.height*factor, self.line_width)

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
                self.line_width * (1 - t) + other.line_width * t
            )
        return Animation(1.0, projector)

    def render_pil(self, ctx: PilContext) -> None:
        if self.width <= 0 or self.height <= 0:
            return
        ctx.rectangle_wh(
            self.x, self.y, self.width, self.height,
            style=Style(
                fill=None,
                outline=0xffffff,
                line_width=max(1, round(self.line_width * 4 * ctx.img.width / 1920))
            ),
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
        cx = sum(item.x for item in self.items)/len(self.items)
        cy = sum(item.y for item in self.items)/len(self.items)
        return (cx, cy)

    def moved(self, dx: float, dy: float) -> Group[P]:
        return Group([item.moved(dx, dy) for item in self.items])

    def scaled_about(self: Group[PS], factor: float, cx: float, cy: float) -> Group[PS]:
        return Group([item.scaled_about(factor, cx, cy) for item in self.items])

    def scaled(self: Group[PS], factor: float) -> Group[PS]:
        return self.scaled_about(factor, *self.center())

    def add(self, new_item: Q) -> Group[Union[P, Q]]:
        return Group([*self.items, new_item])

    def concat(self, other: Group[Q]) -> Group[Union[P, Q]]:
        return Group([*self.items, *other.items])

    def render_pil(self, ctx: PilContext) -> None:
        for item in self.items:
            item.render_pil(ctx)


if TYPE_CHECKING:
    class GTuple2(tuple[A, B], Generic[A, B]):
        ...
else:
    GTuple2 = Generic


@dataclass(frozen=True)
class Pair(GTuple2[P, Q]):
    p: P
    q: Q

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

    @overload
    def __getitem__(self, index: Literal[0]) -> P: ...
    @overload
    def __getitem__(self, index: Literal[1]) -> Q: ...

    def __getitem__(self, index: int):
        return (self.p, self.q)[index]

    def __len__(self):
        return 2

    def as_group(self) -> Group[Union[P, Q]]:
        return Group(self)

    def moved(self, dx: float, dy: float) -> Pair[P, Q]:
        return Pair(self.p.moved(dx, dy), self.q.moved(dx, dy))

    def center(self) -> tuple[float, float]:
        return Group((self.p, self.q)).center()

    def scaled(self: Pair[PS, QS], factor: float) -> Pair[PS, QS]:
        return self.scaled_about(factor, *self.center())

    def scaled_about(self: Pair[PS, QS], factor: float, cx: float, cy: float) -> Pair[PS, QS]:
        return Pair(self.p.scaled_about(factor, cx, cy), self.q.scaled_about(factor, cx, cy))

    def morph_into(self: Pair[PX, QX], other: Pair[PX, QX]) -> Animation[Pair[PX, QX]]:
        return map_a(
            par_a_longest(self.p.morph_into(other.p), self.q.morph_into(other.q)),
            lambda pq: Pair(*pq)
        )

    def flip(self) -> Pair[Q, P]:
        return Pair[Q, P](self.q, self.p)

    def render_pil(self, ctx: PilContext) -> None:
        self.p.render_pil(ctx)
        self.q.render_pil(ctx)


Triple = Pair[P, Pair[Q, R]]


@dataclass(frozen=True)
class Latex:
    x: float
    y: float
    source: str
    scale_factor: float = 1.0

    align: Align = Align.CC

    def morph_into(self, other: Latex) -> Animation[Latex]:
        if other.source != self.source:
            raise NotImplementedError("Morphing of Latex with different source isn't implemented yet")
        def projector(t: float) -> Latex:
            return Latex(
                self.x * (1 - t) + other.x * t,
                self.y * (1 - t) + other.y * t,
                other.source,
                self.scale_factor * (1 - t) + other.scale_factor * t,
                self.align.blend(other.align, t)
            )
        return Animation(1.0, projector)

    def aligned(self, new_align: Align) -> Latex:
        return Latex(self.x, self.y, self.source, self.scale_factor, new_align)

    def scale_upto(self, factor: float) -> Animation[Latex]:
        return self.morph_into(Latex(self.x, self.y, self.source, factor, self.align))

    def scaled(self, factor: float) -> Latex:
        return Latex(self.x, self.y, self.source, self.scale_factor * factor, self.align)

    def scaled_about(self, factor: float, cx: float, cy: float) -> Latex:
        dx = self.x - cx
        dy = self.y - cy
        new_x = cx + dx*factor
        new_y = cy + dy*factor
        return Latex(new_x, new_y, self.source, self.scale_factor * factor, self.align)

    def moved(self, dx: float, dy: float) -> Latex:
        return Latex(self.x + dx, self.y + dy, self.source, self.scale_factor, self.align)

    def render_pil(self, ctx: PilContext) -> None:
        scale_factor = self.scale_factor * (ctx.settings.width / 1920)
        if scale_factor <= 0.025:
            return
        img = render_latex_scaled(self.source, scale_factor)
        cx, cy = ctx.coord(self.x, self.y)
        x, y = self.align.apply(cx, cy, img.width, img.height)
        ix, iy = map(round, (x, y))
        ctx.draw.bitmap((ix, iy), img)
