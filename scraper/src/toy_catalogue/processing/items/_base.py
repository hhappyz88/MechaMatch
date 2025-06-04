from pydantic import BaseModel, Field
from typing import Any
from scrapy.http import Response
from urllib.parse import urlparse


class BaseItem(BaseModel):
    id: str
    state: str
    url: str
    content: bytes
    metadata: dict[str, Any] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(state={self.state!r}, "
            f"url={self.url!r}, content={type(self.content).__name__})"
        )

    @classmethod
    def from_response(cls, response: Response, state: str) -> "BaseItem":
        return cls(
            id=urlparse(response.url).path.replace("/", "_").lstrip("_"),
            state=state,
            url=response.url,
            content=response.body,
            metadata={
                "url": response.url,
                "status": response.status,
                "headers": {
                    k.decode(): [v.decode() for v in vs]
                    for k, vs in response.headers.items()
                },
            },
        )
