# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import requests
from urllib.parse import urlparse
from scrapy import signals
from scrapy.http import Request
import logging
from scrapy.downloadermiddlewares.offsite import OffsiteMiddleware
import time
import random

# useful for handling different item types with a single interface


class JhaoProxyMiddleware:
    API_URL = "http://localhost:5010"
    POOL_PARAMS = {
        "type": "https",
        "score": 5,
        "anonymity": "high_anonymous",
        "limit": 50,
    }
    REFRESH_INTERVAL = 120  # seconds between cache refreshes
    BAN_CODES = {429}

    def __init__(self, proxy_client=None):
        self._proxy_client = proxy_client or _RequestsProxyClient(
            "http://localhost:5010"
        )
        self._last_refresh = 0
        self._proxies = []

    @classmethod
    def from_crawler(cls, crawler):
        # Proxy API base URL & parameters from settings.py or defaults
        proxy_api_url = crawler.settings.get(
            "JHAO_PROXY_API_URL", "http://localhost:5010"
        )
        mw = cls(_RequestsProxyClient(proxy_api_url))
        crawler.signals.connect(mw.spider_opened, signals.spider_opened)
        return mw

    def spider_opened(self, spider):
        pass  # For future use

    def process_request(self, request, spider):
        # If the request already has a proxy (retry) keep it;
        # otherwise assign a fresh one.
        if "proxy" not in request.meta:
            proxy = self._get_proxy(spider)
            if proxy:
                request.meta["proxy"] = proxy

    def process_response(self, request, response, spider):
        # Swap proxy & retry if response is a ban code
        if response.status in self.BAN_CODES:
            bad = request.meta.get("proxy")
            if bad:
                # Optional: tell jhao to delete/bury that proxy
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
            # Give Scrapy a fresh proxy and retry
            new_req = request.copy()
            new_req.dont_filter = True
            new_req.meta.pop("proxy", None)  # ensure we pick a new one
            return new_req
        return response

    def process_exception(self, request, exception, spider):
        # Network error → ditch proxy & retry
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
        new_req = request.copy()
        new_req.dont_filter = True
        new_req.meta.pop("proxy", None)
        return new_req

    def _refresh_cache(self, spider, force=False):
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

    def _ban_proxy(self, proxy_url):
        ip_port = proxy_url.replace("http://", "").replace("https://", "")
        self._proxy_client.ban(ip_port)

    def _get_proxy(self, spider):
        if not self._proxies:
            self._refresh_cache(spider, force=True)
        return self._proxies.pop() if self._proxies else None


class _RequestsProxyClient:
    """Default implementation that really calls jhao proxy_pool via requests."""

    def __init__(self, api_base):
        self.api = api_base.rstrip("/")

    def fetch_batch(self, limit=50):
        params = {
            "type": "https",
            "score": 5,
            "anonymity": "high_anonymous",
            "limit": limit,
        }
        r = requests.get(f"{self.api}/all", params=params, timeout=5)
        r.raise_for_status()
        return [f"http://{p}" if "://" not in p else p for p in r.json()]

    def ban(self, ip_port):
        requests.get(f"{self.api}/ban", params={"proxy": ip_port}, timeout=3)


logstat_logger = logging.getLogger("scrapy.extensions.logstats")


# Disable twisted SSL warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="twisted")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}


class AllowImagesOffsiteMiddleware(OffsiteMiddleware):
    def process_spider_output(self, response, result, spider):
        allowed = []
        for r in result:
            if isinstance(r, Request):
                path = urlparse(r.url).path
                ext = os.path.splitext(path)[1].lower()
                if ext in IMAGE_EXTENSIONS:
                    r.meta["dont_filter"] = True  # Optional
                    r.priority = 1000
                    del r.meta["proxy"]
                    allowed.append(r)
                elif self._filter(r, spider):  # original offsite check
                    continue
                else:
                    allowed.append(r)
            else:
                allowed.append(r)
        return allowed
