"""
Helper file for colorful logging!
"""

import logging
import os
import sys

import colorlog

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
LOG_FORMAT = "%(asctime)s %(name)-9.9s %(levelname)+9.9s  %(message)s"
# LOG_FORMAT = "%(name)-9.9s %(message)s"
basicFormatter = logging.Formatter(LOG_FORMAT)
colorFormatter = colorlog.ColoredFormatter("%(log_color)s" + LOG_FORMAT)


# Check if we're running from a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    LOG_FOLDER = os.path.join(os.getenv("PROGRAMDATA"), "AlphaLoL", "logs")
else:
    LOG_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
# Create directories if missing
os.makedirs(LOG_FOLDER, exist_ok=True)


def getLogger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        # Output colored logs to stderr
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(colorFormatter)
        consoleHandler.setLevel(level)
        logger.addHandler(consoleHandler)
        # Record logs in a file
        fileHandler = logging.FileHandler(os.path.join(LOG_FOLDER, f"{name}.log"))
        fileHandler.setFormatter(basicFormatter)
        fileHandler.setLevel(level)
        logger.addHandler(fileHandler)
    return logger
