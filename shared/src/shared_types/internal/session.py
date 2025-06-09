from pydantic import BaseModel, Field
from typing import Optional, cast
from datetime import datetime
from pathlib import Path
from shared_types.external.input import InputConfig
from moduscrape.processing.items._base import BaseItem


class SessionMeta(BaseModel):
    """
    Immutable-ish snapshot describing session.
    Some fields like item_count and tags are mutable and updated explicitly
    args:
        - site: str
        - mode: str
        - config: InputConfig
        - tags: Optional[list[str]]
        - parent_session_id: Optional[str]
    """

    session_id: str
    site: str
    mode: str
    timestamp: datetime
    config: InputConfig
    tags: list[str] = Field(default_factory=list)
    item_count: dict[type[BaseItem], int] = Field(
        default_factory=lambda: cast(dict[type[BaseItem], int], {})
    )
    parent_session_id: Optional[str] = None

    class Config:
        frozen = True

    # @model_validator(mode="after")
    # def set_session_id(cls, values: Any) -> "SessionMeta":
    #     now_str = values.timestamp.strftime("%Y-%m-%dT%H-%M-%S")
    # # FIXME: make utility function for datetime to string
    #     tag_str = "_".join(values.tags) if values.tags else "no-tag"
    #     values.session_id = f"{now_str}_{values.site}_{tag_str}"
    #     return values


class SessionContext(BaseModel):
    """
    Runtime context for a session
    Holds session directory path and event logging buffer.
    """

    session_id: str
    session_dir: Path
    meta: SessionMeta
