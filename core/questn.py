import time
import re
import asyncio
import string
import random
import twitter

from core.utils import logger
from core.utils import Web3Utils
from curl_cffi.requests import AsyncSession

from core.database.database import MainDB
from core.database.models import Accounts

from data.config import BNB_RPC


class QuestN:
    def __init__(self, thread: int, account: Accounts) -> None:
        self.thread = thread
        self.account = account

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en',
            'Origin': 'https://app.questn.com',
            'Referer': 'https://app.questn.com/',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        self.session = AsyncSession(impersonate="chrome120", proxy=account.proxy, headers=headers)
        self.w3u = Web3Utils(BNB_RPC, account.privatekey, account.proxy)

    @staticmethod
    def get_unix_timestamp() -> int:
        return int(time.time())
    
    async def login(self) -> dict | None:
        timestamp = QuestN.get_unix_timestamp()
        text = f'Welcome to QuestN.\nPlease sign this message to login QuestN.\n\nTimestamp: {timestamp}'

        signature = self.w3u.sign_message(text)[2:]

        payload = {
            "address": self.w3u.address,
            "message": "Welcome to QuestN.\nPlease sign this message to login QuestN.",
            "timestamp": timestamp,
            "signature": signature,
            "login_type": 100,
            "photo": "fashionable_figures_11"
        }
        response = await self.session.post('https://api.questn.com/user/login/', json=payload)
        answer = response.json()

        if answer['success']:
            self.session.headers['Access-Token'] = answer['result']['access_token']
            logger.success(f'Поток {self.thread} | <m>QuestN</m> | Выполнен вход - ID: {answer["result"]["user_info"]["id"]}, Address: {self.w3u.address}')
            return answer
        else:
            logger.error(f'Поток {self.thread} | <m>QuestN</m> |  Не удалось войти в аккаунт | <r>ERROR: {answer["error_message"]}</r>')
            return None
    
    async def bind_twitter(self, twitter_token: str) -> dict:
        params = {
            'state': '300_2_' + ''.join(random.choices(string.ascii_letters + string.digits, k=21)),
            'login_type': 300
        }
        response = await self.session.get('https://api.questn.com/misc/authorization_url/', params=params)
        oauth_token = response.url.split('=')[1]

        account = twitter.Account(auth_token=twitter_token)

        async with twitter.Client(account=account, proxy=self.account.proxy) as twitter_client:
            _, redirect_url = await twitter_client.oauth(oauth_token=oauth_token)

        oauth_token = re.search(r'oauth_token=([^&]+)', redirect_url).group(1)
        oauth_verifier = re.search(r'oauth_verifier=([^&]+)', redirect_url).group(1)

        payload = {
            "code": "",
            "oauth_token": oauth_token,
            "oauth_verifier": oauth_verifier,
            "login_type": 300
        }

        response = await self.session.post('https://api.questn.com/user/auth/bind/', json=payload)
        answer = response.json()
        return answer['result']
    
    async def do_task(self) -> None:
        solutions = [
            [218340, 'B'], [218341, 'D'], [218342, 'D'], [218343, 'A'], [218344, 'A'], [218345, 'C'],
            [218335, 'B'], [218336, 'A'], [218337, 'C'], [218338, 'D'], [218339, 'D']
        ]
        for sol in solutions:
            payload = {
                f"task_id": sol[0],
                "extra": r"{\"user_answer\":\"" + sol[1] + r"\"}"
            }

            response = await self.session.post('https://api.questn.com/consumer/quest/token/task/', json=payload)
            answer = response.json()

            if answer['success']:
                logger.success(f'Поток {self.thread} | <m>QuestN</m> | Задание <c>{sol[0]}</c> выполнено, сплю 3 сек.')
            else:
                logger.success(f'Поток {self.thread} | <m>QuestN</m> | Задание <c>{sol[0]}</c> не выполнено, добавляю задание в конец, сплю 3 сек.')
                solutions.append(sol)
            
            await asyncio.sleep(3)
    
    async def claim_nft(self) -> None:
        pass

    async def quick_start(self) -> None:
        pass



