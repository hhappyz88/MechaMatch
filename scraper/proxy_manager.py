import requests  # type: ignore
import random
from requests.exceptions import RequestException  # type: ignore
from concurrent.futures import ThreadPoolExecutor, as_completed


def validate_proxy(proxy):
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
        proxy_list_url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
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


def save_proxies(proxies):
    with open("data/proxies.txt", "w") as f:
        f.write("\n".join(proxies))
        f.close()


class ProxyPool:
    def __init__(self, max_score=5, min_score=-3):
        with open("proxy_list.txt", "r") as f:
            self.proxies = {proxy: 5 for proxy in f.read().split("\n")}
            f.close()
        self.max_score = max_score
        self.min_score = min_score
        if len(self.proxies) < 10:
            self.proxies = get_working_proxies(self.proxies)
            save_proxies(self.proxies)

    def get(self):
        good = [p for p, v in self.proxies.items() if v["score"] >= 0]
        return random.choice(good)

    def remove(self, proxy):
        self.proxies.pop(proxy)
        if len(self.proxies) < 10:
            self.proxies = get_working_proxies(self.proxies)
            save_proxies(self.proxies)

    def mark_success(self, proxy):
        if proxy in self.proxies:
            self.proxies[proxy] = min(self.max_score, self.proxies[proxy] + 1)

    def mark_failure(self, proxy):
        if proxy in self.proxies:
            self.proxies[proxy] -= 2
            if self.proxies[proxy] < self.min_score:
                self.remove(proxy)


if __name__ == "__main__":
    proxies = get_working_proxies()
    print(len(proxies))
    save_proxies(proxies)
