from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import (
    Callable, ClassVar, Collection, Generic, Iterator, Literal, Optional,
    Protocol, Sequence, TYPE_CHECKING, TypeVar, Union, overload,
)
from PIL import Image, ImageDraw, ImageChops
from lanim.pil_utils import render_latex_scaled
from lanim.core import Animation, Projector, ease_p
from lanim import easings


__all__ = (
    "Align",
    "Style",
    "PilSettings",
    "PilContext",

    "PilRenderable",
    "Scalable",
    "Morphable",
    "Alignable",
    "AlignableMorphable",
    "ScalableMorphable",

    # TypeVars:
    "A", "B", "P", "Q", "R", "R2", "R3", "PA", "PS", "QS", "RS", "RS2", "RS3",
    "PX", "QX", "RX", "RX2", "RX3", "PSX", "QSX", "RSX", "RSX2", "RSX3",
    "PAX", "QAX", "RAX", "RAX2", "RAX3",

    "Rect",
    "Triangle",
    "Group",
    "Pair",
    "Triple",
    "Latex",
    "Nil",
    "Select",
    "Sum",
    "Opacity",
)


@dataclass
class Align:
    """
    Specification of the horizontal and vertical alignment

    Predefined class variables:
    ```
    LU----CU----RU
     |          |
     |          |
    LC    CC    RC
     |          |
     |          |
    LF----VF----RD
    ```
    """

    dx: float
    "Proporton by which to move a LU-aligned object to the right"

    dy: float
    "Proporton by which to move a LU-aligned object to the bottom"

    CC: ClassVar[Align]
    LC: ClassVar[Align]
    RC: ClassVar[Align]
    CU: ClassVar[Align]
    LU: ClassVar[Align]
    RU: ClassVar[Align]
    CD: ClassVar[Align]
    LD: ClassVar[Align]
    RD: ClassVar[Align]

    def __repr__(self):
        for name in (
            "CC", "LC", "RC",
            "CU", "LU", "RU",
            "CD", "LD", "RD"
        ):
            if self == getattr(Align, name):
                return f"Align.{name}"
        return f"Align(dx={self.dx!r}, dy={self.dy}!r)"


    def blend(self, other: Align, t: float) -> Align:
        return Align(self.dx * (1 - t) + other.dx * t, self.dy * (1 - t) + other.dy * t)

    def apply(self, x: float, y: float, width: float, height: float) -> tuple[float, float]:
        """
        Compute the new bottom-left position of a `(x, y, width, height)` rectangle
        after applying this alignemnt
        """
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
    """
    Settings regarding the drawing of a single element
    """
    fill: Optional[Union[str, int]]
    outline: Optional[Union[str, int]]
    line_width: int


@dataclass(frozen=True)
class PilSettings:
    """
    Settings regarding the entire viewport
    """
    width: int
    height: int
    center_x: int
    center_y: int
    unit: int

    def make_ctx(self) -> PilContext:
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.ImageDraw(img)
        return PilContext(self, img, draw)


@dataclass(frozen=True)
class PilContext:
    """
    Context object holding the current state of a frame
    """
    settings: PilSettings
    img: Image.Image
    draw: ImageDraw.ImageDraw

    def coord(self, x: float, y: float) -> tuple[int, int]:
        pixels_x = self.settings.center_x + self.settings.unit * x
        pixels_y = self.settings.center_y + self.settings.unit * y
        return round(pixels_x), round(pixels_y)

    def rectangle_wh(self, cx: float, cy: float, width: float, height: float, style: Style):
        self.rectangle(cx - width/2, cy - height/2, cx + width/2, cy + height/2, style)

    def rectangle(self, x1: float, y1: float, x2: float, y2: float, style: Style):
        self.draw.rectangle(
            (self.coord(x1, y1), self.coord(x2, y2) ),
            fill=style.fill,
            outline=style.outline,
            width=style.line_width,
        )

    def line(self, x1: float, y1: float, x2: float, y2: float, style: Style):
        self.draw.line(
            [*self.coord(x1, y1), *self.coord(x2, y2)],
            fill=style.outline,
            width=style.line_width,
        )

    def triangle(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, style: Style):
        self.draw.line(
            [
                *self.coord(x1, y1),
                *self.coord(x2, y2),
                *self.coord(x3, y3),
                *self.coord(x1, y1),
                *self.coord((x1+x2)/2, (y1+y2)/2),
            ],
            fill=style.outline,
            width=style.line_width,
            joint="curve"
        )



class PilRenderable(Protocol):
    x: float
    "x-coordinate of the object's center"

    y: float
    "y-coordinate of the object's center"

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
    def morphed(self: A, other: A, t: float) -> A: ...

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


@dataclass(frozen=True)
class Rect:
    """
    Axis-aligned rectangle
    """
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

    def morphed(self, other: Rect, t: float) -> Rect:
        return Rect(
            self.x * (1 - t) + other.x * t,
            self.y * (1 - t) + other.y * t,
            self.width * (1 - t) + other.width * t,
            self.height * (1 - t) + other.height * t,
            self.line_width * (1 - t) + other.line_width * t
        )

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


def _automorph(self: P, other: P, t: float, *names: str) -> P:
    kwargs = {name: getattr(self, name) * (1 - t) + getattr(other, name) * t for name in names}
    return dataclass_replace(self, **kwargs)


@dataclass(frozen=True)
class Triangle:
    """
    Triangle, defined by its center and the deviation of each
    point from its center.
    """
    x: float
    y: float
    dx1: float
    dy1: float
    dx2: float
    dy2: float
    dx3: float
    dy3: float
    line_width: float = 1

    def moved(self, dx: float, dy: float) -> Triangle:
        return dataclass_replace(self, x=self.x + dx, y = self.y + dy)

    def scaled(self, factor: float) -> Triangle:
        return dataclass_replace(
            self,
            dx1=self.dx1 * factor,
            dy1=self.dy1 * factor,
            dx2=self.dx2 * factor,
            dy2=self.dy2 * factor,
            dx3=self.dx3 * factor,
            dy3=self.dy3 * factor,
        )

    def scaled_about(self, factor: float, cx: float, cy: float) -> Triangle:
        dx = cx - self.x
        dy = cy - self.y
        return self.scaled(factor).moved(dx*factor, dy*factor)

    def morphed(self, other: Triangle, t: float) -> Triangle:
        return _automorph(
            self, other, t,
            "x", "y", "dx1", "dy1", "dx2", "dy2", "dx3", "dy3", "line_width"
        )

    def render_pil(self, ctx: PilContext) -> None:
        ctx.triangle(
            self.x + self.dx1,
            self.y + self.dy1,
            self.x + self.dx2,
            self.y + self.dy2,
            self.x + self.dx3,
            self.y + self.dy3,
            Style(
                outline=0xffffff,
                fill=0x000000,
                line_width=max(1, round(self.line_width * 4 * ctx.img.width / 1920))
            )
        )


@dataclass(frozen=True)
class Group(Generic[P]):
    """
    Group of `PilRenderable` objects rendered together in order.

    Type variable `P` represents the type of each object contained.
    """

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

    def morphed(self: Group[PX], other: Group[PX], t: float) -> Group[PX]:
        if len(self.items) != len(other.items):
            raise NotImplementedError("Morphing groups with different lengths isn't implemented yet")
        return Group([a.morphed(b, t) for a, b in zip(self.items, other.items)])

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


# The following is needed so that you can unpack a `Pair` like a tuple.
# This is possible without this hack, but the inferred type of each element will be a union:

# a, b = Pair(Rect(...), Latex(...))
# ^  ^
# |__|___a: Rect | Latex, b: Rect | Latex

if TYPE_CHECKING:
    class _GTuple2(tuple[A, B], Generic[A, B]):
        ...
else:
    _GTuple2 = Generic


@dataclass(frozen=True)
class Pair(_GTuple2[P, Q]):
    """
    Pair of two `PilRenderable` objects _p_ and _q_, where
    _p_ is drawn before _q_. Exists primarily for better
    type-checker support.
    """
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

    def morphed(self: Pair[PX, QX], other: Pair[PX, QX], t: float) -> Pair[PX, QX]:
        return Pair(self.p.morphed(other.p, t), self.q.morphed(other.q, t))

    def flip(self) -> Pair[Q, P]:
        return Pair[Q, P](self.q, self.p)

    def render_pil(self, ctx: PilContext) -> None:
        self.p.render_pil(ctx)
        self.q.render_pil(ctx)


Triple = Pair[P, Pair[Q, R]]


@dataclass(frozen=True)
class Latex:
    """
    Graphical primitive rendered via the LaTeX program.
    """
    x: float
    y: float
    source: str
    scale_factor: float = 1.0

    align: Align = Align.CC
    packages: Collection[str] = ("amsmath", "amssymb")
    r"The LaTeX packages to include as `\usepackage{...}` clauses"

    def morphed(self, other: Latex, t: float) -> Latex:
        return Latex(
            self.x * (1 - t) + other.x * t,
            self.y * (1 - t) + other.y * t,
            other.source,
            self.scale_factor * (1 - t) + other.scale_factor * t,
            self.align.blend(other.align, t),
            other.packages
        )

    def aligned(self, new_align: Align) -> Latex:
        return Latex(self.x, self.y, self.source, self.scale_factor, new_align, self.packages)

    def scaled(self, factor: float) -> Latex:
        return Latex(self.x, self.y, self.source, self.scale_factor * factor, self.align, self.packages)

    def scaled_about(self, factor: float, cx: float, cy: float) -> Latex:
        dx = self.x - cx
        dy = self.y - cy
        new_x = cx + dx*factor
        new_y = cy + dy*factor
        return Latex(new_x, new_y, self.source, self.scale_factor * factor, self.align, self.packages)

    def moved(self, dx: float, dy: float) -> Latex:
        return Latex(self.x + dx, self.y + dy, self.source, self.scale_factor, self.align, self.packages)

    def _render(self, scale_factor: float):
        return render_latex_scaled(self.source, self.packages, scale_factor)

    def width(self) -> float:
        img = self._render(self.scale_factor)
        return img.width / 1920 * 16

    def height(self) -> float:
        img = self._render(self.scale_factor)
        return img.height / 1920 * 16

    def render_pil(self, ctx: PilContext) -> None:
        scale_factor = self.scale_factor * (ctx.settings.width / 1920)
        if scale_factor <= 0.025:
            return
        img = self._render(scale_factor)
        cx, cy = ctx.coord(self.x, self.y)
        x, y = self.align.apply(cx, cy, img.width, img.height)
        ix, iy = map(round, (x, y))
        ctx.draw.bitmap((ix, iy), img)


@dataclass(frozen=True)
class Nil:
    """
    Special graphical primitive that doesn't do anything on render.
    """
    x: float
    y: float

    def moved(self, dx: float, dy: float) -> Nil:
        return Nil(self.x + dx, self.y + dy)

    def scaled(self, factor: float) -> Nil:
        return self

    def scaled_about(self, factor: float, cx: float, cy: float) -> Nil:
        dx = cx - self.x
        dy = cy - self.y
        return self.moved(dx*factor, dy*factor)

    def morphed(self, other: Nil, t: float) -> Nil:
        return _automorph(self, other, t, "x", "y")

    def aligned(self, align: Align) -> Nil:
        return self

    def render_pil(self, ctx: PilContext) -> None:
        pass


Select = Union[tuple[Literal["p"], PX], tuple[Literal["q"], QX]]


@dataclass(frozen=True)
class Sum(Generic[PX, QX]):
    """
    Graphical primitive representing a union of two objects.
    The name _Sum_ derives from _sum type_, not from a combination,
    which would be a _product type_.
    """

    item: Select[PX, QX]

    mpq: Callable[[PX, QX], Projector[Select[PX, QX]]]
    "Strategy for morphing the left item into the right item"

    if TYPE_CHECKING:
        x: float = field(init = False)
        y: float = field(init = False)
    else:
        @property
        def x(self) -> float:
            return self.item[1].x

        @property
        def y(self) -> float:
            return self.item[1].y

    @property
    def mqp(self) -> Callable[[QX, PX], Projector[Select[PX, QX]]]:
        return lambda q, p: ease_p(self.mpq(p, q), easings.invert)

    def with_left(self, left: PX) -> Sum[PX, QX]:
        return self.with_pq(("p", left))

    def with_right(self, right: QX) -> Sum[PX, QX]:
        return self.with_pq(("q", right))

    def with_pq(self, pq: Select[PX, QX]) -> Sum[PX, QX]:
        return Sum(pq, self.mpq)

    def map(self, fp: Callable[[PX], RX], fq: Callable[[QX], RX2]) -> Sum[RX, RX2]:
        tag, item = self.item
        if tag == "p":
            return self.with_left(fp(item))  # type: ignore
        else:
            return self.with_right(fq(item))  # type: ignore

    def dispatch(self, fp: Callable[[PX], A], fq: Callable[[QX], A]) -> A:
        tag, item = self.item
        if tag == "p":
            return fp(item)  # type: ignore
        else:
            return fq(item)  # type: ignore

    def moved(self, dx: float, dy: float) -> Sum[PX, QX]:
        return self.map(
            lambda p: p.moved(dx, dy),
            lambda q: q.moved(dx, dy),
        )

    def scaled(self: Sum[PSX, QSX], factor: float) -> Sum[PSX, QSX]:
        return self.map(
            lambda p: p.scaled(factor),
            lambda q: q.scaled(factor),
        )

    def morphed(self, other: Sum[PX, QX], t: float) -> Sum[PX, QX]:
        return self.dispatch(
            lambda p1: other.dispatch(
                lambda p2: self.with_left(p1.morphed(p2, t)),
                lambda q2: self.with_pq(self.mpq(p1, q2)(t)),
            ),
            lambda q1: other.dispatch(
                lambda p2: self.with_pq(self.mqp(q1, p2)(t)),
                lambda q2: self.with_right(q1.morphed(q2, t)),
            ),
        )

    def render_pil(self, ctx: PilContext) -> None:
        _tag, item = self.item
        item.render_pil(ctx)


class Opacity(Generic[P]):
    """
    Wrapper around a PilRenderable value to render it with an opacity (from 0 to 1)
    """

    def __init__(self, child: P, opacity: float = 1.0):
        if not (0 <= opacity <= 1):
            raise ValueError(f"Opacity should be between 0 and 1, got {opacity!r}")

        self.x = child.x
        self.y = child.y
        self.child = child
        self.opacity = opacity

    def morphed(self: Opacity[PX], other: Opacity[PX], t: float) -> Opacity[PX]:
        return Opacity(
            self.child.morphed(other.child, t),
            self.opacity * (1 - t) + other.opacity * t
        )

    def scaled(self: Opacity[PS], factor: float) -> Opacity[PS]:
        return Opacity(self.child.scaled(factor), self.opacity)

    def scaled_about(self: Opacity[PS], factor: float, cx: float, cy: float) -> Opacity[PS]:
        return Opacity(self.child.scaled_about(factor, cx, cy), self.opacity)

    def moved(self, dx: float, dy: float) -> Opacity[P]:
        return Opacity(self.child.moved(dx, dy), self.opacity)

    def fade(self, target: float = 0) -> Animation[Opacity[P]]:
        def projector(t: float):
            return Opacity(self.child, self.opacity * (1 - t) + target * t)
        return Animation(1, projector)

    def render_pil(self, ctx: PilContext):
        new_ctx = ctx.settings.make_ctx()
        self.child.render_pil(new_ctx)

        # TODO: find out if there's a way to do this without creating 3 extra images:

        mask = Image.new("RGBA", new_ctx.img.size, (0, 0, 0, round(255 * self.opacity)))

        transparent = Image.new("RGBA", new_ctx.img.size, (0, 0, 0, 0))
        transparent = ImageChops.composite(new_ctx.img, transparent, mask)

        buffer = Image.new("RGBA", new_ctx.img.size, (0, 0, 0, 0))
        buffer.paste(ctx.img)
        buffer.paste(transparent, mask=transparent)

        ctx.img.paste(buffer)
