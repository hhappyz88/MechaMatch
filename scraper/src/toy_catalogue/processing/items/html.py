from ._base import BaseItem
from scrapy.http import Response
from urllib.parse import urlparse


class HtmlItem(BaseItem):
    encoding: str

    @classmethod
    def from_response(cls, response: Response, state: str) -> "BaseItem":
        encoding = getattr(response, "encoding", None)
        if not isinstance(encoding, str):
            encoding = "utf-8"
        return cls(
            id=urlparse(response.url).path.replace("/", "_").lstrip("_"),
            state=state,
            url=response.url,
            content=response.body,
            encoding=encoding,
            metadata={
                "url": response.url,
                "status": response.status,
                "headers": {
                    k.decode(): [v.decode() for v in vs]
                    for k, vs in response.headers.items()
                },
            },
        )
