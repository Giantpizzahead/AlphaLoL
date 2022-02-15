"""
Simplest AI possible. Combines controllers and listeners to play League of Legends.
"""

import math
import random
import time

import numpy as np

import controllers.game_controller as controller
import listeners.vision.game_vision as vision
from misc import color_logging
from misc.rng import rnum, rsleep

logger = color_logging.getLogger('ai', level=color_logging.DEBUG)
game_time = 0
prev_time = time.time()
curr_level = 0
trist_ability_order = "ewqeereqeqrqqwwrww"


def process(img: np.ndarray) -> None:
    """
    Chooses an action to perform based on the screenshot of the game state.
    Assumes that the AI is using locked camera.
    :param img: Screenshot of the game state.
    """
    global game_time, prev_time, curr_level
    print()

    # Parse the screenshot and update variables
    aspect = 1.6
    game_time += time.time() - prev_time
    logger.debug(f"FPS: {1 / (time.time()-prev_time):.1f}")
    prev_time = time.time()
    raw_minions = vision.find_minions(img)
    ally_minions = []
    enemy_minions = []
    for m in raw_minions:
        if m.allied:
            ally_minions.append(m)
        else:
            enemy_minions.append(m)
    raw_players = vision.find_players(img)
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
    raw_objectives = vision.find_objectives(img)
    ally_objectives = []
    enemy_objectives = []
    for o in raw_objectives:
        if o.allied:
            ally_objectives.append(o)
        else:
            enemy_objectives.append(o)

    if player is None:
        logger.warning("Cannot find controllable player!")
        return
    logger.debug(f"Minions {len(ally_minions)}/{len(enemy_minions)}, "
                 f"Champs {len(ally_players)}/{len(enemy_players)}, "
                 f"Objectives {len(ally_objectives)}/{len(enemy_objectives)}")

    # Level abilities if allowed
    if curr_level < player.level and curr_level < 18:
        logger.info(f"Leveling {trist_ability_order[curr_level]}")
        controller.level_ability(trist_ability_order[curr_level])
        rsleep(0.1)
    curr_level = player.level
    x, y = player.get_x(), player.get_y()

    # Back off if health is low, recall when no enemies are present
    if player.health < 0.5:
        logger.info("Using heal due to low health")
        controller.press_key('f')
        rsleep(0.05)
    if player.health < 0.35:
        logger.info("Health low, attempting to escape")
        if not enemy_minions and not enemy_players:
            controller.right_click(x - rnum(250*aspect), y + rnum(250))
            rsleep(1)
            logger.info("Recalling")
            controller.press_key('b')
            rsleep(12)
            logger.info("(Would buy items now)")
        else:
            controller.right_click(x - rnum(250*aspect), y + rnum(250))
            rsleep(0.05)
            logger.info("Using W to try and escape")
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
        controller.right_click(x + rnum(250*aspect), y - rnum(250))
        return

    # For now, find the nearest enemy minion, player, or objective with the lowest cost and attack it
    best_cost = float('inf')
    best_action = None
    turret_range = 550
    turret_influence = 15
    best_minion_cost = float('inf')
    for m in enemy_minions:
        mx, my = m.get_x(), m.get_y()
        cost = (min(math.hypot(x-mx, y-my), 800) + 100) * (0.4 + m.health)
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
        cost = (min(math.hypot(x-px, y-py), 800) + 100) * (0.1 + p.health ** 2.5)
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
        if enemy_players:
            continue
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
        cost = (min(math.hypot(x-ox, y-oy), 800) + 100) * 0.6
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
            ally_power += p.level * p.health
        else:
            enemy_power += p.level * p.health
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
    back_off_cost = ((5 * ally_power / enemy_power) ** 4) * player.health
    if back_off_cost < best_cost:
        best_cost = back_off_cost
        best_action = "back off"

    logger.debug(f"Back {back_off_cost:.3f} (Ally power: {ally_power:.3f}, Enemy power: {enemy_power:.3f})")
    logger.debug(f"Minion {best_minion_cost:.3f}, Player {best_player_cost:.3f}, Objective {best_objective_cost:.3f}")

    if best_action == "back off" or best_cost == float('inf'):
        # Nothing better to do than move back
        logger.debug("Moving back, nothing else to do")
        controller.right_click(x - rnum(150*aspect), y + rnum(150))
        return

    logger.info(f"Attacking {type(best_action).__name__} with cost {best_cost:.3f}")
    tx = best_action.get_x()
    ty = best_action.get_y()
    th = best_action.health

    # Use abilities if close enough
    if math.hypot(x - tx, y - ty) < 500:
        if type(best_action) is vision.Player:
            # Use long cooldown spells to kill the player
            if th < 0.2:
                # Try to execute
                logger.info(f"Using ultimate to try and kill the player")
                controller.use_skillshot('r', tx, ty)
                rsleep(0.05)
            elif th < 0.4:
                logger.info(f"Using ghost to try and kill the player")
                controller.use_action('d')
                rsleep(0.05)
        if type(best_action) is not vision.Objective:
            # Use short cooldown spells when available
            action = random.randint(1, 4)
            if action == 1:
                logger.info(f"Using Q")
                controller.use_action('q')
            elif action == 2:
                logger.info(f"Using E")
                controller.use_skillshot('e', tx, ty)
            rsleep(0.05)
    # Attack move to keep dealing damage
    controller.attack_move(tx, ty)
