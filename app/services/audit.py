from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import AuditEvent


def add_audit_event(
    db: Session,
    event_type: str,
    outcome: str,
    actor_user_id: str | None = None,
    details: dict[str, object] | None = None,
) -> None:
    db.add(
        AuditEvent(
            event_type=event_type,
            actor_user_id=actor_user_id,
            outcome=outcome,
            details=details or {},
        )
    )

