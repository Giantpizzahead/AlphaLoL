"""
Keeps a log of all chat in the game, including pings.
Note: This is really inaccurate, don't rely on it for anything important.
"""

import math
import random
import time
from datetime import timedelta
from dataclasses import dataclass
from typing import List

import cv2 as cv
import editdistance

import numpy as np

import listeners.vision.game_vision as game_vision
from listeners.keyboard import key_listener
from listeners.vision import image_handler
from misc import color_logging
from misc.rng import rnum, rsleep

logger = color_logging.getLogger('ai', level=color_logging.INFO)
is_debug = False
curr_time = time.time()
prev_time = time.time()

main_status = "loading"
main_status_time = float('-inf')

chat_log = []


def switch_status(new_main: str) -> None:
    global main_status, main_status_time
    if main_status != new_main:
        logger.debug(f"Switching main status from {main_status} to {new_main}")
        main_status = new_main
        main_status_time = 0


def close_match(s1: str, s2: str) -> bool:
    """
    Checks whether or not the two strings are "close enough" to be considered equal.
    :param s1: The first string
    :param s2: The second string
    :return Whether the strings are close enough.
    """
    if len(s1) < 3 or len(s2) < 3:
        return s1 == s2
    acceptable = min(len(s1), len(s2)) // 5 + 1
    return editdistance.eval(s1, s2) <= acceptable


def do_loading(img: np.ndarray) -> None:
    """
    Parses player usernames, and checks if the game is still loading.
    :param img: Screenshot of the game state.
    """

    # Check if the loading screen text is still there
    text = game_vision.find_text(img, 200, 200, 2360, 1000, lower=False)
    if len(text) <= 5:
        logger.info("Loading screen finished!")
        switch_status("ingame")

    if is_debug:
        draw_results_text(img, text, display_scale=0.7)
        logger.debug(text)


def do_ingame(img: np.ndarray) -> None:
    """
    Parses the chat.
    """

    # Check if the game has ended
    end_result = game_vision.find_text(img, 900, 450, 1700, 750)
    for t in end_result:
        if (t.x2 - t.x1) * (t.y2 - t.y1) < 20000:
            continue  # Too small to be a real end result
        elif close_match(t.text, "victory") or close_match(t.text, "defeat"):
            switch_status("end")
            return

    # Get last 3 lines of text from the chat
    text = game_vision.find_text(img, 75, 999, 850, 1075, lower=False)
    text.sort(key=lambda x: x.y1)
    for t in text:
        # Bailout
        bailout = "chat recorder bailout"
        for i in range(0, len(t.text) - len(bailout)):
            if close_match(t.text[i:i+len(bailout)].lower(), bailout.lower()):
                logger.info("Bailout triggered!")
                switch_status("end")
                return
        if len(t.text) <= 20:
            continue  # False positive
        # Check if this text exists in the log already
        for i in range(max(0, len(chat_log)-7), len(chat_log)):
            if close_match(chat_log[i][1].lower(), t.text.lower()):
                break
        else:
            logger.info(f"New chat: {t.text}")
            chat_log.append([main_status_time, t.text])

    if is_debug:
        draw_results_text(img, end_result + text, display_scale=0.7)
        logger.debug(end_result + text)


def do_end() -> None:
    """
    Prints out some useful ending info.
    """
    print("Full chat log:")
    for t in chat_log:
        print(f"{timedelta(seconds=t[0])} | {t[1]}")
    print()
    print("Your chat log:")
    username = "your username here"
    for t in chat_log:
        for i in range(0, len(t[1]) - len(username)):
            if close_match(t[1][i:i+len(username)].lower(), username.lower()):
                print(f"{timedelta(seconds=t[0])} | {t[1]}")
                break


def process(img: np.ndarray) -> None:
    """
    Processes the current frame.
    :param img: Screenshot of the game state.
    """
    global curr_time, prev_time, main_status_time

    # Parse the screenshot and update variables
    curr_time += time.time() - prev_time
    main_status_time += time.time() - prev_time
    # logger.debug(f"New frame, FPS: {1 / (time.time() - prev_time):.1f}")
    prev_time = time.time()

    if img.shape[0] * img.shape[1] < 100:
        logger.warning(f"Image empty, is League minimized?")
        rsleep(1)
        return

    # Run the AI
    if main_status == "loading":
        do_loading(img)
    elif main_status == "ingame":
        do_ingame(img)
    elif main_status == "end":
        # Game is over; toggle the bot
        do_end()
        key_listener.on_shift_t()
    else:
        logger.warning(f"Unknown main status {main_status}")


def draw_results_text(img, text, display_scale=1.0) -> None:
    # Display text boxes
    res = img.copy()
    for r in text:
        cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), (100, 255, 100), 1)

    res = image_handler.scale_image(res, display_scale)

    # Display text
    for r in text:
        cv.putText(res, f"{r.text} {r.score:.2f}",
                   (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6 * display_scale, (100, 255, 100), 1)
    # Show result
    cv.imshow("result", res)
    cv.waitKey(50)
