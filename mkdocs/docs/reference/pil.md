# `pil`


## Graphical objects

### ::: lanim.pil.Rect
    selection:
        members:
            - x
            - y
            - width
            - height
            - line_width

### ::: lanim.pil.Triangle
    selection:
        members:
            - x
            - y
            - dx1
            - dy1
            - dx2
            - dy2
            - dx3
            - dy3
            - line_width

### ::: lanim.pil.Group
    selection:
        members:
            - x
            - y
            - center
            - items
            - add
            - concat

### ::: lanim.pil.Pair
    selection:
        members:
            - p
            - q
            - x
            - y
            - as_group
            - center
            - flip

### ::: lanim.pil.Latex
    selection:
        members:
            - x
            - y
            - source
            - scale_factor
            - align
            - packages
            - width
            - height

### ::: lanim.pil.Nil
    selection:
        members:
            - x
            - y

### ::: lanim.pil.Sum
    selection:
        members:
            - item
            - mpq
            - x
            - y
            - mqp
            - with_left
            - with_right
            - with_pq
            - map
            - dispatch

### ::: lanim.pil.Opacity
    selection:
        members:
            - __init__
            - fade


## Manipulation of graphical primitives

### ::: lanim.pil.moved_to
### ::: lanim.pil.morph_into
### ::: lanim.pil.move_by
### ::: lanim.pil.scale
### ::: lanim.pil.align
### ::: lanim.pil.lpair
### ::: lanim.pil.rpair
### ::: lanim.pil.lrpair_longest
### ::: lanim.pil.lrpair_shortest
### ::: lanim.pil.gbackground
### ::: lanim.pil.gforeground
### ::: lanim.pil.group_join
### ::: lanim.pil.mixed_group_join
### ::: lanim.pil.merge_group_animations
### ::: lanim.pil.parallel
### ::: lanim.pil.group
### ::: lanim.pil.with_last_frame
### ::: lanim.pil.swap
### ::: lanim.pil.m_just
### ::: lanim.pil.m_none
### ::: lanim.pil.appear
### ::: lanim.pil.disappear
### ::: lanim.pil.appear_from
### ::: lanim.pil.disappear_from


## Imperative API


### ::: lanim.pil.scene_any

### `scene`
`scene` is just an alias for `scene_any` but with
a different type signature.


## Trajectories

### ::: lanim.pil.Trajectory
    selection:
        members:
            - __call__

### ::: lanim.pil.ease_t
### ::: lanim.pil.move_t
### ::: lanim.pil.proj_t
### ::: lanim.pil.linear_traj
### ::: lanim.pil.make_arc_traj
### ::: lanim.pil.halfcircle_traj
### ::: lanim.pil.low_arc_traj
### ::: lanim.pil.lift_traj

## Protocols

### ::: lanim.pil.PilRenderable
    selection:
        members:
            - x
            - y
            - moved
            - render_pil

### ::: lanim.pil.Scalable
    selection:
        members:
            - scaled
            - scaled_about

### ::: lanim.pil.Morphable
    selection:
        members:
            - morphed

### ::: lanim.pil.Alignable
    selection:
        members:
            - aligned


## Utility data structures

These objects will be useful if you're implementing your own primitives for rendering with PIL

### ::: lanim.pil.Align
    selection:
        members:
            - dx
            - dy
            - blend
            - apply

### ::: lanim.pil.Style
    selection:
        members:
            - fill
            - outline
            - line_width

### ::: lanim.pil.PilContext
    selection:
        members:
            - settings
            - img
            - draw
            - coord
            - rectangle_wh
            - rectangle
            - line
            - triangle
