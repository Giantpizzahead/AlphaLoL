"""
https://python-mss.readthedocs.io/examples.html
"""

import time
from multiprocessing import Process, Queue

import mss
import mss.tools


def grab(queue):
    # type: (Queue) -> None

    rect = {"top": 0, "left": 0, "width": 2880, "height": 1800}

    # Record at given FPS
    FPS = 0.23
    t = 1 / FPS
    with mss.mss() as sct:
        while True:
            start_time = time.time()
            queue.put(sct.grab(rect))
            elapsed_time = time.time() - start_time
            time.sleep(t - elapsed_time)

    # Tell the other worker to stop
    # queue.put(None)


def save(queue):
    # type: (Queue) -> None

    number = 1
    output = "../../../temp/frame_{}.png"
    to_png = mss.tools.to_png

    while "there are screenshots":
        img = queue.get()
        if img is None:
            break

        to_png(img.rgb, img.size, output=output.format(number))
        number += 1


if __name__ == "__main__":
    # The screenshots queue
    queue = Queue()  # type: Queue

    # 2 processes: one for grabing and one for saving PNG files
    Process(target=grab, args=(queue,)).start()
    Process(target=save, args=(queue,)).start()
