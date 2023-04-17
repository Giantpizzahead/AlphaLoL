"""
Records the data from a match, to be used in machine learning.
"""
import os
import time
import random
import cv2 as cv
import multiprocessing
from queue import Queue
from typing import List
from threading import Timer, Lock

import numpy as np
import key_recorder
import mouse_recorder
from listeners.vision.game_vision import Minion, Player, Objective
from misc.definitions import ROOT_DIR
from timer import get_game_time
from listeners.vision import game_vision, window_tracker

from misc import color_logging

logger = color_logging.getLogger('recorder', level=color_logging.DEBUG)
all_data = []
all_answers = []
curr_batch = 1
list_lock = Lock()


def save_batch():
    global curr_batch, all_data, all_answers
    save_index = curr_batch
    curr_batch += 1
    # Data comes before answers
    num_to_save = len(all_answers)
    np.save(os.path.join(ROOT_DIR, "..", "mldata", f"batch{save_index}_in.npy"), all_data[:num_to_save])
    np.save(os.path.join(ROOT_DIR, "..", "mldata", f"batch{save_index}_out.npy"), all_answers)
    logger.info(f"Saved batch {save_index}")
    list_lock.acquire()
    all_data = all_data[num_to_save:]
    all_answers.clear()
    list_lock.release()


def get_features(img: np.ndarray, raw_minions: List[Minion], raw_players: List[Player], raw_objectives: list[Objective]):
    """
    Records the following data:
    Current game time
    0-20 visible allied minion data
    0-20 visible enemy minion data
    1 player champion data
    0-4 visible allied champion data
    0-5 visible enemy champion data
    0-3 visible allied objective data
    0-3 visible enemy objective data
    Mouse positions for the previous 0.5 seconds (including current)
    Previous 5 mouse events
    Previous 5 keyboard events

    Optional: Previous 2 frames of game data
    """

    # Empty data array
    data_arr = []

    # Game time
    game_time = get_game_time()
    data_arr.append(game_time)

    # Minions
    num_minions = 20
    allied_minions = [minion for minion in raw_minions if minion.allied][:num_minions]
    for i in range(num_minions):
        if i < len(allied_minions):
            data_arr.extend([1, allied_minions[i].get_x(), allied_minions[i].get_y(), allied_minions[i].health])
        else:
            data_arr.extend([0, 0, 0, 0])
    enemy_minions = [minion for minion in raw_minions if not minion.allied][:num_minions]
    for i in range(num_minions):
        if i < len(enemy_minions):
            data_arr.extend([1, enemy_minions[i].get_x(), enemy_minions[i].get_y(), enemy_minions[i].health])
        else:
            data_arr.extend([0, 0, 0, 0])

    # Champions
    player_champions = [champion for champion in raw_players if champion.controllable][:1]
    allied_champions = [champion for champion in raw_players if champion.allied and not champion.controllable][:4]
    enemy_champions = [champion for champion in raw_players if not champion.allied][:5]
    if player_champions:
        player = player_champions[0]
        data_arr.extend([1, player.get_x(), player.get_y(), player.level, player.health, player.mana])
    else:
        data_arr.extend([0, 0, 0, 0, 0, 0])
    for i in range(4):
        if i < len(allied_champions):
            champion = allied_champions[i]
            data_arr.extend([1, champion.get_x(), champion.get_y(), champion.level, champion.health, champion.mana])
        else:
            data_arr.extend([0, 0, 0, 0, 0, 0])
    for i in range(5):
        if i < len(enemy_champions):
            champion = enemy_champions[i]
            data_arr.extend([1, champion.get_x(), champion.get_y(), champion.level, champion.health, champion.mana])
        else:
            data_arr.extend([0, 0, 0, 0, 0, 0])

    # Objectives
    num_objectives = 3
    allied_objectives = [objective for objective in raw_objectives if objective.allied][:3]
    enemy_objectives = [objective for objective in raw_objectives if not objective.allied][:3]
    for i in range(num_objectives):
        if i < len(allied_objectives):
            objective = allied_objectives[i]
            data_arr.extend([1, objective.get_x(), objective.get_y(), int(objective.type == "small"), objective.health])
        else:
            data_arr.extend([0, 0, 0, 0, 0])
    for i in range(num_objectives):
        if i < len(enemy_objectives):
            objective = enemy_objectives[i]
            data_arr.extend([1, objective.get_x(), objective.get_y(), int(objective.type == "small"), objective.health])
        else:
            data_arr.extend([0, 0, 0, 0, 0])

    # Mouse positions
    num_locs = 50
    mouse_positions = mouse_recorder.mouse_positions[-num_locs:][::-1]
    for m in mouse_positions:
        data_arr.extend([m[0], m[1][0], m[1][1]])

    # Mouse events
    num_events = 5
    mouse_events = mouse_recorder.mouse_events[-num_events:][::-1]
    for e in mouse_events:
        options = ['left_press', 'left_release', 'right_press', 'right_release']
        t = options.index(e[1])
        data_arr.extend([1, e[0], t])
    for i in range(num_events - len(mouse_events)):
        data_arr.extend([0, 0, 0])

    # Keyboard events
    keyboard_events = key_recorder.keyboard_events[-num_events:][::-1]
    for e in keyboard_events:
        options = ['press', 'release']
        t = options.index(e[1])
        data_arr.extend([1, e[0], t, e[2]])
    for i in range(num_events - len(keyboard_events)):
        data_arr.extend([0, 0, 0, 0])

    return data_arr


def save_data(img: np.ndarray, raw_minions: List[Minion], raw_players: List[Player], raw_objectives: list[Objective]):
    data_arr = get_features(img, raw_minions, raw_players, raw_objectives)
    # print(data_arr)

    list_lock.acquire()
    all_data.append(data_arr)
    list_lock.release()

    # Get answers after ~0.5 seconds
    thread = Timer(0.55, save_answer, [data_arr[0]])
    thread.start()


def save_answer(game_time: float):
    """
    Outputs:
    Mouse locations for the next 0.5 seconds
    Next 5 mouse events within the next 0.5 seconds
    Next 5 keyboard events within the next 0.5 seconds
    """

    answer_arr = []
    # Both inclusive
    min_time = game_time - 0.005
    max_time = game_time + 0.495

    # Mouse positions
    num_locs = 50
    mouse_positions = []
    # Get tail end of mouse positions with time in the range [min_time, max_time]
    for i in reversed(range(len(mouse_recorder.mouse_positions))):
        if mouse_recorder.mouse_positions[i][0] < min_time:
            break
        if mouse_recorder.mouse_positions[i][0] <= max_time:
            mouse_positions.append(mouse_recorder.mouse_positions[i])
    mouse_positions = mouse_positions[-num_locs:][::-1]
    for m in mouse_positions:
        answer_arr.extend([m[0], m[1][0], m[1][1]])

    # Mouse events
    num_events = 5
    mouse_events = []
    # Get all mouse events that occured in the range [min_time, max_time]
    for i in reversed(range(len(mouse_recorder.mouse_events))):
        if mouse_recorder.mouse_events[i][0] < min_time:
            break
        if mouse_recorder.mouse_events[i][0] <= max_time:
            mouse_events.append(mouse_recorder.mouse_events[i])
    mouse_events = mouse_events[-num_events:][::-1]
    for e in mouse_events:
        options = ['left_press', 'left_release', 'right_press', 'right_release']
        t = options.index(e[1])
        answer_arr.extend([1, e[0], t])
    for i in range(num_events-len(mouse_events)):
        answer_arr.extend([0, 0, 0])

    # Keyboard events
    keyboard_events = []
    # Get all keyboard events that occured in the range [min_time, max_time]
    for i in reversed(range(len(key_recorder.keyboard_events))):
        if key_recorder.keyboard_events[i][0] < min_time:
            break
        if key_recorder.keyboard_events[i][0] <= max_time:
            keyboard_events.append(key_recorder.keyboard_events[i])
    keyboard_events = keyboard_events[-num_events:][::-1]
    for e in keyboard_events:
        options = ['press', 'release']
        t = options.index(e[1])
        answer_arr.extend([1, e[0], t, e[2]])
    for i in range(num_events - len(keyboard_events)):
        answer_arr.extend([0, 0, 0, 0])
    # print(answer_arr)

    list_lock.acquire()
    all_answers.append(answer_arr)
    list_lock.release()

    # Save every so often
    save_interval = 500
    if len(all_answers) % save_interval == 0:
        save_batch()


def main():
    game_vision.init_vision()
    logger.info("Press 0 at 5 seconds ingame time...")
    key_recorder.start_recording()
    mouse_recorder.start_recording()
    while get_game_time() < 0:
        time.sleep(0.01)
    logger.info("Recording started!")
    logger.info("Press 0 to stop recording...")
    # The screenshots queue
    img_queue = multiprocessing.Queue()  # type: Queue
    multiprocessing.Process(target=save_screenshot, args=(img_queue,)).start()
    time.sleep(random.randint(100, 200) / 100)
    while True:
        if get_game_time() < 0:
            break
        logger.info(f"Game time: {get_game_time()}s")
        img = window_tracker.take_game_screenshot()
        img_queue.put(img)
        raw_minions, raw_players, raw_objectives = game_vision.find_all(img)
        save_data(img, raw_minions, raw_players, raw_objectives)
    if all_data:
        save_batch()
    logger.info("Recording stopped!")
    img_queue.put(None)


def save_screenshot(queue):
    # type: (Queue) -> None

    number = 0
    output = os.path.join(ROOT_DIR, "..", "mldata", "images", "frame_{}.png")

    while "there are screenshots":
        img = queue.get()
        if img is None:
            break
        # Don't write every image
        if number % 20 == 0:
            cv.imwrite(output.format(number), img)
        number += 1


if __name__ == "__main__":
    main()
