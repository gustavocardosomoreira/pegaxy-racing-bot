import time

from .pegaxyScreen import PegaxyScreen, PegaxyScreenEnum
from .logger import logger
from .mouse import *
from .utils import *
from .window import get_windows
from .config import Config


def create_pegaxy_managers():
    return [PegaxyManager(w) for w in get_windows()]


class PegaxyManager:
    def __init__(self, window) -> None:
        self.refresh_check_error = 0
        self.window = window
        self.refresh_long_time = 0
        self.race_requested = 0

    def __enter__(self):
        self.window.activate()
        time.sleep(2)
        return self

    def __exit__(self, type, value, tb):
        return

    def do_what_needs_to_be_done(self, current_screen):

        check_error = current_screen == PegaxyScreenEnum.NOT_FOUND.value

        refresh_check_error = Config.get('screen', 'refresh_check_error')*60
        if check_error or (refresh_check_error and (now() - self.refresh_check_error > refresh_check_error)):
            PegaxyScreen.do_check_error(self)

        refresh_long_time = Config.get('screen', 'refresh_long_time')*60
        if refresh_long_time and self.refresh_long_time and (now() - self.refresh_long_time < refresh_long_time):
            return True
        else:
            PegaxyScreen.try_to_race(self)

        return True

    def set_refresh_timer(self, propertie_name):
        setattr(self, propertie_name, time.time())
