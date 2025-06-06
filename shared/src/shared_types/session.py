from __future__ import annotations
from typing import Literal, TypedDict, Any

SessionStatus = Literal["completed", "running", "failed", "pending", "paused"]


class SessionSummary(TypedDict):
    id: str
    name: str
    status: SessionStatus
    lastRun: str


class SessionDetail(SessionSummary):
    config: dict[str, Any]
    logs: list[LogEntry]


class LogEntry(TypedDict):
    timestamp: str
    type: str
    source: str
    details: dict[str, Any]
