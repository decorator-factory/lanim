from __future__ import annotations


from typing import Iterable
from pathlib import Path
from threading import Thread
import time
from lanim.core import Animation, frames
from lanim.pil_types import PilRenderable, PilSettings


def render_pil(
    width: int,
    height: int,
    animation: Animation[PilRenderable],
    path: Path,
    fps: float,
    workers: int
):
    path.mkdir(parents=True, exist_ok=True)

    settings = PilSettings(
        width=width, height=height,
        center_x=width//2, center_y=height//2,
        unit=width//16
    )

    print(f"Size: {width}x{height}, duration: {animation.duration}s @{fps}FPS")
    print(f"Launching {workers} threads")

    jobs = [[] for _ in range(workers)]

    for (i, frame) in enumerate(frames(animation, fps)):
        jobs[i % workers].append((i, frame))

    frame_rendering_threads: list[Thread] = []

    t1 = time.time()

    for (n, job) in enumerate(jobs):
        print(f"Starting job {n} with {len(job)} frames...")
        thread = Thread(target=_render_frames, args=(job, settings, path))
        thread.start()
        frame_rendering_threads.append(thread)

    for (n, thread) in enumerate(frame_rendering_threads):
        print(f"Waiting for frame-job {n}...")
        thread.join()

    t2 = time.time()
    return t2 - t1


def _render_frames(frames: Iterable[tuple[int, PilRenderable]], settings: PilSettings, path: Path):
    ctx = settings.make_ctx()
    for (position, frame) in frames:
        ctx.draw.rectangle((0, 0) + ctx.img.size, fill=(0, 0, 0, 255))  # type: ignore -- bad PIL stubs
        frame.render_pil(ctx)
        ctx.img.save(path / f"frame_{position}.png")
