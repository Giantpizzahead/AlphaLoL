"""
Contains helper functions for using the mouse.
"""

import threading
from queue import Queue

import pynput
from pynput.mouse import Button

from controllers.mouse import bezier_mouse
from misc import color_logging
from misc.rng import rnum, rsleep

logger = color_logging.getLogger('controls', level=color_logging.INFO)
mouse = pynput.mouse.Controller()


def _press_left() -> None:
    rsleep(0.03)
    mouse.press(Button.left)


def _press_right() -> None:
    rsleep(0.03)
    mouse.press(Button.right)


def _release_left() -> None:
    rsleep(0.03)
    mouse.release(Button.left)


def _release_right() -> None:
    rsleep(0.03)
    mouse.release(Button.right)


def _move_mouse(x: float, y: float) -> None:
    logger.debug(f"Move mouse to ({x:.2f}, {y:.2f})")
    cx, cy = bezier_mouse.mouse.position
    abs_error = 5
    if abs(cx-x) <= abs_error and abs(cy-y) <= abs_error:
        return
    rsleep(0.03)
    bezier_mouse.move_mouse(rnum(x, abs(cx-x)/40+abs_error, True), rnum(y, abs(cy-y)/40+abs_error, True))


def _left_click(x: float, y: float) -> None:
    logger.debug(f"Left click at ({x:.2f}, {y:.2f})")
    _move_mouse(x, y)
    _press_left()
    _release_left()


def _right_click(x: float, y: float) -> None:
    logger.debug(f"Right click at ({x:.2f}, {y:.2f})")
    _move_mouse(x, y)
    _press_right()
    _release_right()


# Process all mouse events in a separate thread using a queue
queue = Queue()


def sleep(n: float, s=0.047, a=False) -> None:
    queue.put((rsleep, n, s, a))


def press_left() -> None:
    queue.put((_press_left,))


def press_right() -> None:
    queue.put((_press_right,))


def release_left() -> None:
    queue.put((_release_left,))


def release_right() -> None:
    queue.put((_release_right,))


def move_mouse(x: float, y: float) -> None:
    queue.put((_move_mouse, x, y))


def left_click(x: float, y: float) -> None:
    queue.put((_left_click, x, y))


def right_click(x: float, y: float) -> None:
    queue.put((_right_click, x, y))


def call_function(func: callable, *args: tuple) -> None:
    queue.put((func, *args))


def _mouse_event_loop() -> None:
    while True:
        while queue.qsize() > 10:
            logger.warning(f"Too many elements in mouse queue ({queue.qsize()}), skipping event...")
            queue.get()
        try:
            func, *args = queue.get()
            func(*args)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error processing mouse event: {e}")


mouse_thread = threading.Thread(target=_mouse_event_loop, daemon=True)
mouse_thread.start()
