import pytest
from scrapy.http import TextResponse
from toy_catalogue.spiders.extractors.css import (
    CssGetExtractor,
    CssGetAllExtractor,
    CssParams,
)


@pytest.fixture
def sample_response() -> TextResponse:
    html = b'<html><body><img src="image1.jpg"/><img src="image2.jpg"/></body></html>'
    return TextResponse(url="http://example.com", body=html)


@pytest.fixture
def sample_config() -> CssParams:
    return CssParams.model_validate({"selectors": ["img"], "attrs": ["src"]})


def test_css_get_single_selector(sample_response, sample_config):
    extractor = CssGetExtractor(sample_config)
    result = extractor.extract(sample_response)
    assert result == [sample_response.urljoin(img) for img in ["image1.jpg"]]


def test_css_getall_single_selector(sample_response, sample_config):
    extractor = CssGetAllExtractor(sample_config)
    result = extractor.extract(sample_response)
    assert result == [
        sample_response.urljoin(img) for img in ["image1.jpg", "image2.jpg"]
    ]


def test_css_get_missing_attr(sample_config):
    html = b'<html><body><img/><img src="image.jpg"/></body></html>'
    response = TextResponse(url="http://example.com", body=html)
    extractor = CssGetExtractor(sample_config)
    result = extractor.extract(response)
    assert result == [response.urljoin(img) for img in ["image.jpg"]]
