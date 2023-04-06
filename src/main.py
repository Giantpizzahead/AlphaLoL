"""
TODO: Don't crash if bot is on when game isn't open
"""
import os
import time
import traceback

from queue import Queue

from ai import manual_ai
from ai.recorders.chat import chat_recorder
from controllers import game_controller
from listeners.vision import screenshot, game_vision, window_tracker, game_ocr
from listeners.keyboard import key_listener
from misc import color_logging
from misc import rng
from misc.definitions import ROOT_DIR
from tests.listeners.vision.test_game_vision import test_all

logger = color_logging.getLogger('main', level=color_logging.DEBUG)
q = Queue()


def main():
    logger.info("Starting up!")
    game_vision.init_vision()
    game_ocr.init_ocr()
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
                logger.info("Quitting the application...")
            elif e == "toggle_bot":
                bot_active = not bot_active
                if bot_active:
                    logger.info("The bot is now enabled.")
                else:
                    logger.info("The bot is now disabled.")
            elif e == "toggle_dry_run":
                game_controller.dry_run = not game_controller.dry_run
                if game_controller.dry_run:
                    logger.info("Mouse and keyboard control is now disabled.")
                else:
                    logger.info("Mouse and keyboard control is now enabled.")
            else:
                logger.warning(f"Unknown event found in keyboard listener queue: {e}")
        if bot_active:
            try:
                # chat_recorder.is_debug = True
                # chat_recorder.process(window_tracker.take_game_screenshot())
                # manual_ai.is_debug = True
                manual_ai.process(window_tracker.take_game_screenshot())
            except Exception:
                logger.error(f"Unknown error: {traceback.format_exc()}")
                time.sleep(0.5)
        else:
            time.sleep(0.1)
    logger.info("Shutting down...")
    game_vision.close()


if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()', sort='time')
    # game_vision.init_vision()
    # cProfile.run('test_all(os.path.join(ROOT_DIR, "..", "screenshots"), display_scale=0.7)', sort='time')
