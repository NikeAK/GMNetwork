import warnings
from curl_cffi.requests import AsyncSession

warnings.filterwarnings("ignore", message="Curlm alread closed!", category=UserWarning)


async def check_proxy(proxy: str, timeout: int | float) -> tuple[bool, str]:
    async with AsyncSession(proxy = proxy) as session:
        try:
            await session.get('https://api-launchpad.gmnetwork.ai', proxy=proxy, timeout=timeout)
            response = await session.get('https://api.ipify.org/?format=json', proxy=proxy, timeout=timeout)
            answer = response.json()
        except Exception as error:
            return False, error
        else:
            return True, answer['ip']

