from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AttendanceOrderError, DuplicateAttendanceError
from app.models import AttendanceRecord
from app.services.audit import add_audit_event
from app.services.users import get_or_create_user


class AttendanceService:
    def __init__(self, timezone_name: str) -> None:
        self.timezone = ZoneInfo(timezone_name)

    def record(
        self,
        db: Session,
        *,
        event_type: str,
        mattermost_user_id: str,
        username: str,
        channel_id: str | None,
        note: str | None = None,
        source: str = "slash_command",
        occurred_at: datetime | None = None,
    ) -> AttendanceRecord:
        if event_type not in {"checkin", "checkout"}:
            raise ValueError("event_type must be checkin or checkout")

        instant = occurred_at or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        business_date = instant.astimezone(self.timezone).date()
        user = get_or_create_user(db, mattermost_user_id, username)

        existing = db.scalar(
            select(AttendanceRecord).where(
                AttendanceRecord.user_id == user.id,
                AttendanceRecord.business_date == business_date,
                AttendanceRecord.event_type == event_type,
            )
        )
        if existing:
            add_audit_event(
                db,
                "attendance_duplicate",
                "rejected",
                mattermost_user_id,
                {"event_type": event_type, "business_date": str(business_date)},
            )
            db.commit()
            raise DuplicateAttendanceError(
                f"You already recorded {event_type} for {business_date}."
            )

        if event_type == "checkout":
            checkin = db.scalar(
                select(AttendanceRecord).where(
                    AttendanceRecord.user_id == user.id,
                    AttendanceRecord.business_date == business_date,
                    AttendanceRecord.event_type == "checkin",
                )
            )
            if checkin is None:
                add_audit_event(
                    db,
                    "checkout_without_checkin",
                    "rejected",
                    mattermost_user_id,
                    {"business_date": str(business_date)},
                )
                db.commit()
                raise AttendanceOrderError(
                    "Check in first before recording your check-out."
                )

        record = AttendanceRecord(
            user_id=user.id,
            business_date=business_date,
            event_type=event_type,
            recorded_at=instant.astimezone(timezone.utc),
            status_note=(note or "").strip()[:500] or None,
            channel_id=channel_id,
            source=source,
        )
        db.add(record)
        add_audit_event(
            db,
            f"attendance_{event_type}",
            "accepted",
            mattermost_user_id,
            {"business_date": str(business_date), "source": source},
        )
        db.commit()
        db.refresh(record)
        return record

