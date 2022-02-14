"""
Contains helper functions for parsing info about the current game state.
"""

from dataclasses import dataclass
from typing import List

import numpy as np
import cv2 as cv
import os
import easyocr

from misc import color_logging
from misc.definitions import ROOT_DIR
from listeners.vision import template_match

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)
logger.info("Initializing vision module...")

minion_template = cv.imread(os.path.join(ROOT_DIR, "..", "img", "minion.png"))


@dataclass
class Minion:
    x1: float
    y1: float
    x2: float
    y2: float
    allied: bool
    health: float


def find_minions(img: np.ndarray, scale=1.0) -> List[Minion]:
    """
    Find all minions in the given screenshot.
    Note: This function cannot tell the difference between the different types of minions.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :return: A list of all minions in the screenshot.
    """

    # Find the edges of minion health bars to locate them
    # Old: 0 0 10 and 255 255 22
    lower_edge = np.array([80, 0, 10])
    upper_edge = np.array([140, 255, 23])
    template = minion_template
    all_matches = template_match.find_outline_matches(img, template, lower_edge, upper_edge, scale)

    # Eliminate duplicate matches
    matches = []
    all_matches = all_matches[:2000]
    logger.debug(f"Found {len(all_matches)} matches with duplicates")
    for m1 in all_matches:
        for m2 in matches:
            # Check if these are the same health bars
            if m1.x1 + 10 < m2.x2 - 10 and m1.x2 - 10 > m2.x1 + 10 and abs(m1.y1 - m2.y1) <= 2 and abs(
                    m1.y2 - m2.y2) <= 2:
                break
        else:
            # No intersections
            matches.append(m1)
    logger.debug(f"Found {len(matches)} unique matches")

    # Determine minion side and health
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_blue = np.array([101, 156, 117])
    upper_blue = np.array([105, 163, 212])
    lower_red = np.array([0, 135, 118])
    upper_red = np.array([4, 143, 212])
    minions = []
    for m in matches:
        # Rightmost pixel with a visible health bar color
        width = template.shape[1] - 2
        y = (m.y1 + m.y2) // 2
        low = 0
        high = width
        allied = None
        while low < high:
            mid = (low + high + 1) // 2
            color = img[y, m.x1 + mid]
            # Check if color is within defined bounds
            is_blue = all(lower_blue[i] <= color[i] <= upper_blue[i] for i in range(3))
            is_red = all(lower_red[i] <= color[i] <= upper_red[i] for i in range(3))
            if is_blue:
                allied = True
            elif is_red:
                allied = False
            if is_blue or is_red:
                low = mid
            else:
                high = mid - 1
        health = low / width
        # Only add confirmed minions (no false positives)
        if allied is not None:
            # Minion is below health bar
            # 1280 x 720:
            # minion = Minion(m.x1+10, m.y1+20, m.x2-10, m.y2+45, allied, health)
            # 1920 x 1080:
            minion = Minion(m.x1, m.y1 + 25, m.x2, m.y2 + 75, allied, health)
            minions.append(minion)
    logger.debug(f"Found {len(minions)} minions")
    return minions


ocr_reader = easyocr.Reader(['en'], gpu=True)
player_template = cv.imread(os.path.join(ROOT_DIR, "..", "img", "player.png"))
ocr_reader.readtext(player_template)


@dataclass
class Player:
    x1: float
    y1: float
    x2: float
    y2: float
    allied: bool
    controllable: bool
    health: float
    mana: float
    level: int


def find_players(img: np.ndarray, scale=1.0) -> List[Player]:
    """
    Find all players in the given screenshot.
    Note: This function cannot tell who the player actually is.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :return: A list of all players in the screenshot. Level will be -1 if it can't be parsed.
    """

    # Find the edges of player health bars to locate them
    # Lower: 22 0 51
    # Upper: 60 32 115
    lower_edge = np.array([0, 0, 62])
    upper_edge = np.array([179, 33, 121])
    template = player_template
    all_matches = template_match.find_outline_matches(img, template, lower_edge, upper_edge, scale)
    all_matches = all_matches[:2000]
    logger.debug(f"Found {len(all_matches)} matches with duplicates")

    # Eliminate duplicate matches
    matches = []
    for m1 in all_matches:
        for m2 in matches:
            # Check if these are the same health bars
            if m1.x1 + 30 < m2.x2 - 30 and m1.x2 - 30 > m2.x1 + 30 and abs(m1.y1 - m2.y1) <= 3 and abs(
                    m1.y2 - m2.y2) <= 3:
                break
        else:
            # No intersections
            matches.append(m1)
    logger.debug(f"Found {len(matches)} unique matches")

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_green = np.array([53, 190, 131])
    upper_green = np.array([60, 200, 149])
    lower_blue = np.array([97, 219, 192])
    upper_blue = np.array([103, 227, 215])
    lower_red = np.array([0, 209, 143])
    upper_red = np.array([5, 217, 152])
    lower_mana = np.array([93, 155, 208])
    upper_mana = np.array([104, 195, 225])
    players = []
    for m in matches:
        # Parse health bar
        # TODO: Does not account for shielding (which causes a white hp bar)
        xh_left = m.x1 + 26
        xh_right = m.x2 - 4
        width = xh_right - xh_left
        yh = m.y1 + 15
        player_type = -1
        for i in range(round(width), -1, -1):
            color = hsv[yh, xh_left + i]
            # Check if color is within defined bounds
            is_green = all(lower_green[i] <= color[i] <= upper_green[i] for i in range(3))
            is_blue = all(lower_blue[i] <= color[i] <= upper_blue[i] for i in range(3))
            is_red = all(lower_red[i] <= color[i] <= upper_red[i] for i in range(3))
            if is_green:
                player_type = 0
            elif is_blue:
                player_type = 1
            elif is_red:
                player_type = 2
            if is_green or is_blue or is_red:
                health = i / width
                break
        else:
            health = 0
        # Avoid false positives
        if player_type == -1:
            continue
        # Parse mana bar
        ym = m.y1 + 21
        for i in range(round(width), -1, -1):
            color = hsv[ym, xh_left + i]
            # Check if color is within defined bounds
            is_mana = all(lower_mana[i] <= color[i] <= upper_mana[i] for i in range(3))
            if is_mana:
                mana = i / width
                break
        else:
            mana = 0
        # Attempt to parse level
        # 1920 x 1080
        x1 = m.x1 + 6
        y1 = m.y1 + 8
        x2 = x1 + 16
        y2 = y1 + 12
        img_level = img[y1:y2, x1:x2]
        # disp = template_match.scale_image(img_level, 4)
        # cv.imshow("level", disp)
        level = ocr_reader.recognize(img_level, allowlist="0123456789", detail=0, paragraph=True)
        logger.debug(f"Level OCR: \"{' '.join(level)}\"")
        if not level:
            level = -1
        else:
            level = ' '.join(level)
            if not level.isdigit():
                level = -1
            else:
                level = int(level)
                if level < 1 or level > 18:
                    level = -1
        player = Player(m.x1 + 20, m.y1 + 55, m.x2 - 20, m.y2 + 130, player_type != 2, player_type == 0, health, mana,
                        level)
        players.append(player)
    logger.debug(f"Found {len(players)} players")
    return players


logger.info("Vision module loaded!")
