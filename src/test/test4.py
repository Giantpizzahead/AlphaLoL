import subprocess

import win32com.client
import win32gui


def winEnumHandler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        print(hex(hwnd), win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd))
        # Menu
        if win32gui.GetWindowText(hwnd) == "League of Legends":
            win32gui.ShowWindow(hwnd, 9)
            win32gui.SetForegroundWindow(hwnd)
        # Game
        if win32gui.GetWindowText(hwnd) == "League of Legends (TM) Client":
            pass
            # win32gui.SetForegroundWindow(hwnd)

win32gui.EnumWindows(winEnumHandler, None)
win32com.client.Dispatch("WScript.Shell").SendKeys('%')
i = win32gui.FindWindow(None, "League of Legends")
print(win32gui.ShowWindow(i, 9))
print(win32gui.SetForegroundWindow(i))
subprocess.Popen([r"C:\Riot Games\Riot Client\RiotClientServices.exe",
                  "--launch-product=league_of_legends", "--launch-patchline=live"],
                 creationflags=8)
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
