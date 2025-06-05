# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import time
import random
import logging
import requests

from typing import Any, Dict, Optional, List, Union, Generator
from urllib.parse import urlparse

from scrapy import signals
from scrapy.http import Request, Response
from scrapy.downloadermiddlewares.offsite import OffsiteMiddleware
from scrapy.crawler import Crawler
from scrapy.spiders import Spider


class JhaoProxyMiddleware:
    API_URL: str = "http://localhost:5010"
    POOL_PARAMS: Dict[str, Any] = {
        "type": "https",
        "score": 5,
        "anonymity": "high_anonymous",
        "limit": 50,
    }
    REFRESH_INTERVAL: int = 120  # seconds between cache refreshes
    BAN_CODES: set[int] = {429}

    def __init__(self, proxy_client: Optional["_RequestsProxyClient"] = None) -> None:
        self._proxy_client: _RequestsProxyClient = proxy_client or _RequestsProxyClient(
            self.API_URL
        )
        self._last_refresh: float = 0.0
        self._proxies: List[str] = []

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "JhaoProxyMiddleware":
        proxy_api_url: str = crawler.settings.get("JHAO_PROXY_API_URL", cls.API_URL)
        mw = cls(_RequestsProxyClient(proxy_api_url))
        crawler.signals.connect(mw.spider_opened, signals.spider_opened)
        return mw

    def spider_opened(self, spider: Spider) -> None:
        pass  # Hook for future use

    def process_request(self, request: Request, spider: Spider) -> None:
        if "proxy" not in request.meta:
            proxy = self._get_proxy(spider)
            if proxy:
                request.meta["proxy"] = proxy

    def process_response(
        self, request: Request, response: Response, spider: Spider
    ) -> Union[Request, Response]:
        if response.status in self.BAN_CODES:
            bad = request.meta.get("proxy")
            if bad:
                try:
                    requests.get(
                        f"{self.API_URL}/ban",
                        params={"proxy": bad.replace("http://", "")},
                        timeout=2,
                    )
                except Exception:
                    pass
                self._ban_proxy(bad)
                spider.logger.debug(f"Banned proxy {bad} due to HTTP {response.status}")

            new_req: Request = request.copy()
            new_req.dont_filter = True
            new_req.meta.pop("proxy", None)
            return new_req

        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: Spider
    ) -> Optional[Request]:
        bad = request.meta.get("proxy")
        if bad:
            try:
                requests.get(
                    f"{self.API_URL}/ban",
                    params={"proxy": bad.replace("http://", "")},
                    timeout=2,
                )
            except Exception:
                pass
            self._ban_proxy(bad)
            spider.logger.debug(f"Dropped proxy {bad} due to exception {exception}")

        new_req: Request = request.copy()
        new_req.dont_filter = True
        new_req.meta.pop("proxy", None)
        return new_req

    def _refresh_cache(self, spider: Spider, force: bool = False) -> None:
        now = time.time()
        if force or now - self._last_refresh > self.REFRESH_INTERVAL:
            try:
                self._proxies = self._proxy_client.fetch_batch(
                    limit=self.POOL_PARAMS["limit"]
                )
                random.shuffle(self._proxies)
                self._last_refresh = now
                spider.logger.info(f"Fetched {len(self._proxies)} proxies from pool")
            except Exception as e:
                spider.logger.warning(f"ProxyRotator429: cache refresh failed: {e}")

    def _ban_proxy(self, proxy_url: str) -> None:
        ip_port: str = proxy_url.replace("http://", "").replace("https://", "")
        self._proxy_client.ban(ip_port)

    def _get_proxy(self, spider: Spider) -> Optional[str]:
        if not self._proxies:
            self._refresh_cache(spider, force=True)
        return self._proxies.pop() if self._proxies else None


class _RequestsProxyClient:
    """Default implementation that talks to jhao proxy_pool via requests."""

    def __init__(self, api_base: str) -> None:
        self.api: str = api_base.rstrip("/")

    def fetch_batch(self, limit: int = 50) -> List[str]:
        params: Dict[str, Any] = {
            "type": "https",
            "score": 5,
            "anonymity": "high_anonymous",
            "limit": limit,
        }
        r = requests.get(f"{self.api}/all", params=params, timeout=5)
        r.raise_for_status()
        return [f"http://{p}" if "://" not in p else p for p in r.json()]

    def ban(self, ip_port: str) -> None:
        requests.get(f"{self.api}/ban", params={"proxy": ip_port}, timeout=3)


logstat_logger: logging.Logger = logging.getLogger("scrapy.extensions.logstats")

IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}


class AllowImagesOffsiteMiddleware(OffsiteMiddleware):
    def process_spider_output(
        self,
        response: Response,
        result: Generator[Union[Request, Any], None, None],
        spider: Spider,
    ) -> List[Union[Request, Any]]:
        allowed: List[Union[Request, Any]] = []

        for r in result:
            if isinstance(r, Request):
                path = urlparse(r.url).path
                ext = os.path.splitext(path)[1].lower()
                if ext in IMAGE_EXTENSIONS:
                    r.meta["dont_filter"] = True
                    r.priority = 1000
                    r.meta.pop("proxy", None)
                    allowed.append(r)
                elif self._filter(r, spider):  # type: ignore[attr-defined]
                    continue
                else:
                    allowed.append(r)
            else:
                allowed.append(r)

        return allowed
