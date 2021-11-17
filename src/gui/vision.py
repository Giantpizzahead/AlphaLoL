"""
Handles screenshot feed and image recognition from the computer screen.
"""

import time

import cv2.cv2 as cv
import numpy as np
from mss import mss, screenshot

from misc import color_logging
from misc.rng import rsleep

logger = color_logging.getLogger('vision', level=color_logging.INFO)
resize_ratio = 0.3
update_interval = 0.8
reaction_delay = 0.1
sct = mss()
scr: screenshot.ScreenShot
last_time = -1
img_cache = {}


def take_screenshot(top=0, left=0, width=1600, height=2560) -> None:
    """
    Takes a new screenshot of the screen, resizing it based on the resize ratio.
    """
    global scr
    sct_img = sct.grab({'top': top, 'left': left, 'width': width, 'height': height})
    # noinspection PyTypeChecker
    scr = np.array(sct_img)[:, :, :3]
    r = resize_ratio
    scr = cv.resize(scr, (int(scr.shape[1] * r), int(scr.shape[0] * r)), interpolation=cv.INTER_AREA)


def update() -> None:
    """
    Updates the screenshot.
    """
    take_screenshot()


def update_if_needed() -> None:
    """
    Updates the screenshot if enough time has passed.
    """
    global last_time
    if time.time() - last_time >= update_interval:
        # TODO: Multithread so this isn't blocking (careful with data races though)
        rsleep(reaction_delay / 5)
        last_time = time.time()
        update()
        rsleep(reaction_delay)


def clear_cache() -> None:
    """
    Clears the cache.
    """
    img_cache.clear()


def find_image_locs(filename: str, threshold=0.8, display=False) -> tuple[list[tuple[float, float]], float, float]:
    """
    Finds the locations where a given image is present on the screen.
    :param filename: The filename of the image to search for.
    :param threshold: The threshold needed to count as a match. Higher values mean more exact matches and less results.
    :param display: Whether to display the found matches using a video feed (for debugging purposes).
    :return: tuple[width of matches, height of matches, list[tuples of integer (x, y) coords for center of matches]]
    """

    # TODO: Only look for target images in specific locations?
    # Update screenshot
    update_if_needed()

    # Load image template in BGR format
    r = resize_ratio
    if filename in img_cache:
        # Use cache
        template_pb = img_cache[filename]
    else:
        template_pb = cv.imread("img/{}".format(filename), cv.IMREAD_COLOR)
        # Resize image to make processing faster
        template_pb = cv.resize(template_pb, (int(template_pb.shape[1] * r), int(template_pb.shape[0] * r)),
                                interpolation=cv.INTER_AREA)
        # Cache template image for next time
        img_cache[filename] = template_pb
    _, template_w, template_h = template_pb.shape[::-1]

    # Locate button template in original image
    global scr
    res = cv.matchTemplate(scr, template_pb, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))

    # Display found button locations
    if display:
        new_scr = scr.copy()
        for pt in points:
            cv.rectangle(new_scr, pt, (pt[0] + template_w, pt[1] + template_h), (0, 0, 255), 2)
        cv.imshow("{} t={}".format(filename, threshold), np.array(new_scr))

    # Scale coordinates
    for i, pt in enumerate(points):
        x = (pt[0] + template_w / 2.0) / r / 2
        y = (pt[1] + template_h / 2.0) / r / 2
        points[i] = (x, y)

    logger.debug(f"{filename} with threshold={threshold} found at {len(points)} locations:")
    logger.debug("[" + ", ".join("({:.0f}, {:.0f})".format(pt[0], pt[1]) for pt in points[:5]) + "]")
    return points, template_w, template_h
