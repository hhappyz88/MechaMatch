import random
import logging
from twisted.internet import defer
from twisted.internet.defer import DeferredLock
from typing import List
from toy_catalogue.proxies.proxy import Proxy
from toy_catalogue.proxies.proxy_sourcer import get_proxy_list
from toy_catalogue.proxies.proxy_checker import check_proxies

logger = logging.getLogger(__name__)


class ProxyManager:
    _instance = None
    _proxy_lock: DeferredLock

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.proxies = {}
            cls._instance._proxy_lock = DeferredLock()
            cls._instance._refresh_event = defer.Deferred()
            cls._instance._refresh_check = False
        return cls._instance

    def get_url(self) -> str | None:
        working = [proxy.url for proxy in self.proxies.values() if proxy.is_working]
        return random.choice(working) if working else None

    def mark_success(self, proxy_url: str):
        if proxy_url in self.proxies:
            self.proxies[proxy_url].mark_working()

    def mark_failure(self, proxy_url: str):
        if proxy_url in self.proxies:
            self.proxies[proxy_url].mark_not_working()

    def needs_to_be_refreshed(self) -> bool:
        return (
            not any(p.is_working for p in self.proxies.values()) or self._refresh_check
        )

    def wait_for_refresh(self):
        return self._refresh_event

    def refresh(self):
        if self._refresh_check:
            logger.info("Refresh already in progress.")
            return self._refresh_event

        self._refresh_check = True
        self._refresh_event = defer.Deferred()

        d = self._proxy_lock.acquire()
        d.addCallback(lambda _: self._do_refresh())
        d.addErrback(self._on_refresh_failed)

        return self._refresh_event

    def _do_refresh(self):
        new_proxies = get_proxy_list() + [
            p for p in self.proxies.values() if p.is_working
        ]
        d = check_proxies(new_proxies)
        d.addCallback(self._on_checked)
        logger.info(f"Proxy checks initiated: {len(new_proxies)} proxies")
        return d

    def _on_checked(self, working_proxies: List[Proxy]):
        try:
            self.proxies = {proxy.url: proxy for proxy in working_proxies}
            logger.info(
                f"Proxy refresh complete: {len(working_proxies)} valid proxies."
            )

            if not self._refresh_event.called:
                self._refresh_event.callback(True)

            self._refresh_check = False
            self._proxy_lock.release()  # Make sure this line is reached
        except Exception as e:
            logger.error(f"Exception in _on_checked: {e}", exc_info=True)

        return True

    def _on_refresh_failed(self, failure):
        logger.error(f"[ProxyManager] Refresh failed: {failure}", exc_info=True)

        if not self._refresh_event.called:
            self._refresh_event.errback(failure)

        self._refresh_check = False  # 🔐 Cleanup
        self._proxy_lock.release()
