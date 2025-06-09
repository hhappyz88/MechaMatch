from __future__ import annotations
from pydantic import BaseModel


class StrategyConfig(BaseModel):
    name: str
    # params: dict
