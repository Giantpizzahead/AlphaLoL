"""
Contains helper functions for using the keyboard.
"""

from typing import Union

import pynput
from pynput.keyboard import Key

from misc import color_logging
from misc.rng import rsleep

logger = color_logging.getLogger('keyboard', level=color_logging.INFO)
mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()


def hold_key(key: Union[str, Key], duration: float) -> None:
    logger.debug(f"Holding {key} key for {duration} seconds")
    rsleep(0.032)
    keyboard.press(key)
    rsleep(duration)
    keyboard.release(key)


def press_key(key: Union[str, Key]) -> None:
    logger.debug(f"{key} key pressed")
    rsleep(0.032)
    keyboard.press(key)
    rsleep(0.032)
    keyboard.release(key)
