import requests  # type: ignore
import random
from requests.exceptions import RequestException  # type: ignore
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List


def validate_proxy(proxy: str):
    try:
        response = requests.get(
            "http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5
        )

        if response.status_code == 200:
            print(f"✅ Proxy {proxy} is working.")
            return proxy, True
        else:
            print(f"❌ Proxy {proxy} returned status code {response.status_code}.")
            return proxy, False
    except RequestException as e:
        print(f"❌ Proxy {proxy} failed: {e}")
        return proxy, False


def get_working_proxies(preexisting=[]):
    try:
        proxy_list_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all"
        proxies = preexisting + [
            f"http://{proxy}"
            for proxy in requests.get(proxy_list_url).text.rstrip().split("\r\n")
        ]
        print(f"Scraped {len(proxies)} proxies")

        working = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {
                executor.submit(validate_proxy, proxy): proxy for proxy in proxies
            }
            for future in as_completed(future_to_proxy):
                proxy, is_valid = future.result()
                if is_valid:
                    working.append(proxy)
        return working
    except RequestException:
        print("Proxy list unavailable")
        return []


def save_proxies(proxies: List[str]):
    with open("data/proxies.txt", "w") as f:
        f.write("\n".join(proxies))
        f.close()


class ProxyPool:
    def __init__(
        self,
        proxies: list[str],
        max_score=5,
        min_score=-3,
        failure_penalty=1,
        success_gain=1,
    ):
        self.proxies = {proxy: max_score for proxy in proxies}
        self.max_score = max_score
        self.min_score = min_score
        self.failure_penalty = failure_penalty
        self.success_gain = success_gain

    def get(self):
        valid = [p for p, v in self.proxies.items() if v > self.min_score]
        if not valid:
            raise Exception("No valid proxies")
        return random.choice(valid)

    def mark_success(self, proxy: str):
        if proxy in self.proxies:
            self.proxies[proxy] = min(
                self.max_score, self.proxies[proxy] + self.success_gain
            )

    def mark_failure(self, proxy: str):
        if proxy in self.proxies:
            self.proxies[proxy] -= self.failure_penalty
            if self.proxies[proxy] <= self.min_score:
                del self.proxies[proxy]

    def update(self):
        new_proxies = get_working_proxies(self.proxies)
        self.proxies = {proxy: self.max_score for proxy in new_proxies}


if __name__ == "__main__":
    proxies = get_working_proxies()
    print(len(proxies))
    save_proxies(proxies)
