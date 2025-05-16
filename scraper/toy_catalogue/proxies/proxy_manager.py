import random
import logging
from toy_catalogue.proxies.proxy_sourcer import get_proxy_list
from toy_catalogue.proxies.proxy_checker import check_proxies
from toy_catalogue.proxies.proxy_loader import save_proxies
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class ProxyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        self.proxies = {}
        self._lock = asyncio.Lock()
        self._refresh_in_progress = False
        self._refresh_event = asyncio.Event()
        self._initialised = True

    def get_url(self) -> Optional[str]:
        working = [proxy.url for proxy in self.proxies.values() if proxy.is_working]
        return random.choice(working) if working else None

    def mark_success(self, proxy_url: str):
        proxy = self.proxies.get(proxy_url)
        if proxy:
            proxy.mark_working()

    def mark_failure(self, proxy_url: str):
        proxy = self.proxies.get(proxy_url)
        if proxy:
            proxy.mark_not_working()

    def needs_to_be_refreshed(self) -> bool:
        # Refresh if no proxies working or refresh already in progress
        return (
            not any(p.is_working for p in self.proxies.values())
            or self._refresh_in_progress
        )

    async def wait_for_refresh(self):
        await self._refresh_event.wait()

    async def refresh(self):
        async with self._lock:
            if self._refresh_in_progress:
                logger.info("Refresh already in progress, waiting for completion.")
                await self._refresh_event.wait()
                return

            self._refresh_in_progress = True
            self._refresh_event.clear()

            try:
                loop = asyncio.get_running_loop()
                new_proxies = await loop.run_in_executor(None, get_proxy_list)
                # Append still-working proxies
                new_proxies += [p for p in self.proxies.values() if p.is_working]

                logger.info(f"Proxy checks initiated: {len(new_proxies)} proxies")

                # check_proxies is async so await it
                working_proxies = await check_proxies(new_proxies)

                self.proxies = {proxy.url: proxy for proxy in working_proxies}

                logger.info(
                    f"Proxy refresh complete: {len(working_proxies)} valid proxies."
                )

                self.save_proxies()
                self._refresh_event.set()
            except Exception as e:
                logger.error(f"[ProxyManager] Refresh failed: {e}", exc_info=True)
                self._refresh_event.set()
            finally:
                self._refresh_in_progress = False

    def save_proxies(self):
        # synchronous save of proxies
        save_proxies(self.proxies.values())
