# `core`

The `lanim.core` module provides a rendering frontend-agnostic core
for creating and transforming general animations.

## `Projector`
Generic type alias standing for `Callable[[float], A]`.

The semantics are as follows: a projector is a function mapping
a progress (a `float` from `0` to `1` inclusive) to a still frame A.

Passing a value outside of the `[0; 1]` range is undefined
behaviour. You should watch out for this, especially in light of
floating-point errors.

## ::: lanim.core.Animation
    selection:
        members:
            - duration
            - projector
            - map
            - progress_map
            - ease
            - __mul__
            - __add__
            - __rshift__

## Functions on projectors

### ::: lanim.core.const_p
### ::: lanim.core.map_p
### ::: lanim.core.join_p
### ::: lanim.core.flatmap_p
### ::: lanim.core.ease_p

## Functions on animations

### ::: lanim.core.const_a
### ::: lanim.core.seq_a
### ::: lanim.core.flatmap_a
### ::: lanim.core.par_a_longest
### ::: lanim.core.par_a_shortest
### ::: lanim.core.pause_after
### ::: lanim.core.pause_before
### ::: lanim.core.crop_by_range
### ::: lanim.core.frames
