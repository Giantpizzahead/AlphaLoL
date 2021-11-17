"""
Allows the bot to move / click the mouse and press keys.
"""

from typing import Union

import pynput
from pynput.keyboard import Key
from pynput.mouse import Button
from misc import color_logging
from misc.rng import rnum, rsleep

logger = color_logging.getLogger('input_handler', level=color_logging.DEBUG)
mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()


def left_click(x: float, y: float) -> None:
    logger.debug("Left click at ({:.2f}, {:.2f})".format(x, y))
    mouse.position = (rnum(x, 1.5, True), rnum(y, 1.5, True))
    rsleep(0.032)
    mouse.press(Button.left)
    rsleep(0.032)
    mouse.release(Button.left)


def right_click(x: float, y: float) -> None:
    logger.debug("Right click at ({:.2f}, {:.2f})".format(x, y))
    mouse.position = (rnum(x, 1.5, True), rnum(y, 1.5, True))
    rsleep(0.032)
    mouse.press(Button.right)
    rsleep(0.032)
    mouse.release(Button.right)


def press_key(key: Union[str, Key]) -> None:
    logger.debug("{} key pressed".format(key))
    rsleep(0.032)
    keyboard.press(key)
    rsleep(0.032)
    keyboard.release(key)
