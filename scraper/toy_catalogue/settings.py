# Scrapy settings for toy_catalogue project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

#############################################################################
###################### FUNDAMENTAL CONFIGURATION ############################
BOT_NAME = "toy_catalogue"

SPIDER_MODULES = ["toy_catalogue.spiders"]
NEWSPIDER_MODULE = "toy_catalogue.spiders"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
ROBOTSTXT_OBEY = False
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "timeout": 10000,  # Example: 60 seconds
}
#################################################################################
############################### RETRY ###########################################
# Retry on failed proxies
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 403]

CLOSESPIDER_TIMEOUT = 0
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
CLOSESPIDER_ERRORCOUNT = 0

##################################################################################
################################# SPEED ##########################################
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1
# CONCURRENT_REQUESTS_PER_DOMAIN = 8

#  Configurea delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 60

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
AUTOTHROTTLE_DEBUG = False


# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True


# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware": None,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 110,
    "toy_catalogue.middlewares.JhaoProxyMiddleware": 500,
    "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": 543,
    "toy_catalogue.middlewares.AllowImagesOffsiteMiddleware": 542,
}
JHAO_PROXY_API_URL = "http://localhost:5010"
JHAO_PROXY_TYPE = "https"  # or 'http' or 'socks5' if your pool supports it
JHAO_PROXY_MIN_SCORE = 5  # adjust based on your pool's proxy quality
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#     # "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     # 'toy_catalogue.pipelines.HtmlDownloadPipeline': 100,
#     # 'toy_catalogue.pipelines.ImagesDownloadPipeline': 200,
# }

IMAGES_STORE = "data/miscellaneous"

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

FEED_EXPORT_ENCODING = "utf-8"
DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"

#######################################################################################
#################################### DEBUGGING AND LOGGING ############################
# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True
LOG_STDOUT = True
LOG_LEVEL = "DEBUG"


def silence_scrapy_logs():
    # logging.getLogger().setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("scrapy_user_agents.middlewares").setLevel(logging.INFO)
    # logging.getLogger("scrapy.core.downloader.tls").setLevel(logging.ERROR)
    # logging.getLogger("scrapy.core.engine").setLevel(logging.INFO)
    # logging.getLogger(
    #     "scrapy_user_agents.middlewares.RandomUserAgentMiddleware"
    # ).setLevel(logging.INFO)
    # logging.getLogger("toy_catalogue.middlewares.DynamicProxyMiddleware").setLevel(
    #     logging.INFO
    # )
    pass


# DOWNLOADER_CLIENT_TLS_VERIFY = False
DOWNLOADER_CLIENT_TLS_METHOD = "TLS"
# DOWNLOADER_CLIENT_TLS_VERBOSE_LOGGING = True


DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"
