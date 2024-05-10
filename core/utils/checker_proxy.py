import warnings
from curl_cffi.requests import AsyncSession

warnings.filterwarnings("ignore", category=UserWarning, message="Curlm already closed! quitting from process_data")

async def check_proxy(proxy: str) -> str|bool:
    async with AsyncSession(proxy = proxy) as session:
        try:
            await session.get('https://api-launchpad.gmnetwork.ai', proxy=proxy, timeout=5)
            response = await session.get('https://api.ipify.org/?format=json', proxy=proxy, timeout=5)
            answer = response.json()
        except Exception:
            return False
        else:
            return answer['ip']

