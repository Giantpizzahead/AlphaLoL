import time

match_start_time = -1


def get_game_time() -> float:
    if match_start_time == -1:
        return -1
    else:
        return round(time.time() - match_start_time, 2)


def start_game_time(dt=0) -> None:
    global match_start_time
    if dt == -1:
        match_start_time = -1
    else:
        match_start_time = time.time() - dt
