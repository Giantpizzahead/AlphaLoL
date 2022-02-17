"""
Contains helper functions for using the keyboard.
"""

import threading
from queue import Queue

from typing import Union

import pynput
from pynput.keyboard import Key

from misc import color_logging
from misc.rng import rsleep

logger = color_logging.getLogger('controls', level=color_logging.INFO)
keyboard = pynput.keyboard.Controller()


def _hold_key(key: Union[str, Key], duration: float) -> None:
    logger.debug(f"Holding {key} key for {duration} seconds")
    rsleep(0.03)
    keyboard.press(key)
    rsleep(duration)
    keyboard.release(key)


def _press_key(key: Union[str, Key]) -> None:
    logger.debug(f"{key} key pressed")
    rsleep(0.03)
    keyboard.press(key)
    rsleep(0.03)
    keyboard.release(key)


def _press_key_with_modifier(key: Union[str, Key], modifier: Union[str, Key]) -> None:
    logger.debug(f"{key} key pressed with {modifier} modifier")
    rsleep(0.03)
    keyboard.press(modifier)
    rsleep(0.012)
    keyboard.press(key)
    rsleep(0.018)
    keyboard.release(modifier)
    rsleep(0.01)
    keyboard.release(key)


# Process all keyboard events in a separate thread using a queue
queue = Queue()


def sleep(n: float, s=0.047, a=False) -> None:
    queue.put((rsleep, n, s, a))


def hold_key(key: Union[str, Key], duration: float) -> None:
    queue.put((_hold_key, key, duration))


def press_key(key: Union[str, Key]) -> None:
    queue.put((_press_key, key))


def press_key_with_modifier(key: Union[str, Key], modifier: Union[str, Key]) -> None:
    queue.put((_press_key_with_modifier, key, modifier))


def call_function(func: callable, *args: tuple) -> None:
    queue.put((func, *args))


def _keyboard_event_loop() -> None:
    while True:
        while queue.qsize() > 10:
            logger.warning(f"Too many elements in keyboard queue ({queue.qsize()}), skipping event...")
            queue.get()
        try:
            func, *args = queue.get()
            func(*args)
            rsleep(0.02)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error processing keyboard event: {e}")


keyboard_thread = threading.Thread(target=_keyboard_event_loop, daemon=True)
keyboard_thread.start()
