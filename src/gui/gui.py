"""
General GUI methods, along with the high-level logic.

TODO:
Handle client update
"""

import pynput

from gui import key_listener
from gui import menu
from gui import os_helper
from gui.gui_constants import GUIState, GameTypes
from misc import color_logging
from misc.rng import rsleep

logger = color_logging.getLogger('gui', level=color_logging.DEBUG)
mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()
state = GUIState.CLOSED


def init() -> None:
    """
    Initializes the GUI.
    """
    key_listener.init()


def get_state() -> GUIState:
    """
    Gets the current GUI state, updating it in the process.
    :return: The current GUI state.
    """
    return update_state()


def update_state(focus=False) -> GUIState:
    """
    Updates the current GUI state by checking which windows are currently open.
    :param focus: Whether to focus the game / menu windows
    :return: The current GUI state.
    """

    # Check if the client / game windows are open
    menu_app = os_helper.find_menu()
    game_app = os_helper.find_game()

    # Update the GUI state
    global state
    if game_app:
        state = GUIState.GAME
        if focus:
            os_helper.focus_app(game_app)
    elif menu_app:
        state = GUIState.MENU
        if focus:
            os_helper.focus_app(menu_app)
    else:
        state = GUIState.CLOSED
    logger.debug("Current GUI state: {}".format(state.name))
    return state


def start_client() -> bool:
    """
    Boots up League of Legends (if not already booted).
    :return: Whether the client was successfully booted (True if already on).
    """

    # Check if the client is already on
    if update_state(focus=True) != GUIState.CLOSED:
        logger.info("Client is already on")
        return True

    # Open the client
    logger.info("Opening the League of Legends client...")
    os_helper.launch_client()

    # Periodically check if the client is open
    if update_state(focus=True) == GUIState.CLOSED:
        for i in range(7):
            rsleep(5)
            if update_state(focus=True) != GUIState.CLOSED:
                break
        rsleep(10)
        update_state(focus=True)

    if state != GUIState.CLOSED:
        logger.info("Client opened!")
        return True
    else:
        logger.error("Client could not be started (timed out)")
        return False


def _start_game(game_type: GameTypes) -> bool:
    """
    Starts a game of the given type (goes into but does not do champion select).
    :param game_type: The type of game to start.
    :return: Whether the game was successfully started.
    """

    # Start the client
    logger.info("Starting game of type {}".format(game_type.name))
    if not start_client():
        logger.error("Unable to start game: Client could not be started")
        return False
    elif get_state() == GUIState.GAME:
        logger.error("Unable to start game: Another game is currently in progress")
        return False

    # Start the game
    return menu.start_game(game_type)


def start_game(game_type: GameTypes) -> None:
    """
    Starts a game of the given type (goes into but does not do champion select).
    This is not blocking; a thread is made to start the game.
    :param game_type: The type of game to start.
    :return: Whether the game was successfully started.
    """
    # threading.Thread(target=_start_game, args=(game_type,))
    pass
