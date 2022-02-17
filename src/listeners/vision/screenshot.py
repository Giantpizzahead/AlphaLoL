"""
Contains helper functions for taking screenshots of various portions of the screen.
"""

import cv2 as cv
import numpy as np
from mss import mss, screenshot

from misc import color_logging

logger = color_logging.getLogger('vision', level=color_logging.INFO)
sct = mss()
scr: screenshot.ScreenShot
screen_res = (sct.monitors[0]['width'], sct.monitors[0]['height'])


def take_screenshot(x1=0, y1=0, x2=screen_res[0], y2=screen_res[1], scale=1.0) -> np.ndarray:
    """
    Takes a screenshot of a given portion of the screen (defaults to entire screen).
    :param x1: Top left x coordinate.
    :param y1: Top left y coordinate.
    :param x2: Bottom right x coordinate.
    :param y2: Bottom right y coordinate.
    :param scale: Amount to scale the returned image by (<1 = smaller, >1 = larger).
    :return: The requested OpenCV image, in BGR format.
    """
    sct_img = sct.grab({'top': y1, 'left': x1, 'width': x2-x1, 'height': y2-y1})
    # noinspection PyTypeChecker
    scr = np.array(sct_img)[:, :, :3]
    scr = cv.resize(scr, (int(scr.shape[1] * scale), int(scr.shape[0] * scale)), interpolation=cv.INTER_AREA)
    logger.debug(f"Screenshot ({x1}, {y1}) to ({x2}, {y2})")
    return scr


def get_screen_res() -> (int, int):
    """
    Returns the resolution of the screen.
    :return: The screen resolution as a tuple (x, y).
    """
    return screen_res
