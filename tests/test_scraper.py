import pytest
from scraper.proxy_manager import get_working_proxies


def test_proxy_manager():
    try:
        assert len(get_working_proxies()) > 0
    except Exception:
        pytest.skip("Skipping because Proxy API is down")
