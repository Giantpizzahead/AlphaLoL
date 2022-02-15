"""
Utility tool that generates / modifies numbers randomly.
"""

import time

import numpy as np


def rnum(n: float, s=0.047, a=False) -> float:
    """
    Generates a number that's close to the given one using a normal distribution.
    :param n: The original number.
    :param s: The spread around the number.
    :param a: Whether the spread should be absolute or relative (default = relative).
    :return: The randomized number.
    """
    if not a:
        s = n * s
    return np.random.normal(n, s)


def rsleep(n: float, s=0.047, a=False) -> None:
    """
    Sleeps for a time that's close to the given one using a normal distribution.
    :param n: The original sleep duration, in seconds.
    :param s: The spread around the duration.
    :param a: Whether the spread should be absolute or relative (default = relative).
    """
    time.sleep(max(rnum(n, s, a), 0))
