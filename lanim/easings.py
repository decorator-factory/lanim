"""
Useful easings. For demo see:
https://www.desmos.com/calculator/
"""
import math
from typing import Callable


Easing = Callable[[float], float]


def compose(e1: Easing, e2: Easing) -> Easing:
    return lambda t: e2(e1(t))

def product(e1: Easing, e2: Easing) -> Easing:
    return lambda t: e1(t) * e2(t)

def average(e1: Easing, e2: Easing) -> Easing:
    return lambda t: (e1(t) + e2(t))/2


"""
                       ...XXXXXXX
                      .XXX.......
                    ..X...
                   .XX.
                  .X..
                 .X.
                 ..
                .X.
               .X.
              .X.
              ..
             .X.
           ..X.
          .XX.
       ...X..
.......XXX.
XXXXXXX...
"""
in_out: Easing = lambda t: 4*t**3 if t < 0.5 else -4*(1 - t)**3 + 1


back_and_forth: Easing = lambda t: 1 - 2 * abs(0.5 - t)


"""
XX.
..X...
  .XXX.
   ...X...
      .XXX.
       ...X...
          .XXX.
           ...X...
              .XXX.
               ...X...
                  .XXX.
                   ...X...
                      .XXX.
                       ...X...
                          .XXX.
                           ...X..
                              .XX
"""
invert: Easing = lambda t: 1 - t



"""
                       ....XXXXXX
                    ...XXXX......
                  ..XXX....
                ..XX...
              ..XX..
            ..XX..
           .XX..
         ..X..
        .XX.
       .X..
     ..X.
    .XX.
   .X..
  .X.
 .X.
.X.
X.
"""
iquad: Easing = lambda t: 1 - (1 - t)**2



"""
                              .XX
                           ...X..
                          .XXX.
                       ...X...
                      .XXX.
                   ...X...
                  .XXX.
               ...X...
              .XXX.
           ...X...
          .XXX.
       ...X...
      .XXX.
   ...X...
  .XXX.
..X...
XX.
"""
linear: Easing = lambda t: t



"""
                               .X
                              .X.
                             .X.
                            .X.
                          ..X.
                         .XX.
                        .X..
                      ..X.
                     .XX.
                   ..X..
                 ..XX.
               ..XX..
             ..XX..
          ...XX..
      ....XXX..
......XXXX...
XXXXXX....
"""
quadratic: Easing = lambda t: t**2



"""
                               .X
                              .X.
                             .X.
                            .X.
                           .X.
                          .X.
                         .X.
                        .X.
                      ..X.
                     .XX.
                   ..X..
                  .XX.
               ...X..
             ..XXX.
         ....XX...
.........XXXX..
XXXXXXXXX....
"""
sled: Easing = lambda t: (math.log(1 + t)/math.log(2))**math.pi



if __name__ == "__main__":
    # Automatically document easings
    from lanim import easings
    import inspect

    WIDTH = 32
    HEIGHT = 16

    for name in dir(easings):
        if name.islower() and not name.startswith("_"):
            f = getattr(easings, name)
            if not hasattr(f, "__call__"):
                continue
            print('"""')
            r = [[" "]*(WIDTH + 1) for _ in range(HEIGHT + 1)]
            for x in range(WIDTH + 1):
                y = HEIGHT - round(f(x / WIDTH) * HEIGHT)
                r[y][x] = "X"
                for (dx, dy) in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    px, py = x + dx, y + dy
                    if 0 <= px <= WIDTH and 0 <= py <= HEIGHT:
                        if r[py][px] == " ":
                            r[py][px] = "."
            for y in range(HEIGHT + 1):
                print("".join(map(r[y].__getitem__, range(WIDTH + 1))))
            print('"""')
            print(inspect.getsource(f))
            print()
            print()
