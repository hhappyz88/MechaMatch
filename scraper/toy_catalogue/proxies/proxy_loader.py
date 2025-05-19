import os
from toy_catalogue.proxies.proxy import Proxy
import json


def load_proxies() -> list[Proxy]:
    """
    Load proxies from a file and return them as a list.
    """
    try:
        with open(os.path.join("scraper", "config", "proxies.json"), "r") as file:
            proxies = [Proxy(data) for data in json.load(file)]
        return proxies
    except Exception as e:
        print(f"Exception occured: {e} occured")
        return []


def save_proxies(proxies: list[Proxy]):
    """
    Save a list of proxies to a file.
    """
    try:
        with open(os.path.join("scraper", "config", "proxies.json"), "w") as f:
            json.dump([proxy._data for proxy in proxies], f, indent=2)
    except Exception as e:
        print(f"Exception occured: {e} occured")
