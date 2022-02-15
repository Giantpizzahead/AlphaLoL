"""
Contains helper functions for using the mouse.
"""

import pynput
from pynput.mouse import Button

from controllers.mouse import bezier_mouse
from misc import color_logging
from misc.rng import rnum, rsleep

logger = color_logging.getLogger('mouse', level=color_logging.INFO)
mouse = pynput.mouse.Controller()


def press_left() -> None:
    mouse.press(Button.left)
    rsleep(0.032)


def press_right() -> None:
    mouse.press(Button.right)
    rsleep(0.032)


def release_left() -> None:
    mouse.release(Button.left)
    rsleep(0.032)


def release_right() -> None:
    mouse.release(Button.right)
    rsleep(0.032)


def move_mouse(x: float, y: float) -> None:
    logger.debug(f"Move mouse to ({x:.2f}, {y:.2f})")
    cx, cy = bezier_mouse.mouse.position
    bezier_mouse.move_mouse(rnum(x, abs(cx-x)/40+5, True), rnum(y, abs(cy-y)/40+5, True))
    rsleep(0.01, s=0.3)


def left_click(x: float, y: float) -> None:
    logger.debug(f"Left click at ({x:.2f}, {y:.2f})")
    move_mouse(x, y)
    press_left()
    release_left()


def right_click(x: float, y: float) -> None:
    logger.debug(f"Right click at ({x:.2f}, {y:.2f})")
    move_mouse(x, y)
    press_right()
    release_right()


def hold_left_click() -> None:
    logger.debug("Hold left click")
    press_left()


def hold_right_click() -> None:
    logger.debug("Hold right click")
    rsleep(0.032)
    press_right()


def release_left_click() -> None:
    logger.debug("Release left click")
    release_left()


def release_right_click() -> None:
    logger.debug("Release right click")
    release_right()
