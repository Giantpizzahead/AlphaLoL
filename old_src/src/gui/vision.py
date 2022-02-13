"""
Handles screenshot feed and image recognition from the computer screen.

TODO:
Test different client resolutions
Multiple monitors?
"""

import os
import time

import cv2 as cv
import numpy as np
from mss import mss, screenshot

from misc import color_logging
from misc.rng import rsleep

# The resolution of the League of Legends client
# Must be correct for image recognition to work
client_res = (1280, 720)

# The resolution of the League of Legends game
# Must be correct for image recognition to work
game_res = (1280, 800)

# The amount that the screenshot & templates are scaled by.
# Lower values will be faster, but will make the images more blurry / lower image recognition accuracy.
resize_ratio = 0.5

# The length of time that has to elapse before a new screenshot is taken.
# Higher values will be faster, but will increase the time between updates.
update_interval = 0.8

# The length of time that must elapse after a screenshot is taken.
# This is meant to portray human reaction time.
reaction_delay = 0.1

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)
sct = mss()
scr: screenshot.ScreenShot
screen_res = (sct.monitors[0]['width'], sct.monitors[0]['height'])
template_ratio = 0.5 * (client_res[0] / 1280)
last_time = -1
img_cache = {}

if abs(client_res[0]/client_res[1] - 1280/720) > 1e-5:
    logger.critical("Bad client resolution ({}, {}). (Wrong aspect ratio)".format(client_res[0], client_res[1]))
    logger.critical("Image recognition will not work until the resolution in vision.py is fixed!")

if abs(game_res[0]/game_res[1] - 1280/800) > 1e-5:
    logger.critical("Bad game resolution ({}, {}). (Wrong aspect ratio)".format(client_res[0], client_res[1]))
    logger.critical("Image recognition will not work until the resolution in vision.py is fixed!")


def take_screenshot(top=0, left=0, width=screen_res[0], height=screen_res[1]) -> None:
    """
    Takes a new screenshot of the screen, resizing it based on the resize ratio.
    """
    global scr
    sct_img = sct.grab({'top': top, 'left': left, 'width': width, 'height': height})
    # noinspection PyTypeChecker
    scr = np.array(sct_img)[:, :, :3]
    r = resize_ratio * (screen_res[0] / scr.shape[1])
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
        rsleep(0.05)
        last_time = time.time()
        update()
        rsleep(reaction_delay)


def clear_cache() -> None:
    """
    Clears the cache.
    """
    img_cache.clear()


def find_image_locs(filename: str, threshold=0.75, display=False) -> tuple[list[tuple[float, float]], float, float]:
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
    rr = resize_ratio
    tr = template_ratio
    if filename in img_cache:
        # Use cache
        template_pb = img_cache[filename]
    else:
        template_pb = cv.imread("{}/../../img/{}".format(os.path.dirname(os.path.realpath(__file__)), filename),
                                cv.IMREAD_COLOR)
        # Resize image to make processing faster
        template_pb = cv.resize(template_pb, (int(template_pb.shape[1] * rr * tr), int(template_pb.shape[0] * rr * tr)),
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
        cv.imshow("{} template".format(filename), template_pb)

    # Scale coordinates
    for i, pt in enumerate(points):
        # (tr * 2) is very scuffed workaround for retina display
        x = (pt[0] + template_w / 2.0) / rr / (tr * 2)
        y = (pt[1] + template_h / 2.0) / rr / (tr * 2)
        points[i] = (x, y)

    logger.debug(f"{filename} with threshold={threshold} found at {len(points)} location(s):")
    logger.debug("maximum match = {:.2f} | ".format(np.max(res)) +
                 "[" + ", ".join("({:.0f}, {:.0f})".format(pt[0], pt[1]) for pt in points[:3]) + "]")
    return points, template_w, template_h


def find_menu_locs(filename: str, threshold=0.75, display=False) -> tuple[list[tuple[float, float]], float, float]:
    # Adjust template_ratio
    global template_ratio
    raw_tr = template_ratio
    template_ratio *= (client_res[0] / 1280)
    res = find_image_locs(filename, threshold, display)
    template_ratio = raw_tr
    return res


def find_game_locs(filename: str, threshold=0.75, display=False) -> tuple[list[tuple[float, float]], float, float]:
    # Adjust template_ratio
    global template_ratio
    raw_tr = template_ratio
    template_ratio *= (game_res[0] / 1280)
    res = find_image_locs(filename, threshold, display)
    template_ratio = raw_tr
    return res
