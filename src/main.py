import time

from gui import gui
from gui.gui_constants import GameTypes
from misc import color_logging

logger = color_logging.getLogger('main', level=color_logging.DEBUG)


def main():
    logger.info("Starting up!")
    gui.init()
    logger.info("For a list of commands, press <shift>-h")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("See you next time :)")


if __name__ == '__main__':
    main()
