import sys
import traceback
from time import sleep

from packaging import version

from module.pegaxyScreen import PegaxyScreen, PegaxyScreenEnum
from module.config import Config
from module.image import Image
from module.logger import logger, reset_log_file
from module.manager import create_pegaxy_managers


__version__ = "0.0.1"


def main(config_file):
    # Load configs
    Config.load_config(config_file)
    Image.load_targets()

    pegaxy_managers = create_pegaxy_managers()
    logger(f"{len(pegaxy_managers)} Pegaxy window (s) found")
    pegaxy_browser_count = 1
    show_initial_screen_message = True

    mode = input('Type in the wished test: [R]ead screen|[O]ne target|[N]o of targets|[T]este reconhecimento '
                 'multicavalos: ')
    while True:
        for manager in pegaxy_managers:
            if mode == 'R':
                current_screen = PegaxyScreen.get_current_screen()
                print(PegaxyScreenEnum(current_screen).name)
                sleep(5)
            elif mode == 'O':
                target = input('Type in target name (single mode):')
                if target in Image.TARGETS:
                    try:
                        if Image.get_one_target_position(target):
                            print('1 found')
                    except:
                        print('Not found.')
                else:
                    print('Target is not in the database')
            elif mode == 'N':
                target = input('Type in target name (multiple mode):')
                if target in Image.TARGETS:
                    print(len(Image.get_target_positions(target)), 'found.')
                else:
                    print('Target is not in the database.')
            elif mode == 'T':
                input('Entre na tela de seleção dos cavalos para corrida e pressione enter')
                PegaxyScreen.teste_multicavalos(manager)
            else:
                print('Unreconized mode, exiting.')
                break



if __name__ == "__main__":
    config_path = "config.yaml"

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        config_path = f"config_profiles/{config_file}.yaml"

    main(config_path)
