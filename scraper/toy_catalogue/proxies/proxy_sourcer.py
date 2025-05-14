from bs4 import BeautifulSoup, Tag
import requests
from typing import List
from datetime import datetime, timezone
from toy_catalogue.proxies.proxy import Proxy
from config.config import PROXY_TIMEOUT
import json
import re
import base64
from toy_catalogue.proxies.proxy_loader import load_proxies


def _yes_no_to_bool(yes_or_no: str) -> bool:
    return True if yes_or_no.lower() == "yes" else False


# Some other options:
# https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1
# spys.one/en/http-proxy-list/
# https://www.proxy-list.download/HTTP
# https://www.proxynova.com/proxy-server-list
# https://cyber-gateway.net/get-proxy/free-proxy/24-free-http-proxy
# https://proxydb.net/?protocol=http&protocol=https&offset=1350


def get_proxy_list() -> List[Proxy]:
    """
    Get a list of proxies from the website
    :return: list of proxies
    :rtype: List[Proxy]
    """
    result = (
        get_ssl()
        + load_proxies()
        + get_geonode()
        + get_free_proxy_list()
        + get_proxyscrape()
    )

    return result


# pretty bad got 0/2000
def get_free_proxy() -> list[Proxy]:
    proxies: list[Proxy] = []
    seen: set[str] = set()
    prev_len = -1
    index = 1
    url = f"http://free-proxy.cz/en/proxylist/country/all/all/ping/all/{index}"
    response = requests.get(url)
    try:
        while response.status_code == 200:
            if len(seen) <= prev_len:
                break
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"id": "proxy_list"})
            if not isinstance(table, Tag):
                raise Exception("invalid response")
            body = table.find_all("tbody")[0]
            if not isinstance(body, Tag):
                raise Exception("invalid response")
            rows = body.find_all("tr")
            for row in rows:
                if isinstance(row, Tag):
                    js = row.find_all("script")[0]
                    if not isinstance(js, Tag):
                        continue
                    encoded_ip = re.search(
                        r'Base64\.decode\(\s*["\']([^"\']+)["\']\s*\)', js.text
                    )
                    if not encoded_ip:
                        continue
                    ip = base64.b64decode(encoded_ip.group(1)).decode("utf-8")
                    columns = row.find_all("td")
                    if isinstance(columns, Tag):
                        port = columns[1].text
                        country = columns[3].text
                        anonymity = columns[6].text
                        last_checked = datetime.now(timezone.utc).isoformat()
                        if f"{ip}:{port}" in seen:
                            continue
                        seen.add(f"{ip}:{port}")
                        data = {
                            "ip": ip,
                            "port": port,
                            "country": country,
                            "anomymity": anonymity,
                            "last_checked": last_checked,
                        }
                        proxies.append(Proxy(data=data))
            index += 1
            prev_len = len(seen)
            url = f"http://free-proxy.cz/en/proxylist/country/all/all/ping/all/{index}"
            response = requests.get(url)

    except Exception as e:
        print("error occured", e)
    finally:
        return proxies


# 12/500
def get_geonode() -> list[Proxy]:
    proxies = []
    index = 1
    url = f"https://proxylist.geonode.com/api/proxy-list?protocols=http%2Chttps&limit=500&page={index}&sort_by=lastChecked&sort_type=desc"
    response = requests.get(url)
    try:
        while response.status_code == 200:
            text = json.loads(response.text)["data"]
            if len(text) == 0:
                break
            for proxy in text:
                data = {
                    "ip": proxy["ip"],
                    "port": proxy["port"],
                    "code": proxy["country"],
                    "anonymity": proxy["anonymityLevel"],
                    "google": proxy["google"],
                    "last_checked": datetime.now(timezone.utc).isoformat(),
                }
                proxies.append(Proxy(data))
            index += 1
            url = f"https://proxylist.geonode.com/api/proxy-list?protocols=http%2Chttps&limit=500&page={index}&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url)
    finally:
        return proxies


# 20/186
def get_proxyscrape() -> list[Proxy]:
    proxies = []
    try:
        url = f"https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http,https&proxy_format=protocolipport&format=text&timeout={PROXY_TIMEOUT*1000}"
        response = requests.get(url).text.strip().split("\r\n")
        for proxy in response:
            ip_port = proxy.split(":")
            data = {
                "ip": ip_port[1].strip("/"),
                "port": ip_port[2],
                "country": "all",
                "anonymity": "all",
                "last_checked": datetime.now(timezone.utc).isoformat(),
            }
            proxies.append(Proxy(data))
    finally:
        return proxies


# 10-40/100
def get_ssl() -> list[Proxy]:
    proxies = []
    try:
        html = requests.get("https://www.sslproxies.org").content
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "table table-striped table-bordered"})
        if isinstance(table, Tag):
            rows = table.find_all("tr")
            for row in rows:
                if isinstance(row, Tag):
                    columns = row.find_all("td")
                    if len(columns) == 8:
                        ip = columns[0].text
                        port = columns[1].text
                        code = columns[2].text
                        country = columns[3].text
                        anonymity = True if columns[4].text == "anonymous" else False
                        google = _yes_no_to_bool(columns[5].text)
                        https = _yes_no_to_bool(columns[6].text)
                        last_checked = datetime.now(timezone.utc).isoformat()
                        data = {
                            "ip": ip,
                            "port": port,
                            "code": code,
                            "country": country,
                            "anonymity": anonymity,
                            "google": google,
                            "https": https,
                            "last_checked": last_checked,
                        }
                        proxies.append(Proxy(data=data))
    except requests.exceptions.RequestException:
        pass
    return proxies


# 26/300
def get_free_proxy_list() -> list[Proxy]:
    proxies = []
    try:
        html = requests.get("https://free-proxy-list.net/").content
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "table table-striped table-bordered"})
        if isinstance(table, Tag):
            rows = table.find_all("tr")
            for row in rows:
                if isinstance(row, Tag):
                    columns = row.find_all("td")
                    if len(columns) == 8:
                        ip = columns[0].text
                        port = columns[1].text
                        code = columns[2].text
                        country = columns[3].text
                        anonymity = True if columns[4].text == "anonymous" else False
                        google = _yes_no_to_bool(columns[5].text)
                        https = _yes_no_to_bool(columns[6].text)
                        last_checked = datetime.now(timezone.utc).isoformat()
                        data = {
                            "ip": ip,
                            "port": port,
                            "code": code,
                            "country": country,
                            "anonymity": anonymity,
                            "google": google,
                            "https": https,
                            "last_checked": last_checked,
                        }
                        proxies.append(Proxy(data=data))
    except requests.exceptions.RequestException:
        pass
    return proxies
