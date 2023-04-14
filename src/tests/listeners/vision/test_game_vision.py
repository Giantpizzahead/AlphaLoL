import os
import random
import time

import cv2 as cv

import listeners.vision.game_vision as game_vision
from listeners.vision import image_handler
from misc import color_logging
from misc.definitions import ROOT_DIR

logger = color_logging.getLogger('test', level=color_logging.DEBUG)


def test_find_minions(testpath: str, scale=1.0, display_scale=1.0, is_test=False) -> None:
    """
    Test the find minions function with sets of templates and game screenshots.
    """

    filepaths = []
    for subdir, dirs, files in os.walk(testpath):
        for file in files:
            if file.endswith('.png') and 'ingame' in subdir:
                filepaths.append(os.path.join(subdir, file))
    random.seed(time.time())
    random.shuffle(filepaths)

    for file in filepaths:
        img = image_handler.load_image(file)
        start_time = time.time()
        result = game_vision.find_minions(img, scale)
        end_time = time.time()

        # Display matches
        res = img.copy()
        for r in result:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 1)
        res = image_handler.scale_image(res, display_scale)

        # Display minion health as text
        for r in result:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.putText(res, str(f"{round(r.health * 100)}%"),
                       (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8 * display_scale, color, 2)

        # Show result
        logger.info(f"{file}: {len(result)} minions, {end_time - start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
            cv.waitKey(50)
            if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
                break


def test_find_objectives(testpath: str, scale=1.0, display_scale=1.0, is_test=False) -> None:
    """
    Test the find objectives function with sets of templates and game screenshots.
    """

    filepaths = []
    for subdir, dirs, files in os.walk(testpath):
        for file in files:
            if file.endswith('.png') and 'ingame' in subdir:
                filepaths.append(os.path.join(subdir, file))
    random.seed(time.time())
    random.shuffle(filepaths)
    # filepaths.insert(0, os.path.join(testpath, "frame_44.png"))
    # filepaths.insert(0, os.path.join(testpath, "frame_34.png"))
    # filepaths.insert(0, os.path.join(testpath, "frame_27.png"))
    # filepaths.insert(0, os.path.join(testpath, "frame_21.png"))
    # filepaths.insert(0, os.path.join(testpath, "frame_17.png"))
    # filepaths.insert(0, os.path.join(testpath, "frame_11.png"))

    for file in filepaths:
        img = image_handler.load_image(file)
        start_time = time.time()
        result = game_vision.find_small_objectives(img, scale) + game_vision.find_big_objectives(img, scale)
        end_time = time.time()

        # Display objective matches
        res = img.copy()
        for r in result:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 3)
        res = image_handler.scale_image(res, display_scale)

        # Display objective health as text
        for r in result:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.putText(res, str(f"{r.type} {round(r.health * 100)}%"),
                       (round(r.x1 * display_scale), round((r.y1 - 15) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 1.25 * display_scale, color, 2)

        # Show result
        logger.info(f"{file}: {len(result)} objectives, {end_time - start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
            cv.waitKey(50)
            if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
                break


def test_find_players(testpath: str, scale=1.0, display_scale=1.0, is_test=False) -> None:
    """
    Test the find players function with sets of templates and game screenshots.
    """

    filepaths = []
    for subdir, dirs, files in os.walk(testpath):
        for file in files:
            if file.endswith('.png') and 'ingame' in subdir:
                filepaths.append(os.path.join(subdir, file))
    random.seed(time.time())
    random.shuffle(filepaths)

    for file in filepaths:
        img = image_handler.load_image(file)
        start_time = time.time()
        result = game_vision.find_players(img, scale)
        end_time = time.time()

        # Display matches
        res = img.copy()
        for r in result:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 2)
        res = image_handler.scale_image(res, display_scale)

        # Display player health as text
        for r in result:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            info = f"L{r.level} H{round(r.health * 100)} M{round(r.mana * 100)}"
            cv.putText(res, info, (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8 * display_scale, color, 2)

        # Show result
        logger.info(f"{file}: {len(result)} players, {end_time - start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
            cv.waitKey(50)
            if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
                break


def test_all(testpath: str, scale=1.0, display_scale=1.0) -> None:
    """
    Test the find all function with sets of templates and game screenshots.
    """

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
        minions, players, objectives = game_vision.find_all(img, scale)
        minions = game_vision.find_minions(img, scale)
        end_time = time.time()

        ''''''
        # Display minion matches
        res = img.copy()
        for r in minions:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 1)
        # Display player matches
        for r in players:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 2)
        # Display objective matches
        for r in objectives:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 3)

        res = image_handler.scale_image(res, display_scale)

        # Display minion health as text
        for r in minions:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.putText(res, str(f"{round(r.health * 100)}%"),
                       (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8 * display_scale, color, 2)
        # Display player health as text
        for r in players:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            info = f"L{r.level} H{round(r.health * 100)} M{round(r.mana * 100)}"
            cv.putText(res, info, (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8 * display_scale, color, 2)
        # Display objective health as text
        for r in objectives:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.putText(res, str(f"{r.type} {round(r.health * 100)}%"),
                       (round(r.x1 * display_scale), round((r.y1 - 15) * display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 1.25 * display_scale, color, 2)

        # Show result
        logger.info(f"{file}: {len(players)} players, {len(minions)} minions, {len(objectives)} objectives, {end_time - start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
            cv.waitKey(50)
            if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
                break
        ''''''


if __name__ == '__main__':
    game_vision.init_vision()
    test_all(os.path.join(ROOT_DIR, "screenshots"), display_scale=0.7)
    # test_all(os.path.join(ROOT_DIR, "..", "temp"), scale=1, display_scale=0.5)
    # test_find_players(os.path.join(ROOT_DIR, "screenshots"), display_scale=0.7)
    # test_find_objectives(os.path.join(ROOT_DIR, "screenshots"), display_scale=0.7)
    # test_find_minions(os.path.join(ROOT_DIR, "screenshots"), display_scale=0.7)
    game_vision.close()
