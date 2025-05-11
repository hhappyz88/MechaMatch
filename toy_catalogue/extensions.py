from scrapy import signals
from toy_catalogue.proxies.proxy_manager import ProxyManager


class ProxyRefreshExtension:
    def __init__(self, crawler):
        self.crawler = crawler
        self.refreshing = False

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        return ext

    def spider_idle(self, spider):
        pm = ProxyManager()
        if pm.needs_to_be_refreshed() and not self.refreshing:
            spider.logger.info("[ProxyRefresh] Refreshing proxies...")
            self.refreshing = True
            self.crawler.engine.pause()
            pm.reset_refresh_event()
            pm.refresh().addCallback(lambda _: self._resume(spider))

            raise spider.dont_close

    def _resume(self, spider):
        spider.logger.info("[ProxyRefresh] Resuming engine.")
        self.refreshing = False
        self.crawler.engine.unpause()
