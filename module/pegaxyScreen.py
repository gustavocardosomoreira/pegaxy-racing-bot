from enum import Enum
from time import sleep

from cv2 import cv2

from .mouse import *
from .utils import *


class PegaxyScreenEnum(Enum):
    NOT_FOUND = -1
    RACING_OUT_OF_ENERGY_ERROR = 1
    RACING_UNABLE_TO_JOIN_RACE_ERROR = 2
    RACING_NO_AVAILABLE_PEGAS = 3
    RENTING = 4
    MARKETPLACE = 5
    BREEDING = 6
    MY_ASSETS = 7
    RACING_ROOT = 8
    RACING_PICK_PEGA = 9
    RACING_RACE = 10
    RACING_FINISHED = 11
    RACING_MATCHING = 12
    RACING_MATCH_FOUND = 13  # No Metamask in sight
    # RACING_CALCULATING_REWARDS = 14

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
        targets = {
            PegaxyScreenEnum.RENTING.value: Image.TARGETS["identify_renting"],
            PegaxyScreenEnum.MARKETPLACE.value: Image.TARGETS["identify_marketplace"],
            PegaxyScreenEnum.BREEDING.value: Image.TARGETS["identify_breeding"],
            PegaxyScreenEnum.MY_ASSETS.value: Image.TARGETS["identify_my_assets"],
            PegaxyScreenEnum.RACING_ROOT.value: Image.TARGETS["identify_racing_root"],
            PegaxyScreenEnum.RACING_PICK_PEGA.value: Image.TARGETS["identify_racing_pick_pega"],
            PegaxyScreenEnum.RACING_MATCHING.value: Image.TARGETS["identify_racing_matching"],
            PegaxyScreenEnum.RACING_MATCH_FOUND.value: Image.TARGETS["identify_racing_match_found"],
            PegaxyScreenEnum.RACING_RACE.value: Image.TARGETS["identify_racing_race"],
            PegaxyScreenEnum.RACING_FINISHED.value: Image.TARGETS["identify_racing_finished"],
            PegaxyScreenEnum.RACING_OUT_OF_ENERGY_ERROR.value: Image.TARGETS["identify_racing_out_of_energy_error"],
            PegaxyScreenEnum.RACING_UNABLE_TO_JOIN_RACE_ERROR.value: Image.TARGETS[
                "identify_racing_unable_to_join_race_error"],
            # PegaxyScreenEnum.RACING_CALCULATING_REWARDS.value: Image.TARGETS["racing_calculating_rewards"],
            PegaxyScreenEnum.METAMASK_SIGN.value: Image.TARGETS["sign"],
            PegaxyScreenEnum.RACING_NO_AVAILABLE_PEGAS.value: Image.TARGETS["identify_racing_no_available_pegas"],
        }
        max_value = 0
        img = Image.screen()
        screen_name = -1

        for name, target_img in targets.items():
            result = cv2.matchTemplate(img, target_img, cv2.TM_CCOEFF_NORMED)
            max_value_local = result.max()
            if max_value_local > max_value:
                max_value = max_value_local
                screen_name = name

        return screen_name if max_value > Config.get("threshold", "default") else -1

    @staticmethod
    def go_to_racing_root(manager, current_screen=None):
        """This function goes to the racing_start screen.
        Making sure not to interrupt running races.
        WIP"""
        current_screen = PegaxyScreen.get_current_screen() if current_screen == None else current_screen
        if current_screen == PegaxyScreenEnum.RACING_ROOT.value:
            return
        elif current_screen == PegaxyScreenEnum.RENTING.value or \
                current_screen == PegaxyScreenEnum.MARKETPLACE.value or \
                current_screen == PegaxyScreenEnum.BREEDING.value or \
                current_screen == PegaxyScreenEnum.MY_ASSETS.value:
            click_when_target_appears("racing_menu")
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_screen(PegaxyScreenEnum.RACING_ROOT.value)
        else:
            # Missing future implementation
            return

    @staticmethod
    def go_to_racing_pick_pega(manager, current_screen=None):
        """This function goes to the pick_pega screen
        Making sure not to interrupt running races.
        WIP"""
        current_screen = PegaxyScreen.get_current_screen() if current_screen == None else current_screen
        if current_screen == PegaxyScreenEnum.RACING_PICK_PEGA.value:
            return
        elif current_screen == PegaxyScreenEnum.RACING_ROOT.value:
            click_when_target_appears("pick_a_pega")
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_screen(PegaxyScreenEnum.RACING_PICK_PEGA.value)
            return
        elif current_screen == PegaxyScreenEnum.RENTING.value or \
                current_screen == PegaxyScreenEnum.MARKETPLACE.value or \
                current_screen == PegaxyScreenEnum.BREEDING.value or \
                current_screen == PegaxyScreenEnum.MY_ASSETS.value:
            PegaxyScreen.go_to_racing_root(manager, current_screen)
            PegaxyScreen.go_to_racing_pick_pega(manager)
            return
        else:
            # Missing future implementation
            return

    @staticmethod
    def race(manager):
        """This function selects a pega available to race.
        Returns True if there is one.
        Returns False if all pegas are out of energy"""
        pos = Image.get_target_positions('horse_active')
        # pos2(Image.get_target_positions('horse_inactive'))
        sorted(pos, key=lambda l: l[1])

        return PegaxyScreen._race(manager, pos)

    @staticmethod
    def _race(manager, positions, n=0):
        if n == len(positions):
            return False

        click_randomly_in_position(*positions[n])
        click_when_target_appears('start')
        pyautogui.moveTo(10, 10)
        PegaxyScreen.wait_for_leave_screen(PegaxyScreenEnum.RACING_PICK_PEGA.value)
        sleep(1)
        current_screen = PegaxyScreen.get_current_screen()
        if current_screen == PegaxyScreenEnum.RACING_OUT_OF_ENERGY_ERROR.value:
            click_when_target_appears('out_of_energy_error')
            sleep(1)
            manager.race_requested = 0

            if not PegaxyScreen._race(manager, positions, n=n + 1):
                return False

        manager.race_requested = 1
        return True

    @staticmethod
    def do_check_error(manager):
        return

    @staticmethod
    def try_to_race(manager):
        current_screen = PegaxyScreen.get_current_screen()

        if current_screen == PegaxyScreenEnum.RACING_PICK_PEGA.value:
            manager.race_requested = 0
            if PegaxyScreen.race(manager):
                manager.refresh_long_time = 0
                PegaxyScreen.try_to_race(manager)
            else:
                manager.refresh_long_time = now()
                return

        elif current_screen == PegaxyScreenEnum.RACING_RACE.value:
            return

        elif current_screen == PegaxyScreenEnum.RACING_UNABLE_TO_JOIN_RACE_ERROR.value:
            click_when_target_appears('find_another')
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_leave_screen(current_screen)
            manager.race_requested = 1
            sleep(3)
            PegaxyScreen.try_to_race(manager)

        elif current_screen == PegaxyScreenEnum.RACING_FINISHED.value:
            # This returns to the pick a pega screen
            click_when_target_appears('next_match')
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_leave_screen(current_screen)
            manager.race_requested = 1
            sleep(3)
            PegaxyScreen.try_to_race(manager)

        elif current_screen == PegaxyScreenEnum.RENTING.value or \
                current_screen == PegaxyScreenEnum.MARKETPLACE.value or \
                current_screen == PegaxyScreenEnum.BREEDING.value or \
                current_screen == PegaxyScreenEnum.MY_ASSETS.value or \
                current_screen == PegaxyScreenEnum.RACING_ROOT.value:
            manager.race_requested = 0
            PegaxyScreen.go_to_racing_pick_pega(manager, current_screen)
            PegaxyScreen.try_to_race(manager)

        elif current_screen == PegaxyScreenEnum.RACING_NO_AVAILABLE_PEGAS.value:
            manager.refresh_long_time = now()
            manager.race_requested = 0
            return

        elif current_screen == PegaxyScreenEnum.RACING_MATCHING.value or \
                current_screen == PegaxyScreenEnum.RACING_MATCH_FOUND.value:
            PegaxyScreen.try_to_race(manager)

        elif current_screen == PegaxyScreenEnum.METAMASK_SIGN.value:
            # Se o sinal "race_requested" estiver ligado:
            #   Assinar a metamask
            # Senao:
            #   Clicar em cancelar
            #   Desligar o sinal "race_requested"
            # recursivar try_to_race()
            if manager.race_requested == 1:
                click_when_target_appears('sign')
                manager.race_requested = 0
                pyautogui.moveTo(10, 10)
            PegaxyScreen.try_to_race(manager)

        else:
            PegaxyScreen.try_to_race(manager)

# class Pega:
# Future class, there is some future use here though I can't think of any right now.
# Use no1: Store energy of pegas to reduce windows switches.
# Use no2: Record pega return times to try to _race more in the end.


# class PegaxyScreen:
#     def get_current_screen(time_beteween: float = 0.5, timeout: float = 20):
#         targets = {
#             PegaxyScreenEnum.RENTING.value:
#                 [ ("2d_renting", Image.TARGETS_RGB["2d_renting"]) ],
#             PegaxyScreenEnum.MARKETPLACE.value:
#                 [ ("2d_marketplace", Image.TARGETS_RGB["2d_marketplace"]) ],
#             PegaxyScreenEnum.BREEDING.value:
#                 [ ("2d_breeding", Image.TARGETS_RGB["2d_breeding"]) ],
#             PegaxyScreenEnum.MY_ASSETS.value:
#                 [ ("2d_my_assets", Image.TARGETS_RGB["2d_my_assets"]) ],
#
#             PegaxyScreenEnum.RACING_START.value:
#                 [ ("2d_racing_start", Image.TARGETS_RGB["2d_racing_start"]) ],
#             PegaxyScreenEnum.RACING_PICK_PEGA.value:
#                 [ ("2d_identify_racing_pick_pega", Image.TARGETS_RGB["2d_identify_racing_pick_pega"]) ],
#             PegaxyScreenEnum.RACING_RACE.value:
#                 [ ("2d_identify_racing_race", Image.TARGETS_RGB["2d_identify_racing_race"]) ],
#             PegaxyScreenEnum.RACING_FINISHED.value:
#                 [ ("2d_identify_racing_finished", Image.TARGETS_RGB["2d_identify_racing_finished"]) ],
#
#             # PegaxyScreenEnum.RACING_OUT_OF_ENERGY_ERROR.value: Image.TARGETS["2d_identify_racing_"],
#
#             PegaxyScreenEnum.RACING_UNABLE_TO_JOIN_RACE_ERROR.value:
#                 [ ("2d_identify_racing_unable_to_join_race_error", Image.TARGETS_RGB["2d_identify_racing_unable_to_join_race_error"]) ],
#             PegaxyScreenEnum.METAMASK_SIGN.value:
#                 [ ("2d_identify_metamask_sign", Image.TARGETS_RGB["2d_identify_metamask_sign"]) ],
#
#             # PegaxyScreenEnum.RACING_MATCHING.value: Image.TARGETS["2d_identify_racing_matching"],
#             # PegaxyScreenEnum.RACING_MATCH_FOUND.value: Image.TARGETS["2d_identify_racing_match_found"],
#             # PegaxyScreenEnum.RACING_CALCULATING_REWARDS.value: Image.TARGETS["2d_identify_racing_calculating_rewards"],
#         }
#         max_value = 0
#         img = Image.screen()
#         screen_name = -1
#
#         listTemplate = Image.TARGETS_RGB
#
#         # key = PegaxyScreenEnum.RENTING.value
#         # listTemplate = [(key, targets.get(key))]
#
#         Hits = matchTemṕlates(
#             listTemplate,
#             img,
#             method = cv2.TM_CCOEFF_NORMED,
#             N_object = 2,
#             maxOverlap = 0,
#             score_threshold = Config.get("threshold", "default"),
#             )
#
#         pd.
#
#         screen_name = key
#
#         return screen_name
