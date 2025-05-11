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

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.proxies = {}
            cls._instance._proxy_lock = DeferredLock()
            cls._instance._refresh_event = defer.Deferred()
            cls._instance._refresh_check = False
        return cls._instance

    def get_url(self):
        working = [proxy.url for proxy in self.proxies.values() if proxy.is_working]
        return random.choice(working) if working else None

    def mark_success(self, proxy_url):
        if proxy_url in self.proxies:
            self.proxies[proxy_url].mark_working()

    def mark_failure(self, proxy_url):
        if proxy_url in self.proxies:
            self.proxies[proxy_url].mark_not_working()

    def needs_to_be_refreshed(self):
        return (
            not any(p.is_working for p in self.proxies.values()) or self._refresh_check
        )

    def wait_for_refresh(self):
        return self._refresh_event

    def refresh(self):
        if self._refresh_check:
            logger.info("Refresh already in progress.")
            return self._refresh_event

        logger.info("Starting proxy refresh...")
        self._refresh_check = True
        self._refresh_event = defer.Deferred()
        self._refresh_check = False
        d = self._proxy_lock.acquire()
        d.addCallback(lambda _: self._do_refresh())
        return self._refresh_event

    def _do_refresh(self):
        new_proxies = get_proxy_list() + [
            p for p in self.proxies.values() if p.is_working
        ]
        logger.info(f"[ProxyManager] Total proxies to check: {len(new_proxies)}")
        return check_proxies(new_proxies).addCallback(self._on_checked)

    def _on_checked(self, working_proxies: List[Proxy]):
        try:
            self.proxies = {proxy.url: proxy for proxy in working_proxies}
            logger.info(
                f"Proxy refresh complete: {len(working_proxies)} valid proxies."
            )
            if not self._refresh_event.called:
                self._refresh_event.callback(True)
            self._proxy_lock.release()
        except Exception as e:
            logger.error(f"Exception in _on_checked: {e}", exc_info=True)
        return True
