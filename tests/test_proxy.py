import requests
from toy_catalogue.proxy_manager import (
    ProxyPool,
    validate_proxy,
    save_proxies,
)
from unittest.mock import mock_open


def test_validate_proxy(mocker):
    """Test that validate_proxy function correctly validates a proxy."""
    # Mock a successful response
    mocker.patch("requests.get", return_value=mocker.Mock(status_code=200))
    proxy, is_valid = validate_proxy("http://valid.proxy:8080")
    assert is_valid is True

    # Mock a failed response (status code 500)
    mocker.patch("requests.get", return_value=mocker.Mock(status_code=500))
    proxy, is_valid = validate_proxy("http://invalid.proxy:8080")
    assert is_valid is False

    # Mock a RequestException
    mocker.patch(
        "requests.get", side_effect=requests.exceptions.RequestException("Timeout")
    )
    proxy, is_valid = validate_proxy("http://timeout.proxy:8080")
    assert is_valid is False


def test_save_proxies(mocker):
    """Test that save_proxies function correctly saves proxies to a file."""
    proxies = ["http://proxy1:8080", "http://proxy2:8080"]
    mocked_open = mocker.patch("builtins.open", new_callable=mock_open)
    save_proxies(proxies)
    mocked_open.assert_called_once_with("data/proxies.txt", "w")
    handle = mocked_open()
    handle.write.assert_called_once_with("\n".join(proxies))


def test_proxy_pool_init():
    """Test that ProxyPool is initialized correctly."""
    proxies = ["http://proxy1:8080", "http://proxy2:8080"]
    proxy_pool = ProxyPool(
        proxies, max_score=5, min_score=-3, failure_penalty=1, success_gain=1
    )
    assert proxy_pool.proxies == {proxy: 5 for proxy in proxies}
    assert proxy_pool.max_score == 5
    assert proxy_pool.min_score == -3
    assert proxy_pool.failure_penalty == 1
    assert proxy_pool.success_gain == 1


def test_proxy_pool_get():
    """Test that ProxyPool.get() returns a proxy."""
    proxies = ["http://proxy1:8080", "http://proxy2:8080"]
    proxy_pool = ProxyPool(
        proxies, max_score=5, min_score=-3, failure_penalty=1, success_gain=1
    )
    proxy = proxy_pool.get()
    assert proxy in proxies


def test_proxy_pool_mark_success():
    """Test that ProxyPool.mark_success() marks a proxy as successful."""
    proxies = ["http://proxy1:8080"]
    proxy_pool = ProxyPool(
        proxies, max_score=5, min_score=-3, failure_penalty=1, success_gain=1
    )
    proxy_pool.mark_success("http://proxy1:8080")
    assert proxy_pool.proxies["http://proxy1:8080"] == 5
    proxy_pool.mark_success("http://proxy1:8080")
    assert proxy_pool.proxies["http://proxy1:8080"] == 5


def test_proxy_pool_mark_failure():
    """Test that ProxyPool.mark_failure() marks a proxy as failed."""
    proxies = ["http://proxy1:8080"]
    proxy_pool = ProxyPool(
        proxies, max_score=5, min_score=-3, failure_penalty=2, success_gain=1
    )
    proxy_pool.mark_failure("http://proxy1:8080")
    assert proxy_pool.proxies["http://proxy1:8080"] == 3
    proxy_pool.mark_failure("http://proxy1:8080")
    proxy_pool.mark_failure("http://proxy1:8080")
    proxy_pool.mark_failure("http://proxy1:8080")
    assert "http://proxy1:8080" not in proxy_pool.proxies


def test_proxy_pool_mark():
    """Test that ProxyPool.mark_failure() marks a proxy as failed."""
    proxies = ["http://proxy1:8080"]
    proxy_pool = ProxyPool(
        proxies, max_score=5, min_score=-3, failure_penalty=2, success_gain=1
    )
    proxy_pool.mark_failure("http://proxy1:8080")
    assert proxy_pool.proxies["http://proxy1:8080"] == 3
    proxy_pool.mark_success("http://proxy1:8080")
    assert proxy_pool.proxies["http://proxy1:8080"] == 4


def test_proxy_pool_update(mocker):
    """Test that ProxyPool.update() updates the proxy list."""
    proxies = ["http://proxy1:8080", "http://proxy2:8080"]
    proxy_pool = ProxyPool(
        proxies, max_score=5, min_score=-3, failure_penalty=1, success_gain=1
    )
    mocker.patch(
        "toy_catalogue.proxy_manager.get_working_proxies",
        return_value=["http://proxy3:8080", "http://proxy4:8080"],
    )
    proxy_pool.update()
    assert proxy_pool.proxies == {"http://proxy3:8080": 5, "http://proxy4:8080": 5}
