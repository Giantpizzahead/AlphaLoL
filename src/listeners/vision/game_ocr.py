"""
Contains helper functions for parsing text info from the game.
Most functions in this file are slow, and should be called sparingly.
"""
import math
import os
from dataclasses import dataclass
from typing import List

import cv2 as cv
import easyocr
import numpy as np

from misc import color_logging
from misc.definitions import ROOT_DIR
from listeners.vision import image_handler

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)

ocr_reader: easyocr.Reader
dummy_img = cv.imread(os.path.join(ROOT_DIR, "..", "img", "minion.png"))


def init_ocr():
    logger.info("Initializing OCR module...")
    global ocr_reader
    ocr_reader = easyocr.Reader(['en'], gpu=True)
    ocr_reader.detect(dummy_img)
    ocr_reader.recognize(dummy_img)
    logger.info("OCR modules loaded!")


@dataclass
class Text:
    x1: float
    y1: float
    x2: float
    y2: float
    text: str
    score: float

    def get_x(self) -> float:
        return (self.x1 + self.x2) / 2

    def get_y(self) -> float:
        return (self.y1 + self.y2) / 2


def find_text(img: np.ndarray, x1=-1, y1=-1, x2=-1, y2=-1, scale=1.0, lower=True) -> List[Text]:
    """
    Find any text within the given region in the screenshot.
    :param img: The screenshot to search in.
    :param x1: The left x coordinate of the region.
    :param y1: The top y coordinate of the region.
    :param x2: The right x coordinate of the region.
    :param y2: The bottom y coordinate of the region.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :param lower: Whether to lowercase the text.
    :return: A list of all the text in the screenshot, along with their locations.
    """
    if x1 != -1:
        # Crop image
        img = img[int(y1):int(y2), int(x1):int(x2)]
    else:
        x1 = 0
        y1 = 0
    # Read text from image
    if scale != 1:
        img = image_handler.scale_image(img, scale)
    raw_text = ocr_reader.readtext(img, text_threshold=0.5)
    text = []
    for r in raw_text:
        if r[2] < 0.4:
            continue
        nx1 = round(math.floor(min(r[0][0][0], r[0][3][0])) / scale + x1)
        nx2 = round(math.ceil(max(r[0][1][0], r[0][2][0])) / scale + x1)
        ny1 = round(math.floor(min(r[0][0][1], r[0][1][1])) / scale + y1)
        ny2 = round(math.ceil(max(r[0][2][1], r[0][3][1])) / scale + y1)
        text.append(Text(nx1, ny1, nx2, ny2, (r[1].lower() if lower else r[1]), r[2]))
    return text
