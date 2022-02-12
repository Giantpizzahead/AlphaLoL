from controllers.controller import *

from misc.rng import rsleep


def test_annie_combo(x: float, y: float) -> None:
    right_click(x, y)
    rsleep(0.07)
    use_skillshot('d', x, y)
    use_action('r')
    rsleep(0.03)
    use_action('q')
    rsleep(0.13)
    attack_move(x, y)
    rsleep(0.3)
    use_skillshot('w', x, y)
    rsleep(0.35)
    use_action('e')


if __name__ == '__main__':
    x = int(input("X coordinate of combo: "))
    y = int(input("Y coordinate of combo: "))
    print("Performing combo in 3 seconds...")
    rsleep(3, s=0)
    print("TIBBERS! :)")
    test_annie_combo(x, y)
