import time

from gui import gui
from misc import color_logging

logger = color_logging.getLogger('main', level=color_logging.DEBUG)


def main():
    logger.info("Starting up!")
    gui.init()
    if gui.menu.MENU_DEBUG:
        logger.warning("MENU_DEBUG is on: Debugging menu")
        while True:
            gui.menu.update_state()
            time.sleep(1)
    elif gui.game.GAME_DEBUG:
        logger.warning("GAME_DEBUG is on: Debugging game")
        while True:
            gui.game.update_state()
            time.sleep(1)

    logger.info("For a list of commands, press Shift-H")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("See you next time :)")


if __name__ == '__main__':
    main()
