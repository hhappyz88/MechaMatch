from urllib.parse import urlparse, urlunparse
import hashlib


def canonicalise_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))


def generate_id(url: str) -> str:
    return urlparse(url).path.replace("/", "_").lstrip("_")


def make_safe_folder_name(
    long_name: str, prefix_len: int = 20, hash_len: int = 8
) -> str:
    # Truncate to prefix_len characters (replace spaces etc. if you want)
    prefix = long_name[:prefix_len].rstrip().replace(" ", "_")
    # Generate short hash of full string
    h = hashlib.sha256(long_name.encode("utf-8")).hexdigest()[:hash_len]
    # Combine prefix and hash
    return f"{prefix}_{h}"
