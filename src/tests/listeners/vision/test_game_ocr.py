import os
import random
import time

import cv2 as cv

import listeners.vision.game_ocr as game_ocr
from listeners.vision import image_handler
from misc import color_logging
from misc.definitions import ROOT_DIR

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)


def test_find_text(testpath: str, scale=1.0, display_scale=1.0) -> None:
    """
    Test the find text function with sets of templates and game screenshots.
    """

    filepaths = []
    for subdir, dirs, files in os.walk(testpath):
        for file in files:
            if file.endswith('.png') and 'ingame' in subdir:
                filepaths.append(os.path.join(subdir, file))
    random.seed(time.time())
    random.shuffle(filepaths)
    # Useful scenarios
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_328.png"))
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_237.png"))
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_81.png"))

    for file in filepaths:
        img = image_handler.load_image(file)
        start_time = time.time()
        text = game_ocr.find_text(img, scale=scale)
        end_time = time.time()

        # Display text boxes
        res = img.copy()
        for r in text:
            print(r)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), (100, 255, 100), 1)

        res = image_handler.scale_image(res, display_scale)

        # Display text
        for r in text:
            cv.putText(res, f"{r.text} {r.score:.2f}",
                       (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6 * display_scale, (100, 255, 100), 1)

        # Show result
        print(f"{file}: {len(text)} text boxes, {end_time - start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
            cv.waitKey(50)
            if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
                break


if __name__ == '__main__':
    game_ocr.init_ocr()
    test_find_text(os.path.join(ROOT_DIR, "..", "screenshots"), display_scale=0.7)
