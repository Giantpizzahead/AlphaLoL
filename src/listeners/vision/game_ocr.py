"""
Contains helper functions for parsing text info from the game.
Most functions in this file are slow, and should be called sparingly.
"""
import math
import os
from dataclasses import dataclass
from typing import List

import cv2 as cv
import pytesseract
from pytesseract import Output
import numpy as np

from misc import color_logging
from misc.definitions import ROOT_DIR
from listeners.vision import image_handler

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)

dummy_img = cv.imread(os.path.join(ROOT_DIR, "img", "minion.png"))


def init_ocr():
    logger.info("Initializing OCR module...")
    # global ocr_reader
    # ocr_reader = easyocr.Reader(['en'], gpu=True)
    # ocr_reader.detect(dummy_img)
    # ocr_reader.recognize(dummy_img)
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

    # Invert and grayscale image
    img = cv.bitwise_not(img)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(img, config="--psm 12", output_type=Output.DICT)

    # Only keep boxes with level 5 that aren't only spaces and have confidence > 50
    text = []
    for i in range(len(data["level"])):
        # Remove non-english characters
        data["text"][i] = "".join([c for c in data["text"][i] if ord(c) < 128]).strip()
        if data["level"][i] == 5 and data["text"][i] != "" and data["conf"][i] > 50:
            nx1 = round(data["left"][i] / scale + x1)
            nx2 = round(data["left"][i] + data["width"][i] / scale + x1)
            ny1 = round(data["top"][i] / scale + y1)
            ny2 = round(data["top"][i] + data["height"][i] / scale + y1)
            text.append(Text(nx1, ny1, nx2, ny2,
                             (data["text"][i].lower() if lower else data["text"][i]),
                             data["conf"][i] / 100))
    return text
