import os
import sys
from enum import Enum

# Check if we're running from a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    ROOT_DIR = os.path.realpath(sys._MEIPASS)
else:
    ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAX_MATCHES = 2000


class GlobalState(Enum):
    NOT_RUNNING, LOBBY, PREGAME, INGAME, POSTGAME = range(5)


class GameState(Enum):
    NOT_RUNNING, NOT_VISIBLE, ACTIVE = range(3)
