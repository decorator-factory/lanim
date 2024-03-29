# Hello, λanim!

In this tutorial, we're going to recreate the `lanim.examples.hello` animation.

![Step 11](step11.gif)

## 1. Create a stub

Create a file called `tutorial_hello.py` with this content:

```py
from lanim.examples.hello import export
```

Then run `python -m lanim -o hello.mp4 tutorial_hello` in the same directory.

This explains how to make `lanim` animate your module: it needs to export the
animation under the `export` name.

## 2. Create the greeting
```py
from lanim.pil import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")
```
Theis object doesn't _do_ anything yet --- it's a simple value, like a number
or a string.

## 3. Make a static animation of the greeting

```py hl_lines="1 6"
from lanim.core import const_a
from lanim.pil import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

export = const_a(sign)
```
Now try `python -m lanim -o hello.mp4 tutorial_hello` and see what happens.
![Step 3](step3.gif)

This animation is only 1 second long, how do we make it longer?


## 3. Stretch the animation
```py hl_lines="6"
from lanim.core import const_a
from lanim.pil import Latex

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

export = const_a(sign) * 5
```

Render the video again. It should be five seconds long.

## 4. Make the sign scale out instead of just sitting there

```py hl_lines="1 5"
from lanim.pil import Latex, appear

sign = Latex(x=0, y=0, source=r"Hello, $\lambda$anim!")

export = appear(sign) * 2
```
![Step 6](step4.gif)

## 5. Create a border around the greeting
```py hl_lines="1 5-10"
from lanim.pil import Latex, Rect

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
```py hl_lines="1 12 14"
from lanim.pil import appear, Latex, Rect, Pair

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
![Step 6](step6.gif)

`Pair` is also an ordinary immutable value, like `Latex` and `Rect`.


## 7. Make the last frame persist for a while

You can put one animation after another by adding them:

```py hl_lines="1 15"
from lanim.core import const_a
from lanim.pil import appear, Latex, Rect, Pair

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
![Step 7](step7.gif)



## 8. Make the border appear before the sign

### 8.1. Make the sign appear inside the border
```py hl_lines="2 15"
from lanim.core import const_a
from lanim.pil import appear, gbackground, Latex, Rect, Pair

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
![Step 8.1](step8_1.gif)

`gbackground` accepts an animation and a list of graphics to put in the background.


### 8.2. Stretch out the border before the greeting animation
```py hl_lines="15"
from lanim.core import const_a
from lanim.pil import appear, gbackground, Latex, Rect, Pair

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
![Step 8.2](step8_2.gif)


### 8.3. Formatting tweak
```py hl_lines="15-19"
from lanim.core import const_a
from lanim.pil import appear, gbackground, Latex, Rect, Pair

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

## 9. Move the assembly down
```py hl_lines="2 19"
from lanim.core import const_a
from lanim.pil import appear, gbackground, move_by, Latex, Rect, Pair

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
![Step 9](step9.gif)

---

The animation is doing the action we wanted it to do, but it's not pretty.
Let's fix that.

## 10. Add easings

An [_easing function_](https://easings.net/) allows you to change the "shape"
or "texture" of the change.

=== "Animation"

    To illustrate, look at these easings:

    - The _linear_ easing moves at a steady pace. It doesn't change an animation.
    - The _in-out_ easing has a gentle start and end
    - The _sled_ easing starts out slow and then accelerates

    ![Demonstration of three easings](easings.gif)

=== "Formulas"

    An easing is a function from `[0; 1]` to `[0; 1]`.

    You can see their graphs in on [Desmos](https://www.desmos.com/calculator/ljbkaftbej)

    ![Formulas](easing_formulas.gif)


```py hl_lines="3 18 20"
from lanim.core import const_a
from lanim.pil import appear, gbackground, move_by, Latex, Rect, Pair
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
![Step 10](step10.gif)


## 11. Adjust durations

Timing is to animation what intonation is to speech.

Let's spice our animation up by tweaking some of the durations.

```py hl_lines="17 19"
from lanim.core import const_a
from lanim.pil import appear, gbackground, move_by, Latex, Rect, Pair
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
![Step 11](step11.gif)


## Recap

In this tutorial, you've learned how to:

1. Export a simple animation from a Python module
2. Create graphical objects, namely `Latex`, `Rect` and `Pair`
3. Animate still frames, as well as scale out and move objects
4. Change the duration of animations
5. Put animations in sequence
6. Use easings to make transitions more interesting

