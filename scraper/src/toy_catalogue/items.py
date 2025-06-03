from typing import Any, Optional


class StateItem:
    def __init__(
        self,
        state: str,
        url: str,
        content: Any,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.state = state
        self.url = url
        self.content = content
        self.metadata = metadata

    def __repr__(self) -> str:
        return ""
