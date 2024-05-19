import time
import asyncio
import random

from core.utils import logger
from core.utils import Web3Utils
from curl_cffi.requests import AsyncSession, Response, RequestsError
from core.utils import Captcha

from core.database.database import MainDB
from core.database.models import Accounts

from data.config import RATELIMIT_SLEEP, REQUESTSERROR_ATTEMPTS


class GMNetwork:
    def __init__(self, thread: int, account: Accounts) -> None:
        self.thread = thread
        self.account = account
        self.status = 0

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en',
            'Origin': 'https://launchpad.gmnetwork.ai',
            'Referer': 'https://launchpad.gmnetwork.ai/',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        self.session = AsyncSession(impersonate="chrome124", proxy=self.account.proxy, headers=headers)
        self.w3u = Web3Utils('https://rpc.ankr.com/eth', self.account.privatekey, self.account.proxy)
    
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
        for attempt in range(1, REQUESTSERROR_ATTEMPTS + 1):
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
                    continue
            except RequestsError as error:
                logger.error(f'Поток {self.thread} | <r>RequestsError: {error}</r>, попытка <y>{attempt}</y>/<r>{REQUESTSERROR_ATTEMPTS+1}</r> сплю 10 сек.')
                await asyncio.sleep(10)
            else:
                return response
        else:
            logger.error(f'Поток {self.thread} | Превышено максимальное количество попыток - <r>{REQUESTSERROR_ATTEMPTS}</r>')
            raise RequestsError('I think bad proxy')

    async def login(self) -> str:
        if self.account.access_token:
            self.session.headers['Access-Token'] = self.account.access_token
            user_info = await self.get_user_info()
        else:
            user_info = None
        
        if user_info:
            logger.success(f'Поток {self.thread} | Выполнен вход - ID: {user_info["id"]}, Privatekey: {self.account.privatekey[:6]}...{self.account.privatekey[60:]}')
            self.status = user_info['status']
            return self.account.access_token
        
        timestamp = GMNetwork.get_unix_timestamp()
        text = f'Welcome to GM Launchpad.\nPlease sign this message to login GM Launchpad.\n\nTimestamp: {timestamp}'
        signature = self.w3u.sign_message(text)[2:]
        captcha_code = await Captcha(self.thread, self.account.proxy).turnstile()
        self.session.headers['Cf-Turnstile-Resp'] = captcha_code

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
            del self.session.headers['Cf-Turnstile-Resp'] 
            self.session.headers['Access-Token'] = answer['result']['access_token']
            logger.success(f'Поток {self.thread} | Выполнен вход - ID: {answer["result"]["user_info"]["id"]}, Privatekey: {self.account.privatekey[:6]}...{self.account.privatekey[60:]}')
            self.status = answer['result']['user_info']['status']
            return answer['result']['access_token']
        else:
            logger.error(f'Поток {self.thread} | Не удалось войти в аккаунт, Privatekey: {self.account.privatekey[:6]}...{self.account.privatekey[60:]} | <r>ERROR: {answer["error_message"]}</r>')
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
                logger.error(f'Поток {self.thread} | Не удалось установить реферальный код | <r>ERROR: {answer["error_message"]}</r>')
            return answer['success']
        return False
    
    async def set_agent(self) -> bool:
        agent = (await self.get_user_info())['agent']
        
        if not agent:
            payload = {
                "nft_id":""
            }

            response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/user/auth/agent_set/', json=payload)
            answer = response.json()

            if answer['success']:
                agent = (await self.get_user_info())['agent']
                logger.success(f'Поток {self.thread} | Установил <c>GM AGENT#{agent["nft_id"]}</c> - Rarity: <m>{agent["rarity"]}</m>, Energy: <m>{agent["energy"]}</m>')
            else:
                logger.error(f'Поток {self.thread} | Не удалось установить GM AGENT | <r>ERROR: {answer["error_message"]}</r>')
            return answer['success']
        else:
            return True
    
    async def get_tasks(self, season_um: int = 1) -> dict:
        params = {
            'season_um': season_um
        }

        response = await self.request('GET', 'https://api-launchpad.gmnetwork.ai/task/auth/task_center/', params=params)
        answer = response.json()
        return answer['result']
    
    async def get_user_info(self) -> dict | None:
        response = await self.request('GET', 'https://api-launchpad.gmnetwork.ai/user/auth/info/')
        answer = response.json()
        return answer.get('result')
    
    async def get_balance(self, daily: bool = False) -> float:
        response = await self.request('GET', 'https://api-launchpad.gmnetwork.ai/energy/auth/user_energy/')
        answer = response.json()
        return answer['result']['daily'] if daily else answer['result']['total']
    
    async def claim_daily(self) -> int:
        tasks = await self.get_tasks()
        task_daily = tasks['check_in_task_info']

        delta_time = self.get_unix_timestamp() - task_daily['last_check_in_time']

        if delta_time >= 86400:
            payload = {
                "task_id": task_daily['id'],
                "category": 200
            }

            response = await self.request('POST', 'https://api-launchpad.gmnetwork.ai/task/auth/task/', json=payload)
            answer = response.json()

            tasks = await self.get_tasks()
            task_daily = tasks['check_in_task_info']

            if answer['success']:
                logger.success(f'Поток {self.thread} | Daily CHECK-IN <g>+{task_daily["extra"][str(task_daily["user_check_in_count"])]}</g>$GN')
            else:
                logger.error(f'Поток {self.thread} | Не удалось Daily CHECK-IN | <r>ERROR: {answer["error_message"]}</r>')
        else:
            logger.info(f'Поток {self.thread} | Daily CHECK-IN через <y>{(86400 - delta_time) / 60 / 60:.2f}</y> часа')
        return task_daily['last_check_in_time']
    
    async def claim_tasks(self):
        dict_tasks = await self.get_tasks()
        this_tasks = ['903134427382845867', '903134427458343407', '903134427496092045', '903134427529646177', '903134427571589375']
        all_tasks = dict_tasks['questn_tasks_info'] + dict_tasks['launchpad_tasks_info']

        for task in all_tasks:
            if task['id'] not in this_tasks:
                continue
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
                        logger.success(f'Поток {self.thread} | Задание <c>{task["title"]}</c> выполнено <g>+{int(task["energy"])}</g>$GN')

                    else:
                        logger.error(f'Поток {self.thread} | Ошибка при выполнении задания <c>{task["title"]}</c>')

                else:
                    logger.error(f'Поток {self.thread} | Ошибка при выполнении задания <c>{task["title"]}</c>')

                t_sleep = random.randint(5, 15)
                logger.info(f'Поток {self.thread} | Сплю {t_sleep}сек. ')
                await asyncio.sleep(t_sleep)

    async def quick_start(self) -> dict:
        try:
            auth_token = await self.login()
            if not auth_token:
                return None

            await self.enter_refcode(self.account.refcode)
            while True:
                if await self.set_agent():break

            checkin = await self.claim_daily()
            
            await self.claim_tasks()

            balance = await self.get_balance()
            user_info = await self.get_user_info()

            data = {
                'access_token': auth_token,
                'id_gm': user_info['id'],
                'email': user_info['email'],
                'checkin': int(checkin),
                'balance': int(balance),
                'invite_code': user_info['invite_code'],
                'agent_id': user_info['agent']['id'],
                'agent_nft_id': user_info['agent']['nft_id'],
                'agent_token_id': user_info['agent']['token_id'],
                'agent_name': user_info['agent']['name'],
                'agent_description': user_info['agent']['description'],
                'agent_image': user_info['agent']['image'],
                'agent_rarity': user_info['agent']['rarity'],
                'agent_energy': user_info['agent']['energy'],
                'boost': user_info['boost'],
                'level': user_info['level']
            }
            
            logger.info(f'Поток {self.thread} | Баланс: <g>{balance}</g>$GN')
            return data
        except RequestsError:
            return None

