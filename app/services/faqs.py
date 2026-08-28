from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import FAQConfigurationError
from app.models import FAQEntry


class FAQService:
    def __init__(self, faq_path: Path) -> None:
        self.faq_path = faq_path

    def _read_entries(self) -> list[dict[str, object]]:
        try:
            payload = yaml.safe_load(self.faq_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise FAQConfigurationError(f"Unable to read FAQ configuration: {exc}") from exc
        entries = payload.get("entries") if isinstance(payload, dict) else None
        if not isinstance(entries, list):
            raise FAQConfigurationError("FAQ configuration must contain an entries list")

        validated: list[dict[str, object]] = []
        seen: set[str] = set()
        for raw in entries:
            if not isinstance(raw, dict):
                raise FAQConfigurationError("Every FAQ entry must be an object")
            topic = str(raw.get("topic", "")).strip().lower()
            title = str(raw.get("title", "")).strip()
            answer = str(raw.get("answer", "")).strip()
            keywords_raw = raw.get("keywords", [])
            if not topic or not title or not answer or not isinstance(keywords_raw, list):
                raise FAQConfigurationError(
                    "Every FAQ needs topic, title, answer, and a keyword list"
                )
            if topic in seen:
                raise FAQConfigurationError(f"Duplicate FAQ topic: {topic}")
            seen.add(topic)
            keywords = [str(item).strip().lower() for item in keywords_raw if str(item).strip()]
            validated.append(
                {"topic": topic, "title": title, "answer": answer, "keywords": keywords}
            )
        return validated

    def sync(self, db: Session) -> int:
        entries = self._read_entries()
        active_topics: set[str] = set()
        for raw in entries:
            normalized = json.dumps(raw, sort_keys=True, separators=(",", ":"))
            checksum = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            topic = str(raw["topic"])
            active_topics.add(topic)
            item = db.scalar(select(FAQEntry).where(FAQEntry.topic == topic))
            if item is None:
                item = FAQEntry(topic=topic)
                db.add(item)
            item.title = str(raw["title"])
            item.answer = str(raw["answer"])
            item.keywords = list(raw["keywords"])
            item.source_checksum = checksum
            item.active = True

        for stale in db.scalars(select(FAQEntry).where(FAQEntry.active.is_(True))):
            if stale.topic not in active_topics:
                stale.active = False
        db.commit()
        return len(entries)

    def find(self, db: Session, query: str) -> FAQEntry | None:
        normalized = " ".join(query.lower().strip().split())
        if not normalized:
            return None
        entries = db.scalars(
            select(FAQEntry).where(FAQEntry.active.is_(True)).order_by(FAQEntry.topic)
        ).all()

        for entry in entries:
            if normalized == entry.topic:
                return entry
        for entry in entries:
            if any(normalized == keyword for keyword in entry.keywords):
                return entry
        for entry in entries:
            candidates = [entry.topic, *entry.keywords]
            if any(len(candidate) >= 4 and candidate in normalized for candidate in candidates):
                return entry
        return None

    def topics(self, db: Session) -> list[str]:
        return list(
            db.scalars(
                select(FAQEntry.topic)
                .where(FAQEntry.active.is_(True))
                .order_by(FAQEntry.topic)
            )
        )

