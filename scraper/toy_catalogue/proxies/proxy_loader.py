import os


def load_proxies() -> list:
    """
    Load proxies from a file and return them as a list.
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    with open(os.path.join(__location__, "proxies.txt"), "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies


def save_proxies(proxy_urls: list):
    """
    Save a list of proxies to a file.
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    with open(os.path.join(__location__, "proxies.txt"), "w") as file:
        for proxy in proxy_urls:
            file.write(f"{proxy}\n")
