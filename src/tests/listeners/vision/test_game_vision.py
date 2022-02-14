import os
import random
import time

import cv2 as cv

import listeners.vision.game_vision as game_vision
from listeners.vision import template_match
from misc import color_logging
from misc.definitions import ROOT_DIR

logger = color_logging.getLogger('vision', level=color_logging.DEBUG)


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

    num_images = int(input("# test images: "))
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    for file in filepaths:
        img = template_match.load_image(file)
        start_time = time.time()
        result = game_vision.find_minions(img)
        end_time = time.time()

        # Display matches
        res = img.copy()
        for r in result:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 1)
        res = template_match.scale_image(res, display_scale)

        # Display minion health as text
        for r in result:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.putText(res, str(f"{round(r.health*100)}%"), (round(r.x1*display_scale), round((r.y1-6)*display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8*display_scale, color, 2)

        # Show result
        print(f"{file}: {len(result)} minions, {end_time-start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
           cv.waitKey(50)
           if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
               break

        if is_test:
            is_correct = input("Correct? (Leave blank for yes): ")
            if not is_correct:
                missed = 0
                wrong = 0
            else:
                missed = int(input("# missed: "))
                wrong = int(input("# wrong: "))
            false_negatives += missed
            false_positives += wrong
            true_positives += len(result) - wrong

        num_images -= 1
        if num_images <= 0:
            break
    # Show test results (if applicable)
    if is_test:
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        print(f"True positives: {true_positives}")
        print(f"False positives: {false_positives}")
        print(f"False negatives: {false_negatives}")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall: {recall*100:.2f}%")


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

    num_images = 100
    # num_images = int(input("# test images: "))
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    for file in filepaths:
        img = template_match.load_image(file)
        start_time = time.time()
        result = game_vision.find_players(img)
        end_time = time.time()

        # Display matches
        res = img.copy()
        for r in result:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 2)
        res = template_match.scale_image(res, display_scale)

        # Display player health as text
        for r in result:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            info = f"L{r.level} H{round(r.health*100)} M{round(r.mana*100)}"
            cv.putText(res, info, (round(r.x1*display_scale), round((r.y1-6)*display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8*display_scale, color, 2)

        # Show result
        print(f"{file}: {len(result)} players, {end_time-start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
           cv.waitKey(50)
           if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
               break

        if is_test:
            is_correct = input("Correct? (Leave blank for yes): ")
            if not is_correct:
                missed = 0
                wrong = 0
            else:
                missed = int(input("# missed: "))
                wrong = int(input("# wrong: "))
            false_negatives += missed
            false_positives += wrong
            true_positives += len(result) - wrong

        num_images -= 1
        if num_images <= 0:
            break
    # Show test results (if applicable)
    if is_test:
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        print(f"True positives: {true_positives}")
        print(f"False positives: {false_positives}")
        print(f"False negatives: {false_negatives}")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall: {recall*100:.2f}%")



def test_all(testpath: str, scale=1.0, display_scale=1.0) -> None:
    """
    Test all vision function for fun!
    """

    filepaths = []
    for subdir, dirs, files in os.walk(testpath):
        for file in files:
            if file.endswith('.png') and 'ingame' in subdir:
                filepaths.append(os.path.join(subdir, file))
    random.seed(time.time())
    random.shuffle(filepaths)
    filepaths.insert(0, os.path.join(testpath, "beginnerbot/ingame/frame_553.png"))
    filepaths.insert(0, os.path.join(testpath, "blindpick/ingame/frame_131.png"))

    for file in filepaths:
        img = template_match.load_image(file)
        start_time = time.time()
        minions = game_vision.find_minions(img)
        players = game_vision.find_players(img)
        end_time = time.time()

        # Display minion matches
        res = img.copy()
        for r in minions:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 1)
        # Display player matches
        for r in players:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 2)

        res = template_match.scale_image(res, display_scale)

        # Display minion health as text
        for r in minions:
            color = (255, 150, 0) if r.allied else (0, 0, 255)
            cv.putText(res, str(f"{round(r.health*100)}%"),
                       (round(r.x1 * display_scale), round((r.y1-6)*display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8*display_scale, color, 2)
        # Display player health as text
        for r in players:
            color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
            info = f"L{r.level} H{round(r.health*100)} M{round(r.mana*100)}"
            cv.putText(res, info, (round(r.x1*display_scale), round((r.y1-6)*display_scale)),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8*display_scale, color, 2)

        # Show result
        print(f"{file}: {len(players)} players, {len(minions)} minions, {end_time-start_time:.3f}s")
        cv.imshow(f"{file}", res)
        while True:
           cv.waitKey(50)
           if cv.getWindowProperty(f"{file}", cv.WND_PROP_VISIBLE) < 1:
               break


if __name__ == '__main__':
    test_all(os.path.join(ROOT_DIR, "..", "screenshots"), display_scale=0.7)
    # test_find_players(os.path.join(ROOT_DIR, "..", "screenshots"), display_scale=0.7)
    # test_find_minions(os.path.join(ROOT_DIR, "..", "screenshots"), display_scale=0.7)
