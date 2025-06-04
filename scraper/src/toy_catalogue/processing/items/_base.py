from pydantic import BaseModel, Field
from typing import Any
from scrapy.http import Response
from toy_catalogue.utils.url import generate_id


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
        base_data: dict[str, Any] = {
            "id": generate_id(response.url),
            "state": state,
            "url": response.url,
            "content": response.body,
            "metadata": {
                "url": response.url,
                "status": response.status,
                "headers": {
                    k.decode(): [v.decode() for v in vs]
                    for k, vs in response.headers.items()
                },
                "response_meta": response.meta,
            },
        }
        extra_data = cls._extra_from_response(response)
        return cls(**base_data, **extra_data)

    @classmethod
    def _extra_from_response(cls, response: Response) -> dict[str, Any]:
        return {}
