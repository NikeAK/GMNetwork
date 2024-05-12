import asyncio
import platform

from core.cli import CLInterface
from core.task_mgr import TaskManager
from core.utils import logger

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def async_start(func):
    def wrapper(self, *args, **kwargs):
        try:
            asyncio.run(func(self, *args, **kwargs))
        except KeyboardInterrupt:
            logger.critical("Прервано пользователем")
    return wrapper


class Core:
    def __init__(self) -> None:
        self.__cli = CLInterface(self)

    def initialization(self):
        self.__cli.clear_console()
        self.__cli.show_logo()
        self.__cli.show_main_menu()

    @staticmethod
    async def setup_task(threads: int, task_type: str, *args):
        logger.info(f'♻️  Генерирую потоки - [{threads}]\n')
        task_manager = TaskManager()

        tasks = []
        for thread in range(1, threads+1):
            task_func = getattr(task_manager, task_type)
            tasks.append(asyncio.create_task(task_func(thread, *args)))
        
        res = await asyncio.gather(*tasks)

        messages = {
            'nokeys': "Список приватных ключей отбработан",
            'noaccounts': "Список аккаунтов БД отбработан"
        }

        for flag, message in messages.items():
            if flag in res:
                logger.info(f"Все потоки завершены | {message}")
                break
                
    @async_start
    def task_setup_launch(self, threads: int, *args):
        return Core.setup_task(threads, 'launch', *args)
    
    @async_start
    def task_setup_generate(self, threads: int, *args):
        return Core.setup_task(threads, 'generate_wallets', *args)

    @async_start
    def task_setup_export(self, threads: int, *args):
        return Core.setup_task(threads, 'export_info', *args)

