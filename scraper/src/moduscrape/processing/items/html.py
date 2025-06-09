from ._base import BaseItem
from scrapy.http import Response
from typing import Any


class HtmlItem(BaseItem):
    encoding: str

    @classmethod
    def _extra_from_response(cls, response: Response) -> dict[str, Any]:
        encoding = getattr(response, "encoding", "utf-8")
        return {"encoding": encoding}
