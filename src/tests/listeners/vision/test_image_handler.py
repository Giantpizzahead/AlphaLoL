import os
from typing import Callable, List

import cv2 as cv
import numpy as np

import listeners.vision.image_handler as image_handler
from misc import color_logging
from misc.definitions import ROOT_DIR

logger = color_logging.getLogger('test', level=color_logging.DEBUG)


def test_matches(match_function: Callable[[np.ndarray, np.ndarray, ...], List[image_handler.Match]],
                 testpath: str, n: int, m: int, scale=1.0, display_scale=1.0) -> None:
    """
    Test the given template matching function with sets of templates and images.
    :param match_function: The function to test.
    :param testpath: Path to the test folder.
    :param n: Number of test images.
    :param m: Number of template images.
    """

    images = []
    for i in range(1, n+1):
        images.append(image_handler.load_image(f"{testpath}/test{i}.png"))
    templates = []
    for i in range(1, m+1):
        templates.append(image_handler.load_image(f"{testpath}/template{i}.png"))

    for i in range(n):
        for j in range(m):
            result = match_function(images[i], templates[j], scale)
            # Display matches
            res = images[i].copy()
            for r in result:
                cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), (0, 0, 255), 2)

            # Combine images
            h1, w1 = templates[j].shape[:2]
            h2, w2 = res.shape[:2]
            disp = np.zeros((max(h1, h2), w1 + w2, 3), np.uint8)
            disp[:h1, :w1, :3] = templates[j]
            disp[:h2, w1:w1 + w2, :3] = res
            disp = image_handler.scale_image(disp, display_scale)
            logger.info(
                f"Test {i}, template {j}: {len(result)} matches, max score = {max([0.0] + [x.score for x in result])},"
                f"raw = {result}")
            cv.imshow(f"Test {i}, template {j}", disp)
            while True:
                cv.waitKey(50)
                if cv.getWindowProperty(f"Test {i}, template {j}", cv.WND_PROP_VISIBLE) < 1:
                    break


if __name__ == '__main__':
    test_matches(image_handler.find_exact_matches,
                 os.path.join(ROOT_DIR, "img", "minion_match"), 5, 1, 1, 1.2)
