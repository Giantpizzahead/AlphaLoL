"""
Contains helper functions for matching templates to images.
Has functions for exact matches, outline matches, and scaled matches.
"""

from dataclasses import dataclass

import cv2 as cv
import numpy as np
from typing import List

from misc import color_logging
from misc.definitions import MAX_MATCHES

logger = color_logging.getLogger('template_match', level=color_logging.INFO)
# TODO: may cause issues with relative paths
img_cache = {}


def scale_image(img: np.ndarray, scale: float) -> np.ndarray:
    """
    Scales an image by a given factor.
    :param img: The image to scale.
    :param scale: The factor to scale by.
    :return: The scaled image.
    """
    return cv.resize(img, (round(img.shape[1] * scale), round(img.shape[0] * scale)), interpolation=cv.INTER_AREA)


def load_image(filename: str, scale=1) -> np.ndarray:
    """
    Loads and scales an image from a file. If the image is cached, returns that instead.
    :param filename: The image file.
    :param scale: The factor to scale by.
    :return: The scaled image.
    """
    if (filename, scale) not in img_cache:
        img = scale_image(cv.imread(filename, cv.IMREAD_COLOR), scale)
        img_cache[(filename, scale)] = img
    return img_cache[(filename, scale)]


@dataclass
class Match:
    x1: float
    y1: float
    x2: float
    y2: float
    score: float


def find_exact_matches(img: np.ndarray, template: np.ndarray, scale=1, threshold=0.75) -> List[Match]:
    """
    Finds the locations where a given template is present on the image, without scaling or rotation.
    :param img: The image to search in.
    :param template: The template to search for.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :param threshold: The threshold needed to count as a match. Lower values allow for more lenient matches.
    :return: A list of matches, sorted by highest score first.
    """

    # Can the image have a match?
    if template.shape[0] > img.shape[0] or template.shape[1] > img.shape[1]:
        return []

    # Downscale images for efficiency
    if scale != 1:
        img = scale_image(img, scale)
        template = scale_image(template, scale)

    # Locate template in original image
    res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))

    # Return matches
    matches = []
    for pt in points:
        matches.append(Match(x1=pt[0], y1=pt[1], x2=pt[0]+template.shape[1]-1, y2=pt[1]+template.shape[0]-1,
                             score=res[pt[1]][pt[0]]))
        if len(matches) >= MAX_MATCHES:
            break
    # Upscale coordinates
    if scale != 1:
        for m in matches:
            m.x1 = round(m.x1 / scale)
            m.x2 = round(m.x2 / scale)
            m.y1 = round(m.y1 / scale)
            m.y2 = round(m.y2 / scale)
    matches = sorted(matches, key=lambda m: m.score, reverse=True)
    return matches


def find_outline_matches(img: np.ndarray, template: np.ndarray, lower_mask: np.ndarray, upper_mask: np.ndarray,
                         scale=1, threshold=0.75) -> List[Match]:
    """
    Finds the locations where a given template's outline is present on the image, without scaling or rotation.
    This turns the images into binary images depending on whether the colors are in [lower_mask, upper_mask], then looks
    for template matches in the binary images.
    :param img: The image to search in.
    :param template: The template to search for.
    :param lower_mask: The lower HSV mask to use.
    :param upper_mask: The upper HSV mask to use.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :param threshold: The threshold needed to count as a match. Lower values allow for more lenient matches.
    :return: A list of matches, sorted by highest score first.
    """

    # Can the image have a match?
    if template.shape[0] > img.shape[0] or template.shape[1] > img.shape[1]:
        return []

    # Downscale images for efficiency
    if scale != 1:
        img = scale_image(img, scale)
        template = scale_image(template, scale)

    # Generate binary images
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    img_mask = cv.inRange(img, lower_mask, upper_mask)
    template = cv.cvtColor(template, cv.COLOR_BGR2HSV)
    template_mask = cv.inRange(template, lower_mask, upper_mask)

    # Display images for debugging purposes
    '''
    # Combine images
    h1, w1 = template_mask.shape[:2]
    h2, w2 = img_mask.shape[:2]
    disp = np.zeros((max(h1, h2), w1 + w2), np.uint8)
    disp[:h1, :w1] = template_mask
    disp[:h2, w1:w1 + w2] = img_mask
    disp = scale_image(disp, 0.7)
    cv.imshow("disp", disp)
    cv.waitKey(0)
    '''

    # Find exact matches
    matches = find_exact_matches(img_mask, template_mask, threshold=threshold)

    # Upscale coordinates
    if scale != 1:
        for m in matches:
            m.x1 = round(m.x1 / scale)
            m.x2 = round(m.x2 / scale)
            m.y1 = round(m.y1 / scale)
            m.y2 = round(m.y2 / scale)
    return matches


def find_exact_scaled_matches(img: np.ndarray, template: np.ndarray, scale=1, threshold=0.75) -> List[Match]:
    """
    Finds the locations where a given template is present on the image, with scaling but without rotation.
    :param img: The image to search in.
    :param template: The template to search for.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :param threshold: The threshold needed to count as a match. Lower values allow for more lenient matches.
    :return: A list of matches.
    """

    # Downscale images for efficiency
    if scale != 1:
        img = scale_image(img, scale)
        template = scale_image(template, scale)

    # Try a bunch of different scales, and return the best one
    # Scales are relative to known League resolutions
    scales = [2560/1920, 1920/1920, 1600/1920, 1280/1920, 1024/1920]
    all_matches = []
    scores = []
    for s in scales:
        # s = Amount to scale the template by to find the image
        matches: List[Match]
        if s <= 1:
            new_template = scale_image(template, s)
            matches = find_exact_matches(img, new_template, threshold=threshold)
        else:
            # Downscale image instead of upscaling template for efficiency
            new_img = scale_image(img, 1/s)
            matches = find_exact_matches(new_img, template, threshold=threshold)
            for m in matches:
                m.x1 *= s
                m.x2 *= s
                m.y1 *= s
                m.y2 *= s
        logger.debug(f"Found {len(matches)} matches at scale {s}")
        if len(matches) > 0:
            all_matches.append(matches)
            scores.append(max(m.score for m in matches))

    # Get and return best matches
    matches = []
    if all_matches:
        matches = all_matches[np.argmax(scores)]
    # Upscale coordinates
    if scale != 1:
        for m in matches:
            m.x1 = round(m.x1 / scale)
            m.x2 = round(m.x2 / scale)
            m.y1 = round(m.y1 / scale)
            m.y2 = round(m.y2 / scale)
    return matches
