from __future__ import annotations
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, PrivateAttr

from toy_catalogue.config.schema.external.schema import SiteConfig
from toy_catalogue.config.parameters import SESSION_BASE_DIR
from datetime import datetime, timezone
import json


class SessionMeta(BaseModel):
    session_id: str
    site: str
    mode: str
    timestamp: datetime
    config: SiteConfig
    tags: list[str] = []
    item_count: Optional[int] = None
    parent_session_id: Optional[str] = None


class SessionContext(BaseModel):
    session_id: str
    session_dir: Path
    meta: SessionMeta

    _events: list[dict[str, Any]] = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._events = []

    def record_success(self, source: str, msg: str, extra: dict[str, Any] = {}) -> None:
        self.record_event("success", source, {"message": msg, **extra})

    def record_error(self, source: str, msg: str, error: Exception | str) -> None:
        self.record_event(
            "error",
            source,
            {
                "message": msg,
                "error": repr(error) if isinstance(error, Exception) else error,
            },
        )

    def record_event(
        self, event_type: str, source: str, details: dict[str, Any]
    ) -> None:
        self._events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": event_type,
                "source": source,
                "details": details,
            }
        )

    def flush_events(self) -> None:
        event_path = self.session_dir / "events.jsonl"
        with open(event_path, "a", encoding="utf-8") as f:
            for event in self._events:
                f.write(json.dumps(event) + "\n")
        self._events.clear()

    @property
    def product_path(self) -> Path:
        return self.session_dir / "products.jsonl"

    @property
    def log_path(self) -> Path:
        return self.session_dir / "log.txt"

    @property
    def job_dir(self) -> Path:
        return self.session_dir / "jobdir"


class SessionManager:
    INDEX_FILE = SESSION_BASE_DIR / "index.jsonl"

    @classmethod
    def create_session(
        cls,
        config: SiteConfig,
        mode: str,
        tags: list[str] = [],
        parent_session_id: Optional[str] = None,
    ) -> SessionContext:
        now = datetime.now(timezone.utc)
        now_str = now.strftime("%Y-%m-%dT%H-%M-%S")
        tag_str = "_".join(tags) if tags else "untagged"
        session_id = f"{now_str}_{config.site}_{tag_str}"
        session_dir = SESSION_BASE_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=False)

        meta = SessionMeta(
            session_id=session_id,
            site=config.site,
            mode=mode,
            timestamp=now,
            config=config,
            tags=tags,
            parent_session_id=parent_session_id,
        )

        with open(session_dir / "meta.json", "w", encoding="utf-8") as f:
            f.write(meta.model_dump_json(indent=2))

        with open(cls.INDEX_FILE, "a", encoding="utf-8") as index:
            index.write(meta.model_dump_json() + "\n")

        return SessionContext(session_id=session_id, session_dir=session_dir, meta=meta)

    @classmethod
    def get_session_dir(cls, session_id: str) -> Path:
        return SESSION_BASE_DIR / session_id

    @classmethod
    def load_session_meta(cls, session_id: str) -> SessionMeta:
        meta_path = cls.get_session_dir(session_id) / "meta.json"
        with open(meta_path, encoding="utf-8") as f:
            return SessionMeta.model_validate_json(f.read())

    @classmethod
    def update_session_meta(cls, session_id: str, patch: dict[str, Any]) -> None:
        meta_path = cls.get_session_dir(session_id) / "meta.json"
        with open(meta_path, encoding="utf-8") as f:
            meta = SessionMeta.model_validate_json(f.read())

        updated_meta = meta.model_copy(update=patch)

        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(updated_meta.model_dump_json(indent=2))

        # Optionally also update the index file (if you’re querying it regularly)

    @classmethod
    def record_item_count(cls, session_id: str, count: int) -> None:
        cls.update_session_meta(session_id, {"item_count": count})

    @classmethod
    def list_sessions(
        cls, filters: Optional[dict[str, Any]] = None
    ) -> list[SessionMeta]:
        if not cls.INDEX_FILE.exists():
            return []

        results: list[SessionMeta] = []
        with open(cls.INDEX_FILE, encoding="utf-8") as f:
            for line in f:
                meta = SessionMeta.model_validate_json(line)
                if filters:
                    match = all(getattr(meta, k, None) == v for k, v in filters.items())
                    if not match:
                        continue
                results.append(meta)
        return results
