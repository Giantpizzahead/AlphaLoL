"""
Listens to and handles keyboard events (for manually controlling the AI).
"""

import _thread
import pynput
from pynput.keyboard import HotKey, Key

from gui import gui
from gui.gui_constants import GameTypes
from misc import color_logging

logger = color_logging.getLogger('keyboard', level=color_logging.INFO)
keyboard = pynput.keyboard.Controller()


def init() -> None:
    """
    Initializes the keyboard listener.
    """
    logger.debug("Listening for keyboard events...")
    listener.start()


def on_shift_h() -> None:
    """
    Displays a help menu for the application.
    """
    logger.info("""
    Shift-H: Display help menu
    Shift-Q: Quit the program
    Shift-T: Toggles the bot's mouse and keyboard control
    Shift-M: Starts a game (Tutorial Part 2)
    """)


def on_shift_q() -> None:
    """
    Quit the application.
    """
    logger.info("Shift-Q pressed, exiting...")
    _thread.interrupt_main()


def on_shift_t() -> None:
    """
    Toggle the bot (stop allowing it to control the mouse / keyboard).
    """
    logger.info("Shift-T pressed, toggling bot...")


def on_shift_m() -> None:
    """
    Starts a game (Tutorial Part 2).
    """
    logger.info("Shift-M pressed, starting game...")
    gui._start_game(GameTypes.TUTORIAL_2)


def on_press(key) -> None:
    # Hotkeys
    for hotkey in hotkeys:
        hotkey.press(listener.canonical(key))

    # Single key handling
    key = getattr(key, 'char', key)
    if key == 'e':
        pass
    elif key == Key.esc:
        pass

    # Log
    logger.debug("Key {0} pressed".format(key))


def on_release(key) -> None:
    # Hotkeys
    for hotkey in hotkeys:
        hotkey.release(listener.canonical(key))

    # Single key handling
    key = getattr(key, 'char', key)
    if key == 'e':
        pass
    elif key == Key.esc:
        pass

    # Log
    logger.debug("Key {0} released".format(key))


# Initialize the hotkeys and the listener
hotkeys = [
    HotKey(HotKey.parse('<shift>+h'), on_shift_h),
    HotKey(HotKey.parse('<shift>+q'), on_shift_q),
    HotKey(HotKey.parse('<shift>+t'), on_shift_t),
    HotKey(HotKey.parse('<shift>+m'), on_shift_m),
]
listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
