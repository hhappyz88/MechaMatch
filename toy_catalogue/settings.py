# Scrapy settings for toy_catalogue project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging

BOT_NAME = "toy_catalogue"

SPIDER_MODULES = ["toy_catalogue.spiders"]
NEWSPIDER_MODULE = "toy_catalogue.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "toy_catalogue (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16
# CONCURRENT_REQUESTS_PER_DOMAIN = 8

#  Configurea delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 15

# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "toy_catalogue.middlewares.ToyCatalogueSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
    # "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 110,
    "toy_catalogue.middlewares.DynamicProxyMiddleware": 610,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
}

EXTENSIONS = {
    # 'toy_catalogue.extensions.ProxyRefreshExtension': 500,
    "toy_catalogue.middlewares.ProxyRefreshMiddleware": 501,
}

# Retry on failed proxies
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 403, 429]
# HTTPERROR_ALLOWED_CODES = [429]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "toy_catalogue.pipelines.ToyCataloguePipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"

# LOG_LEVEL = "INFO"
LOG_STDOUT = True

logging.getLogger("httpx").setLevel(logging.WARNING)
""" import logging
logging.getLogger("scrapy_user_agents.middlewares").setLevel(logging.INFO)
logging.getLogger("scrapy.core.engine").setLevel(logging.INFO)
logging.getLogger("scrapy.downloadermiddlewares.offsite").setLevel(logging.INFO)
logging.getLogger("scrapy.downloadermiddlewares.redirect").setLevel(logging.INFO) """

# import logging
# from toy_catalogue.logging_filters import HTTP429Filter

# # Attach the filter to the Scrapy core logger
# scrapy_logger = logging.getLogger("scrapy.core.engine")
# scrapy_logger.addFilter(HTTP429Filter())

DOWNLOADER_CLIENT_TLS_METHOD = "TLS"
DOWNLOADER_CLIENT_TLS_VERIFY = False

CLOSESPIDER_TIMEOUT = 0
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
CLOSESPIDER_ERRORCOUNT = 0
