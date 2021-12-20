"""
Game-specific (fullscreen client) GUI code.
"""

from pynput.keyboard import Key

import cv2.cv2 as cv
from gui import input_handler
from gui import vision
from gui.gui_constants import GameState, GameOffsets
from gui.input_handler import press_key
from misc import color_logging
from misc.rng import rsleep

GAME_DEBUG = True

logger = color_logging.getLogger('game', level=color_logging.DEBUG)
state = GameState.NOT_VISIBLE
origin = (0, 0)


def left_click(x: float, y: float) -> None:
    """
    Left clicks at the given location *in the game*, applying appropriate offsets.
    :param x: The x location to click.
    :param y: The y location to click.
    """
    input_handler.left_click(x + origin[0], y + origin[1])


def right_click(x: float, y: float) -> None:
    """
    Right clicks at the given location *in the game*, applying appropriate offsets.
    :param x: The x location to click.
    :param y: The y location to click.
    """
    input_handler.right_click(x + origin[0], y + origin[1])


def move_mouse(x: float, y: float) -> None:
    """
    Moves the mouse to the given location *in the game*, applying appropriate offsets.
    :param x: The x location to click.
    :param y: The y location to click.
    """
    input_handler.move_mouse(x + origin[0], y + origin[1])


def get_state() -> GameState:
    """
    Gets the current menu state, updating it in the process.
    :return: The current menu state.
    """
    return update_state()


def update_state() -> GameState:
    """
    Updates the current menu state by searching for markers on the screen.
    :return: The current menu state.
    """

    global state, origin

    # Testing
    if GAME_DEBUG:
        logger.info((input_handler.mouse.position[0] - origin[0], input_handler.mouse.position[1] - origin[1]))
        anchor_l, _, _ = vision.find_game_locs("game_anchor.png", display=True)
        if (cv.waitKey(25) & 0xFF) == ord('q'):
            cv.destroyAllWindows()

    # Locate the game window
    anchor_l, _, _ = vision.find_game_locs("game_anchor.png")
    on_client = (len(anchor_l) != 0)
    if on_client:
        x = anchor_l[0][0] - GameOffsets.ANCHOR[0]
        y = anchor_l[0][1] - GameOffsets.ANCHOR[1]
        # origin = (x, y)
        state = GameState.OTHER
    else:
        state = GameState.NOT_VISIBLE
        logger.debug("Current game state: {}".format(state.name))
        return state

    return state


def auto_attack(x: float, y: float) -> None:
    press_key('a')
    rsleep(0.15)
    left_click(x, y)


def ping_missing(x: float, y: float) -> None:
    press_key('g')
    rsleep(0.15)
    move_mouse(x, y)
