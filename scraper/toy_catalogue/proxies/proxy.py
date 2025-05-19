from datetime import datetime


class Proxy:
    def __init__(self, data):
        self._data = data
        self.ip = data.get("ip", None)
        self.port = data.get("port", None)
        self.code = data.get("code", None)
        self.country = data.get("country", None)
        self.anonymity = data.get("anonymity", None)
        self.google = data.get("google", None)
        self.https = data.get("https", None)
        self.last_checked = data.get("last_checked", None)
        self.is_working = False
        self.last_working = None

    @property
    def ip_and_port(self):
        return f"{self.ip}:{self.port}"

    @property
    def url(self):
        return f"http://{self.ip_and_port}"

    @property
    def is_anonymous(self):
        return self.anonymity

    @property
    def requests_dict(self):
        return {"http": self.url, "https:": self.url}

    def mark_working(self):
        self.last_checked = datetime.now()
        self.last_working = datetime.now()
        self.is_working = True

    def mark_not_working(self):
        self.last_checked = datetime.now()
        self.is_working = False
