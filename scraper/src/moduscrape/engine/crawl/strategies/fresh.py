from ..base import BaseCrawlStrategy


class FreshCrawlStrategy(BaseCrawlStrategy):
    """
    Strategy for performing a fresh crawl from scratch.

    This strategy:
      - Ignores previously seen URLs
      - Starts traversal from the configured entrypoint(s)
      - Yields all links and items matching the current configuration

    Attributes:
        registry (ServiceRegistry):
          - Session-level registry to access preprocessors and state traversal mapping
    """
