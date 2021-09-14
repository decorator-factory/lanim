# Hello, λanim!

In this tutorial, we're going to recreate the `lanim.examples.hello` animation.

![Step 11](hello/step11.gif)

## 1. Create a stub

Create a file called `tutorial_hello.py` with this content:

```py
from lanim.examples.hello import export
```

Then run `python -m lanim -o hello.mp4 tutorial_hello` in the same directory.

This explains how to make `lanim` animate your module: it needs to export the
animation under the `export` name.

Now we're going to make an

## 2. Create the greeting
```py
from lanim.pil_types import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")
```
Theis object doesn't _do_ anything yet --- it's a simple value, like a number
or a string.

## 3. Make a static animation of the sign

```py hl_lines="1 6"
from lanim.anim import const_a
from lanim.pil_types import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

export = const_a(sign)
```
Now try `python -m lanim -o hello.mp4 tutorial_hello` and see what happens.
![Step 3](hello/step3.gif)

This animation is only 1 second long, how do we make it longer?


## 3. Stretch the animation
```py hl_lines="6"
from lanim.anim import const_a
from lanim.pil_types import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

export = const_a(sign) * 5
```

The animation now lasts for five seconds.

## 4. Make the sign scale out instead of just sitting there

```py hl_lines="1 6"
from lanim.pil_graphics import appear
from lanim.pil_types import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

export = appear(sign) * 2
```
![Step 6](hello/step4.gif)

## 5. Create a border around the greeting
```py hl_lines="1 5-10"
from lanim.pil_types import Latex, Rect

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)
```

How do we animate both of them?


## 6. Animate a pair of the greeting and the border
```py hl_lines="1 13 15"
from lanim.pil_graphics import appear
from lanim.pil_types import Latex, Rect, Pair

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = appear(pair)
```
![Step 6](hello/step6.gif)

`Pair` is also an ordinary immutable value, like `Latex` and `Rect`.


## 7. Make the last frame persist for a while:

```py hl_lines="1 16"
from lanim.anim import const_a
from lanim.pil_graphics import appear
from lanim.pil_types import Latex, Rect, Pair

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = appear(pair) + const_a(pair)
```
![Step 7](hello/step7.gif)


## 8. Make the border appear before the sign

### 8.1. Make the sign appear inside the border
```py hl_lines="2 16"
from lanim.anim import const_a
from lanim.pil_graphics import appear, gbackground
from lanim.pil_types import Latex, Rect, Pair

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = gbackground(appear(sign), [border]) + const_a(pair)
```
![Step 8.1](hello/step8_1.gif)

`gbackground` accepts an animation and a list of things to put in the background.


### 8.2. Stretch out the border before the greeting animation
```py hl_lines="16"
from lanim.anim import const_a
from lanim.pil_graphics import appear, gbackground
from lanim.pil_types import Latex, Rect, Pair

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = appear(border) + gbackground(appear(sign), [border]) + const_a(pair)
```
![Step 8.2](hello/step8_2.gif)


### 8.3. Split a complex expression across several lines
```py hl_lines="16-20"
from lanim.anim import const_a
from lanim.pil_graphics import appear, gbackground
from lanim.pil_types import Latex, Rect, Pair

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = (
    appear(border)
    + gbackground(appear(sign), [border])
    + const_a(pair)
)
```

## 9. Move the whole thing down
```py hl_lines="2 20"
from lanim.anim import const_a
from lanim.pil_graphics import appear, gbackground, move_by
from lanim.pil_types import Latex, Rect, Pair

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = (
    appear(border)
    + gbackground(appear(sign), [border])
    + const_a(pair)
    + move_by(pair, dx=0, dy=10)
)
```
![Step 9](hello/step9.gif)

---

The animation is doing the action we wanted it to do, but it's not pretty.
Let's fix that.

## 10. Add easings

An [_easing function_](https://easings.net/) allows you to change the "shape"
of the change.

=== "Animation"

    Here you can see that

    - The _linear_ easing moves at a steady pace
    - The _in-out_ easing has a gentle start and end
    - The _sled_ easing starts out slow and then accelerates

    ![Demonstration of three easings](hello/easings.gif)

=== "Formulas"

    An easing is a function from `[0; 1]` to `[0; 1]`.

    You can see their graphs in action on [Desmos](https://www.desmos.com/calculator/ljbkaftbej)

    ![Formulas](hello/easing_formulas.gif)

=== "Code (advanced)"
    This should mostly be understandable, but has a lot of stuff going on
    (you can animate numbers? WTF?)

    ```py
    from lanim.anim import Animation, const_a
    from lanim.pil_types import Align, Group, Latex, Rect, Pair, Triangle
    from lanim.easings import linear, in_out, sled


    def slider(x1: float, x2: float, t: float):
        slider_xpos = x1*(1-t) + x2*t
        bar = Rect(
            x=(x1 + x2)/2, y=0,
            width=x2 - x1, height=0.05,
            line_width=1.5
        )
        pointer = Triangle(
            x=slider_xpos, y=-0.3,
            dx1=-0.3, dy1=-0.2,
            dx2=+0.3, dy2=-0.2,
            dx3=0,    dy3=+0.3
        )
        return Pair(bar, pointer)


    def slider_row(label: str, t: float):
        latex = Latex(x=-0.5, y=0, source=label, align=Align.RC)
        slider_ = slider(0.5, 5, t).moved(dx=0, dy=0.25)
        return Pair(latex, slider_)


    def all_rows(t: float):
        linear_row = slider_row(r"\texttt{linear}:", linear(t)).moved(dx=0, dy=-2.5)
        in_out_row = slider_row(r"\texttt{in\_out}:", in_out(t))
        sled_row = slider_row(r"\texttt{sled}:", sled(t)).moved(dx=0, dy=2.5)
        return Group([linear_row, in_out_row, sled_row])


    zero = const_a(0.0)
    one = const_a(1.0)
    rise = Animation(1, lambda t: t)
    fall = Animation(1, lambda t: -t)
    timing = zero*2 + rise*3 + one*2 + fall*3 + zero*0.5 + rise + one + fall + zero*2

    export = timing.map(all_rows)
    ```

    Formulas:

    ```py
    linear_formula = r"$linear(t) = t$"
    in_out_formula = r"""
    \begin{equation}
        in\_out(t) =
        \begin{cases}
            4 t^3          & \text{ if } t < \frac{1}{2} \\
            1 - 4(1 - t)^3 & \text{otherwise}
        \end{cases}
    \end{equation}
    """
    sled_formula = r"$ sled(t) = \left( \dfrac{\ln(1 + t)}{\ln 2} \right) ^ \text{\large{$\pi$}}$"
    export = Group([
        Latex(-7, -2.8, linear_formula, align=Align.LC).scaled(0.5),
        Latex(-7,  0.0, in_out_formula, align=Align.LC).scaled(0.5),
        Latex(-7, +2.8, sled_formula,   align=Align.LC).scaled(0.5),
    ])
    ```


```py hl_lines="4 19 21"
from lanim.anim import const_a
from lanim.pil_graphics import appear, gbackground, move_by
from lanim.pil_types import Latex, Rect, Pair
from lanim.easings import in_out, sled

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = (
    appear(border)
    + gbackground(appear(sign), [border]).ease(in_out)
    + const_a(pair)
    + move_by(pair, dx=0, dy=10).ease(sled)
)
```
![Step 10](hello/step10.gif)


## 11. Adjust durations

Timing is crucial. It's like the accents and intonation in speech.

Let's spice our animation up by tweaking some of the durations.

```py hl_lines="18 20"
from lanim.anim import const_a
from lanim.pil_graphics import appear, gbackground, move_by
from lanim.pil_types import Latex, Rect, Pair
from lanim.easings import in_out, sled

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

border = Rect(
    x=0,
    y=0,
    width=sign.width() + 1,
    height=sign.height() + 1
)

pair = Pair(sign, border)

export = (
    appear(border) * 0.5
    + gbackground(appear(sign), [border]).ease(in_out)
    + const_a(pair) * 0.25
    + move_by(pair, dx=0, dy=10).ease(sled)
)
```
![Step 11](hello/step11.gif)


## Recap

In this tutorial, you've learned how to:

1. Export a simple animation from a Python module
2. Create graphical objects, namely `Latex`, `Rect` and `Pair`
3. Animate still frames, as well as scale out and move objects
4. Change the duration of animations
5. Put animations in sequence
6. Use easings to make transitions more interesting

