import subprocess

from module.platform import Platform, PlatformEnum

from .config import Config


def get_windows():
    return (
        _get_linux_pegaxy_windows()
        if Platform().get_platform() == PlatformEnum.LINUX
        else _get_pegaxy_windows()
    )


def _get_linux_pegaxy_windows():
    browser = Config.get('generals', 'browser')
    if browser == 1:
        title = 'Pegaxy - Mozilla Firefox'
    elif browser == 2:
        title = 'Pegaxy - Google Chrome'
    else:
        title = 'Pegaxy - Chromium'

    stdout = (
        subprocess.Popen(
            f"xdotool search --name '{title}'", shell=True, stdout=subprocess.PIPE
        )
        .communicate()[0]
        .decode("utf-8")
        .strip()
    )
    windows = stdout.split("\n")
    return [LinuxWindow(w) for w in windows]

def _get_pegaxy_windows():
    import pygetwindow

    return [DefaultWindow(w) for w in pygetwindow.getWindowsWithTitle("Pegaxy")]

class LinuxWindow:
    def __init__(self, window_id) -> None:
        self.window = window_id

    def activate(self):        
        subprocess.Popen(f"xdotool windowactivate {self.window}", shell=True)

class DefaultWindow:
    def __init__(self, window) -> None:
        self.window = window

    def activate(self):
        self.window.activate()
