"""
Combines controllers and listeners to play League of Legends.

This AI is manually coded, to serve as a baseline for the more advanced AIs.
It can only play Annie mid.

To use (IMPORTANT: Every step here must be followed, otherwise the bot will *not* work!):
- Play on 1920 x 1080 resolution.
- Enable locked camera (press Y).
- Create a custom item page containing a good Annie build, see https://app.mobalytics.gg/lol/champions/annie/build.
  There should only be one section. Name it "Optimal" (case-sensitive, the bot uses this to find the shop!).
  Put all items, including components, in order. The bot will simply right-click on each item in the given order
  whenever it can buy the next one. If done correctly, the bot should be able to just naively click one after the other
  and get a full build. (Remember to keep the 6 item inventory limit in mind!)

Optional but highly recommended:
- Use Flash on D and Heal on F for summoner spells.
- Set a good rune page for Annie. Make sure to include Electrocute.

The item set I use (you can import it into the game client):
{"title":"Annie","associatedMaps":[11,12],"associatedChampions":[1],"blocks":[{"items":[{"id":"3070","count":1},{"id":"1052","count":1},{"id":"1027","count":1},{"id":"1052","count":1},{"id":"3802","count":1},{"id":"1001","count":1},{"id":"3020","count":1},{"id":"1026","count":1},{"id":"6655","count":1},{"id":"1052","count":1},{"id":"1028","count":1},{"id":"3145","count":1},{"id":"1058","count":1},{"id":"4645","count":1},{"id":"1058","count":1},{"id":"1058","count":1},{"id":"3089","count":1},{"id":"1052","count":1},{"id":"4630","count":1},{"id":"3135","count":1},{"id":"3003","count":1},{"id":"2139","count":1},{"id":"2139","count":1},{"id":"2139","count":1},{"id":"2139","count":1},{"id":"2139","count":1},{"id":"2139","count":1}],"type":"Optimal"}]}
"""

import math
import random
import time
from typing import List

import cv2 as cv
import editdistance

import numpy as np

import controllers.game_controller as controller
import listeners.vision.game_vision as vision
from listeners.keyboard import key_listener
from listeners.vision import image_handler
from misc import color_logging
from misc.rng import rnum, rsleep
from listeners.vision.game_vision import Minion, Player, Objective

logger = color_logging.getLogger('ai', level=color_logging.DEBUG)
is_debug = False
curr_time = time.time()
prev_time = time.time()
last_log_time = time.time()

# Game constants
# q = Point-and-click, w = Cone, e = Shield, r = Bear!, d = Flash, f = Heal
ABILITIES = ['q', 'w', 'e', 'r', 'd', 'f']
COOLDOWNS = [0.5, 8, [0, 14, 13, 12, 11, 10], [0, 120, 100, 80], 300, 240]
# % health to safely last hit using Q
LAST_HIT_PC = [0.1, 0.2, 0.27, 0.32, 0.37, 0.45]
# Annie level-up order
LEVEL_ORDER = [0, 1, 2, 0, 0, 3, 0, 1, 0, 1, 3, 1, 1, 2, 2, 3, 2, 2]
# Range of Q and W
BASIC_RANGE = 350
# Range of Flash-R combo
ALL_IN_RANGE = 450
# Turret aggro range
TURRET_RANGE = 650
# Enemy champion risk range
RISK_RANGE = 600
# Horizontal screen stretch
ASPECT = 1.4
# Minimap margin
MINIMAP_MARGIN = 20
# Debug display scale
debug_display_scale = 0.5

# Which side of the map we're on
on_top_right = False
# Which lane we're playing in
assigned_lane = "mid"  # Also "top" or "bot"
# assigned_lane = "bot"
EDGEL = 0.03
EDGER = 0.97
LANE_POINTS = {
    # Equally spaced from 0 to 1
    "mid": [(-99., -99.)] + [(i, i) for i in np.linspace(EDGEL, EDGER, 9)] + [(99., 99.)],
    "top": [(EDGEL, -99.)] + [(EDGEL, i) for i in np.linspace(EDGEL, EDGER, 6)][:-1]
           + [(EDGEL + 0.04, EDGER - 0.04)] + [(i, EDGER) for i in np.linspace(EDGEL, EDGER, 6)][1:] + [(99., EDGER)],
    "bot": [(-99., EDGEL)] + [(i, EDGEL) for i in np.linspace(EDGEL, EDGER, 6)][:-1]
           + [(EDGER - 0.04, EDGEL + 0.04)] + [(EDGER, i) for i in np.linspace(EDGEL, EDGER, 6)][1:] + [(EDGER, 99.)],
}
retreat_dir = -135
push_dir = 45

level = 0
ability_levels = [0, 0, 0, 0, 1, 1]
cooldowns = [0, 0, 0, 0, 0, 0]
has_turret_aggro = False
last_seen_health = 0
past_health = []
last_seen_enemy = float('-inf')
last_base = float('-inf')
minimap_bounds = (-1, -1, -1, -1)
closest_point = (0, 0)
player_loc = (0, 0)

main_status = "base"
sub_status = "loading"
# Skip loading screen
# sub_status = "going_to_lane"
main_status_time = float('-inf')
sub_status_time = float('-inf')


# --- Main AI logic ---


def reset() -> None:
    """
    Resets the AI.
    """
    global main_status, sub_status, main_status_time, sub_status_time, level, ability_levels, cooldowns, \
        on_top_right, has_turret_aggro, last_seen_health, last_seen_enemy, last_base, used_items, minimap_bounds, past_health
    main_status = "base"
    sub_status = "loading"
    main_status_time = float('-inf')
    sub_status_time = float('-inf')
    level = 0
    ability_levels = [0, 0, 0, 0, 1, 1]
    cooldowns = [0, 0, 0, 0, 0, 0]
    on_top_right = False
    has_turret_aggro = False
    last_seen_health = 0
    past_health = []
    minimap_bounds = (-1, -1, -1, -1)
    last_seen_enemy = float('-inf')
    last_base = float('-inf')
    used_items = set()


def has_stun_up(img: np.ndarray, player: Player) -> bool:
    """
    Checks if the player has 4 passive stacks (stun up).
    :param img: The current frame.
    :param player: The player.
    :return: Whether stun is up.
    """
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    purple_pixel = hsv_img[player.y1 - 75 + 30, player.x1 - 20 + 104]
    if 139 <= purple_pixel[0] <= 145:
        return True
    else:
        return False


def get_current_loc(img: np.ndarray) -> None:
    """
    Gets your location on the map, expressed as two coordinates in the range [0, 1], and saves it to player_loc.
    Also does some initial side setup when the game starts.
    :param img: The current frame.
    """
    global minimap_bounds, on_top_right, player_loc
    # Only look at the bottom-right part of the image
    if minimap_bounds[0] == -1:
        curr_bounds = (img.shape[1] - 500, img.shape[0] - 500, img.shape[1], img.shape[0])
        curr_bounds = tuple(map(int, curr_bounds))
    else:
        curr_bounds = minimap_bounds
    res = img[curr_bounds[1]:curr_bounds[3], curr_bounds[0]:curr_bounds[2]]
    # Filter out everything except white-ish pixels
    filtered = cv.inRange(res, (220, 220, 220), (255, 255, 255))
    # Find the largest batch of white pixels in the image
    contours, _ = cv.findContours(filtered, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return
    contour = max(contours, key=cv.contourArea)
    # Get the leftmost, rightmost, topmost, and bottommost points of the contour
    leftmost = contour[contour[:, :, 0].argmin()][0][0]
    rightmost = contour[contour[:, :, 0].argmax()][0][0]
    topmost = contour[contour[:, :, 1].argmin()][0][1]
    bottommost = contour[contour[:, :, 1].argmax()][0][1]
    cx = (leftmost + rightmost) / 2
    cy = (topmost + bottommost) / 2

    # Get minimap size if not yet found
    if minimap_bounds[0] == -1:
        if leftmost < topmost:
            # Playing on bottom left side
            bot_margin = curr_bounds[3] - (curr_bounds[1] + cy)
            right_margin = bot_margin
            minimap_size = curr_bounds[2] - (curr_bounds[0] + cx) - right_margin
            on_top_right = False
        else:
            # Playing on top right side
            right_margin = curr_bounds[2] - (curr_bounds[0] + cx)
            bot_margin = right_margin
            minimap_size = curr_bounds[3] - (curr_bounds[1] + cy) - bot_margin
            on_top_right = True
        minimap_bounds = (
            int(img.shape[1] - minimap_size - right_margin - MINIMAP_MARGIN),
            int(img.shape[0] - minimap_size - bot_margin - MINIMAP_MARGIN),
            int(img.shape[1] - right_margin + MINIMAP_MARGIN),
            int(img.shape[0] - bot_margin + MINIMAP_MARGIN)
        )
        # logger.debug(f"Minimap bounds: {minimap_bounds}")
        logger.info(f"Playing {assigned_lane} on the {'blue' if not on_top_right else 'red'} side")
        return get_current_loc(img)

    # Convert to coordinates in the range [0, 1]
    cx = (cx - MINIMAP_MARGIN) / (minimap_bounds[2] - minimap_bounds[0] - MINIMAP_MARGIN * 2)
    cy = (cy - MINIMAP_MARGIN) / (minimap_bounds[3] - minimap_bounds[1] - MINIMAP_MARGIN * 2)
    cx = min(1, max(0, cx))
    cy = min(1, max(0, 1 - cy))
    # logger.debug(f"Current location: {cx:.3f}, {cy:.3f}")
    player_loc = (cx, cy)
    update_closest_point(cx, cy)


def minimap_right_click(x: float, y: float) -> None:
    """
    Right-clicks on the minimap at the given coordinates.
    :param x: The x coordinate in the range [0, 1].
    :param y: The y coordinate in the range [0, 1].
    """
    global minimap_bounds
    if minimap_bounds is None:
        logger.warning("Cannot right-click on minimap because minimap has not yet been found")
        return
    x = x * (minimap_bounds[2] - minimap_bounds[0]) + minimap_bounds[0]
    y = y * (minimap_bounds[3] - minimap_bounds[1]) + minimap_bounds[1]
    controller.move_mouse_precise(x, y)
    controller.right_click_only()


def update_closest_point(x: float, y: float) -> None:
    """
    Updates the closest point and movement directions for the bot.
    The closest the point is the one with a center diagonal nearest to the bot's.
    :param x: The bot's x coordinate in the range [0, 1].
    :param y: The bot's y coordinate in the range [0, 1].
    """
    global closest_point, retreat_dir, push_dir
    # Find closest node in the current lane
    lane_points = LANE_POINTS[assigned_lane]
    if on_top_right:
        lane_points = lane_points[::-1]
    closest_point = min(lane_points, key=lambda p: abs((p[0] + p[1]) - (x + y)))
    closest_i = lane_points.index(closest_point)
    # logger.debug(f"Closest point: {closest_point[0]:.3f}, {closest_point[1]:.3f}")
    # Find the direction to retreat and push (by getting the next point or previous point)
    prev_point, next_point = lane_points[closest_i - 1], lane_points[closest_i + 1]
    # In degrees
    retreat_dir = math.degrees(math.atan2(prev_point[1] - player_loc[1], prev_point[0] - player_loc[0]))
    push_dir = math.degrees(math.atan2(next_point[1] - player_loc[1], next_point[0] - player_loc[0]))
    # logger.debug(f"Retreat direction: {retreat_dir:.3f}")
    # logger.debug(f"Push direction: {push_dir:.3f}")


def distance_from_lane(x: float, y: float) -> float:
    """
    Gets the minimum distance from the given coordinates to the bot's current lane.
    :param x: The x coordinate in the range [0, 1].
    :param y: The y coordinate in the range [0, 1].
    :return: The distance from the lane.
    """
    return math.hypot(x - closest_point[0], y - closest_point[1])


# def move_towards_lane(x: float, y: float) -> None:
#     """
#     Moves the bot towards the closest point in the current lane.
#     :param x: The x coordinate in the range [0, 1].
#     :param y: The y coordinate in the range [0, 1].
#     """
#     global closest_point
#     # Move towards the closest point in the current lane
#     dx, dy = closest_point[0] - x, closest_point[1] - y
#     d = math.hypot(dx, dy)
#     if d > 0.02:
#         dx, dy = dx / d, dy / d
#         minimap_right_click(x + dx, y + dy)


def do_laning(img: np.ndarray, player: Player,
              ally_minions: List[Minion], ally_players: List[Player], ally_objectives: List[Objective],
              enemy_minions: List[Minion], enemy_players: List[Player], enemy_objectives: List[Objective]) -> None:
    global sub_status, sub_status_time, last_seen_enemy, has_turret_aggro, \
        level, last_seen_health, past_health, player_loc

    # Check if the player is visible
    if player is None:
        logger.warning("Cannot find controllable player")
        switch_status("laning", "unknown")
        if sub_status_time >= 3:
            # Assume that the player died
            logger.info("Assuming that the player died")
            rsleep(1)
            switch_status("base", "shopping")
        return
    get_current_loc(img)

    # Level abilities if allowed
    if level < player.level and level < 18:
        logger.info(f"Leveling {ABILITIES[LEVEL_ORDER[level]]}")
        controller.level_ability(ABILITIES[LEVEL_ORDER[player.level - 1]])
    level = player.level
    # Update ability levels
    for i in range(4):
        ability_levels[i] = 0
    for i in range(level):
        ability_levels[LEVEL_ORDER[i]] += 1

    has_stun = has_stun_up(img, player)
    x, y = player.get_x(), player.get_y()
    if enemy_players:
        last_seen_enemy = curr_time

    # Update turret aggro
    player_in_range = False
    enemy_in_range = False
    allies_in_range = 0
    for t in enemy_objectives:
        if in_turret_range(t, player):
            player_in_range = True
        for p in enemy_players:
            if in_turret_range(t, p):
                enemy_in_range = True
        # noinspection PyTypeChecker
        for m in ally_minions + ally_players:
            if in_turret_range(t, m, -100):
                allies_in_range += 1
    if not player_in_range:
        has_turret_aggro = False
    elif enemy_in_range or allies_in_range <= 1 or player.health < last_seen_health - 0.1:
        has_turret_aggro = True

    # Check if we're being damaged by something (other than turret aggro)
    past_health.append(player.health)
    past_health = past_health[-4:]
    health_change = player.health - np.average(past_health)
    if health_change <= -0.0025:
        # Being damaged by something
        if sub_status != "all_in" and sub_status != "trading":
            logger.info("Taking damage, falling back a bit")
            # logger.debug(f"Health change: {health_change:.3f}")
            right_click_direction(player, 300, rnum(retreat_dir, s=15, a=True))
            return
        elif sub_status == "trading":
            use_ability(2)
    last_seen_health = player.health

    # Heal if at low health
    if player.health < 0.15 and health_change > -0.25 and can_use_skillshot(5):
        logger.info("Healing due to low health")
        use_ability(5)

    # Should we back?
    if sub_status != "backing" and sub_status != "backing_wait" and sub_status != "all_in":
        # Consider backing to buy items (occasionally)
        if abs(health_change) > 0.02:
            gold = find_gold(img)
            if level < 18 and gold >= 2500 or (gold >= 1300 and player.health < 0.7):
                logger.info(f"Backing to buy items ({gold} gold)")
                switch_status("laning", "backing")
        # Low health or mana
        if player.health < 0.35:
            logger.info(f"Backing due to low health ({player.health:.2f})")
            switch_status("laning", "backing")
        elif player.mana < 0.05:
            logger.info(f"Backing due to low mana ({player.mana:.2f})")
            switch_status("laning", "backing")
        # Too much time passed (failsafe)
        elif main_status_time > 300:
            logger.info(f"Backing due to too much time passed ({main_status_time:.0f} seconds)")
            switch_status("laning", "backing")

    # Should we push?
    if sub_status != "pushing" and sub_status != "backing" and sub_status != "backing_wait":
        if last_seen_enemy + 10 < curr_time:
            logger.info("No enemies seen in a while, switching to pushing")
            switch_status("laning", "pushing")
        elif not enemy_players and [t for t in ally_objectives if in_turret_range(t, player)]:
            logger.info("Under ally turret with no enemies, switching to pushing")
            switch_status("laning", "pushing")

    # Check if status should be switched
    if sub_status == "" or sub_status == "unknown":
        switch_status("laning", "passive")
    elif sub_status == "passive":
        # Can we play aggressive?
        if player.health >= 0.5 and has_stun and not has_turret_aggro:
            logger.info("Stun up and safe, switching to aggressive")
            switch_status("laning", "aggressive")
    elif sub_status == "aggressive":
        # Can we still play aggressive?
        if player.health < 0.5:
            logger.info("Low health, switching to passive")
            switch_status("laning", "passive")
        elif not has_stun:
            logger.info("Stun down, switching to passive")
            switch_status("laning", "passive")
        elif has_turret_aggro:
            logger.info("Under turret aggro, switching to passive")
            switch_status("laning", "passive")
    elif sub_status == "trading":
        # Are we in turret aggro range?
        if has_turret_aggro:
            logger.info("In turret aggro range, switching to passive")
            switch_status("laning", "passive")
        # Are enemy champions in trade range?
        nearest_enemy_dist = float('inf')
        for p in enemy_players:
            nearest_enemy_dist = min(math.hypot(p.get_x() - x, p.get_y() - y), nearest_enemy_dist)
        if nearest_enemy_dist >= BASIC_RANGE:
            logger.info("No enemy champions in range, switching to passive")
            switch_status("laning", "passive")
        # Should we stop trading?
        if sub_status_time > 2:
            logger.info("Trading timer expired, switching to passive")
            switch_status("laning", "passive")
    elif sub_status == "all_in":
        # Should we stop the all-in?
        if sub_status_time > 2.5 and has_turret_aggro:
            logger.info("All in timer expired with turret aggro, switching to passive")
            switch_status("laning", "passive")
    elif sub_status == "pushing":
        # Are we safe to keep pushing?
        if enemy_players:
            logger.info("Enemy players visible, switching to passive")
            switch_status("laning", "passive")

    # If enemy outnumbers us, move back if we're too close
    if len(enemy_players) > len([p for p in ally_players if math.hypot(p.get_x() - x, p.get_y() - y) < RISK_RANGE]) + 1:
        nearest_enemy_dist = float('inf')
        for p in enemy_players:
            nearest_enemy_dist = min(math.hypot(p.get_x() - x, p.get_y() - y), nearest_enemy_dist)
        if nearest_enemy_dist < RISK_RANGE + 50:
            logger.info("Too many enemies, backing off")
            right_click_direction(player, 300, retreat_dir)
            return

    # Are enemy champions in trade range?
    if sub_status != "trading" and sub_status != "backing" and sub_status != "backing_wait" and sub_status != "all_in":
        nearest_enemy_dist = float('inf')
        for p in enemy_players:
            nearest_enemy_dist = min(math.hypot(p.get_x() - x, p.get_y() - y), nearest_enemy_dist)
        if not has_turret_aggro and nearest_enemy_dist < BASIC_RANGE:
            logger.info("Enemy champions in range, switching to trading")
            switch_status("laning", "trading")

    # Can we all-in?
    if sub_status != "all_in" and sub_status != "backing" and sub_status != "backing_wait" and enemy_players:
        # Calculate power of controlled character
        my_damage = 0
        if can_use_skillshot(0):
            my_damage += 0.15
        if not can_use_skillshot(1):
            my_damage += 0.15
        if can_use_skillshot(3):
            my_damage += 0.4
        if player.mana < 0.25:
            my_damage /= 2
        if not has_stun:
            my_damage /= 1.5

        # Calculate contribution of all allies (including you), enemies, and turrets
        all_players = ally_players + enemy_players + [player]
        # Turret dives are very risky; treat an enemy turret like a level 10 player
        if has_turret_aggro:
            all_players.append(Player(-1, -1, -1, -1, False, False, 1, 1, 10))
        # Is there an ally turret in range of an enemy? If so, treat it like a level 10 player
        ally_turret = len([(t, e) for t in ally_objectives for e in enemy_players if in_turret_range(t, e, -100)]) > 0
        if ally_turret:
            all_players.append(Player(-1, -1, -1, -1, True, False, 1, 1, 10))
        average_level = sum([p.level for p in all_players]) / len(all_players)

        # Calculate all in power
        all_in_power = 0
        for p in all_players:
            level_diff = p.level - average_level
            # Calculate player's power
            base_damage = 0.5 if p != player else my_damage
            power = base_damage * (1.3 ** level_diff) * (p.health ** 1.15)
            if p in ally_players or p == player:
                all_in_power += power
            else:
                all_in_power -= power
        nearest_enemy_dist = min(math.hypot(p.get_x() - x, p.get_y() - y) for p in enemy_players)
        # Should we all in?
        power_needed = 0.25
        if all_in_power > power_needed and nearest_enemy_dist < ALL_IN_RANGE + 50:
            logger.warning(f"Ppwer = {all_in_power:.2f} > {power_needed:.2f}, going all in!")
            switch_status("laning", "all_in")
        else:
            logger.debug(f"Power = {all_in_power:.2f} < {power_needed:.2f}")

    if sub_status == "passive" or sub_status == "aggressive" or sub_status == "pushing":
        # Play passively, only going up to last hit, and trading if opponent gets into range
        if not ally_players and not ally_objectives and not ally_minions:
            # Make sure we're still roughly in our lane (and not in the jungle somewhere)
            # if player_loc is not None:
            #     if distance_from_lane(*player_loc) > 0.25:
            #         logger.info(f"Too far from {assigned_lane}, moving back")
            #         move_towards_lane(*player_loc)
            #         return
            # Move back to allies
            right_click_direction(player, 300, retreat_dir)
            return

        # If turret is aggroed on us, move back
        if has_turret_aggro:
            logger.info("Turret aggroed, backing off")
            right_click_direction(player, 300, retreat_dir)
            return

        # Are there minions to last hit?
        enemy_last_hits = []
        for m in enemy_minions:
            # Close enough
            if math.hypot(m.get_x() - x, m.get_y() - y) >= BASIC_RANGE + 150:
                continue
            # Low enough health
            if m.health > LAST_HIT_PC[ability_levels[0]]:
                continue
            enemy_last_hits.append(m)
        # Last hit the closest minion first
        if enemy_last_hits and random.random() < 0.75:
            enemy_last_hits.sort(key=lambda m: math.hypot(m.get_x() - x, m.get_y() - y))
            m = enemy_last_hits[0]
            logger.info(f"Last hitting minion with HP {m.health:.2f}")
            if can_use_skillshot(0) and (not has_stun or sub_status == "pushing" or random.random() < 0.08):
                dist, angle = absolute_to_angle(x, y, m.get_x(), m.get_y())
                if dist >= BASIC_RANGE:
                    move_towards(player, m.get_x(), m.get_y())
                    rsleep(0.3)
                use_skillshot(0, m.get_x(), m.get_y())
            attack_move(m.get_x(), m.get_y())
            return

        # Is there an open enemy turret to hit?
        if enemy_objectives and random.random() < 0.75:
            t = enemy_objectives[0]
            allies_in_range = 0
            # noinspection PyTypeChecker
            for m in ally_minions + ally_players:
                if in_turret_range(t, m, -150):
                    allies_in_range += 1
            if allies_in_range > 1:
                # Can hit this turret
                logger.info(f"Attacking enemy objective")
                if random.random() < 0.5:
                    attack_move(t.get_x(), t.get_y())
                return

        # If pushing, use AOE ability on closest minions
        if sub_status == "pushing" and enemy_minions and random.random() < 0.75:
            enemy_minions.sort(key=lambda m: math.hypot(m.get_x() - x, m.get_y() - y))
            m = enemy_minions[0]
            if math.hypot(m.get_x() - x, m.get_y() - y) < BASIC_RANGE:
                use_skillshot(1, m.get_x(), m.get_y())
            attack_move(m.get_x(), m.get_y())
            return

        # No targetable minions or objectives; stay behind center point of furthest forward allies
        ally_x = 0
        ally_y = 0
        # noinspection PyTypeChecker
        allies = ally_minions + ally_players + ally_objectives
        allies = sorted(allies, key=lambda p: p.get_y() - p.get_x())[:3]
        for a in allies:
            ally_x += a.get_x()
            ally_y += a.get_y()
        ally_x /= len(allies)
        ally_y /= len(allies)
        back_dist = 150
        if (sub_status == "aggressive" or sub_status == "pushing") and not has_turret_aggro:
            back_dist = 25
        tx, ty = angle_to_absolute(ally_x, ally_y, back_dist, rnum(retreat_dir, 3, True))
        to_do = random.random()
        if 0 <= to_do <= 0.3:
            # Move to bottom right (side to side)
            tx, ty = angle_to_absolute(tx, ty, rnum(120, 0.2), rnum(push_dir - 90, 5, True))
        elif 0.3 <= to_do <= 0.6:
            # Move to top left (side to side)
            tx, ty = angle_to_absolute(tx, ty, rnum(120, 0.2), rnum(push_dir + 90, 5, True))
        else:
            # Don't click
            return
        # Move in this direction
        dist, angle = absolute_to_angle(x, y, tx, ty)
        dist = min(200.0, dist)
        right_click_direction(player, dist, angle)
    elif sub_status == "trading":
        # Trade by using abilities while backing off
        # Target the closest low health champion
        target = []
        for p in enemy_players:
            target.append(p)
        if not target:
            # No one to trade with
            logger.info("No one to trade with, switching to passive")
            switch_status("laning", "passive")
            return
        target = sorted(target, key=lambda p: math.hypot(p.get_x() - x, p.get_y() - y))[0]
        has_turret_aggro = True

        # Move away from the target
        dist = math.hypot(target.get_x() - x, target.get_y() - y)
        if dist < BASIC_RANGE:
            # Use some abilities
            logger.info("Trading with enemy")
            use_ability(2)
            if target.health < 0.25 and can_use_skillshot(3):
                use_skillshot(3, target.get_x(), target.get_y())
                rsleep(0.1)
                return
            if can_use_skillshot(0):
                use_skillshot(0, target.get_x(), target.get_y())
                rsleep(0.1)
                return
            if can_use_skillshot(1):
                use_skillshot(1, target.get_x(), target.get_y())
                rsleep(0.1)
                return
            attack_move(target.get_x(), target.get_y())
            rsleep(0.3)
        right_click_direction(player, 150, rnum(retreat_dir, 5, True))
        rsleep(0.3)
    elif sub_status == "all_in":
        # Attempt to kill as many enemies as possible
        # All-in if enemy health is below 70% at 3 or 4 stacks with E-W-Flash-R-Q-AA.
        # Target the closest low health champion
        target = []
        for p in enemy_players:
            target.append(p)
        if not target:
            # No one to all-in?
            logger.info("No one to all-in, switching to passive")
            switch_status("laning", "passive")
            return
        target = sorted(target, key=lambda p: math.hypot(p.get_x() - x, p.get_y() - y))[0]
        has_turret_aggro = True

        # Move towards the target
        dist = math.hypot(target.get_x() - x, target.get_y() - y)
        if BASIC_RANGE + 50 <= dist <= ALL_IN_RANGE + 50 and can_use_skillshot(4):
            # Flash
            use_skillshot(4, target.get_x(), target.get_y())
            rsleep(0.3)
        elif dist >= BASIC_RANGE - 25:
            # Move towards the target
            use_ability(2)
            move_towards(player, target.get_x(), target.get_y())
        else:
            # Start (or continue) combo
            if can_use_skillshot(1):
                use_skillshot(1, target.get_x(), target.get_y())
                rsleep(0.1)
                return
            if can_use_skillshot(3):
                dist, angle = absolute_to_angle(x, y, target.get_x(), target.get_y())
                dist = min(BASIC_RANGE - 75.0, dist)
                tx, ty = angle_to_absolute(x, y, dist, angle)
                use_skillshot(3, tx, ty)
                rsleep(0.1)
                return
            if can_use_skillshot(0):
                use_skillshot(0, target.get_x(), target.get_y())
                rsleep(0.1)
                return
            attack_move(target.get_x(), target.get_y())
    elif sub_status == "backing" or sub_status == "backing_wait":
        # Go to a safe place and recall
        if not enemy_minions and not enemy_players and not enemy_objectives:
            if sub_status == "backing":
                right_click_direction(player, 500, retreat_dir)
                rsleep(2)
                logger.info("Recalling")
                switch_status("laning", "backing_wait")
                controller.press_key('b')
            elif sub_status_time > 9:
                rsleep(4)
                logger.info("Switching to base")
                switch_status("base", "shopping")
        else:
            # Run away
            if sub_status != "backing":
                logger.info("Backing off from enemies")
                switch_status("laning", "backing")
            use_ability(2)
            right_click_direction(player, 300, retreat_dir)
            # Flash if needed
            if player.health < 0.3 and health_change <= -0.15 and can_use_skillshot(4):
                logger.info("Flashing as a last resort")
                right_click_direction(player, 300, retreat_dir)
                use_ability(4)
                right_click_direction(player, 300, retreat_dir)
    else:
        logger.warning("Unknown sub-status: " + sub_status)


# --- Base logic ---

optimal = None
prev_gold = None
used_items = set()


def close_match(s1: str, s2: str) -> bool:
    if len(s1) < 3 or len(s2) < 3:
        return s1 == s2
    acceptable = min(len(s1), len(s2)) // 5 + 1
    return editdistance.eval(s1, s2) <= acceptable


def open_shop() -> None:
    logger.info("Opening the shop")
    switch_status("base", "shopping")
    prev_gold = None
    controller.move_mouse(900, 800)
    controller.left_click(900, 800)
    rsleep(0.35)
    controller.press_key('p')
    rsleep(0.3)


def exit_shop() -> None:
    switch_status("base", "going_to_lane")
    controller.press_key('p')
    rsleep(0.5)


def find_gold(img: np.ndarray) -> int:
    """
    Finds the amount of gold the player has.
    :param img: Screenshot of the game state.
    :return: The amount of gold the player has, or -1 if it's not found.
    """
    width = img.shape[1]
    height = img.shape[0]
    scale = height / 1080
    x1 = int(width * 0.5 + 165 * scale)
    y1 = int(height - 35 * scale)
    x2 = int(width * 0.5 + 220 * scale)
    y2 = int(height - 8 * scale)
    gold_img = img[y1:y2, x1:x2]
    # cv.imshow("Gold", cv.resize(gold_img, (0, 0), fx=5, fy=5))
    gold = vision.find_number(gold_img)
    logger.debug(f"Gold: {gold}")
    return gold


def do_base(img: np.ndarray, player: Player,
            ally_minions: List[Minion], ally_players: List[Player], ally_objectives: List[Objective],
            enemy_minions: List[Minion], enemy_players: List[Player], enemy_objectives: List[Objective]) -> None:
    """
    Buys items from the shop, or runs to lane.
    :param img: Screenshot of the game state.
    """
    global optimal, prev_gold, last_base, used_items
    last_base = time.time()

    if sub_status == "shopping" or sub_status == "loading":
        # If shopping takes too long, uncomment these lines to skip it
        # exit_shop()
        # return

        # Locate certain pieces of text in the shop
        if optimal is None:
            # logger.debug("Searching the whole screen for text, this might take a bit...")
            w = img.shape[1]
            h = img.shape[0]
            if sub_status == "loading":
                logger.info("Loading...")
                # Look for level up on the bottom half of the screen
                text = vision.find_text(img, w // 4, h // 2, w * 3 // 4, h)
            else:
                # Look for optimal or victory/defeat text
                text = vision.find_text(img, 150, 150, w * 2 // 3, h * 3 // 4)
        else:
            # Only need to search in a specific portion of the screen
            text = vision.find_text(img, optimal.x1 - 10, optimal.y1 - 10, optimal.x2 + 560, optimal.y2 + 350)
        if is_debug:
            draw_results_text(img, text, display_scale=debug_display_scale)
        optimal = None
        game_end = None
        game_end_continue = None
        afk_text = None
        leaverbuster_text = None
        level_text = None
        for t in text:
            if close_match(t.text, "optimal"):
                optimal = t
            elif close_match(t.text, "victory") or close_match(t.text, "defeat"):
                game_end = t
            elif close_match(t.text, "continue"):
                game_end_continue = t
            elif close_match(t.text, "afk"):
                afk_text = t
            elif close_match(t.text, "leaverbuster"):
                leaverbuster_text = t
            elif close_match(t.text, "level up!") or close_match(t.text, "level up! + 1"):
                level_text = t

        # Check if still on loading screen
        if sub_status == "loading":
            if level_text is None:
                return
            logger.info("Loading complete")
            open_shop()
            return

        # Check if the game is over
        if game_end is not None and game_end_continue is not None:
            if close_match(game_end.text, "victory"):
                logger.info("Match result: Victory!")
            else:
                logger.info("Match result: Defeat")
            switch_status("end")
            return

        # Handle AFK warning
        if afk_text is not None and leaverbuster_text is not None:
            logger.warning("AFK warning detected, dismissing...")
            # Dismiss the warning
            click_x = (afk_text.x1 + leaverbuster_text.x1) // 2 - 16
            for i in range(7):
                click_y = (afk_text.y2 + leaverbuster_text.y2) // 2 + 60 + i * 40
                controller.left_click(click_x, click_y)
                rsleep(0.15)
            # Move randomly
            for i in range(7):
                click_y = (afk_text.y2 + leaverbuster_text.y2) // 2 + 100
                controller.right_click(click_x + rnum(0, 200, True), click_y + rnum(0, 150, True))
                rsleep(0.4)
            logger.warning("Dismissed, attempting to reset...")
            # Back
            switch_status("laning", "backing")
            return

        # Time bailout
        if main_status_time > 15:
            logger.info("Exiting the shop (too much time)")
            exit_shop()
            return

        # Open the shop if it isn't open yet
        if optimal is None:
            open_shop()
            return

        # Locate gold amount and items to buy
        gold = find_gold(img)
        prev_gold = gold

        items = []
        for t in text:
            if not t.text.isdigit():
                continue
            if optimal.x1 - 30 <= t.x1 <= optimal.x1 + 600 and optimal.y1 + 30 <= t.y1 <= optimal.y1 + 350:
                # Items to buy
                t.row = (t.y1 - optimal.y1 + 35) // 73
                t.col = (t.x1 - optimal.x1 + 25) // 55
                if (t.row, t.col) not in used_items:
                    items.append(t)
        if gold == -1:
            logger.warning("Gold not found in shop, assuming 0")
            gold = 0

        # Buy items by location on the shop screen
        items = sorted(items, key=lambda t: (t.row, t.col))
        logger.debug(f"Items: {[t.text for t in items]}")
        bought_items = False
        for t in items:
            cost = int(t.text)
            if cost <= gold:
                logger.info(f"Buying item at row {t.row} column {t.col} with cost {cost}")
                controller.move_mouse_precise(t.get_x(), t.get_y() - 35)
                controller.right_click_only()
                gold -= cost
                used_items.add((t.row, t.col))
                bought_items = True
                rsleep(0.3)
            else:
                break

        # Move away from the shop
        controller.move_mouse_precise(optimal.x1 + 250, optimal.y1 - 40)
        rsleep(0.35)

        if not bought_items:
            # Exit the shop
            logger.info("Exiting the shop")
            exit_shop()
    elif sub_status == "going_to_lane" or sub_status == "unknown":
        # Check if the player is visible
        if player is None:
            logger.info("Cannot find controllable player")
            switch_status("base", "unknown")
            if sub_status_time >= 2:
                # Assume that the player died
                logger.info("Assuming that the player died")
                open_shop()
            return
        else:
            switch_status("base", "going_to_lane")
        # Find player location (and initialize minimap)
        get_current_loc(img)
        # Walk towards the lane
        if random.random() < 0.75:
            right_click_direction(player, 400, push_dir)
        # Switch to laning once we near the middle of the map and/or the action
        if (level <= 6 and player_loc is not None and abs(1 - (player_loc[1] + player_loc[0])) <= 0.05) \
                or enemy_minions or enemy_players or enemy_objectives:
            logger.info(f"Switching to laning")
            switch_status("laning", "passive")
    else:
        logger.warning(f"Unknown sub_status: {sub_status}")


# --- Generic logic ---


def can_use_skillshot(n: int) -> bool:
    if ability_levels[n] == 0 or cooldowns[n] > 0:
        return False
    else:
        return True


def use_ability(n: int) -> None:
    if not can_use_skillshot(n):
        return
    logger.info(f"Using {ABILITIES[n]}")
    controller.press_key(ABILITIES[n])
    cooldowns[n] = COOLDOWNS[n] if type(COOLDOWNS[n]) != list else COOLDOWNS[n][ability_levels[n]]


def use_skillshot(n: int, x: float, y: float) -> None:
    if not can_use_skillshot(n):
        return
    logger.info(f"Using {ABILITIES[n]} at {x}, {y}")
    controller.use_skillshot(ABILITIES[n], x, y)
    cooldowns[n] = COOLDOWNS[n] if type(COOLDOWNS[n]) != list else COOLDOWNS[n][ability_levels[n]]


def move_towards(player: Player, x: float, y: float) -> None:
    dist, angle = absolute_to_angle(player.get_x(), player.get_y(), x, y)
    dist = min(dist, 150)
    right_click_direction(player, dist, angle)


def angle_to_absolute(x: float, y: float, dist: float, deg: float) -> (float, float):
    """
    Gets the point a certain distance away from (x, y) in the given direction.
    :param x: The x coordinate.
    :param y: The y coordinate.
    :param dist: The distance to travel.
    :param deg: The direction to travel.
    :return: The new x and y coordinates.
    """
    # Consider rectangle aspect scaling
    deg = deg * math.pi / 180
    return x + dist * math.cos(deg) * ASPECT, y - dist * math.sin(deg)


def absolute_to_angle(x1: float, y1: float, x2: float, y2: float) -> (float, float):
    """
    Gets the distance and angle between two points.
    :param x1: The x coordinate of the first point.
    :param y1: The y coordinate of the first point.
    :param x2: The x coordinate of the second point.
    :param y2: The y coordinate of the second point.
    :return: The distance and angle between the two points.
    """
    # Consider rectangle aspect scaling
    return math.hypot((x2 - x1) / ASPECT, y2 - y1), math.atan2(-(y2 - y1), (x2 - x1) / ASPECT) / math.pi * 180


def right_click_direction(player: Player, dist: float, deg: float, is_precise=False) -> None:
    """
    Right clicks in the given distance and direction from the player.
    :param player: The player.
    :param dist: The distance to travel.
    :param deg: The direction to travel.
    :param is_precise: Whether to use precise mouse movement.
    """
    x, y = angle_to_absolute(player.get_x(), player.get_y(), dist, deg)
    if is_precise:
        controller.move_mouse(x, y)
    controller.right_click(x, y)


def attack_move_direction(player: Player, dist: float, deg: float, is_precise=False) -> None:
    """
    Attack moves in the given distance and direction from the player.
    :param player: The player.
    :param dist: The distance to travel.
    :param deg: The direction to travel.
    :param is_precise: Whether to use precise mouse movement.
    """
    x, y = angle_to_absolute(player.get_x(), player.get_y(), dist, deg)
    if is_precise:
        controller.move_mouse(x, y)
    controller.attack_move(x, y)


def right_click(x: float, y: float, is_precise=False) -> None:
    """
    Right clicks at the given coordinates.
    :param x: The x coordinate.
    :param y: The y coordinate.
    :param is_precise: Whether to use precise mouse movement.
    """
    if is_precise:
        controller.move_mouse_precise(x, y)
    else:
        controller.move_mouse(x, y)
    controller.right_click(x, y)


def attack_move(x: float, y: float, is_precise=False) -> None:
    """
    Attack moves at the given coordinates.
    :param x: The x coordinate.
    :param y: The y coordinate.
    :param is_precise: Whether to use precise mouse movement.
    """
    if is_precise:
        controller.move_mouse_precise(x, y)
    else:
        controller.move_mouse(x, y)
    controller.attack_move(x, y)


def in_turret_range(turret: Objective, loc, delta=0) -> bool:
    # Get distance between turret and loc
    dist = math.hypot(turret.get_x() - loc.get_x(), turret.get_y() - loc.get_y())
    return dist < TURRET_RANGE + delta


def switch_status(new_main: str, new_sub="") -> None:
    global main_status, sub_status, main_status_time, sub_status_time
    if main_status != new_main:
        logger.debug(f"Switching main status from {main_status} to {new_main}")
        main_status = new_main
        main_status_time = 0
    if sub_status != new_sub or main_status != new_main:
        logger.debug(f"Switching sub status from {sub_status} to {new_sub}")
        sub_status = new_sub
        sub_status_time = 0


def process(img: np.ndarray) -> None:
    """
    Chooses an action to perform based on the screenshot of the game state.
    Assumes that the AI is using locked camera.
    :param img: Screenshot of the game state.
    """
    global curr_time, prev_time, last_log_time, level, main_status_time, sub_status_time

    # Parse the screenshot and update variables
    curr_time += time.time() - prev_time
    main_status_time += time.time() - prev_time
    sub_status_time += time.time() - prev_time
    for i in range(len(cooldowns)):
        cooldowns[i] -= time.time() - prev_time
        cooldowns[i] = max(0, cooldowns[i])
    if last_log_time + 5 < time.time():
        logger.info(f"FPS: {1 / (time.time() - prev_time):.1f}")
        last_log_time = time.time()
    prev_time = time.time()

    # Get all game information
    raw_minions, raw_players, raw_objectives = vision.find_all(img, scale=1)
    if is_debug:
        draw_results(img, raw_minions, raw_players, raw_objectives, display_scale=debug_display_scale)

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
    # logger.debug(f"Player visible = {player is not None}, "
    #              f"Minions {len(ally_minions)}/{len(enemy_minions)}, "
    #              f"Champs {len(ally_players)}/{len(enemy_players)}, "
    #              f"Objectives {len(ally_objectives)}/{len(enemy_objectives)}")

    # Run the AI
    if main_status == "base":
        do_base(img, player, ally_minions, ally_players, ally_objectives, enemy_minions, enemy_players,
                enemy_objectives)
    elif main_status == "laning":
        do_laning(img, player, ally_minions, ally_players, ally_objectives, enemy_minions, enemy_players,
                  enemy_objectives)
    elif main_status == "end":
        # Game is over; toggle and reset the bot
        logger.info("Automatically toggling and resetting the bot...")
        rsleep(0.6)
        key_listener.on_shift_t()
        rsleep(0.2)
        key_listener.on_shift_9()
    else:
        logger.warning(f"Unknown main status {main_status}")


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

    if players:
        x = players[0].x1 - 20 + 104
        y = players[0].y1 - 75 + 30
        cv.rectangle(res, (x, y), (x, y), (0, 0, 255), 2)

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

    def get_minimap_loc(x, y):
        draw_margin = MINIMAP_MARGIN / 1.5
        nx = minimap_bounds[0] + draw_margin + x * (minimap_bounds[2] - minimap_bounds[0] - draw_margin * 2)
        ny = minimap_bounds[3] - draw_margin - y * (minimap_bounds[3] - minimap_bounds[1] - draw_margin * 2)
        return int(nx * display_scale), int(ny * display_scale)

    # Draw minimap box
    cv.rectangle(res, (int(minimap_bounds[0] * display_scale), int(minimap_bounds[1] * display_scale)),
                 (int(minimap_bounds[2] * display_scale), int(minimap_bounds[3] * display_scale)), (0, 255, 255), 1)
    # Draw circle on minimap location
    cv.circle(res, get_minimap_loc(*player_loc), 3, (0, 255, 0), 3)

    # Draw circles and arrows for lane positions
    lane_points = []
    for point in LANE_POINTS[assigned_lane][1:-1]:
        x, y = get_minimap_loc(*point)
        lane_points.append((x, y))
    # Draw small circles and arrows
    # team_color = (255, 0, 0) if not on_top_right else (0, 0, 255)
    team_color = (0, 255, 255)
    for i in range(len(lane_points)):
        cv.circle(res, lane_points[i], 1, team_color, 1)
        if i > 0:
            cv.arrowedLine(res, lane_points[i - 1], lane_points[i], team_color, 1)

    # Show result
    cv.imshow("result", res)
    cv.waitKey(50)


def draw_results_text(img, text, display_scale=1.0, write_to_files=False) -> None:
    # Handle writing to files
    if write_to_files:
        display_scale = 1.0

    # Display text boxes
    res = img.copy()
    for r in text:
        cv.rectangle(res, (r.x1, r.y1), (r.x2, r.y2), (100, 255, 100), 1)
    res = image_handler.scale_image(res, display_scale)

    # Display text
    for r in text:
        displayed_text = r.text
        # displayed_text = f"{r.text} {r.score:.2f}"
        cv.putText(res, f"{r.text}",
                   (round(r.x1 * display_scale), round((r.y1 - 6) * display_scale)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6 * display_scale, (100, 255, 100), 1)
    # Show result or save to image
    if not write_to_files:
        cv.imshow("result", res)
        cv.waitKey(1)
    else:
        from misc.definitions import ROOT_DIR
        log_dir = f"{ROOT_DIR}/logs"
        cv.imwrite(f"{log_dir}/{int(time.time() * 1000)}.png", img)
        cv.imwrite(f"{log_dir}/{int(time.time() * 1000)}_res.png", res)
        logger.info(f"Saved results to {log_dir}")
