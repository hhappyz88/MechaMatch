# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from scrapy.http import Request, Response
from scrapy.spiders import CrawlSpider
from scrapy.crawler import Crawler
from twisted.python.failure import Failure
import logging
from toy_catalogue.proxies.proxy_manager import ProxyManager
from toy_catalogue.proxies.log_handler import BufferingLogHandler

# useful for handling different item types with a single interface


class ToyCatalogueSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ToyCatalogueDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DynamicProxyMiddleware:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        self.refreshing = False
        self._logstat_original_level = logging.getLogger().level
        self.buffer_handler = BufferingLogHandler()

    @classmethod
    def from_crawler(cls, crawler: Crawler, *args, **kwargs):
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        return ext

    def spider_opened(self, spider: CrawlSpider):
        """Begin by refreshing proxies."""
        self._pause(spider)

    def spider_idle(self, spider: CrawlSpider):
        """Pause the engine to refresh proxies when proxies are exhausted."""
        spider.logger.info(
            f"{self.refreshing}, {ProxyManager().needs_to_be_refreshed()}"
        )
        if ProxyManager().needs_to_be_refreshed() and not self.refreshing:
            self._pause(spider)

    def _on_refresh_complete(self, spider: CrawlSpider):
        spider.logger.info(
            "[ProxyRefreshMiddleware] Proxy refresh completed. Resuming engine."
        )
        self._unpause(spider)

    def _on_refresh_failed(self, spider: CrawlSpider, failure: Failure):
        spider.logger.error(f"[ProxyRefreshMiddleware] Proxy refresh failed: {failure}")
        self._unpause(spider)

    def _pause(self, spider: CrawlSpider):
        """Pause the engine to refresh proxies when proxies are exhausted."""
        spider.logger.info("Initialising ProxyManager.")
        self.refreshing = True
        if spider.crawler.engine:
            spider.crawler.engine.pause()
            logging.getLogger().addHandler(self.buffer_handler)
            logging.getLogger().setLevel(logging.CRITICAL)

        d = ProxyManager().refresh()  # This must return a Deferred
        d.addCallback(lambda _: self._on_refresh_complete(spider))
        d.addErrback(lambda f: self._on_refresh_failed(spider, f))

        return d

    def _unpause(self, spider: CrawlSpider):
        self.refreshing = False
        if spider.crawler.engine:
            spider.crawler.engine.unpause()
            logging.getLogger().setLevel(self._logstat_original_level)
            self.buffer_handler.flush_to(logging.getLogger())
            logging.getLogger().removeHandler(self.buffer_handler)

    def process_request(self, request: Request, spider: CrawlSpider):
        try:
            request.meta["proxy"] = self._get_new_proxy(spider)
            return None
        except Exception as e:
            spider.logger.error(f"Error in proxy middleware: {e}")

    def process_response(
        self, request: Request, response: Response, spider: CrawlSpider
    ):
        if response.status != 200:
            spider.logger.debug(
                f"Request for {request.url} using proxy {request.meta['proxy']}"
                + f"failed: response status {response.status}"
            )
            proxy = request.meta.get("proxy")
            if proxy:
                ProxyManager().mark_failure(proxy)
            response.meta["proxy"] = self._get_new_proxy(spider)
            spider.logger.debug(f"Retrying with new proxy: {response.meta['proxy']}")
        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: CrawlSpider
    ):
        proxy = request.meta.get("proxy")
        if proxy:
            ProxyManager().mark_failure(proxy)

        spider.logger.debug(
            f"Request for {request.url} using proxy {request.meta['proxy']}"
            + f"failed: exception occured {exception}"
        )

        request.dont_filter = True
        request.meta["proxy"] = self._get_new_proxy(spider)
        spider.logger.debug(f"Retrying with new proxy: {request.meta['proxy']}")

        return request

    def _get_new_proxy(self, spider: CrawlSpider):
        proxy = ProxyManager().get_url()
        if proxy:
            return proxy
        else:
            spider.logger.debug("No available proxy found. Resetting proxies")
            self._pause(spider)


logstat_logger = logging.getLogger("scrapy.extensions.logstats")


# Disable twisted SSL warnings
# warnings.filterwarnings("ignore", category=UserWarning, module="twisted")
