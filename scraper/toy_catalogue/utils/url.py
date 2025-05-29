from urllib.parse import urlparse, urlunparse


def canonicalise_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))
