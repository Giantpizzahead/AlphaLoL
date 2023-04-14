"""
Contains helper functions to do common actions in League of Legends.
"""
from typing import Union, Tuple

from pynput.keyboard import Key

import controllers.keyboard.keyboard as keyboard
import controllers.mouse.mouse as mouse
from misc import color_logging
from listeners.vision import window_tracker

logger = color_logging.getLogger('controls', level=color_logging.INFO)
dry_run = False


def calc_position(x: float, y: float) -> Tuple[float, float]:
    # Don't click too close to the bottom of the screen
    y = min(y, window_tracker.get_game_res()[1] - 100)
    x, y = window_tracker.offset_game_pos(x, y)
    return x, y


def use_action(key: Union[str, Key]) -> None:
    """
    Uses an ability / item / summoner spell by pressing the given key.
    :param key: The key to press.
    """
    logger.debug(f"Use action {key}")
    if dry_run:
        return
    keyboard.press_key(key)


def use_skillshot(key: Union[str, Key], x: float, y: float) -> None:
    """
    Uses a skillshot with the given key, aimed at the given coordinates.
    :param key: The key to press.
    :param x: The x coordinate to aim at.
    :param y: The y coordinate to aim at.
    """
    logger.debug(f"Use skillshot {key} at ({x}, {y})")
    if dry_run:
        return
    x, y = calc_position(x, y)
    mouse.move_mouse(x, y)
    mouse.call_function(keyboard.press_key, key)


def attack_move(x: float, y: float) -> None:
    """
    Attack moves to the given coordinates.
    :param x: The x coordinate to move to.
    :param y: The y coordinate to move to.
    """
    logger.debug(f"Attack move to ({x}, {y})")
    if dry_run:
        return
    x, y = calc_position(x, y)
    mouse.move_mouse(x, y)
    mouse.call_function(keyboard.press_key, 'a')


def level_ability(key: Union[str, Key]) -> None:
    """
    Attempts to level an ability by pressing Control + the given key.
    :param key: The key to press.
    """
    logger.debug(f"Level ability {key}")
    if dry_run:
        return
    keyboard.press_key_with_modifier(key, Key.ctrl)


def press_key(key: Union[str, Key]) -> None:
    logger.debug(f"Press key {key}")
    if dry_run:
        return
    keyboard.press_key(key)


def left_click(x: float, y: float) -> None:
    logger.debug(f"Left click at ({x:.2f}, {y:.2f})")
    if dry_run:
        return
    x, y = calc_position(x, y)
    mouse.left_click(x, y)


def right_click(x: float, y: float) -> None:
    logger.debug(f"Right click at ({x:.2f}, {y:.2f})")
    if dry_run:
        return
    x, y = calc_position(x, y)
    mouse.right_click(x, y)


def left_click_only() -> None:
    logger.debug("Left click")
    if dry_run:
        return
    mouse.press_left()
    mouse.release_left()


def right_click_only() -> None:
    logger.debug("Right click")
    if dry_run:
        return
    mouse.press_right()
    mouse.release_right()


def move_mouse(x: float, y: float) -> None:
    logger.debug(f"Move mouse to ({x:.2f}, {y:.2f})")
    if dry_run:
        return
    x, y = calc_position(x, y)
    mouse.move_mouse(x, y)


def move_mouse_precise(x: float, y: float) -> None:
    logger.debug(f"Move mouse precisely to ({x:.2f}, {y:.2f})")
    if dry_run:
        return
    x, y = calc_position(x, y)
    # Move twice to offset randomness
    mouse.move_mouse(x, y)
    mouse.move_mouse(x, y)
