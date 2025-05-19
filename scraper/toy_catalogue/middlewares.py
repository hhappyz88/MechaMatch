# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
from urllib.parse import urlparse
from scrapy import signals
from scrapy.http import Request, Response
from scrapy.spiders import CrawlSpider
from scrapy.crawler import Crawler
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from twisted.web._newclient import ResponseNeverReceived
from OpenSSL.SSL import Error as SSLError
import logging
from toy_catalogue.proxies.proxy_manager import ProxyManager
from scrapy.downloadermiddlewares.offsite import OffsiteMiddleware

# useful for handling different item types with a single interface
import asyncio


def get_proxy_from_request(request):
    # if request.meta.get("playwright") is True:
    #     return request.meta["proxy"].get("server")
    # else:
    return request.meta.get("proxy")


def set_proxy_from_request(request, proxy):
    # if request.meta.get("playwright") is True:
    # return {"server": proxy}
    return proxy


class DynamicProxyMiddleware:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        self.refreshing = False
        self.refresh_lock = asyncio.Lock()
        self.logstats_logger = logging.getLogger("scrapy.extensions.logstats")
        self._logstat_original_level = self.logstats_logger.getEffectiveLevel()

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        return ext

    def spider_opened(self, spider: CrawlSpider):
        loop = asyncio.get_event_loop()
        loop.call_soon(asyncio.create_task, self._pause(spider))

    def spider_idle(self, spider: CrawlSpider):
        if ProxyManager().needs_to_be_refreshed() and not self.refreshing:
            asyncio.create_task(self._pause(spider))

    async def _pause(self, spider: CrawlSpider):
        async with self.refresh_lock:
            if self.refreshing:
                return  # already refreshing
            self.refreshing = True
            spider.logger.info("Initialising ProxyManager and refreshing proxies.")
            if spider.crawler.engine:
                spider.crawler.engine.pause()
            self.logstats_logger.setLevel(
                logging.ERROR
            )  # reduce log noise during refresh

            try:
                await ProxyManager().refresh()
            except Exception as e:
                spider.logger.error(
                    f"[ProxyRefreshMiddleware] Proxy refresh failed: {e}"
                )
            else:
                spider.logger.info(
                    "[ProxyRefreshMiddleware] Proxy refresh completed. Resuming engine."
                )
            finally:
                self.refreshing = False
                if spider.crawler.engine:
                    spider.crawler.engine.unpause()
                self.logstats_logger.setLevel(self._logstat_original_level)

    def process_request(self, request: Request, spider: CrawlSpider):
        try:
            proxy = self._get_new_proxy(spider)
            request.meta["proxy"] = set_proxy_from_request(request, proxy)
        except Exception as e:
            spider.logger.error(f"Error getting proxy: {e}")
        return None

    def process_response(
        self, request: Request, response: Response, spider: CrawlSpider
    ):
        if response.status != 200:
            proxy = get_proxy_from_request(request)
            spider.logger.debug(
                f"Request for {request.url} using proxy {proxy}"
                + f"failed: status {response.status}"
            )
            if proxy:
                ProxyManager().mark_failure(proxy)
            new_proxy = self._get_new_proxy(spider)
            count = len(
                [proxy for proxy in ProxyManager().proxies.values() if proxy.is_working]
            )
            spider.logger.debug(
                f"Proxies {count} left Retrying with new proxy: {new_proxy}"
            )
            new_request = request.replace(dont_filter=True)
            new_request.meta["proxy"] = set_proxy_from_request(new_request, new_proxy)
            return new_request
        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: CrawlSpider
    ):
        proxy = get_proxy_from_request(request)
        if proxy:
            ProxyManager().mark_failure(proxy)

        spider.logger.debug(
            f"Request for {request.url} using proxy "
            + f"{proxy} failed: exception {exception}"
        )
        spider.logger.debug(f"{request.meta}")
        new_proxy = self._get_new_proxy(spider)
        spider.logger.debug(f"Retrying with new proxy: {new_proxy}")

        new_request = request.replace(dont_filter=True)
        new_request.meta["proxy"] = set_proxy_from_request(new_request, new_proxy)
        return new_request

    def _get_new_proxy(self, spider: CrawlSpider) -> str:
        proxy = ProxyManager().get_url()
        if proxy:
            return proxy
        else:
            spider.logger.debug("No available proxy found. Refreshing proxies...")
            if ProxyManager().needs_to_be_refreshed() and not self.refreshing:
                asyncio.create_task(self._pause(spider))
            proxy = ProxyManager().get_url()
            if proxy:
                return proxy
            raise RuntimeError("No proxies available after refresh.")


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


class CustomRetryMiddleware(RetryMiddleware):
    EXCEPTIONS_TO_RETRY = (
        TimeoutError,
        TCPTimedOutError,
        DNSLookupError,
        ConnectionRefusedError,
        ResponseNeverReceived,
        SSLError,
    )

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            spider.logger.warning(
                f"Retrying {request.url} due to exception: {repr(exception)}"
            )
            ProxyManager().mark_failure(get_proxy_from_request(request))
            request.meta["proxy"] = set_proxy_from_request(
                request, ProxyManager().get_url()
            )
            return self._retry(request, exception, spider)
