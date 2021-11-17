"""
GUI constants, like enums and button locations.
"""

from enum import Enum


class GUIState(Enum):
    """
    Current state of the GUI.
    """
    CLOSED, MENU, GAME = range(3)


class MenuState(Enum):
    """
    Current state of the menu.
    """
    HOME, MODE_SELECT, PARTY, IN_QUEUE, CHAMP_SELECT, OTHER, NOT_VISIBLE = range(7)


class MenuOffsets():
    """
    Locations (relative to the top-left corner) of objects in the menu.
    """
    ANCHOR = (1202.43359375, 10.578125)
    ACTION_BUTTON_TOP = (120.4765625, 35.8515625)
    HOME_BUTTON_TOP = (292.4609375, 38.8828125)
    PVP_TOP = (62.96484375, 92.14453125)
    COOP_VS_AI_TOP = (149.04296875, 93.36328125)
    COOP_VS_AI_INTRO = (458.0625, 491.4140625)
    COOP_VS_AI_BEGINNER = (467.39453125, 520.8671875)
    COOP_VS_AI_INTERMEDIATE = (485.2734375, 550.80859375)
    TRAINING_TOP = (253.73828125, 93.33984375)
    TUTORIAL = (377.56640625, 267.00390625)
    TUTORIAL_LEFT_ARROW = (48.1875, 355.9609375)
    TUTORIAL_RIGHT_ARROW = (1231.453125, 353.06640625)
    TUTORIAL_START_BUTTON = (655.34375, 680.33203125)
    PRACTICE_TOOL = (625.3046875, 275.15234375)
    ACTION_BUTTON_BOTTOM = (540.6171875, 680.13671875)
    CANCEL_BUTTON_BOTTOM = (557.78125, 678.7760416666666)


class GameTypes(Enum):
    """
    Types of games that the bot can play.
    """
    TUTORIAL_1, TUTORIAL_2, TUTORIAL_3, \
    AI_INTRO, AI_BEGINNER, AI_INTERMEDIATE, \
    BLIND, DRAFT, RANKED = range(9)
