"""
Menu-specific (windowed client) GUI code.
"""

from pynput.keyboard import Key

from gui import input_handler
from gui import vision
from gui.gui_constants import MenuState, MenuOffsets, GameTypes
from gui.input_handler import press_key
from misc import color_logging
from misc.rng import rsleep

logger = color_logging.getLogger('menu', level=color_logging.DEBUG)
state = MenuState.NOT_VISIBLE
origin = (0, 0)


def left_click(x: float, y: float) -> None:
    """
    Left clicks at the given location *in the menu*, applying appropriate offsets.
    :param x: The x location to click.
    :param y: The y location to click.
    """
    input_handler.left_click(x + origin[0], y + origin[1])


def right_click(x: float, y: float) -> None:
    """
    Right clicks at the given location *in the menu*, applying appropriate offsets.
    :param x: The x location to click.
    :param y: The y location to click.
    """
    input_handler.right_click(x + origin[0], y + origin[1])


def get_state() -> MenuState:
    """
    Gets the current menu state, updating it in the process.
    :return: The current menu state.
    """
    return update_state()


def update_state() -> MenuState:
    """
    Updates the current menu state by searching for markers on the screen.
    :return: The current menu state.
    """

    global state, origin

    '''
    # Testing
    logger.info((input_handler.mouse.position[0] - origin[0], input_handler.mouse.position[1] - origin[1]))
    while True:
        anchor_l, _, _ = vision.find_image_locs("menu_anchor.png", threshold=0.75, display=True)
        if (cv.waitKey(25) & 0xFF) == ord('q'):
            cv.destroyAllWindows()
            break
    '''

    # Locate the client
    anchor_l, _, _ = vision.find_image_locs("menu_anchor.png", threshold=0.75)
    on_client = (len(anchor_l) != 0)
    if on_client:
        x = anchor_l[0][0] - MenuOffsets.ANCHOR[0]
        y = anchor_l[0][1] - MenuOffsets.ANCHOR[1]
        origin = (x, y)
        state = MenuState.OTHER
    else:
        state = MenuState.NOT_VISIBLE
        logger.debug("Current menu state: {}".format(state.name))
        return state

    # Look for home markers
    home1_l, _, _ = vision.find_image_locs("home_marker1.png", threshold=0.75)
    home2_l, _, _ = vision.find_image_locs("home_marker2.png", threshold=0.75)
    on_home = False
    for p1 in home1_l:
        for p2 in home2_l:
            if abs(p1[0] - p2[0]) < 10 and abs(p1[1] - p2[1]) < 30:
                # Home is selected
                on_home = True

    # Look for mode select marker
    mode_select_l, _, _ = vision.find_image_locs("mode_select_marker.png", threshold=0.85)
    on_mode_select = (len(mode_select_l) != 0)

    # Look for in queue & party markers
    in_queue_l, _, _ = vision.find_image_locs("in_queue_marker.png")
    on_in_queue = (len(in_queue_l) != 0)
    party_l, _, _ = vision.find_image_locs("party_marker.png")
    on_party = (len(in_queue_l) == 0 and len(party_l) != 0)

    # Look for champ select marker
    champ_select1_l, _, _ = vision.find_image_locs("champ_select_marker1.png", threshold=0.75)
    champ_select2_l, _, _ = vision.find_image_locs("champ_select_marker2.png", threshold=0.75)
    champ_select3_l, _, _ = vision.find_image_locs("champ_select_marker3.png")
    on_champ_select = (len(champ_select1_l) != 0 and len(champ_select2_l) != 0) or len(champ_select3_l) != 0

    # Update state based on results
    if on_home + on_mode_select + on_in_queue + on_party + on_champ_select > 1:
        logger.debug("Multiple screens fit the current page (switching pages?)")
        state = MenuState.OTHER
    elif on_home:
        state = MenuState.HOME
    elif on_mode_select:
        state = MenuState.MODE_SELECT
    elif on_party:
        state = MenuState.PARTY
    elif on_in_queue:
        state = MenuState.IN_QUEUE
    elif on_champ_select:
        state = MenuState.CHAMP_SELECT
    else:
        state = MenuState.OTHER
    logger.debug("Current menu state: {}".format(state.name))
    return state


def start_game(game_type: GameTypes) -> bool:
    """
    Starts a game of the given type (goes into but does not do champion select).
    Assumes that the game client is already open and ready to navigate.
    :param game_type: The type of game to start.
    :return: Whether the game was successfully started.
    """

    # Make sure the client is visible
    if get_state() == MenuState.NOT_VISIBLE:
        rsleep(3)
        if get_state() == MenuState.NOT_VISIBLE:
            logger.error("Unable to start game: Client is not visible")
            logger.error("Make sure the entire client is visible on screen, then try again")
            return False

    # Go home
    logger.debug("Navigating to home")
    for _ in range(3):
        if get_state() == MenuState.HOME:
            break
        # Get unstuck
        left_click(*MenuOffsets.HOME_BUTTON_TOP)
        rsleep(0.2)
        press_key(Key.esc)
        rsleep(0.2)
        left_click(*MenuOffsets.CANCEL_BUTTON_BOTTOM)
        rsleep(1)
    if get_state() != MenuState.HOME:
        logger.error("Unable to start game: Could not navigate to home screen")
        return False

    # Go to mode select
    logger.debug("Navigating to mode select")
    for _ in range(3):
        if get_state() == MenuState.MODE_SELECT:
            break
        left_click(*MenuOffsets.ACTION_BUTTON_TOP)
        rsleep(1)
    if get_state() != MenuState.MODE_SELECT:
        logger.error("Unable to start game: Could not navigate to mode select screen")
        return False

    if game_type.value in (GameTypes.TUTORIAL_1.value, GameTypes.TUTORIAL_2.value, GameTypes.TUTORIAL_3.value):
        # Select the tutorial and move to part 1
        logger.debug("Navigating to tutorial")
        left_click(*MenuOffsets.TRAINING_TOP)
        rsleep(1)
        left_click(*MenuOffsets.TUTORIAL)
        rsleep(1)
        left_click(*MenuOffsets.ACTION_BUTTON_BOTTOM)
        rsleep(1)
        # Select the right tutorial part
        logger.debug("Selecting the right tutorial part")
        left_click(*MenuOffsets.TUTORIAL_LEFT_ARROW)
        rsleep(0.4)
        left_click(*MenuOffsets.TUTORIAL_LEFT_ARROW)
        rsleep(1)
        if game_type in (GameTypes.TUTORIAL_2, GameTypes.TUTORIAL_3):
            left_click(*MenuOffsets.TUTORIAL_RIGHT_ARROW)
            rsleep(0.4)
            if game_type == GameTypes.TUTORIAL_3:
                left_click(*MenuOffsets.TUTORIAL_RIGHT_ARROW)
                rsleep(0.4)
        # Begin the game
        logger.debug("Launching the game")
        rsleep(1)
        left_click(*MenuOffsets.TUTORIAL_START_BUTTON)
        rsleep(1)
    else:
        logger.error("Mode not supported: {}".format(game_type.name))

    return True
