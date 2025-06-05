import pytest
from scrapy.http import TextResponse
from toy_catalogue.engine.extractors.link_extractor import LinkExtractor, LEParams


@pytest.fixture
def simple_response() -> TextResponse:
    html = b"""
    <html><body>
      <a href="page1.html">First</a>
      <a href="page2.html">Second</a>
      <a>Missing href</a>
    </body></html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def test_basic_single_link(simple_response):
    cfg = LEParams.model_validate({})
    urls = LinkExtractor(cfg).extract(simple_response)
    # strip & unique by default
    assert urls == [
        "http://example.com/base/page1.html",
        "http://example.com/base/page2.html",
    ]


def test_basic_missing_href_skipped(simple_response):
    cfg = LEParams.model_validate({})
    urls = LinkExtractor(cfg).extract(simple_response)
    # only two valid hrefs
    assert "Missing href" not in " ".join(urls)


@pytest.fixture
def base_response() -> TextResponse:
    html = b"""
    <html>
      <body>
        <a href="http://foo.com/one.html">One</a>
        <a href="http://bar.com/two.pdf">Two PDF</a>
        <a href="/relative/three.html">Three</a>
        <div class="section">
          <a href="http://foo.com/four.html">Four</a>
          <a href="http://baz.com/five.html?b=2&a=1#frag">Five</a>
        </div>
        <a href="   http://foo.com/six.html   "> Six with spaces </a>
        <a href="http://foo.com/dup.html">Dup</a>
        <a href="http://foo.com/dup.html">Dup</a>
        <img data-href="http://img.com/picture.jpg"/>
      </body>
    </html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def extract(params: dict, response: TextResponse):
    cfg = LEParams.model_validate(params)
    return LinkExtractor(cfg).extract(response)


def test_default_strips_whitespace_and_unique(base_response):
    urls = extract({}, base_response)
    # whitespace stripped, duplicates removed, order preserved
    assert "http://foo.com/six.html" in urls
    assert all(not u.startswith(" ") and not u.endswith(" ") for u in urls)
    assert urls.count("http://foo.com/dup.html") == 1


def test_default_extracts_all(base_response):
    urls = extract({}, base_response)
    expected = {
        "http://foo.com/one.html",
        "http://bar.com/two.pdf",
        "http://example.com/relative/three.html",
        "http://foo.com/four.html",
        "http://baz.com/five.html?a=1&b=2",
        "http://foo.com/six.html",
        "http://foo.com/dup.html",
    }
    assert set(urls) == expected


@pytest.mark.parametrize(
    "allow,expected",
    [
        (r".*one\.html$", ["http://foo.com/one.html"]),
        (
            [r".*three\.html$", r".*four\.html$"],
            ["http://example.com/relative/three.html", "http://foo.com/four.html"],
        ),
    ],
)
def test_allow_regex_filters(allow, expected, base_response):
    urls = extract({"allow": allow}, base_response)
    assert urls == expected


@pytest.mark.parametrize(
    "deny,expected",
    [
        (
            r".*\.pdf$",
            [
                "http://foo.com/one.html",
                "http://example.com/relative/three.html",
                "http://foo.com/four.html",
                "http://baz.com/five.html?a=1&b=2",
                "http://foo.com/six.html",
                "http://foo.com/dup.html",
            ],
        ),
    ],
)
def test_deny_regex_filters(deny, expected, base_response):
    urls = extract({"deny": deny}, base_response)
    assert urls == expected


def test_allow_and_deny_domains_together(base_response):
    urls = extract(
        {"allow_domains": ["foo.com", "baz.com"], "deny_domains": "baz.com"},
        base_response,
    )
    assert set(urls) == {
        "http://foo.com/one.html",
        "http://foo.com/four.html",
        "http://foo.com/six.html",
        "http://foo.com/dup.html",
    }


def test_allow_domains_as_string(base_response):
    urls = extract({"allow_domains": "foo.com"}, base_response)
    assert set(urls) == {
        "http://foo.com/one.html",
        "http://foo.com/four.html",
        "http://foo.com/six.html",
        "http://foo.com/dup.html",
    }


def test_deny_domains_as_list(base_response):
    urls = extract({"deny_domains": ["bar.com", "baz.com"]}, base_response)
    assert all("bar.com" not in u and "baz.com" not in u for u in urls)


def test_deny_extensions_string(base_response):
    urls = extract({"deny_extensions": "pdf"}, base_response)
    assert all(not u.lower().endswith(".pdf") for u in urls)


def test_deny_extensions_multiple(base_response):
    urls = extract({"deny_extensions": ["pdf", "html"]}, base_response)
    assert urls == []


def test_restrict_xpaths_limits_scope(base_response):
    urls = extract({"restrict_xpaths": "//div[@class='section']"}, base_response)
    assert set(urls) == {
        "http://foo.com/four.html",
        "http://baz.com/five.html?a=1&b=2",
    }


def test_restrict_css_limits_scope(base_response):
    urls = extract({"restrict_css": ".section"}, base_response)
    assert set(urls) == {
        "http://foo.com/four.html",
        "http://baz.com/five.html?a=1&b=2",
    }


@pytest.mark.parametrize(
    "text_allow,expected",
    [
        ("^One$", ["http://foo.com/one.html"]),
        ("Six", ["http://foo.com/six.html"]),
    ],
)
def test_restrict_text_filters_by_link_text(text_allow, expected, base_response):
    urls = extract({"restrict_text": text_allow}, base_response)
    assert urls == expected


@pytest.mark.parametrize(
    "text_filters,expected_count",
    [
        (["One", "Three"], 2),
        (["^Four$"], 1),
    ],
)
def test_restrict_text_as_list(base_response, text_filters, expected_count):
    urls = extract({"restrict_text": text_filters}, base_response)
    assert len(urls) == expected_count


def test_custom_tags_and_attrs_extracts_from_img(base_response):
    urls = extract(
        {"deny_extensions": [], "tags": ["img"], "attrs": ["data-href"]}, base_response
    )
    assert urls == ["http://img.com/picture.jpg"]


def test_canonicalize_sorts_query_and_removes_fragment(base_response):
    # explicit canonicalize False preserves fragment and order
    urls_no = extract({"canonicalize": False}, base_response)
    assert any("five.html?b=2&a=1" in u for u in urls_no)
    urls_yes = extract({"canonicalize": True}, base_response)
    assert "http://baz.com/five.html?a=1&b=2" in urls_yes


def test_explicit_unique_flags(base_response):
    # override defaults: disable strip and unique
    params = {"unique": False}
    urls = extract(params, base_response)
    # whitespace preserved and duplicates kept
    assert urls.count("http://foo.com/dup.html") == 2


def test_process_value_applies_callable(base_response):
    urls = extract({"process_value": lambda u: u.lower()}, base_response)
    assert "http://foo.com/one.html" in urls


def test_allow_and_deny_combination(base_response):
    urls = extract({"allow_domains": "foo.com", "deny": r".*one\.html$"}, base_response)
    assert all("foo.com" in u for u in urls)
    assert all(not u.endswith("one.html") for u in urls)


@pytest.fixture
def whitespace_response() -> TextResponse:
    html = b"""
    <html><body>
      <a href="   http://example.com/space.html   ">Space</a>
      <a href="http://example.com/space.html">Duplicate</a>
    </body></html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def test_unique_false_keeps_duplicates(whitespace_response):
    urls = extract({"unique": False}, whitespace_response)
    count = urls.count("http://example.com/space.html")
    assert count == 2  # duplicates kept


def test_unique_true_removes_duplicates(whitespace_response):
    urls = extract({"unique": True}, whitespace_response)
    count = urls.count("http://example.com/space.html")
    assert count == 1  # duplicates removed


@pytest.fixture
def canonicalize_response() -> TextResponse:
    html = b"""
    <html><body>
      <a href="http://example.com/page?b=2&a=1#fragment">Canonical</a>
    </body></html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def test_canonicalize_false_keeps_fragment(canonicalize_response):
    urls = extract({"canonicalize": False}, canonicalize_response)
    assert any("#fragment" in u for u in urls)


@pytest.fixture
def filter_response() -> TextResponse:
    html = b"""
    <html><body>
      <a href="http://example.com/allowed.html">Allowed</a>
      <a href="http://example.com/denied.pdf">Denied PDF</a>
      <a href="http://blocked.com/blocked.html">Blocked Domain</a>
    </body></html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def test_allow_domains_filter(filter_response):
    urls = extract({"allow_domains": ["example.com"]}, filter_response)
    assert all("example.com" in u for u in urls)


def test_deny_domains_filter(filter_response):
    urls = extract({"deny_domains": ["blocked.com"]}, filter_response)
    assert all("blocked.com" not in u for u in urls)


def test_deny_extensions_filter(filter_response):
    urls = extract({"deny_extensions": ["pdf"]}, filter_response)
    assert all(not u.lower().endswith(".pdf") for u in urls)


@pytest.fixture
def restrict_scope_response() -> TextResponse:
    html = b"""
    <html><body>
      <div class="allowed">
        <a href="http://example.com/inside.html">Inside</a>
      </div>
      <a href="http://example.com/outside.html">Outside</a>
    </body></html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def test_restrict_xpath_scope(restrict_scope_response):
    urls = extract(
        {"restrict_xpaths": "//div[@class='allowed']"}, restrict_scope_response
    )
    assert urls == ["http://example.com/inside.html"]


def test_restrict_css_scope(restrict_scope_response):
    urls = extract({"restrict_css": ".allowed"}, restrict_scope_response)
    assert urls == ["http://example.com/inside.html"]


@pytest.fixture
def custom_tag_attr_response() -> TextResponse:
    html = b"""
    <html><body>
      <img data-href="http://example.com/picture.jpg"/>
      <a href="http://example.com/link.html">Link</a>
    </body></html>
    """
    return TextResponse(url="http://example.com/base/", body=html)


def test_custom_tags_and_attrs_extract(custom_tag_attr_response):
    urls = extract({"tags": ["img"], "attrs": ["data-href"]}, custom_tag_attr_response)
    assert urls == ["http://example.com/picture.jpg"]


def test_process_value_callable_applied(filter_response):
    # Make all URLs lowercase
    urls = extract({"process_value": lambda u: u.lower()}, filter_response)
    assert all(u == u.lower() for u in urls)


def test_type_error_on_non_textresponse():
    from scrapy.http import Response

    params = LEParams.model_validate({})
    with pytest.raises(TypeError):
        LinkExtractor(params).extract(Response(url="http://example.com"))


def test_handles_invalid_urls_gracefully():
    html = '<a href="http://example.com/invalid\udc80">Bad Link</a>'.encode(
        "utf-8", "replace"
    )
    response = TextResponse(url="http://example.com", body=html)
    extractor = LinkExtractor(LEParams.model_validate({}))
    urls = []
    try:
        urls = extractor.extract(response)
    except UnicodeEncodeError:
        pytest.fail("Extractor raised UnicodeEncodeError on invalid URL")
    # Assert extractor skipped or handled bad url
    assert all("\udc80" not in url for url in urls)
