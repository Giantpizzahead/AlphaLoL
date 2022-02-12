"""
Contains OS specific code that does things like finding windows and focusing apps.

TODO:
Support Linux?
"""

import platform
import subprocess

from misc import color_logging

try:
    from AppKit import NSRunningApplication, NSApplicationActivateIgnoringOtherApps, NSApplicationActivateAllWindows
except ImportError:
    import pythoncom
    import win32com.client
    import win32gui

logger = color_logging.getLogger('os_helper', level=color_logging.DEBUG)


def system_is_mac() -> bool:
    """
    Determines whether this is a Mac operating system.
    """
    return platform.system() == 'Darwin'


def system_is_windows() -> bool:
    """
    Determines whether this is a Windows operating system.
    """
    return platform.system() == 'Windows'


if not system_is_mac() and not system_is_windows():
    logger.critical("The operating system '{}' is not supported.".format(platform.system()))
    logger.critical("You will need to launch the League of Legends client manually.")
    logger.critical("It's very likely that the bot will crash - use it at your own risk!")


def find_app(id):
    """
    Checks if the given app is running on the system.
    :return: An OS-specific handle for the app, or None if the app isn't open.
    """
    if system_is_mac():
        menu_app = NSRunningApplication.runningApplicationsWithBundleIdentifier_(id)
        return menu_app[0] if menu_app else None
    else:
        menu_app = win32gui.FindWindow(None, id)
        return menu_app if menu_app else None


def find_menu():
    """
    Finds the League of Legends menu (windowed client).
    :return: An OS-specific handle for the menu, or None if the menu isn't open.
    """
    if system_is_mac():
        return find_app("com.riotgames.LeagueofLegends.LeagueClientUx")
    else:
        return find_app("League of Legends")


def find_game():
    """
    Finds the League of Legends game (fullscreen client).
    :return: An OS-specific handle for the game, or None if the game isn't open.
    """
    if system_is_mac():
        return find_app("com.riotgames.LeagueofLegends.GameClient")
    else:
        return find_app("League of Legends (TM) Client")


def focus_app(app) -> None:
    """
    Brings the specified handle to the front. Does nothing if the handle is None.
    """
    if app is None:
        return
    elif system_is_mac():
        # Activate the specified window
        app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps | NSApplicationActivateAllWindows)
    else:
        # Activate all windows with the specified name
        pythoncom.CoInitialize()
        target_name = win32gui.GetWindowText(app)

        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                if win32gui.GetWindowText(hwnd) == target_name:
                    win32com.client.Dispatch("WScript.Shell").SendKeys('%')
                    win32gui.ShowWindow(hwnd, 9)
                    win32gui.SetForegroundWindow(hwnd)
        win32gui.EnumWindows(winEnumHandler, None)


def launch_client() -> None:
    """
    Launches the League of Legends client.
    """
    if system_is_mac():
        subprocess.call(["open", r"/Applications/League of Legends.app"])
    else:
        subprocess.Popen([r"C:\Riot Games\Riot Client\RiotClientServices.exe",
                         "--launch-product=league_of_legends", "--launch-patchline=live"],
                         creationflags=8)
