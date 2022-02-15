"""
Contains helper functions to do common actions in League of Legends.
"""

from controllers.keyboard.keyboard import *
from controllers.mouse.mouse import *
from misc import color_logging
from misc.rng import rsleep
from listeners.vision import window_tracker

logger = color_logging.getLogger('game_controller', level=color_logging.INFO)


def use_action(key: Union[str, Key]) -> None:
    """
    Uses an ability / item / summoner spell by pressing the given key.
    :param key: The key to press.
    """
    logger.debug(f"Use action {key}")
    press_key(key)


def use_skillshot(key: Union[str, Key], x: float, y: float) -> None:
    """
    Uses a skillshot with the given key, aimed at the given coordinates.
    :param key: The key to press.
    :param x: The x coordinate to aim at.
    :param y: The y coordinate to aim at.
    """
    logger.debug(f"Use skillshot {key} at ({x}, {y})")
    x, y = window_tracker.offset_game_pos(x, y)
    move_mouse(x, y)
    rsleep(0.01, s=0.3)
    press_key(key)


def attack_move(x: float, y: float) -> None:
    """
    Attack moves to the given coordinates.
    :param x: The x coordinate to move to.
    :param y: The y coordinate to move to.
    """
    logger.debug(f"Attack move to ({x}, {y})")
    x, y = window_tracker.offset_game_pos(x, y)
    move_mouse(x, y)
    press_key('a')
    press_left()
    release_left()


def level_ability(key: Union[str, Key]) -> None:
    """
    Attempts to level an ability by pressing Control + the given key.
    :param key: The key to press.
    """
    logger.debug(f"Level ability {key}")
    press_key_with_modifier(key, Key.ctrl)


def right_click(x: float, y: float) -> None:
    logger.debug(f"Right click at ({x:.2f}, {y:.2f})")
    x, y = window_tracker.offset_game_pos(x, y)
    move_mouse(x, y)
    press_right()
    release_right()
