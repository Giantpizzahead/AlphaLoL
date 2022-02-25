"""
Record mouse clicks and movements.
"""
import threading
import time
import pynput

from timer import get_game_time
from listeners.vision import window_tracker

from misc import color_logging

logger = color_logging.getLogger('recorder', level=color_logging.INFO)

# Makes time.sleep() more accurate
# https://stackoverflow.com/questions/40594587/why-time-sleep-is-so-slow-in-windows
from ctypes import windll

timeBeginPeriod = windll.winmm.timeBeginPeriod
timeBeginPeriod(1)

mouse_positions = []
mouse_events = []

# Controller to record mouse positions
controller = pynput.mouse.Controller()
def record_loop():
    next_update_time = 0
    while True:
        if get_game_time() >= next_update_time:
            pos = controller.position
            mouse_positions.append((next_update_time, pos))
            next_update_time = round(next_update_time + 0.01, 2)
        time.sleep(0.001)


# Listener to record mouse clicks
def on_click(x, y, button, pressed):
    if button == pynput.mouse.Button.left:
        evt = 'left_press' if pressed else 'left_release'
    elif button == pynput.mouse.Button.right:
        evt = 'right_press' if pressed else 'right_release'
    else:
        return
    mouse_events.append((get_game_time(), evt))
listener = pynput.mouse.Listener(on_click=on_click)


def start_recording():
    listener.start()
    thread = threading.Thread(target=record_loop, daemon=True)
    thread.start()
    logger.info("Mouse recording started!")
