from enum import Enum
from time import sleep

from cv2 import cv2

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
        targets = {
            PegaxyScreenEnum.RENT.value: Image.TARGETS["identify_rent"],
            PegaxyScreenEnum.MARKET.value: Image.TARGETS["identify_market"],
            PegaxyScreenEnum.BREED.value: Image.TARGETS["identify_breed"],
            PegaxyScreenEnum.MYASSETS.value: Image.TARGETS["identify_myassets"],

            PegaxyScreenEnum.ROOT.value: Image.TARGETS["identify_root"],
            PegaxyScreenEnum.PICKPEGA.value: Image.TARGETS["identify_pickpega"],
            PegaxyScreenEnum.RACE.value: Image.TARGETS["identify_race"],
            PegaxyScreenEnum.FINISHED.value: Image.TARGETS["identify_finished"],
            PegaxyScreenEnum.MATCHING.value: Image.TARGETS["identify_matching"],
            PegaxyScreenEnum.MATCHFOUND.value: Image.TARGETS["identify_matchfound"],

            PegaxyScreenEnum.OUTOFENERGY.value: Image.TARGETS["identify_outofenergy"],
            PegaxyScreenEnum.UNABLETOJOINRACE.value: Image.TARGETS["identify_unabletojoinrace"],
            # PegaxyScreenEnum.RACING_CALCULATING_REWARDS.value: Image.TARGETS["racing_calculating_rewards"],
            PegaxyScreenEnum.NOAVAILABLEPEGAS.value: Image.TARGETS["identify_noavailablepegas"],

            PegaxyScreenEnum.METAMASK_SIGN.value: Image.TARGETS["sign"],
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
        current_screen = PegaxyScreen.get_current_screen() if current_screen is None else current_screen
        if current_screen == PegaxyScreenEnum.RENT.value or \
                current_screen == PegaxyScreenEnum.MARKET.value or \
                current_screen == PegaxyScreenEnum.BREED.value or \
                current_screen == PegaxyScreenEnum.MYASSETS.value:
            click_when_target_appears("racing_menu")
            pyautogui.moveTo(10, 10)
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
        result = PegaxyScreen.treat_error_no_available_pegas(manager)

        return result

    @staticmethod
    def prepare(manager, current_screen=None):
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
                manager.set_refresh_timer("refresh_long_time")
                result = False

        return result

    @staticmethod
    def confirm_race(manager, current_screen=None, n=0):
        if n == 240:
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
            PegaxyScreen.confirm_race(manager, n=n + 1)

        elif current_screen == PegaxyScreenEnum.METAMASK_SIGN.value:
            signed = Metamask.sign_race(manager)
            if signed:
                manager.set_attr("race_requested", 0)
                PegaxyScreen.confirm_race(manager, n=n + 1)

        return result

    @staticmethod
    def treat_error_no_available_pegas(manager):
        """Returns True if the error was treated
           Returns False if you shoud leave the manager"""
        current_screen = PegaxyScreen.get_current_screen()

        if current_screen == PegaxyScreenEnum.NOAVAILABLEPEGAS.value:
            logger_translated("Long timer", LoggerEnum.TIMER_REFRESH)
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

        return PegaxyScreen._select_pega(manager, pos)

    @staticmethod
    def _select_pega(manager, positions, reverse=True, n=0):
        if n == len(positions):
            return None

        if reverse:
            pos = len(positions) - n - 1
        else:
            pos = n

        click_randomly_in_position(*positions[pos])
        click_when_target_appears('start')
        pyautogui.moveTo(10, 10)

        current_screen = PegaxyScreen.get_current_screen()
        if current_screen == PegaxyScreenEnum.OUTOFENERGY.value:
            click_when_target_appears('out_of_energy_error')
            pyautogui.moveTo(10, 10)
            manager.set_attr("race_request", 0)
            if PegaxyScreen._select_pega(manager, positions, reverse=reverse, n=n + 1) is None:
                return None

        manager.set_attr("race_requested", 1)
        return True

    @staticmethod
    def do_check_error(manager):
        current_screen = PegaxyScreen.get_current_screen()
        if current_screen == PegaxyScreenEnum.NOT_FOUND.value or \
                current_screen == PegaxyScreenEnum.UNABLETOJOINRACE.value or \
                current_screen == PegaxyScreenEnum.NOAVAILABLEPEGAS.value:
            refresh_page(manager)
            sleep(5)
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
            click_when_target_appears('sign')
            manager.set_attr("race_requested", 0)
            pyautogui.moveTo(10, 10)
            PegaxyScreen.wait_for_leave_screen(PegaxyScreenEnum.METAMASK_SIGN.value)
            return True
        return False

    # @staticmethod
    # def try_to_race(manager, current_screen=None):
    #     """ This function contains the main logic of the bot.
    #     Returns False: If it has to perform more steps to start a select_pega.
    #     Returns True: If all steps to start a select_pega have been performed,
    #                   Or if no other actions can be taken in this manager."""
    #     current_screen = PegaxyScreen.get_current_screen() if current_screen == None else current_screen
    #
    #     ## Possible screens that start a select_pega ###############3 Create a funct called select_pega for this
    #     # Pick a Pega with enough energy
    #     if current_screen == PegaxyScreenEnum.PICKPEGA.value:
    #         manager.race_requested = 0
    #         if PegaxyScreen.select_pega(manager):
    #             manager.refresh_long_time = 0
    #             return None
    #         else:
    #             manager.refresh_long_time = now()
    #             return True
    #
    #     # Deal with Racing Match Errors ###################### Create a funct called select_pega for this
    #     elif current_screen == PegaxyScreenEnum.UNABLETOJOINRACE.value:
    #         click_when_target_appears('find_another')
    #         pyautogui.moveTo(10, 10)
    #         PegaxyScreen.wait_for_screen(PegaxyScreenEnum.MATCHING.value)
    #         manager.race_requested = 1
    #         return PegaxyScreen.try_to_race(manager, PegaxyScreenEnum.MATCHING.value)
    #
    #     ## Helper screens to start a select_pega #################33 Create a funct called try again for this
    #     # Race finished. Start new select_pega.
    #     elif current_screen == PegaxyScreenEnum.FINISHED.value:
    #         # This returns to the pick a pega screen
    #         click_when_target_appears('next_match')
    #         pyautogui.moveTo(10, 10)
    #         PegaxyScreen.wait_for_screen(PegaxyScreenEnum.PICKPEGA.value)
    #         manager.race_requested = 1
    #         return PegaxyScreen.try_to_race(manager, PegaxyScreenEnum.PICKPEGA.value)
    #
    #     ## Screens that confirm a select_pega is underway
    #     # Race confirmed. Go to the next manager
    #     elif current_screen == PegaxyScreenEnum.RACE.value:
    #         return True
    #
    #     ## Helper screen to get back to the racing module ##### Create a funct called prepare for this
    #     # Out of the racing module. Go to the right module.
    #     elif current_screen == PegaxyScreenEnum.RENT.value or \
    #             current_screen == PegaxyScreenEnum.MARKET.value or \
    #             current_screen == PegaxyScreenEnum.BREED.value or \
    #             current_screen == PegaxyScreenEnum.MYASSETS.value or \
    #             current_screen == PegaxyScreenEnum.ROOT.value:
    #         manager.race_requested = 0
    #         PegaxyScreen.go_to_racing_pick_pega(manager, current_screen)
    #         return None
    #
    #     ## Error screen that is impossible to overcome
    #     elif current_screen == PegaxyScreenEnum.NOAVAILABLEPEGAS.value:
    #         manager.refresh_long_time = now()
    #         manager.race_requested = 0
    #         return True
    #
    #     ## Screens that will be waiting for metamask sign soon
    #     elif current_screen == PegaxyScreenEnum.MATCHING.value or \
    #             current_screen == PegaxyScreenEnum.MATCHFOUND.value:
    #         sleep(3)
    #         return None
    #
    #     ## Metamask sign screen
    #     elif current_screen == PegaxyScreenEnum.METAMASK_SIGN.value:
    #         return PegaxyScreen.sign_mask(manager)
    #
    #     return True

# class Pega:
# Future class, there is some future use here though I can't think of any right now.
# Use no1: Store energy of pegas to reduce windows switches.
# Use no2: Record pega return times to try to _select_pega more in the end.


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
