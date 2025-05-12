# domain_utils.py

import hashlib
import requests
from requests.exceptions import RequestException


class DomainUtils:
    @staticmethod
    def hash_content(domain):
        try:
            r = requests.get(f"https://{domain}", timeout=5)
            content = r.text.strip()
            return hashlib.sha256(content.encode()).hexdigest()
        except RequestException:
            return None

    @staticmethod
    def is_alias_via_content(domain1, domain2):
        return DomainUtils.hash_content(domain1) == DomainUtils.hash_content(domain2)
