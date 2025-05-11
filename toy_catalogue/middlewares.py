# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from toy_catalogue.proxies.proxy_manager import ProxyManager
import warnings

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
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def process_request(self, request, spider):
        try:
            proxy = ProxyManager().get_url()
            if proxy:
                spider.logger.debug(
                    f"Assigned new proxy: {proxy} for request: {request.url}"
                )
                request.meta["proxy"] = proxy
            else:
                spider.logger.warning("No available proxy found. Resetting proxies")
                spider.crawler.engine.pause()
            return None
        except Exception as e:
            spider.logger.error(f"Error in proxy middleware: {e}")

    def process_response(self, request, response, spider):
        if response.status != 200:
            spider.logger.info(
                f"Request for {request.url} using proxy {request.meta['proxy']}"
                + "failed: response status {response.status}"
            )
            ProxyManager().mark_failure(request.meta.get("proxy"))
            response.meta["proxy"] = ProxyManager().get_url()
            spider.logger.info(f"Retrying with new proxy: {response.meta['proxy']}")
        return response

    def process_exception(self, request, exception, spider):
        proxy = request.meta.get("proxy")
        ProxyManager().mark_failure(proxy)

        spider.logger.info(
            f"Request for {request.url} using proxy {request.meta['proxy']}"
            + "failed: exception occured {exception}"
        )

        request.dont_filter = True
        request.meta["proxy"] = ProxyManager().get_url()
        spider.logger.info(f"Retrying with new proxy: {request.meta['proxy']}")

        return request


class ProxyRefreshMiddleware:
    def __init__(self, crawler):
        self.crawler = crawler
        self.refreshing = False

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        return ext

    def spider_opened(self, spider):
        """Begin by refreshing proxies."""

        # ensureDeferred(ProxyManager().refresh())
        spider.logger.info("[ProxyRefreshMiddleware] Initialising ProxyManager.")
        self.refreshing = True
        self.crawler.engine.pause()
        d = ProxyManager().refresh()  # This must return a Deferred
        d.addCallback(lambda _: self._on_refresh_complete(spider))
        d.addErrback(lambda f: self._on_refresh_failed(spider, f))

        raise spider.dont_close  # Prevent spider from closing

    def spider_idle(self, spider):
        """Pause the engine to refresh proxies when proxies are exhausted."""
        if ProxyManager().needs_to_be_refreshed() and not self.refreshing:
            spider.logger.info(
                "[ProxyRefreshMiddleware] Pausing engine to refresh proxies."
            )
            self.refreshing = True
            self.crawler.engine.pause()
            d = ProxyManager().refresh()
            d.addCallback(lambda _: self._on_refresh_complete(spider))
            d.addErrback(lambda f: self._on_refresh_failed(spider, f))

            raise spider.dont_close

    def _on_refresh_complete(self, spider):
        spider.logger.info(
            "[ProxyRefreshMiddleware] Proxy refresh completed. Resuming engine."
        )
        self.refreshing = False
        self.crawler.engine.unpause()

    def _on_refresh_failed(self, spider, failure):
        spider.logger.error(f"[ProxyRefreshMiddleware] Proxy refresh failed: {failure}")
        self.refreshing = False
        self.crawler.engine.unpause()


# Disable twisted SSL warnings
warnings.filterwarnings("ignore", category=UserWarning, module="twisted")
