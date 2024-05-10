import time
import asyncio
import random

from core.utils import logger
from core.utils import Web3Utils
from curl_cffi.requests import AsyncSession, Response, RequestsError

from data.config import RATELIMIT_SLEEP

class GMNetwork:
    def __init__(self, thread: int, private_key: str, proxy: str = None) -> None:
        self.thread = thread
        self.status = 0

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en',
            'Origin': 'https://launchpad.gmnetwork.ai',
            'Referer': 'https://launchpad.gmnetwork.ai/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = AsyncSession(impersonate="chrome120", proxy=proxy, headers=headers)
        self.w3u = Web3Utils('https://rpc.ankr.com/eth', private_key, proxy)
    
    @staticmethod
    def get_unix_timestamp() -> int:
        return int(time.time())
    
    async def request(
            self, 
            method: str, 
            url: str, 
            params: dict | list| tuple | None = None, 
            json: dict = None
        ) -> Response:
        while True:
            try:
                response = await self.session.request(
                    method=method, 
                    url=url, 
                    params=params, 
                    json=json
                )
                if '1015' in response.text:
                    t_sleep = random.randint(RATELIMIT_SLEEP[0], RATELIMIT_SLEEP[1])
                    logger.error(f'Поток {self.thread} | <r>RateLimit Request</r>, сплю {t_sleep} сек.')
                    await asyncio.sleep(t_sleep)
                else:
                    return response
            except RequestsError:
                logger.error(f'Поток {self.thread} | <r>RequestsError</r>, сплю 10 сек.')
                await asyncio.sleep(10)

    async def login(self) -> dict | None:
        timestamp = GMNetwork.get_unix_timestamp()
        text = f'Welcome to GM Launchpad.\nPlease sign this message to login GM Launchpad.\n\nTimestamp: {timestamp}'

        signature = self.w3u.sign_message(text)[2:]

        payload = {
            "address": self.w3u.address,
            "message": "Welcome to GM Launchpad.\nPlease sign this message to login GM Launchpad.",
            "timestamp": timestamp,
            "signature": signature,
            "login_type": 100
        }

        response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/user/login/', json=payload)
        answer = response.json()

        if answer['success']:
            self.session.headers['Access-Token'] = answer['result']['access_token']
            logger.success(f'Поток {self.thread} | Выполнен вход - ID: {answer['result']['user_info']['id']}, Address: {self.w3u.address}')
            self.status = answer['result']['user_info']['status']
            return answer
        else:
            logger.error(f'Поток {self.thread} | Не удалось установить реферальный код | <r>ERROR: {answer['error_message']}</r>')
            return None

    async def enter_refcode(self, refcode: str) -> bool:
        if self.status == 300:
            payload = {
                "invite_code": refcode,
                "address": self.w3u.address
            }

            response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/user/invite_code/', json=payload)
            answer = response.json()
            
            if answer['success']:
                logger.success(f'Поток {self.thread} | Установил реферальный код - <c>{refcode}</c>')
            else:
                logger.error(f'Поток {self.thread} | Не удалось установить реферальный код | <r>ERROR: {answer['error_message']}</r>')
            return answer['success']
        return False
    
    async def set_agent(self) -> bool:
        agent = (await self.get_user_info())['result']['agent']
        
        if not agent:
            payload = {
                "nft_id":""
            }

            response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/user/auth/agent_set/', json=payload)
            answer = response.json()

            if answer['success']:
                agent = (await self.get_user_info())['result']['agent']
                logger.success(f'Поток {self.thread} | Установил <c>GM AGENT#{agent['nft_id']}</c> - Rarity: <m>{agent['rarity']}</m>, Energy: <m>{agent['energy']}</m>')
            else:
                logger.error(f'Поток {self.thread} | Не удалось установить GM AGENT | <r>ERROR: {answer['error_message']}</r>')
            return answer['success']
    
    async def get_tasks(self, season_um: int = 1) -> dict:
        params = {
            'season_um': season_um
        }

        response = await self.request('GET', 'https://api-launchpad.gmnetwork.ai/task/auth/task_center/', params=params)
        answer = response.json()
        return answer
    
    async def get_user_info(self) -> dict:
        response = await self.request('GET', 'https://api-launchpad.gmnetwork.ai/user/auth/info/')
        answer = response.json()
        return answer
    
    async def get_balance(self, daily: bool = False) -> float:
        response = await self.request('GET', 'https://api-launchpad.gmnetwork.ai/energy/auth/user_energy/')
        answer = response.json()
        return answer['result']['daily'] if daily else answer['result']['total']
    
    async def claim_daily(self) -> bool:
        tasks = await self.get_tasks()
        task_daily = tasks['result']['check_in_task_info']

        delta_time = self.get_unix_timestamp() - task_daily['last_check_in_time']

        if delta_time >= 86400:
            payload = {
                "task_id": task_daily['id'],
                "category": 200
            }

            response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/task/auth/task/', json=payload)
            answer = response.json()

            tasks = await self.get_tasks()
            task_daily = tasks['result']['check_in_task_info']

            if answer['success']:
                logger.success(f'Поток {self.thread} | Daily CHECK-IN <g>+{task_daily['extra'][str(task_daily['user_check_in_count'])]}</g>$GN')
            else:
                logger.error(f'Поток {self.thread} | Не удалось Daily CHECK-IN | <r>ERROR: {answer['error_message']}</r>')
            return answer['success']
        else:
            logger.info(f'Поток {self.thread} | Daily CHECK-IN через <y>{(86400 - delta_time) / 60 / 60:.2f}</y> часа')
    
    async def claim_launchpad_tasks(self):
        tasks = (await self.get_tasks())['result']['launchpad_tasks_info']

        for task in tasks:
            if not task['user_done_status']:
                payload = {
                    "task_id": task['id'],
                    "category": 100
                }

                response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/task/auth/task/', json=payload)
                answer = response.json()

                if answer['success'] and answer['result']:
                    await asyncio.sleep(7)
                    payload = {
                        "task_id": task['id'],
                        "category": 200
                    }
                    
                    response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/task/auth/task/', json=payload)
                    answer = response.json()

                    if answer['success'] and answer['result']:
                        logger.success(f'Поток {self.thread} | Задание <c>{task['title']}</c> выполнено <g>+{int(task['energy'])}</g>$GN')

                    else:
                        logger.error(f'Поток {self.thread} | Ошибка при выполнении задания <c>{task['title']}</c>')

                else:
                    logger.error(f'Поток {self.thread} | Ошибка при выполнении задания <c>{task['title']}</c>')

                t_sleep = random.randint(5, 15)
                logger.info(f'Поток {self.thread} | Сплю {t_sleep}сек. ')
                await asyncio.sleep(t_sleep)

    async def quick_start(self, refcode: str) -> None:
        await self.login()
        await self.enter_refcode(refcode)

        while True:
            if await self.set_agent():break

        await self.claim_daily()
        await self.claim_launchpad_tasks()
        balance = await self.get_balance()
        logger.info(f'Поток {self.thread} | Поинтов: <g>{balance}</g>$GN')
