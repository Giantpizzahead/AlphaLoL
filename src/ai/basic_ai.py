"""
Simplest AI possible. Combines controllers and listeners to play League of Legends.
"""

import math
import random
import time
import cv2 as cv
from Levenshtein import distance

import numpy as np

import controllers.game_controller as controller
import listeners.vision.game_vision as vision
import listeners.vision.game_ocr as ocr
from listeners.vision import image_handler
from misc import color_logging
from misc.rng import rnum, rsleep

logger = color_logging.getLogger('ai', level=color_logging.INFO)
game_time = 0
prev_time = time.time()
curr_level = 0
is_debug = False

# Miss Fortune
ability_order = "qweqqrqwqwrwweeree"
# Tristana
# ability_order = "ewqeereqeqrqqwwrww"
status = "shopping"
time_in_status = float('-inf')
prev_gold = None


def close_match(s1: str, s2: str) -> bool:
    if len(s1) < 3 or len(s2) < 3:
        return s1 == s2
    acceptable = min(len(s1), len(s2)) // 5 + 1
    return distance(s1, s2) <= acceptable


def switch_status(s: str) -> None:
    global status, time_in_status
    if s == status:
        return
    status = s
    time_in_status = 0


def buy_items(img: np.ndarray) -> None:
    """
    Buys as many components for the first recommended item(s) from the shop as possible.
    Warning: This function takes a long time to run!
    :param img: Screenshot of the game state.
    """
    global prev_gold, status

    # Locate certain pieces of text in the shop
    text = ocr.find_text(img)
    if is_debug:
        draw_results_text(img, text, display_scale=0.35)
    builds_into = None
    sell = None
    for t in text:
        if close_match(t.text, "builds into"):
            builds_into = t
        elif close_match(t.text, "sell"):
            sell = t
    if builds_into is None:
        # Open the shop
        logger.info("Opening the shop")
        controller.move_mouse(100, 100)
        controller.press_key('p')
        prev_gold = float('inf')
        rsleep(0.5)
        return

    # Time bailout
    if time_in_status > 25:
        logger.info("Exiting the shop (too much time)")
        controller.press_key('p')
        rsleep(0.5)
        switch_status("playing")
        return

    # Locate gold amount and items to buy
    gold = None
    big_items = []
    components = []
    for t in text:
        if close_match(t.text, "good against") or close_match(t.text, "generally good"):
            big_items.append(t)
        # Gold
        if t.text.isdigit() and abs(t.get_y() - sell.get_y()) < 20:
            gold = int(t.text)
        # Component within the bounds of the shop's right side
        if not t.text.isdigit() or \
                t.x1 < builds_into.x1 - 20 or t.x2 > builds_into.x1 + 410 or \
                t.y1 < builds_into.y1 or t.y2 > builds_into.y1 + 400 or 1 < t.x1 < 5:
            continue
        components.append(t)
    if gold is None:
        logger.warning("Gold not found in shop, assuming 0")
        gold = 0
    big_items = sorted(big_items, key=lambda x: x.x1)
    components = sorted(components, key=lambda x: x.y1)
    logger.debug(f"Gold: {gold}")
    logger.debug(f"Big items: {[t.text for t in big_items]}")
    logger.debug(f"Components: {[t.text for t in components]}")

    # Check if more items need to be bought
    if (prev_gold is not None and gold >= prev_gold) or len(big_items) == 0:
        # Did not buy anything last round, that means we can't afford anything
        logger.info("Exiting the shop (not enough gold)")
        controller.press_key('p')
        rsleep(0.5)
        switch_status("playing")
        return

    # Check if components are open
    if prev_gold is not None:
        logger.debug("Opening big item")
        i = big_items[min(len(big_items)-1, 1)]
        controller.move_mouse_precise(i.get_x() + 25, i.get_y() - 50)
        controller.left_click(i.get_x() + 25, i.get_y() - 50)
        prev_gold = None
        rsleep(0.7)
        return

    # Buy as many expensive components as we can afford
    prev_gold = gold
    for c in components:
        if int(c.text) > gold:
            continue
        logger.debug(f"Buying component with cost {c.text}")
        controller.move_mouse_precise(c.get_x(), c.get_y() - 35)
        controller.right_click(c.get_x(), c.get_y() - 35)
        rsleep(0.7)
    rsleep(0.5)


def process(img: np.ndarray) -> None:
    """
    Chooses an action to perform based on the screenshot of the game state.
    Assumes that the AI is using locked camera.
    :param img: Screenshot of the game state.
    """
    global game_time, prev_time, curr_level, status, time_in_status

    # Parse the screenshot and update variables
    aspect = 1.6
    game_time += time.time() - prev_time
    time_in_status += time.time() - prev_time
    logger.debug(f"New frame, FPS: {1 / (time.time() - prev_time):.1f}")
    prev_time = time.time()

    # Buy items (or continue buying) if needed
    if status == "shopping":
        buy_items(img)
        return

    # Get all game information
    raw_minions, raw_players, raw_objectives = vision.find_all(img)
    if is_debug:
        draw_results(img, raw_minions, raw_players, raw_objectives, display_scale=0.35)

    # Process minions
    ally_minions = []
    enemy_minions = []
    for m in raw_minions:
        if m.allied:
            ally_minions.append(m)
        else:
            enemy_minions.append(m)

    # Process players
    player = None
    ally_players = []
    enemy_players = []
    for p in raw_players:
        if p.controllable:
            player = p
        elif p.allied:
            ally_players.append(p)
        else:
            enemy_players.append(p)
    ally_objectives = []
    enemy_objectives = []
    for o in raw_objectives:
        if o.allied:
            ally_objectives.append(o)
        else:
            enemy_objectives.append(o)

    if player is None:
        logger.warning("Cannot find controllable player")
        switch_status("unknown")
        if time_in_status > 5:
            # Assume that the player died
            logger.info("Assuming that the player died")
            switch_status("shopping")
        return
    logger.debug(f"Minions {len(ally_minions)}/{len(enemy_minions)}, "
                 f"Champs {len(ally_players)}/{len(enemy_players)}, "
                 f"Objectives {len(ally_objectives)}/{len(enemy_objectives)}")

    # Level abilities if allowed
    if curr_level < player.level and curr_level < 18:
        logger.info(f"Leveling {ability_order[curr_level]}")
        controller.level_ability(ability_order[curr_level])
    curr_level = player.level
    x, y = player.get_x(), player.get_y()

    # Back off if health is low, recall when no enemies are present
    if player.health < 0.3 or player.mana < 0.1:
        logger.info("Health or mana low, attempting to escape")
        if player.health < 0.3:
            logger.info("Using heal due to low health")
            controller.press_key('f')
        if not enemy_minions and not enemy_players:
            controller.right_click(x - rnum(250 * aspect), y + rnum(250))
            rsleep(1)
            logger.info("Recalling")
            controller.press_key('b')
            # TODO: Do something smarter while waiting for recall, react to stopped recalls
            rsleep(12)
            switch_status("shopping")
        else:
            controller.right_click(x - rnum(250 * aspect), y + rnum(250))
            logger.debug("Using W to try and escape")
            controller.press_key('w')
        return

    # Try to stay behind allied minions
    '''
    if ally_minions or ally_players:
        furthest_x = float('-inf')
        furthest_y = float('inf')
        for m in ally_minions:
            if m.get_x() > furthest_x:
                furthest_x = m.get_x()
            if m.get_y() < furthest_y:
                furthest_y = m.get_y()
        back_left = furthest_x <= x
        back_bot = furthest_y >= y
        if back_left or back_bot:
            logger.info("Staying behind allied minions")
            if back_left and back_bot:
                controller.right_click(x - rnum(150*aspect), y + rnum(150))
                return
            elif back_left:
                controller.right_click(x - rnum(125*aspect), y + rnum(50))
                return
            elif back_bot:
                controller.right_click(x - rnum(50*aspect), y + rnum(125))
                return
    '''

    # If nothing's visible, move back to the location of battle, but don't walk beyond turrets
    if not enemy_minions and not enemy_players and not enemy_objectives:
        logger.info("No enemies, moving to top right")
        controller.right_click(x + rnum(250 * aspect), y - rnum(250))
        return

    # For now, find the nearest enemy minion, player, or objective with the lowest cost and attack it
    best_cost = float('inf')
    best_action = None
    turret_range = 550
    turret_influence = 18
    best_minion_cost = float('inf')
    for m in enemy_minions:
        mx, my = m.get_x(), m.get_y()
        cost = (min(math.hypot(x - mx, y - my), 800) + 100) * (0.4 + m.health)
        # Within range of a turret?
        for o in enemy_objectives:
            ox, oy = o.get_x(), o.get_y()
            if math.hypot(mx - ox, my - oy) < turret_range:
                cost *= turret_influence
        if cost < best_cost:
            best_cost = cost
            best_action = m
        best_minion_cost = min(best_minion_cost, cost)
    best_player_cost = float('inf')
    for p in enemy_players:
        px, py = p.get_x(), p.get_y()
        cost = (min(math.hypot(x - px, y - py), 800) + 100) * (0.1 + p.health ** 2.5)
        # Within range of a turret?
        for o in enemy_objectives:
            ox, oy = o.get_x(), o.get_y()
            if math.hypot(px - ox, py - oy) < turret_range:
                cost *= turret_influence
        if cost < best_cost:
            best_cost = cost
            best_action = p
        best_player_cost = min(best_player_cost, cost)
    best_objective_cost = float('inf')
    for o in enemy_objectives:
        ox, oy = o.get_x(), o.get_y()
        # Is it safe to attack this turret?
        allies_near = 0
        for m in ally_minions:
            mx, my = m.get_x(), m.get_y()
            if math.hypot(ox - mx, oy - my) < turret_range:
                allies_near += 1
        for p in ally_players:
            px, py = p.get_x(), p.get_y()
            if math.hypot(ox - px, oy - py) < turret_range:
                allies_near += 1
        if allies_near < 2:
            continue
        # Safe to attack the turret
        cost = (min(math.hypot(x - ox, y - oy), 800) + 100) * 0.6
        if enemy_players:
            cost *= 1 + (len(enemy_players) ** 2)
        if cost < best_cost:
            best_cost = cost
            best_action = o
        best_objective_cost = min(best_objective_cost, cost)

    # What about backing off?
    ally_power = 0
    enemy_power = 0
    for m in raw_minions:
        if m.allied:
            ally_power += m.health
        else:
            enemy_power += m.health
    for p in raw_players:
        if p.allied or p.controllable:
            ally_power += (p.level ** 1.15) * p.health * 1.2
        else:
            enemy_power += (p.level ** 1.15) * p.health
            # Don't let enemies get too close
            px, py = p.get_x(), p.get_y()
            dist = math.hypot(x - px, y - py)
            close_dist = 250
            if dist < close_dist:
                enemy_power += p.level * p.health * (close_dist - dist) / close_dist
    for o in raw_objectives:
        ox, oy = o.get_x(), o.get_y()
        if not o.allied:
            # Is it safe to go near this turret?
            allies_near = 0
            for m in ally_minions:
                mx, my = m.get_x(), m.get_y()
                if math.hypot(ox - mx, oy - my) < turret_range:
                    allies_near += 1
            for p in ally_players:
                px, py = p.get_x(), p.get_y()
                if math.hypot(ox - px, oy - py) < turret_range:
                    allies_near += 1
            if allies_near < 2:
                enemy_power += turret_influence * 2
    if enemy_power == 0:
        enemy_power = 0.00001
    back_off_cost = ((5 * ally_power / enemy_power) ** 4) * (player.health ** 0.5)
    if back_off_cost < best_cost:
        best_cost = back_off_cost
        best_action = "back off"

    if back_off_cost >= 1e5:
        logger.debug(f"Back large (Ally power: {ally_power:.1f}, Enemy power: {enemy_power:.1f})")
    else:
        logger.debug(f"Back {back_off_cost:.1f} (Ally power: {ally_power:.1f}, Enemy power: {enemy_power:.1f})")
    logger.debug(f"Minion {best_minion_cost:.1f}, Player {best_player_cost:.1f}, Objective {best_objective_cost:.1f}")

    if best_action == "back off" or best_cost == float('inf'):
        # Nothing better to do than move back
        logger.info(f"Moving back with cost {best_cost:.3f}")
        controller.right_click(x - rnum(150 * aspect), y + rnum(150))
        return

    logger.info(f"Attacking {type(best_action).__name__} with cost {best_cost:.3f}")
    tx = best_action.get_x()
    ty = best_action.get_y()
    th = best_action.health

    # Use abilities if close enough
    if math.hypot(x - tx, y - ty) < 500:
        if type(best_action) is vision.Player:
            # Use long cooldown spells to kill the player
            if th < 0.3:
                # Try to execute
                logger.info(f"Using ultimate to try and kill the player")
                controller.use_skillshot('r', tx, ty)
                rsleep(1.3)
            elif th < 0.5:
                logger.info(f"Using ghost to try and kill the player")
                controller.use_action('d')
        if type(best_action) is not vision.Objective:
            # Use short cooldown spells when available
            action = random.randint(1, 4)
            if action == 1:
                logger.debug(f"Using Q")
                controller.use_action('q')
            elif action == 2:
                logger.debug(f"Using E")
                controller.use_skillshot('e', tx, ty)
    # Attack move to keep dealing damage
    controller.attack_move(tx, ty)


def draw_results(img, minions, players, objectives, display_scale=1.0) -> None:
    # Display minion matches
    res = img.copy()
    for r in minions:
        color = (255, 150, 0) if r.allied else (0, 0, 255)
        cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 1)
    # Display player matches
    for r in players:
        color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
        cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 1)
    # Display objective matches
    for r in objectives:
        color = (255, 150, 0) if r.allied else (0, 0, 255)
        cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), color, 2)

    res = image_handler.scale_image(res, display_scale)

    # Display minion health as text
    for r in minions:
        color = (255, 150, 0) if r.allied else (0, 0, 255)
        cv.putText(res, str(f"{round(r.health * 100)}%"),
                   (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.8 * display_scale, color, 1)
    # Display player health as text
    for r in players:
        color = (100, 255, 100) if r.controllable else (255, 150, 0) if r.allied else (0, 0, 255)
        info = f"L{r.level} H{round(r.health * 100)} M{round(r.mana * 100)}"
        cv.putText(res, info, (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.8 * display_scale, color, 1)
    # Display objective health as text
    for r in objectives:
        color = (255, 150, 0) if r.allied else (0, 0, 255)
        cv.putText(res, str(f"{r.type} {round(r.health * 100)}%"),
                   (round(r.x1 * display_scale), round((r.y1 - 15) * display_scale)),
                   cv.FONT_HERSHEY_SIMPLEX, 1.25 * display_scale, color, 1)

    # Show result
    cv.imshow("result", res)
    cv.waitKey(50)


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
