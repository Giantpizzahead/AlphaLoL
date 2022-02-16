"""
Manages the location of the League of Legends client and game windows.
TODO: This code is Windows-specific
"""

from typing import Tuple, Optional

import numpy as np
import win32gui
from listeners.vision import screenshot

client = None
game = None
screen_res = screenshot.get_screen_res()


def get_window_res(hwnd) -> Tuple[int, int]:
    """
    Returns the resolution of the given window.
    :param hwnd: The window handle.
    :return: A tuple (w, h).
    """
    rect = win32gui.GetWindowRect(hwnd)
    return rect[2] - rect[0], rect[3] - rect[1]


def get_window_pos(hwnd) -> Tuple[int, int]:
    """
    Returns the position of the given window.
    :param hwnd: The window handle.
    :return: A tuple for the top-left position (x, y).
    """
    rect = win32gui.GetWindowRect(hwnd)
    return rect[0], rect[1]


def set_window_props(hwnd, x, y, w, h) -> None:
    """
    Sets the position and size of the given window.
    :param hwnd: The window handle.
    :param x: The top-left x-coordinate.
    :param y: The top-left y-coordinate.
    :param w: The window width.
    :param h: The window height.
    """
    win32gui.MoveWindow(hwnd, x-7, y, w, h, True)


def get_client_res() -> Tuple[Optional[float], Optional[float]]:
    """
    Returns the resolution of the League of Legends client window.
    :return: A tuple (w, h), or None if the client window is not found.
    """
    update_handles()
    return get_window_res(client) if client else (None, None)


def get_game_res() -> Tuple[Optional[float], Optional[float]]:
    """
    Returns the resolution of the League of Legends game window.
    :return: A tuple (w, h), or None if the game window is not found.
    """
    update_handles()
    return get_window_res(game) if game else (None, None)


def get_client_pos() -> Tuple[Optional[float], Optional[float]]:
    """
    Returns the position of the League of Legends client window.
    :return: A tuple for the top-left position (x, y), or None if the client window is not found.
    """
    update_handles()
    return get_window_pos(client) if client else (None, None)


def get_game_pos() -> Tuple[Optional[float], Optional[float]]:
    """
    Returns the position of the League of Legends game window.
    :return: A tuple for the top-left position (x, y), or None if the game window is not found.
    """
    update_handles()
    return get_window_pos(game) if game else (None, None)


def offset_client_pos(x: float, y: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Converts coordinates relative to the client into absolute positions.
    :param x: The relative x-coordinate.
    :param y: The relative y-coordinate.
    :return: A tuple for the absolute position (x, y), or None if the client window is not found.
    """
    update_handles()
    if client:
        pos = get_window_pos(client)
        return pos[0] + x, pos[1] + y
    else:
        return None, None


def offset_game_pos(x: float, y: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Converts coordinates relative to the game into absolute positions.
    :param x: The relative x-coordinate.
    :param y: The relative y-coordinate.
    :return: A tuple for the absolute position (x, y), or None if the game window is not found.
    """
    update_handles()
    if game:
        pos = get_window_pos(game)
        return pos[0] + x, pos[1] + y
    else:
        return None, None


def set_client_props(x, y, w, h) -> None:
    """
    Sets the position and size of the League of Legends client window.
    :param x: The top-left x-coordinate.
    :param y: The top-left y-coordinate.
    :param w: The window width.
    :param h: The window height.
    """
    update_handles()
    if client:
        set_window_props(client, x, y, w, h)


def set_game_props(x, y, w, h) -> None:
    """
    Sets the position and size of the League of Legends game window.
    :param x: The top-left x-coordinate.
    :param y: The top-left y-coordinate.
    :param w: The window width.
    :param h: The window height.
    """
    update_handles()
    if game:
        set_window_props(game, x, y, w, h)


def update_handles() -> None:
    """
    Updates handles for the League of Legends client and game windows.
    """
    global client, game
    client = None
    game = None

    def callback(hwnd, extra):
        name = win32gui.GetWindowText(hwnd)
        if name == "League of Legends" and win32gui.GetWindowRect(hwnd)[3] > 200:
            global client
            client = hwnd
        elif name == "League of Legends (TM) Client":
            global game
            game = hwnd
    win32gui.EnumWindows(callback, None)


def take_client_screenshot() -> np.ndarray:
    """
    Takes a screenshot of the League of Legends client.
    :return: An image of the client.
    """
    x, y = get_client_pos()
    w, h = get_client_res()
    if x is None:
        raise Exception("Client isn't open")
    return screenshot.take_screenshot(x, y, x + w, y + h)


def take_game_screenshot() -> np.ndarray:
    """
    Takes a screenshot of the League of Legends game window.
    :return: An image of the game.
    """
    x, y = get_game_pos()
    w, h = get_game_res()
    if x is None:
        raise Exception("Game isn't open")
    return screenshot.take_screenshot(x, y, x + w, y + h)
