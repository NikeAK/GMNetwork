import asyncio
import eth_account
import pandas
import time

from tqdm import tqdm
from better_proxy import Proxy
from core.gmnetwork import GMNetwork
from core.utils import FileManager, logger, check_proxy

from core.database.database import MainDB
from core.database.models import Accounts

from data.config import (
    USE_PROXY, LOGGER_PROXY, 
    EXPORT_DATA, EXPORT_SEPARATOR, 
    PROXY_CHEKER_TIMEOUT, REFERRAL_CODE
)


class TaskManager:
    def __init__(self) -> None:
        self.private_keys = FileManager.read_file('data/private_keys.txt')
        self.proxies = FileManager.read_file('data/proxy.txt')

        self.__db = MainDB()
        self.accounts_db = self.__db.get_accounts()

        self.lock = asyncio.Lock()
        self.counter = 0
    
    async def get_proxy(self, thread: int) -> str:
        while True:
            async with self.lock:
                pop_proxy: str = self.proxies[self.counter % len(self.proxies)]
                self.counter += 1
            proxy = Proxy.from_str(pop_proxy if pop_proxy.startswith('http://') else 'http://' + pop_proxy).as_url
            
            if not await check_proxy(proxy, PROXY_CHEKER_TIMEOUT):
                if LOGGER_PROXY:
                    logger.error(f"Поток {thread} | <r>BadProxy</r> {pop_proxy}")
                continue
            else:
                if LOGGER_PROXY:
                    logger.success(f"Поток {thread} | <g>GoodProxy</g> {pop_proxy}")
                return proxy, pop_proxy
    
    async def launch(self, thread: int, storage: str) -> None:
        while True:
            if storage == 'Launch DataBase':
                async with self.lock:
                    if not self.accounts_db:
                        return 'noaccounts'
                    account: Accounts = self.accounts_db.pop(0)
                
                result = await GMNetwork(thread, account).quick_start(REFERRAL_CODE)
                self.__db.update_account(account.privatekey, result)

                logger.info(f"Поток {thread} | Завершил работу с аккаунтом - PrivateKey: {account.privatekey}")
            else:
                async with self.lock:
                    if not self.private_keys:
                        return 'nokeys'
                    else:
                        private_key = self.private_keys.pop(0)

                account = self.__db.get_account_by_pv(private_key)

                if account is None:
                    proxy, t_proxy = await self.get_proxy(thread) if USE_PROXY else None

                    account = Accounts(
                        address = eth_account.Account.from_key(private_key).address,
                        privatekey=private_key,
                        proxy=proxy
                    )

                    self.__db.add_account(account)
                    
                    async with self.lock:
                        FileManager.delete_str_file('data/private_keys.txt', private_key)
                        FileManager.delete_str_file('data/proxy.txt', t_proxy)
                else:
                    logger.warning(f'Поток {thread} | Аккаунт найден в БД! Задания будут выполнены повторно.')

                result = await GMNetwork(thread, account).quick_start(REFERRAL_CODE)
                self.__db.update_account(account.privatekey, result)

                logger.info(f"Поток {thread} | Завершил работу с аккаунтом - PrivateKey: {account.privatekey}")
    
    async def generate_wallets(self, thread: int, count: int) -> None:
        with tqdm(total=count) as pbar:
            for _ in range(count):
                acct = eth_account.Account.create()
                data = acct.key.hex()
                FileManager.save_str_file('data/generate/wallets.txt', data)
                pbar.update(1)
        logger.success(f"Успешно сгенерировано <g>{count}</g> кошельков, сохранил по пути -> <c>data/generate/wallets.txt</c>")
    
    async def export_info(self, thread: int, extension: str):
        accounts = self.__db.get_accounts()
        export_list = EXPORT_DATA.replace(" ","").split(",")

        if extension == 'txt':
            data = ''
            for account in accounts:
                for export in export_list:
                    if export == 'checkin':
                        data += ('✅' if 86400 - (int(time.time()) - getattr(account, export)) > 0 else '❌') + EXPORT_SEPARATOR
                    else:
                        data += str(getattr(account, export)) + EXPORT_SEPARATOR
                data = data[:-len(EXPORT_SEPARATOR)] + '\n'
                logger.info(f"Аккаунт <g>{account.privatekey}</g> экспортирован!")
            FileManager.save_data('data/export/wallets.txt', data)
            logger.success(f"Успешно экспортировано <g>{len(accounts)}</g> кошельков, сохранил по пути -> <c>data/export/wallets.txt</c>")
        else:
            df = pandas.DataFrame(columns=[export.capitalize() for export in export_list])
            for account in accounts:
                row_data = []
                for export in export_list:
                    if export == 'checkin':
                        status = '✅' if 86400 - (int(time.time()) - getattr(account, export)) > 0 else '❌'
                        row_data.append(status)
                    else:
                        row_data.append(str(getattr(account, export)))
                df.loc[len(df)] = row_data
                logger.info(f"Аккаунт <g>{account.privatekey}</g> экспортирован!")
            excel_file_path = 'data/export/wallets.xlsx'
            df.to_excel(excel_file_path, index=False) 
            logger.success(f"Успешно экспортировано <g>{len(accounts)}</g> кошельков, сохранил по пути -> <c>data/export/wallets.xlsx</c>")

