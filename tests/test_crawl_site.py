import pytest
from unittest.mock import patch, MagicMock
from toy_catalogue.spiders.crawl_site import CrawlSiteSpider
from urllib.parse import urlparse
import os
import shutil


@pytest.fixture
def crawl_site_spider():
    start_url = "http://example.com"
    spider = CrawlSiteSpider(start_url=start_url)
    test_data_dir = "test_data"
    os.makedirs(test_data_dir, exist_ok=True)
    yield spider
    # Remove the test data directory after each test
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)


def test_spider_name(crawl_site_spider: CrawlSiteSpider):
    assert CrawlSiteSpider.name == "crawl_site"


def test_start_url_required():
    with pytest.raises(ValueError):
        CrawlSiteSpider()


def test_start_urls(crawl_site_spider: CrawlSiteSpider):
    start_url = "http://example.com"
    assert crawl_site_spider.start_urls == [start_url]


def test_allowed_domain(crawl_site_spider: CrawlSiteSpider):
    start_url = "http://example.com"
    domain = urlparse(start_url).netloc
    assert crawl_site_spider.allowed_domain == domain


@patch("toy_catalogue.spiders.crawl_site.open", create=True)
@patch("toy_catalogue.spiders.crawl_site.os.makedirs")
def test_parse_saves_html(mock_makedirs, mock_open):
    start_url = "http://example.com"
    spider = CrawlSiteSpider(start_url=start_url)

    mock_response = MagicMock()
    mock_response.url = start_url
    mock_response.body = b"<html>Test HTML</html>"
    mock_response.css.return_value.getall.return_value = []  # No links to follow

    list(spider.parse(mock_response))

    mock_makedirs.assert_called_with("data/example.com", exist_ok=True)
    mock_open.assert_called_with("data/example.com/index", "wb")
    mock_open().__enter__().write.assert_called_with(mock_response.body)


@patch("toy_catalogue.spiders.crawl_site.open", create=True)
@patch("toy_catalogue.spiders.crawl_site.os.makedirs")
def test_parse_follows_internal_links(mock_makedirs, mock_open):
    start_url = "http://example.com"
    spider = CrawlSiteSpider(start_url=start_url)

    # Create a mock response with some internal links
    mock_response = MagicMock()
    mock_response.url = start_url
    mock_response.body = b"""<html><a href='/page1'>Page 1</a>
        <a href='http://external.com/page2'>Page 2</a></html>"""
    mock_response.css.return_value.getall.return_value = [
        "/page1",
        "http://external.com/page2",
    ]
    mock_response.urljoin.side_effect = (
        lambda x: start_url + x if x.startswith("/") else x
    )

    # Patch scrapy.Request to prevent actual requests
    with patch("scrapy.Request") as mock_request:
        # Call the parse method
        list(spider.parse(mock_response))

        # Assert that scrapy.Request was called with the internal link
        mock_request.assert_called_once_with(
            start_url + "/page1", callback=spider.parse
        )
        mock_makedirs.assert_called_with("data/example.com", exist_ok=True)
        mock_open.assert_called_with("data/example.com/index", "wb")
