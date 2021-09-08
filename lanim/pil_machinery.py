from __future__ import annotations


from typing import Iterable, Literal, Union
from PIL import Image
from pathlib import Path
from threading import Thread
from queue import Queue
import time
from lanim import anim
from lanim.anim import Animation
from lanim.pil_types import PilRenderable, PilSettings


ImageQ = Queue[Union[Literal["stop"], tuple[int, Image.Image]]]


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

    print(f"Rendering animation {width}x{height} {animation.duration}s @{fps}FPS")

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
        image.save(path / f"frame_{i}.png", format="PNG")


def _render_frames(frames: Iterable[tuple[int, PilRenderable]], settings: PilSettings, queue: ImageQ):
    ctx = settings.make_ctx()
    for (i, frame) in frames:
        ctx.draw.rectangle((0, 0) + ctx.img.size, fill=(0, 0, 0, 255))
        frame.render_pil(ctx)
        queue.put((i, ctx.img.copy()), block=True)
