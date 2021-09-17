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
