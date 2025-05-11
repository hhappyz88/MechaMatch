from toy_catalogue.proxies.proxy import Proxy
from bs4 import BeautifulSoup
import requests
from typing import List, Union
from datetime import datetime, timedelta


def _yes_no_to_bool(yes_or_no: str) -> bool:
    return True if yes_or_no.lower() == "yes" else False


def _last_checked_to_datetime(last_checked: str) -> Union[datetime, None]:
    number = int(last_checked.split(" ")[0])
    unit = last_checked.split(" ")[1]
    if unit in ["sec", "secs", "second", "seconds"]:
        return datetime.now() - timedelta(seconds=number)
    if unit in ["min", "mins", "minute", "minutes"]:
        return datetime.now() - timedelta(minutes=number)
    elif unit in ["hr", "hrs", "hour", "hours"]:
        return datetime.now() - timedelta(hours=number)
    elif unit == "days":
        return datetime.now() - timedelta(days=number)
    else:
        return None


def get_proxy_list() -> List[Proxy]:
    """
    Get a list of proxies from the website
    :return: list of proxies
    :rtype: List[Proxy]
    """
    proxies = []
    try:
        html = requests.get("https://www.sslproxies.org").content
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "table table-striped table-bordered"})
        rows = table.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if len(columns) == 8:
                ip = columns[0].text
                port = columns[1].text
                code = columns[2].text
                country = columns[3].text
                anonymity = True if columns[4].text == "anonymous" else False
                google = _yes_no_to_bool(columns[5].text)
                https = _yes_no_to_bool(columns[6].text)
                last_checked = _last_checked_to_datetime(columns[7].text)
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
