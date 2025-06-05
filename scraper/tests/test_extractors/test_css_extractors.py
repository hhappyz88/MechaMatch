import pytest
from scrapy.http import TextResponse
from toy_catalogue.engine.extractors.css import (
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


@pytest.fixture
def response_with_mixed_elements() -> TextResponse:
    html = b"""
    <html>
        <body>
            <img src="img1.jpg" data-src="fallback1.jpg"/>
            <div class="product" data-src="fallback2.jpg"></div>
            <img data-src="img2.jpg"/>
            <script src="script.js"></script>
        </body>
    </html>
    """
    return TextResponse(url="http://example.com", body=html)


@pytest.fixture
def multi_selector_multi_attr_config() -> CssParams:
    return CssParams.model_validate(
        {"selectors": ["img", "div.product", "script"], "attrs": ["src", "data-src"]}
    )


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


def test_cross_product_extraction(
    response_with_mixed_elements, multi_selector_multi_attr_config
):
    extractor = CssGetAllExtractor(multi_selector_multi_attr_config)
    result = extractor.extract(response_with_mixed_elements)
    expected = [
        "http://example.com/img1.jpg",  # img[src]
        "http://example.com/fallback1.jpg",  # img[data-src]
        "http://example.com/fallback2.jpg",  # div[data-src]
        "http://example.com/img2.jpg",  # img[data-src]
        "http://example.com/script.js",  # script[src]
    ]
    assert set(result) == set(expected)


def test_empty_selectors_returns_empty(sample_response: TextResponse):
    config = CssParams.model_validate({"selectors": [], "attrs": ["src"]})
    extractor = CssGetAllExtractor(config)
    assert extractor.extract(sample_response) == []


def test_empty_attrs_returns_empty(sample_response: TextResponse):
    config = CssParams.model_validate({"selectors": ["img"], "attrs": []})
    extractor = CssGetAllExtractor(config)
    assert extractor.extract(sample_response) == []


def test_no_matching_elements_returns_empty():
    html = b"<html><body><p>No match here</p></body></html>"
    response = TextResponse(url="http://example.com", body=html)
    config = CssParams.model_validate({"selectors": ["img"], "attrs": ["src"]})
    extractor = CssGetAllExtractor(config)
    assert extractor.extract(response) == []


def test_malformed_html_is_handled_gracefully():
    html = b"<html><body><img src='bad.jpg><img src=missingquote.jpg></body>"
    response = TextResponse(url="http://example.com", body=html)
    config = CssParams.model_validate({"selectors": ["img"], "attrs": ["src"]})
    extractor = CssGetAllExtractor(config)
    result = extractor.extract(response)
    # Depending on how strict lxml is, this may yield 1 or 2 — but should not crash
    assert isinstance(result, list)


def test_handles_relative_and_absolute_paths():
    html = b"""
    <html><body>
        <img src="relative1.jpg"/>
        <img src="/relative2.jpg"/>
        <img src="http://cdn.example.com/absolute.jpg"/>
    </body></html>
    """
    response = TextResponse(url="http://example.com", body=html)
    config = CssParams.model_validate({"selectors": ["img"], "attrs": ["src"]})
    extractor = CssGetAllExtractor(config)
    result = extractor.extract(response)
    assert result == [
        "http://example.com/relative1.jpg",
        "http://example.com/relative2.jpg",
        "http://cdn.example.com/absolute.jpg",
    ]


def test_duplicates_are_preserved():
    html = b"""
    <html><body>
        <img src="duplicate.jpg"/>
        <img src="duplicate.jpg"/>
    </body></html>
    """
    response = TextResponse(url="http://example.com", body=html)
    config = CssParams.model_validate({"selectors": ["img"], "attrs": ["src"]})
    extractor = CssGetAllExtractor(config)
    result = extractor.extract(response)
    assert result == [
        "http://example.com/duplicate.jpg",
        "http://example.com/duplicate.jpg",
    ]
