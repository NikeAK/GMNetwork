import asyncio

from curl_cffi.requests import AsyncSession, BrowserType
from core.utils import logger
from data.config import (
    CAPMONSTER_API_KEY,
    ANTICAPTCHA_API_KEY,
    RUCAPTCHA_API_KEY,
    TWOCAPTCHA_API_KEY
)

CAPTCHA_SERVICES = {
    "capmonster": ('https://api.capmonster.cloud', CAPMONSTER_API_KEY),
    "2captcha": ('https://api.2captcha.com', TWOCAPTCHA_API_KEY),
    "anticaptcha": ('https://api.anti-captcha.com', ANTICAPTCHA_API_KEY),
    "rucaptcha": ('https://api.rucaptcha.com', RUCAPTCHA_API_KEY),
}

class CaptchaService:
    def __init__(self, thread: int, proxy: str, url_service: str, api_key: str):
        self.thread = thread
        self.url_service = url_service
        self.api_key = api_key
        self.session = AsyncSession(
            impersonate=BrowserType.chrome124,
            proxy=proxy,
            verify=False
        )

    async def create_task(self, data_task: dict) -> dict:
        payload = {'clientKey': self.api_key, 'task': data_task}
        response = await self.session.post(self.url_service+'/createTask', json=payload)
        return response.json()

    async def get_result_task(self, task_id: int) -> dict:
        payload = {"clientKey": self.api_key, "taskId": task_id}
        for _ in range(100):
            response = await self.session.post(self.url_service+'/getTaskResult', json=payload)
            answer = response.json()
            if answer["status"] == "ready":
                return answer
            await asyncio.sleep(4)

    async def resolve(self, data_task: dict) -> dict | None:
        task = await self.create_task(data_task)
        if task.get('errorId'):
            logger.error(f'Поток {self.thread} | Капча - Не удалось создать задачу: {task}')
            return None

        task_id = task['taskId']
        logger.success(f'Поток {self.thread} | Капча - Создал задачу | TaskID: {task_id}')
        result = await self.get_result_task(task_id)
        if result.get('errorId'):
            logger.error(f'Поток {self.thread} | Капча - Ошибка в ответе [{result["errorDescription"]}]')
            return None

        logger.success(f'Поток {self.thread} | Капча - Получил решение | TaskID: {task_id}')
        return result.get('solution')

class Captcha:
    def __init__(self, thread: int, proxy: str | None = None):
        self.thread = thread
        self.proxy = proxy

    def _choice_(self) -> CaptchaService:
        for service_name, (url, api_key) in CAPTCHA_SERVICES.items():
            if api_key:
                return CaptchaService(self.thread, self.proxy, url, api_key)

    async def solve_captcha(self, website_url: str, website_key: str) -> str | None:
        cap_obj = self._choice_()
        data = {
            'type': 'TurnstileTaskProxyless',
            'websiteURL': website_url,
            'websiteKey': website_key
        }
        res = await cap_obj.resolve(data)
        return res.get('token') if res else None

    async def turnstile(self) -> str | None:
        return await self.solve_captcha('https://launchpad.gmnetwork.ai', '0x4AAAAAAAaAdLjFNjUZZwWZ')

