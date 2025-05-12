from twisted.internet.defer import DeferredSemaphore, DeferredList
from twisted.web.client import ProxyAgent, Response
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.web.http_headers import Headers
from twisted.internet import reactor as _reactor
from twisted.internet.interfaces import IReactorTime
from twisted.python.failure import Failure
from tqdm import tqdm
from typing import cast
import logging
from scraper.toy_catalogue.proxies.proxy import Proxy

logger = logging.getLogger(__name__)
reactor = cast(IReactorTime, _reactor)


def check_proxy(proxy: Proxy, test_url="https://httpbingo.org/ip", timeout=1):
    endpoint = TCP4ClientEndpoint(reactor, proxy.ip, int(proxy.port))
    agent = ProxyAgent(endpoint)
    headers = Headers({"User-Agent": ["Scrapy"]})
    d = agent.request(b"GET", test_url.encode(), headers)

    timeout_triggered = [False]

    def on_timeout():
        if not d.called:
            timeout_triggered[0] = True
            d.cancel()
        proxy.mark_not_working()

    timeout_call = reactor.callLater(timeout, on_timeout)

    def resolve(value):
        if timeout_call.active():
            timeout_call.cancel()
        return value

    def handle_success(response: Response):
        if timeout_triggered[0]:
            return proxy
        if response.code == 200:
            proxy.mark_working()
        else:
            proxy.mark_not_working()
        return proxy

    def handle_error(failure: Failure):
        if timeout_triggered[0]:
            return proxy
        proxy.mark_not_working()
        return proxy

    d.addCallback(handle_success)
    d.addErrback(handle_error)
    d.addBoth(resolve)  # Ensure the timeout is always handled correctly

    return d


def check_proxies(proxies, concurrency=10):
    sem = DeferredSemaphore(concurrency)
    progress = tqdm(total=len(proxies), desc="Checking proxies", leave=True)

    def run(proxy):
        def wrapped():
            d = check_proxy(proxy)

            def advance(result):
                progress.update(1)
                return result

            return d.addBoth(advance)

        return sem.run(wrapped)

    tasks = [run(p) for p in proxies]
    dlist = DeferredList(tasks, consumeErrors=True)

    def _on_complete(results):
        progress.close()
        successful = [
            r[1] for r in results if r[0] and type(r[1]) is Proxy and r[1].is_working
        ]
        logger.info(f"{len(results) - len(successful)} proxies failed.")
        return successful

    d = dlist.addCallback(_on_complete)

    def _close_and_pass(result):
        progress.close()
        return result

    d.addBoth(_close_and_pass)
    return d
