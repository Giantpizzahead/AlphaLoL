import warnings
warnings.filterwarnings("ignore", category=UserWarning)
# Torch patch for PyInstaller
# https://github.com/pytorch/vision/issues/1899
def script_method(fn, _rcb=None):
    return fn
def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj
import torch.jit
torch.jit.script_method = script_method
torch.jit.script = script

import time
import traceback

from queue import Queue

from ai import manual_ai
from controllers import game_controller
from listeners.vision import game_vision, window_tracker
from listeners.keyboard import key_listener
from misc import color_logging

logger = color_logging.getLogger('main', level=color_logging.DEBUG)
q = Queue()


def main():
    logger.info("Starting up!")
    manual_ai.is_debug = True
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
                logger.info("Quitting the application...")
            elif e == "toggle_bot":
                bot_active = not bot_active
                if bot_active:
                    logger.info("The bot is now enabled.")
                else:
                    logger.info("The bot is now disabled.")
            elif e == "choose_lane":
                if bot_active:
                    logger.warning("The bot must be disabled to choose a lane!")
                    continue
                logger.info("Choose a lane for the bot to play in (type in the terminal).")
                time.sleep(0.3)
                lane = input("Enter a lane ([t]op, [m]id, [b]ot): ")
                if lane.lower().startswith("t"):
                    manual_ai.assigned_lane = "top"
                elif lane.lower().startswith("m"):
                    manual_ai.assigned_lane = "mid"
                elif lane.lower().startswith("b"):
                    manual_ai.assigned_lane = "bot"
                else:
                    logger.warning(f"Invalid lane '{lane}'!")
                    continue
                logger.info(f"Bot will now play in the {manual_ai.assigned_lane} lane.")
            elif e == "toggle_debug":
                if bot_active:
                    logger.warning("The bot must be disabled to toggle debug mode!")
                    continue
                manual_ai.is_debug = not manual_ai.is_debug
                if manual_ai.is_debug:
                    logger.info("Debug mode is now enabled.")
                    logger.info("Choose a debug display scale (type in the terminal).")
                    time.sleep(0.3)
                    scale = input("Enter a scale relative to the game's resolution (default 0.5):")
                    try:
                        scale = float(scale)
                    except ValueError:
                        if scale != "":
                            logger.warning(f"Invalid scale '{scale}'! Using default scale of 0.5.")
                        else:
                            logger.info("Using default scale of 0.5.")
                        scale = 0.5
                    logger.info(f"Debug mode scale set to {scale}. Toggle on the bot for changes to take effect.")
                    manual_ai.debug_scale = scale
                else:
                    logger.info("Debug mode is now disabled.")
            elif e == "toggle_dry_run":
                game_controller.dry_run = not game_controller.dry_run
                if game_controller.dry_run:
                    logger.info("Mouse and keyboard control is now disabled.")
                else:
                    logger.info("Mouse and keyboard control is now enabled.")
            elif e == "reset":
                logger.info("Resetting the bot...")
                manual_ai.reset()
                logger.info("Bot reset complete!")
            else:
                logger.warning(f"Unknown event found in keyboard listener queue: {e}")
        if bot_active:
            try:
                manual_ai.process(window_tracker.take_game_screenshot())
            except RuntimeWarning:
                logger.info(f"Waiting for the game to load...")
                time.sleep(10)
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
    # cProfile.run('test_all(os.path.join(ROOT_DIR, "screenshots"), display_scale=0.7)', sort='time')
