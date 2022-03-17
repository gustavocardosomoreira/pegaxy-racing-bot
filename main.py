import sys
import traceback
from time import sleep

from packaging import version

from module.pegaxyScreen import PegaxyScreen, PegaxyScreenEnum
from module.config import Config
from module.image import Image
from module.logger import logger, reset_log_file
from module.manager import create_pegaxy_managers


__version__ = "0.0.3"


def main(config_file):
    try:
        # Load configs
        Config.load_config(config_file)
        Image.load_targets()

        if Config.get("generals", "reset_log_file"):
            reset_log_file()

        pegaxy_managers = create_pegaxy_managers()
        logger(f"{len(pegaxy_managers)} Pegaxy window (s) found")
        pegaxy_browser_count = 1
        show_initial_screen_message = True
        while True:
            try:
                for manager in pegaxy_managers:
                    current_screen = PegaxyScreen.get_current_screen()

                    if show_initial_screen_message:
                        logger(f"💫 Pegaxy window[{pegaxy_browser_count}] inicializado em: {PegaxyScreenEnum(current_screen).name}")

                    with manager:
                        manager.do_what_needs_to_be_done(current_screen)

                    if pegaxy_browser_count == len(pegaxy_managers):
                        pegaxy_browser_count = 1
                        show_initial_screen_message = False
                    else:
                        pegaxy_browser_count += 1
            except Exception as e:
                logger(
                    traceback.format_exc(),
                    color="red",
                    force_log_file=True,
                    terminal=False,
                )
                logger(
                    f"😬 Ohh no! A error has occurred in the last action.\n{e}\n Check the log  file for more details.",
                    color="yellow",
                )
            sleep(5)
    except Exception:
        logger(traceback.format_exc(), color="red", force_log_file=True, terminal=True)
        logger("😬 Ohh no! We couldn't start the bot.", color="red")


if __name__ == "__main__":
    config_path = "config.yaml"

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        config_path = f"config_profiles/{config_file}.yaml"

    main(config_path)
