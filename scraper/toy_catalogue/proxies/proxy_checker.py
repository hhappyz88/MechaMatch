# from twisted.internet.defer import DeferredSemaphore, DeferredList
# from twisted.web.client import ProxyAgent, Response
# from twisted.internet.endpoints import clientFromString
# from twisted.web.http_headers import Headers
# from twisted.internet import reactor as _reactor
# from twisted.internet.interfaces import IReactorTime
# from twisted.python.failure import Failure
from tqdm import tqdm
from toy_catalogue.proxies.proxy import Proxy
from config.config import PROXY_TIMEOUT
import asyncio
import aiohttp


async def check_proxy(proxy: Proxy, test_url="https://httpbingo.org/ip"):
    proxy_url = proxy.url
    try:
        timeout_cfg = aiohttp.ClientTimeout(total=PROXY_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
            async with session.get(
                test_url, proxy=proxy_url, headers={"User-Agent": "Scrapy"}
            ) as resp:
                if resp.status == 200:
                    proxy.mark_working()
                else:
                    proxy.mark_not_working()
    except Exception:
        proxy.mark_not_working()
    return proxy


async def check_proxies(proxies: list[Proxy], concurrency: int = 50) -> list[Proxy]:
    semaphore = asyncio.Semaphore(concurrency)
    results: list[Proxy] = []

    async def sem_task(proxy: Proxy):
        async with semaphore:
            return await check_proxy(proxy)

    tasks = [sem_task(p) for p in proxies]
    for future in tqdm(
        asyncio.as_completed(tasks), total=len(tasks), desc="Checking proxies"
    ):
        result = await future
        results.append(result)

    # Return only working proxies
    return [p for p in results if p.is_working]
