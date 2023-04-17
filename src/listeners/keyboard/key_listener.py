"""
Listens to and handles keyboard events (for manually controlling the AI).
"""

import pynput
from pynput.keyboard import HotKey, Key
from queue import Queue

from misc import color_logging

logger = color_logging.getLogger('listener', level=color_logging.INFO)
queue = Queue()


def init_listener(q: Queue) -> None:
    """
    Initializes the keyboard listener.
    :param q: The queue to put events into.
    """
    global queue
    logger.info("Initializing keyboard listener...")
    listener.start()
    logger.info("Keyboard listener active! Press Shift-H to display a help menu.")
    queue = q


def on_shift_h() -> None:
    """
    Displays a help menu for the application.
    """
    logger.info("""
    Shift-H: Display help menu
    Shift-T: Toggle the entire bot
    Shift-C: Toggle the bot's ability to control the mouse and keyboard
    Shift-L: Choose a lane for the bot to play in
    Shift-8: Toggle debug mode and set debug display scale
    Shift-9: Quick reset the bot (for a new game with *no setting changes*)
    Shift-0: Quit the program
    """)


def on_shift_t() -> None:
    """
    Toggles the bot's AI functions.
    """
    logger.debug("Toggling bot...")
    queue.put("toggle_bot")


def on_shift_c() -> None:
    """
    Toggles the bot's mouse and keyboard control.
    """
    logger.debug("Toggling mouse and keyboard control...")
    queue.put("toggle_dry_run")


def on_shift_l() -> None:
    """
    Prompts the user to choose a lane for the bot to play in.
    """
    logger.debug("Attempting to choose a lane...")
    queue.put("choose_lane")


def on_shift_8() -> None:
    """
    Toggles debug mode and sets the debug display scale.
    """
    logger.debug("Attempting to toggle debug mode and set debug display scale...")
    queue.put("toggle_debug")


def on_shift_0() -> None:
    """
    Quit the application.
    """
    logger.debug("Exiting the application...")
    queue.put("quit")


def on_shift_9() -> None:
    """
    Reset the bot.
    """
    logger.debug("Resetting the bot...")
    queue.put("reset")


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
    HotKey(HotKey.parse('<shift>+t'), on_shift_t),
    HotKey(HotKey.parse('<shift>+c'), on_shift_c),
    HotKey(HotKey.parse('<shift>+l'), on_shift_l),
    HotKey(HotKey.parse('<shift>+8'), on_shift_8),
    HotKey(HotKey.parse('<shift>+9'), on_shift_9),
    HotKey(HotKey.parse('<shift>+0'), on_shift_0),
]
listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
