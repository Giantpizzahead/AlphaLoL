"""
Contains helper functions for parsing info about the current game state.
TODO: Lots of code reuse here, could probably be boiled down a LOT.
"""
import math
import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import cv2 as cv
import os
import easyocr

from misc import color_logging
from misc.definitions import ROOT_DIR
from listeners.vision import image_handler

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)

dummy_img = cv.imread(os.path.join(ROOT_DIR, "..", "img", "minion.png"))
minion_template: np.ndarray
player_template: np.ndarray
big_objective_template: np.ndarray
small_objective_template: np.ndarray
ocr_reader: easyocr.Reader

# These wider bounds detect everything, including stuff like ward health bars, which may be undesirable.
lower_blue = np.array([90, 140, 95])
upper_blue = np.array([112, 240, 230])
lower_red = np.array([0, 120, 100])
upper_red = np.array([10, 230, 225])

pool_find_minions: mp.Pool
pool_find_players: mp.Pool
pool_find_small_objectives: mp.Pool
pool_find_big_objectives: mp.Pool


def init_pool_find_minions():
    global minion_template
    minion_template = cv.imread(os.path.join(ROOT_DIR, "..", "img", "minion.png"))
    logger.debug("Minions module loaded")


def init_pool_find_players():
    global player_template
    player_template = cv.imread(os.path.join(ROOT_DIR, "..", "img", "player.png"))
    # OCR setup and warmup
    global ocr_reader
    ocr_reader = easyocr.Reader(['en'], gpu=True)
    ocr_reader.detect(dummy_img)
    ocr_reader.recognize(dummy_img)
    logger.debug("Players module loaded")


def init_pool_find_small_objectives():
    global small_objective_template
    small_objective_template = cv.imread(os.path.join(ROOT_DIR, "..", "img", "small_objective.png"))
    logger.debug("Small objective module loaded")


def init_pool_find_big_objectives():
    global big_objective_template
    big_objective_template = cv.imread(os.path.join(ROOT_DIR, "..", "img", "big_objective.png"))
    logger.debug("Big objective module loaded")


def init_vision() -> None:
    """
    Initializes the vision module.
    """
    logger.info("Initializing vision modules (this might take a bit)...")
    global pool_find_minions, pool_find_players, pool_find_small_objectives, pool_find_big_objectives
    pool_find_minions = mp.Pool(processes=1, initializer=init_pool_find_minions)
    pool_find_players = mp.Pool(processes=1, initializer=init_pool_find_players)
    pool_find_small_objectives = mp.Pool(processes=1, initializer=init_pool_find_small_objectives)
    pool_find_big_objectives = mp.Pool(processes=1, initializer=init_pool_find_big_objectives)
    find_all(dummy_img, timeout=30)
    logger.info("Vision modules loaded!")


@dataclass
class Minion:
    x1: float
    y1: float
    x2: float
    y2: float
    allied: bool
    health: float

    def get_x(self) -> float:
        return (self.x1 + self.x2) / 2

    def get_y(self) -> float:
        return (self.y1 + self.y2) / 2


def _find_minions(img: np.ndarray, scale=1.0) -> List[Minion]:
    # Find the edges of minion health bars to locate them
    # Old: 0 0 10 and 255 255 22
    lower_edge = np.array([80, 0, 10])
    upper_edge = np.array([140, 255, 23])
    template = minion_template
    all_matches = image_handler.find_outline_matches(img, template, lower_edge, upper_edge, scale)

    # Eliminate duplicate matches
    matches = []
    # logger.debug(f"Found {len(all_matches)} matches with duplicates")
    for m1 in all_matches:
        for m2 in matches:
            # Check if these are the same health bars
            if m1.x1 + 10 < m2.x2 - 10 and m1.x2 - 10 > m2.x1 + 10 and abs(m1.y1 - m2.y1) <= 2 and abs(
                    m1.y2 - m2.y2) <= 2:
                break
        else:
            # No intersections
            matches.append(m1)
    # logger.debug(f"Found {len(matches)} unique matches")

    # Determine minion side and health
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # lower_blue = np.array([101, 156, 117])
    # upper_blue = np.array([105, 163, 212])
    # lower_red = np.array([0, 135, 118])
    # upper_red = np.array([4, 143, 212])
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


def find_minions(img: np.ndarray, scale=1.0) -> List[Minion]:
    """
    Find all minions in the given screenshot.
    Note: This function cannot tell the difference between the different types of minions.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :return: A list of all minions in the screenshot.
    TODO: Use more precise color masks? Maybe don't need to? (Using vague ones detects wards /
    has false positives and weird detections for jg monsters)
    """
    return pool_find_minions.apply(_find_minions, args=(img, scale))


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

    def get_x(self) -> float:
        return (self.x1 + self.x2) / 2

    def get_y(self) -> float:
        return (self.y1 + self.y2) / 2


def _find_players(img: np.ndarray, scale=1.0) -> List[Player]:
    # Find the edges of player health bars to locate them
    # Lower: 22 0 51
    # Upper: 60 32 115
    lower_edge = np.array([0, 0, 62])
    upper_edge = np.array([179, 33, 121])
    template = player_template
    all_matches = image_handler.find_outline_matches(img, template, lower_edge, upper_edge, scale)
    # logger.debug(f"Found {len(all_matches)} matches with duplicates")

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
    # logger.debug(f"Found {len(matches)} unique matches")

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower_green = np.array([53, 190, 131])
    upper_green = np.array([60, 200, 149])
    # lower_blue = np.array([97, 219, 192])
    # upper_blue = np.array([103, 227, 215])
    # lower_red = np.array([0, 209, 143])
    # upper_red = np.array([5, 217, 152])
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
        # disp = image_handler.scale_image(img_level, 4)
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
        player = Player(m.x1 + 20, m.y1 + 75, m.x2 - 20, m.y2 + 150, player_type != 2, player_type == 0, health, mana,
                        level)
        players.append(player)
    logger.debug(f"Found {len(players)} players")
    return players


def find_players(img: np.ndarray, scale=1.0) -> List[Player]:
    """
    Find all players in the given screenshot.
    Note: This function cannot tell who the player actually is.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :return: A list of all players in the screenshot. Level will be -1 if it can't be parsed.
    """
    return pool_find_players.apply(_find_players, args=(img, scale))


@dataclass
class Objective:
    x1: float
    y1: float
    x2: float
    y2: float
    allied: bool
    type: str
    health: float

    def get_x(self) -> float:
        return (self.x1 + self.x2) / 2

    def get_y(self) -> float:
        return (self.y1 + self.y2) / 2


def _find_small_objectives(img: np.ndarray, scale=1.0) -> List[Objective]:
    # Find the edges of objective health bars to locate them
    lower_edge = np.array([16, 68, 70])
    upper_edge = np.array([28, 190, 220])
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Find small objectives
    all_matches = image_handler.find_outline_matches(img, small_objective_template, lower_edge, upper_edge, scale)
    # Eliminate duplicate matches
    matches = []
    for m1 in all_matches:
        for m2 in matches:
            # Check if these are the same health bars
            if m1.x1 + 10 < m2.x2 - 10 and m1.x2 - 10 > m2.x1 + 10 and abs(m1.y1 - m2.y1) <= 2 and abs(
                    m1.y2 - m2.y2) <= 2:
                break
        else:
            # No intersections
            matches.append(m1)
    small = []
    for m in matches:
        # Parse health bar
        xh_left = m.x1 + 3
        xh_right = m.x2 - 4
        width = xh_right - xh_left
        yh = m.y1 + 8
        obj_type = -1
        for i in range(round(width), -1, -1):
            color = hsv[yh, xh_left + i]
            # Check if color is within defined bounds
            is_blue = all(lower_blue[i] <= color[i] <= upper_blue[i] for i in range(3))
            is_red = all(lower_red[i] <= color[i] <= upper_red[i] for i in range(3))
            if is_blue:
                obj_type = 0
            elif is_red:
                obj_type = 1
            if is_blue or is_red:
                health = i / width
                break
        else:
            health = 0
        # Avoid false positives
        if obj_type == -1:
            continue
        small.append(Objective(m.x1 + 15, m.y1 + 100, m.x2 - 15, m.y2 + 270, obj_type == 0, "small", health))

    logger.debug(f"Found {len(small)} small objectives")
    return small


def find_small_objectives(img: np.ndarray, scale=1.0) -> List[Objective]:
    """
    Find all small objectives in the given screenshot.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :return: A list of all small objectives in the screenshot.
    """
    return pool_find_small_objectives.apply(_find_small_objectives, args=(img, scale))


def _find_big_objectives(img: np.ndarray, scale=1.0) -> List[Objective]:
    # Find the edges of objective health bars to locate them
    lower_edge = np.array([16, 68, 70])
    upper_edge = np.array([28, 190, 220])
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    # Find big objectives
    all_matches = image_handler.find_outline_matches(img, big_objective_template, lower_edge, upper_edge, scale)
    # Eliminate duplicate matches
    matches = []
    for m1 in all_matches:
        for m2 in matches:
            # Check if these are the same health bars
            if m1.x1 + 10 < m2.x2 - 10 and m1.x2 - 10 > m2.x1 + 10 and abs(m1.y1 - m2.y1) <= 2 and abs(
                    m1.y2 - m2.y2) <= 2:
                break
        else:
            # No intersections
            matches.append(m1)
    big = []
    for m in matches:
        # Parse health bar
        xh_left = m.x1 + 6
        xh_right = m.x2 - 7
        width = xh_right - xh_left
        yh = m.y1 + 12
        obj_type = -1
        for i in range(round(width), -1, -1):
            color = hsv[yh, xh_left + i]
            # Check if color is within defined bounds
            is_blue = all(lower_blue[i] <= color[i] <= upper_blue[i] for i in range(3))
            is_red = all(lower_red[i] <= color[i] <= upper_red[i] for i in range(3))
            if is_blue:
                obj_type = 0
            elif is_red:
                obj_type = 1
            if is_blue or is_red:
                health = i / width
                break
        else:
            health = 0
        # Avoid false positives
        if obj_type == -1:
            continue
        big.append(Objective(m.x1 + 40, m.y1 + 100, m.x2 - 40, m.y2 + 320, obj_type == 0, "big", health))

    logger.debug(f"Found {len(big)} big objectives")
    return big


def find_big_objectives(img: np.ndarray, scale=1.0) -> List[Objective]:
    """
    Find all big objectives in the given screenshot.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :return: A list of all big objectives in the screenshot.
    """
    return pool_find_big_objectives.apply(_find_big_objectives, args=(img, scale))


def find_all(img, scale=1.0, timeout=5) -> Tuple[List[Minion], List[Player], List[Objective]]:
    """
    Finds players, turrets, and all objectives in the given screenshot.
    :param img: The screenshot to search in.
    :param scale: The amount to scale the images by. Lower values will be faster, but less accurate.
    :param timeout: The maximum amount of time to wait for the searches to finish.
    :return: Lists of minions, players, and objectives.
    """
    raw_minions = pool_find_minions.apply_async(_find_minions, args=(img, scale))
    raw_players = pool_find_players.apply_async(_find_players, args=(img, scale))
    raw_small_objectives = pool_find_small_objectives.apply_async(_find_small_objectives, args=(img, scale))
    raw_big_objectives = pool_find_big_objectives.apply_async(_find_big_objectives, args=(img, scale))
    raw_minions = raw_minions.get(timeout=timeout)
    raw_players = raw_players.get(timeout=timeout)
    raw_small_objectives = raw_small_objectives.get(timeout=timeout)
    raw_big_objectives = raw_big_objectives.get(timeout=timeout)
    return raw_minions, raw_players, raw_small_objectives + raw_big_objectives


def close() -> None:
    pool_find_minions.close()
    pool_find_minions.join()
    pool_find_players.close()
    pool_find_players.join()
    pool_find_small_objectives.close()
    pool_find_small_objectives.join()
    pool_find_big_objectives.close()
    pool_find_big_objectives.join()
