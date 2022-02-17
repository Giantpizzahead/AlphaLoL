"""
Record keyboard inputs.
"""
import pynput
from pynput.keyboard import Key

from timer import get_game_time, start_game_time

from misc import color_logging

logger = color_logging.getLogger('recorder', level=color_logging.INFO)

keyboard_events = []
keys = {Key.shift_l: 300, Key.ctrl_l: 301, Key.alt_l: 302, Key.cmd_l: 303, Key.caps_lock: 304, Key.esc: 305,
        Key.f1: 306, Key.f2: 307, Key.f3: 308, Key.f4: 309, Key.tab: 310, Key.enter: 311, Key.backspace: 312}


def on_press(key):
    try:
        c = ord(key.char)
        if c == ord('0'):
            if get_game_time() < 0:
                logger.info("Game time set to 5!")
                start_game_time(5)
            else:
                logger.info("Game time set to negative value!")
                start_game_time(-1)
    except AttributeError:
        if key in keys:
            c = keys[key]
        else:
            return
    if get_game_time() < 0:
        return
    keyboard_events.append((get_game_time(), 'press', c))


def on_release(key):
    try:
        c = ord(key.char)
    except AttributeError:
        if key in keys:
            c = keys[key]
        else:
            return
    if get_game_time() < 0:
        return
    keyboard_events.append((get_game_time(), 'release', c))


listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)


def start_recording():
    listener.start()
    logger.info("Keyboard recording started!")
