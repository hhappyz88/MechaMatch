import types
import pytest
import requests
from moduscrape.middlewares import JhaoProxyMiddleware  # adjust import path
import random
from typing import Any


# --- helpers -------------------------------------------------------------
class MockProxyClient:
    """In-memory stand-in for jhao API."""

    banned: list[str]

    def __init__(self):
        self.fetch_calls = 0
        self.banned = []
        # a rotating pool we control
        self.pool = ["1.1.1.1:8000", "2.2.2.2:9000", "3.3.3.3:7000"]

    def fetch_batch(self, limit=50):
        self.fetch_calls += 1
        # return up to 'limit' items, wrap if necessary
        batch = random.sample(self.pool, k=min(limit, len(self.pool)))
        return [f"http://{p}" for p in batch]

    def ban(self, ip_port):
        self.banned.append(ip_port)


class DummySpider:
    name = "dummy"

    def __init__(self):
        self.logger = types.SimpleNamespace(
            info=lambda *a, **k: None,
            debug=lambda *a, **k: None,
            warning=lambda *a, **k: None,
        )


class DummyResponse:
    def __init__(self, url: str = "https://example.com", status: int = 200):
        self.url = url
        self.status = status


class DummyRequest:
    def __init__(self, url: str = "https://example.com"):
        self.url = url
        self.dont_filter = False
        self.meta: dict[str, Any] = {}

    def copy(self):
        r = DummyRequest(self.url)
        r.meta = dict(self.meta)
        r.dont_filter = True
        return r


# --- fixtures ------------------------------------------------------------


@pytest.fixture(autouse=True)
def requests_mock(monkeypatch):
    """Intercept outbound requests.get inside JhaoProxyMiddleware"""
    calls = {"ban": [], "all": []}

    def fake_get(url, params=None, timeout=5):
        if url.endswith("/all"):
            calls["all"].append((url, params))
            # Return two dummy proxies
            data = ["1.1.1.1:8000", "2.2.2.2:9000"]
            return types.SimpleNamespace(json=lambda: data, status_code=200)
        elif url.endswith("/ban"):
            calls["ban"].append(params["proxy"])
            return types.SimpleNamespace(status_code=200)
        raise RuntimeError("Unexpected URL")

    monkeypatch.setattr(requests, "get", fake_get)
    yield calls


@pytest.fixture
def mw():
    proxy_client = MockProxyClient()
    m = JhaoProxyMiddleware(proxy_client=proxy_client)
    spider = DummySpider()
    m.spider_opened(spider)
    return m, proxy_client


# -----------------------------------------------------------
def test_first_request_uses_cached_proxy(mw):
    middleware, client = mw
    spider = DummySpider()
    r = DummyRequest()
    middleware.process_request(r, spider)

    assert "proxy" in r.meta
    assert client.fetch_calls == 1  # one batch call
    assert r.meta["proxy"].startswith("http://")


def test_rotates_on_429_and_bans(mw):
    """A 429 response should trigger a retry *and* ban the old proxy."""
    middleware, client = mw
    spider = DummySpider()

    # ➊ First request assigns a proxy
    req1 = DummyRequest()
    middleware.process_request(req1, spider)
    first_proxy = req1.meta["proxy"]

    # ➋ Feed a 429 response
    retry_req = middleware.process_response(req1, DummyResponse(status=429), spider)

    # ➌ Assertions
    assert isinstance(retry_req, DummyRequest)  # a new request is returned
    assert "proxy" not in retry_req.meta  # it has no proxy yet
    assert first_proxy.replace("http://", "") in client.banned


def test_refresh_interval_forces_second_fetch(mw):
    """Forcing a cache refresh should increment fetch_calls."""
    middleware, client = mw
    spider = DummySpider()

    # ➊ Initial request loads cache → fetch_calls == 1
    middleware.process_request(DummyRequest(), spider)
    assert client.fetch_calls == 1

    # ➋ Force a manual refresh (simulate time passing)
    middleware._refresh_cache(spider, force=True)

    # ➌ Any new request should now use the refreshed cache
    middleware.process_request(DummyRequest(), spider)
    assert client.fetch_calls == 2
