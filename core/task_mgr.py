import asyncio
import eth_account

from tqdm import tqdm
from better_proxy import Proxy
from core.gmnetwork import GMNetwork
from core.utils import FileManager, logger, check_proxy

from data.config import USE_PROXY, LOGGER_PROXY, REFERRAL_CODE


class TaskManager:
    def __init__(self) -> None:
        self.private_keys = FileManager.read_file('data/private_keys.txt')
        self.proxies = FileManager.read_file('data/proxy.txt')

        self.lock = asyncio.Lock()
    
    async def launch(self, thread: int):
        while True:
            async with self.lock:
                if not self.private_keys:
                    return 'nokeys'
                
                private_key = self.private_keys.pop(0)

            if USE_PROXY:
                while True:
                    async with self.lock:
                        if not self.proxies:
                            return 'noproxy'
                        
                        pop_proxy = self.proxies.pop(0)
                        proxy = Proxy.from_str(pop_proxy if pop_proxy.startswith('http://') else 'http://' + pop_proxy).as_url
                    
                    if not await check_proxy(proxy):
                        if LOGGER_PROXY:
                            logger.error(f"Поток {thread} | <r>BadProxy</r> {pop_proxy}")
                        async with self.lock:
                            FileManager.delete_str_file('data/proxy.txt', pop_proxy)
                        continue

                    else:
                        if LOGGER_PROXY:
                            logger.success(f"Поток {thread} | <g>GoodProxy</g> {pop_proxy}")
                        break
            else:
                proxy = None

            await GMNetwork(thread, private_key, proxy).quick_start(REFERRAL_CODE)

            logger.info(f"Поток {thread} | Завершил работу с аккаунтом - PrivateKey: {private_key}")\
    
    async def generate_wallets(self, thread: int, count: int):
        logger.info("Start Generate Wallet")
        with tqdm(total=count) as pbar:
            for _ in range(count):
                acct = eth_account.Account.create()
                data = acct.key.hex()
                FileManager.save_str_file('data/generate/wallets.txt', data)
                pbar.update(1)
        logger.success(f"Successfully generated {count} wallets")

