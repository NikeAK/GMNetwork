import os
import inquirer

from pyfiglet import figlet_format
from core.utils import FileManager, logger
from data.config import USE_PROXY

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.root import Core


def continue_dec(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        input("\nPress [ENTER] to continue...")
        self.clear_console()
        self.show_logo()
        self.show_main_menu()
    return wrapper

class CLInterface:
    def __init__(self, core: 'Core') -> None:
        self.__core = core
    
    @staticmethod
    def clear_console():
        return os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def show_logo():
        logo = figlet_format('GMNetwork', font='slant')
        print(f'\033[92m{logo}\033[0m')
        print("| 👦 Software Author: IKEK2K \n| ✈️  Telegram: https://t.me/oxcode1")
    
    def show_main_menu(self):

        menu = [
            inquirer.List('menu_item',
                message='Main Menu',
                choices=[
                    'Launch',
                    'Generate Wallets',
                    'Exit'
                ]
            )
        ]

        answer = (inquirer.prompt(menu)['menu_item']).lower().split()

        self.clear_console()

        getattr(self, f'_selected_{answer[0]}_{answer[1]}' if len(answer) == 2 else f'_selected_{answer[0]}')()
    
    @continue_dec
    def _selected_launch(self):
        logo = figlet_format('Launch', font='standard')
        print(f'\033[96m{logo[:-1]}\033[0m')

        accounts = len(FileManager.read_file('data/private_keys.txt'))
        proxy = len(FileManager.read_file('data/proxy.txt'))
        
        logger.info(f'📥  Аккаунтов загружено - [{accounts}]\n')

        if USE_PROXY:
            if proxy == 0:
                logger.error(f'Проверьте файл с прокси! Прокси не найдено!')
                return
            else:
                logger.info(f'📥  Загружено proxy - [{proxy}]')

        while True:
            try:
                enter_thread = [
                    inquirer.Text('thread',
                        message="👉 Введите кол-во потоков"
                    )
                ]

                threads = int(inquirer.prompt(enter_thread)['thread'])
                print("")
                if threads > 0:
                    break
                else:
                    logger.info("❌  Пожалуйста введите положительное число.\n")
            except ValueError:
                logger.info("❌  Пожалуйста введите цифру.\n")

        self.__core.task_setup_launch(threads)

    @continue_dec
    def _selected_generate_wallets(self):
        logo = figlet_format('GenWallets', font='standard')
        print(f'\033[96m{logo}\033[0m')

        while True:
            try:
                enter_count = [
                    inquirer.Text('count',
                        message="👉 Введите кол-во аккаунтов"
                    )
                ]

                count = int(inquirer.prompt(enter_count)['count'])
                print("")
                if count > 0:
                    break
                else:
                    logger.info("❌  Пожалуйста введите положительное число.\n")
            except ValueError:
                logger.info("❌  Пожалуйста введите цифру.\n")

        self.__core.task_setup_generate(1, count)

    def _selected_exit(self):
        return exit()

