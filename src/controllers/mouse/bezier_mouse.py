"""
Realistic mouse movements. Modified version of the below library:
https://github.com/vincentbavitz/bezmouse/blob/master/mouse.py
"""
import threading

import pynput
import time
import math

from random import randint, choice
from math import ceil
from misc.rng import rnum

# Makes time.sleep() more accurate
# https://stackoverflow.com/questions/40594587/why-time-sleep-is-so-slow-in-windows
from ctypes import windll

timeBeginPeriod = windll.winmm.timeBeginPeriod
timeBeginPeriod(1)

mouse = pynput.mouse.Controller()


def pascal_row(n):
    # This returns the nth row of Pascal's Triangle
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    return result


def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n - 1)

    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t ** i for i in range(n))
            upowers = reversed([(1 - t) ** i for i in range(n)])
            coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                list(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result

    return bezier


def mouse_bez(init_pos, fin_pos, deviation, speed):
    """
    GENERATE BEZIER CURVE POINTS
    Takes init_pos and fin_pos as a 2-tuple representing xy coordinates
        variation is a 2-tuple representing the
        max distance from fin_pos of control point for x and y respectively
        speed is an int multiplier for speed. The lower, the faster. 1 is fastest.

    """

    # find number of frames to move
    dist = math.hypot(fin_pos[0] - init_pos[0], fin_pos[1] - init_pos[1])
    time_to_move = dist / speed + rnum(0.05)
    # print(f"Time: {time_to_move}")
    frames = max(round(time_to_move * 96 - 1), 0)

    # time parameter
    ts = [t / frames for t in range(frames)]
    ts.append(1)

    # bezier centre control points between (deviation / 2) and (deviaion) of travel distance, plus or minus at random
    control_1 = (
        init_pos[0] + choice((-1, 1)) * abs(ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(deviation / 2,
                                                                                                   deviation),
        init_pos[1] + choice((-1, 1)) * abs(ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(deviation / 2,
                                                                                                   deviation)
    )
    control_2 = (
        init_pos[0] + choice((-1, 1)) * abs(ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(deviation / 2,
                                                                                                   deviation),
        init_pos[1] + choice((-1, 1)) * abs(ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(deviation / 2,
                                                                                                   deviation)
    )

    xys = [init_pos, control_1, control_2, fin_pos]
    bezier = make_bezier(xys)
    points = bezier(ts)

    return points


def connected_bez(coord_list, deviation, speed):
    """
    Connects all the coords in coord_list with bezier curve
    and returns all the points in new curve

    ARGUMENT: DEVIATION (INT)
        deviation controls how straight the lines drawn my the cursor
        are. Zero deviation gives straight lines
        Accuracy is a percentage of the displacement of the mouse from point A to
        B, which is given as maximum control point deviation.
        Naturally, deviation of 10 (10%) gives maximum control point deviation
        of 10% of magnitude of displacement of mouse from point A to B,
        and a minimum of 5% (deviation / 2)
    """

    i = 1
    points = []

    while i < len(coord_list):
        points += mouse_bez(coord_list[i - 1], coord_list[i], deviation, speed)
        i += 1

    return points


def move_mouse_list(coord_list, deviation=30, speed=-1):
    """
    Moves the mouse through the specified points.
    """
    if speed == -1:
        speed = rnum(3500, s=0.1)
    all_coords = connected_bez(coord_list, deviation, speed)
    # print(f"Total points: {len(all_coords)}")
    # start_time = time.time()
    for coord in all_coords:
        mouse.position = (coord[0], coord[1])
        time.sleep(0.01)
    # print(f"Time taken: {time.time() - start_time}")


def move_mouse(x, y, deviation=30, speed=-1):
    """
    Moves the mouse to the specified location.
    speed * 100 / dist(x, y) = # of frames the movement will take (approximately).
    """
    move_mouse_list([mouse.position, (x, y)], deviation, speed)
