import pynput

from misc import color_logging

logger = color_logging.getLogger('main')
mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def on_release(key):
    print('{0} released'.format(
        key))
    if key == pynput.keyboard.Key.esc:
        # Stop listener
        return False


def main():
    logger.info("Hello!")
    logger.critical("LKDFjksljsldfjsf")
    listener = pynput.keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()
    '''
    mouse.position = (500, 500)
    mouse.press(Button.left)
    time.sleep(0.5)
    mouse.position = (800, 800)
    mouse.press(Button.left)
    '''
    from AppKit import NSWorkspace, NSApplicationActivateIgnoringOtherApps
    active_app_name = NSWorkspace.sharedWorkspace().runningApplications()
    for app in active_app_name:
        print(app.bundleIdentifier())
        if app.bundleIdentifier() == "com.riotgames.LeagueofLegends.LeagueClientUx":
            app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
    print(active_app_name)


if __name__ == '__main__':
    main()
