"""
TODO: Don't crash if bot is on when game isn't open
"""

import time

from queue import Queue
from ai import basic_ai
from listeners.vision import screenshot, game_vision, window_tracker
from listeners.keyboard import key_listener
from misc import color_logging
from misc import rng

logger = color_logging.getLogger('main', level=color_logging.DEBUG)
q = Queue()


def main():
    time.sleep(3)
    logger.info("Starting up!")
    game_vision.init_vision()
    key_listener.init_listener(q)
    logger.info("Ready to go! Press Shift-T to toggle the bot.")
    loop_active = True
    bot_active = False
    while loop_active:
        # Process any events from the queue
        while not q.empty():
            e = q.get()
            if e == "quit":
                loop_active = False
            elif e == "toggle_bot":
                bot_active = not bot_active
            else:
                logger.warning(f"Unknown event found in keyboard listener queue: {e}")
        if bot_active:
            x, y = window_tracker.get_game_pos()
            w, h = window_tracker.get_game_res()
            basic_ai.process(screenshot.take_screenshot(x, y, x+w, y+h))
            rng.rsleep(0.07, s=0.2)
        else:
            time.sleep(0.5)
    logger.info("Shutting down...")


if __name__ == '__main__':
    main()
