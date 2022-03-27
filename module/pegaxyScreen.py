from enum import Enum
from time import sleep

from cv2 import cv2
from MTM import matchTemplates

from .mouse import *
from .utils import *
from .logger import LoggerEnum, logger, logger_translated


class PegaxyScreenEnum(Enum):
    NOT_FOUND = -1
    RENT = 1
    MARKET = 2
    BREED = 3
    MYASSETS = 4

    ROOT = 5
    PICKPEGA = 6
    RACE = 7
    FINISHED = 8
    MATCHING = 9
    MATCHFOUND = 10  # No Metamask in sight
    # RACING_CALCULATING_REWARDS = 14

    OUTOFENERGY = 11
    UNABLETOJOINRACE = 12
    NOAVAILABLEPEGAS = 13

    METAMASK_SIGN = 20


class PegaxyScreen:
    @staticmethod
    def wait_for_screen(
            pegaxyScreenEnum, time_beteween: float = 0.5, timeout: float = 60
    ):
        def check_screen():
            screen = PegaxyScreen.get_current_screen()
            if screen == pegaxyScreenEnum:
                return True
            else:
                return None

        res = do_with_timeout(
            check_screen, time_beteween=time_beteween, timeout=timeout
        )

        if res is None:
            raise Exception(f'Timeout waiting for screen {PegaxyScreenEnum(pegaxyScreenEnum).name}.')

        return res

    @staticmethod
    def wait_for_leave_screen(
            pegaxyScreenEnum, time_beteween: float = 0.5, timeout: float = 60
    ):
        def check_screen():
            screen = PegaxyScreen.get_current_screen()
            if screen == pegaxyScreenEnum:
                return None
            else:
                return True

        return do_with_timeout(
            check_screen, time_beteween=time_beteween, timeout=timeout
        )

    @staticmethod
    def get_current_screen(time_beteween: float = 0.5, timeout: float = 20):
        templates = {
            "rent_button": Image.TARGETS["rent"],
            "market_button": Image.TARGETS["market"],
            "breed_button": Image.TARGETS["breed"],
            "myassets_button": Image.TARGETS["myassets"],
            "pickpega_button": Image.TARGETS["pick_a_pega"],
            "start_button": Image.TARGETS["start"],
            "stadiummetaverse_image": Image.TARGETS["stadion_metaverse"],
            "nextmatch_button": Image.TARGETS["next_match"],
            "matching_text": Image.TARGETS["matching"],
            "matchfound_text": Image.TARGETS["matchfound"],
            "outofenergy_text": Image.TARGETS["outofenergy"],
            "findanothermatch_button": Image.TARGETS["find_another"],
            "noavailablepegas_text": Image.TARGETS["noavailablepegas"],
            "sign_button": Image.TARGETS["sign"],
         }

        screens = {
            frozenset(["rent_button"]): PegaxyScreenEnum.RENT.value,
            frozenset(["market_button"]): PegaxyScreenEnum.MARKET.value,
            frozenset(["breed_button"]): PegaxyScreenEnum.BREED.value,
            frozenset(["myassets_button"]): PegaxyScreenEnum.MYASSETS.value,

            frozenset(["pickpega_button"]): PegaxyScreenEnum.ROOT.value,
            frozenset(["start_button"]): PegaxyScreenEnum.PICKPEGA.value,
            frozenset(["stadiummetaverse_image"]): PegaxyScreenEnum.RACE.value,
            frozenset(["nextmatch_button"]): PegaxyScreenEnum.FINISHED.value,
            frozenset(["matching_text"]): PegaxyScreenEnum.MATCHING.value,
            frozenset(["matchfound_text"]): PegaxyScreenEnum.MATCHFOUND.value,

            frozenset(["outofenergy_text", "start_button"]): PegaxyScreenEnum.OUTOFENERGY.value,
            frozenset(["findanothermatch_button"]): PegaxyScreenEnum.UNABLETOJOINRACE.value,
            frozenset(["noavailablepegas_text", "pickpega_button"]): PegaxyScreenEnum.NOAVAILABLEPEGAS.value,

            frozenset(["sign_button", "matchfound_text"]): PegaxyScreenEnum.METAMASK_SIGN.value,
            frozenset(["sign_button"]): PegaxyScreenEnum.METAMASK_SIGN.value,
        }

        img = Image.screen()

        listTemplate = list(templates.items())
        hits = matchTemplates(
            listTemplate,
            img,
            method = cv2.TM_CCOEFF_NORMED,
            N_object = 2,
            maxOverlap = 0,
            score_threshold = Config.get("threshold", "default"),
            )

        hits_set = frozenset(hits.iloc[:, 0].tolist())

        return screens.get(hits_set) if screens.get(hits_set) else -1

    @staticmethod
    def go_to_racing_root(manager, current_screen=None):
        current_screen = PegaxyScreen.get_current_screen() if current_screen is None else current_screen
        if current_screen == PegaxyScreenEnum.RENT.value or \
                current_screen == PegaxyScreenEnum.MARKET.value or \
                current_screen == PegaxyScreenEnum.BREED.value or \
                current_screen == PegaxyScreenEnum.MYASSETS.value:
            click_when_target_appears("racing_menu")
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_screen(PegaxyScreenEnum.ROOT.value, time_beteween=1)
            return True

    @staticmethod
    def go_to_racing_pick_pega(manager, current_screen=None):
        """This function goes to the pick_pega screen. WIP"""
        current_screen = PegaxyScreen.get_current_screen() if current_screen is None else current_screen
        result = True

        if current_screen == PegaxyScreenEnum.ROOT.value:
            click_when_target_appears("pick_a_pega")
        elif current_screen == PegaxyScreenEnum.FINISHED.value:
            click_when_target_appears('next_match')

        pyautogui.moveTo(10, 10)
        PegaxyScreen.wait_for_leave_screen(current_screen, time_beteween=1)
        result = PegaxyScreen.treat_error_no_available_pegas(manager)

        return result

    @staticmethod
    def prepare(manager, refresh=False, current_screen=None):
        if refresh:
            logger_translated("pegas energy", LoggerEnum.TIMER_REFRESH)
            refresh_page()
            sleep(10)

        current_screen = PegaxyScreen.get_current_screen() if current_screen is None else current_screen
        result = True
        if current_screen == PegaxyScreenEnum.RENT.value or \
                current_screen == PegaxyScreenEnum.MARKET.value or \
                current_screen == PegaxyScreenEnum.BREED.value or \
                current_screen == PegaxyScreenEnum.MYASSETS.value:
            PegaxyScreen.go_to_racing_root(manager, current_screen)
            result = PegaxyScreen.go_to_racing_pick_pega(manager)

        elif current_screen == PegaxyScreenEnum.ROOT.value or \
                current_screen == PegaxyScreenEnum.FINISHED.value:
            result = PegaxyScreen.go_to_racing_pick_pega(manager, current_screen)

        elif current_screen == PegaxyScreenEnum.RACE.value:
            result = False

        return result

    @staticmethod
    def race(manager, current_screen=None):
        current_screen = PegaxyScreen.get_current_screen() if current_screen is None else current_screen
        result = True
        if current_screen == PegaxyScreenEnum.PICKPEGA.value:  # Pick a Pega with enough energy
            manager.set_attr("race_requested", 0)
            pega = PegaxyScreen.select_pega(manager)
            if pega:
                manager.set_attr("race_requested", 1)
                result = PegaxyScreen.confirm_race(manager)
            else:
                logger_translated("skip and set long timer (horses have 0 energy)", LoggerEnum.TIMER_REFRESH)
                manager.set_refresh_timer("refresh_long_time")
                result = False

        return result

    @staticmethod
    def confirm_race(manager, current_screen=None, n=0):
        if n == 180:
            refresh_page(manager)
            return False

        current_screen = PegaxyScreen.get_current_screen() if current_screen is None else current_screen
        result = None
        if current_screen == PegaxyScreenEnum.RACE.value:  # Race confirmed.
            result = True

        elif current_screen == PegaxyScreenEnum.MATCHING.value or \
                current_screen == PegaxyScreenEnum.MATCHFOUND.value:  # Wait a little bit more
            sleep(1)
            PegaxyScreen.confirm_race(manager, n=n + 1)

        elif current_screen == PegaxyScreenEnum.UNABLETOJOINRACE.value:  # Deal with Racing Match Errors
            click_when_target_appears('find_another')
            pyautogui.moveTo(10, 10)
            manager.set_attr("race_requested", 1)
            PegaxyScreen.wait_for_leave_screen(current_screen, time_beteween=1)
            PegaxyScreen.confirm_race(manager, n=n + 1)

        elif current_screen == PegaxyScreenEnum.METAMASK_SIGN.value:
            signed = Metamask.sign_race(manager)
            if signed:
                manager.set_attr("race_requested", 0)
                PegaxyScreen.confirm_race(manager, n=n + 1)

        else:
            PegaxyScreen.confirm_race(manager, n=n + 1)

        return result

    @staticmethod
    def treat_error_no_available_pegas(manager):
        """Returns True if the error was treated
           Returns False if you shoud leave the manager"""
        current_screen = PegaxyScreen.get_current_screen()

        if current_screen == PegaxyScreenEnum.NOAVAILABLEPEGAS.value:
            logger_translated("skip and set long timer (no available pegas)", LoggerEnum.TIMER_REFRESH)
            manager.set_refresh_timer("refresh_long_time")
            return False
        else:
            return True

    @staticmethod
    def select_pega(manager):
        """This function selects a pega available to select_pega.
        Returns True if there is one.
        Returns False if all pegas are out of energy"""
        pos = Image.get_target_positions('horse_active')
        # pos2(Image.get_target_positions('horse_inactive'))
        sorted(pos, key=lambda l: l[1])

        order_config = Config.get('screen', 'order')
        return PegaxyScreen._select_pega(manager, pos, order=order_config)

    @staticmethod
    def _select_pega(manager, positions, order, n=0):
        if n == len(positions):
            return False

        if order:
            pos = len(positions) - n - 1
        else:
            pos = n

        click_randomly_in_position(*positions[pos])
        click_when_target_appears('start')
        pyautogui.moveTo(10, 10)
        PegaxyScreen.wait_for_leave_screen(PegaxyScreenEnum.PICKPEGA.value, time_beteween=1)

        current_screen = PegaxyScreen.get_current_screen()
        if current_screen == PegaxyScreenEnum.OUTOFENERGY.value:
            click_when_target_appears('Iunderstand')
            pyautogui.moveTo(10, 10)
            manager.set_attr("race_request", 0)
            PegaxyScreen.wait_for_leave_screen(current_screen, time_beteween=1)
            if PegaxyScreen._select_pega(manager, positions, order=order, n=n + 1) is False:
                return False

        manager.set_attr("race_requested", 1)
        return True

    @staticmethod
    def do_check_error(manager):
        current_screen = PegaxyScreen.get_current_screen()
        if current_screen == PegaxyScreenEnum.NOT_FOUND.value:
            logger_translated("Check screen error found, restarting...", LoggerEnum.ERROR)
            refresh_page(manager)
            sleep(20)
            return


class Metamask:
    @staticmethod
    def sign_race(manager):
        # Se o sinal "race_requested" estiver ligado:
        #   Assinar a metamask
        # Senao:
        #   Clicar em cancelar
        #   Desligar o sinal "race_requested"
        # recursivar try_to_race()
        if manager.race_requested == 1:
            logger_translated("Metamask sign", LoggerEnum.BUTTON_CLICK)
            click_when_target_appears('sign')
            manager.set_attr("race_requested", 0)
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_leave_screen(PegaxyScreenEnum.METAMASK_SIGN.value, time_beteween=1)
            return True
        return False
