"""
Listens to and handles keyboard events (for manually controlling the AI).
"""

import pynput
from pynput.keyboard import HotKey, Key
from queue import Queue

from misc import color_logging

logger = color_logging.getLogger('key_listener', level=color_logging.INFO)
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
    Shift-Q: Quit the program
    Shift-T: Toggles the bot's mouse and keyboard control
    """)


def on_shift_q() -> None:
    """
    Quit the application.
    """
    logger.info("Exiting the application...")
    queue.put("quit")


def on_shift_t() -> None:
    """
    Toggles the bot.
    """
    logger.info("Toggling bot...")
    queue.put("toggle_bot")


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
    HotKey(HotKey.parse('<shift>+t'), on_shift_t)
]
listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
