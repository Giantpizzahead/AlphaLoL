import os
import random
import time

import cv2 as cv

import listeners.vision.game_vision as game_vision
from ai import basic_ai
from controllers import game_controller
from listeners.vision import image_handler
from misc import color_logging
from misc.definitions import ROOT_DIR

logger = color_logging.getLogger('test', level=color_logging.DEBUG)


def test_ai(testpath: str, display_scale=1.0) -> None:
    """
    Test the AI with game screenshots.
    """

    game_controller.dry_run = True
    filepaths = []
    for subdir, dirs, files in os.walk(testpath):
        for file in files:
            if file.endswith('.png') and 'ingame' in subdir:
                filepaths.append(os.path.join(subdir, file))
    random.seed(time.time())
    random.shuffle(filepaths)
    # Useful scenarios
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_300.png"))
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_205.png"))
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_177.png"))

    for file in filepaths:
        img = image_handler.load_image(file)
        start_time = time.time()
        basic_ai.process(img)
        end_time = time.time()
        logger.info(f"{file}: {end_time - start_time:.3f}s")
        disp = image_handler.scale_image(img, display_scale)
        cv.imshow(f"{file}", disp)
        while True:
            cv.waitKey(50)
            if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
                break


if __name__ == '__main__':
    game_vision.init_vision()
    test_ai(os.path.join(ROOT_DIR, "..", "screenshots"), display_scale=0.7)
    game_vision.close()
