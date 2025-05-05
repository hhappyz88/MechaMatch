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
    with open("proxies.txt", "w") as f:
        f.write("\n".join(proxies))
        f.close()


class ProxyPool:
    def __init__(self):
        with open("proxy_list.txt", "r") as f:
            self.proxies = f.read().split("\n")
            f.close()
        if len(self.proxies) < 10:
            self.proxies = get_working_proxies(self.proxies)
            save_proxies(self.proxies)

    def get(self):
        return random.choice(self.proxies)

    def delete(self, proxy):
        self.proxies.remove(proxy)
        if len(self.proxies) < 10:
            self.proxies = get_working_proxies(self.proxies)
            save_proxies(self.proxies)


if __name__ == "__main__":
    proxies = get_working_proxies()
    print(len(proxies))
    save_proxies(proxies)
