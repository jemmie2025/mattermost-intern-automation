from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.errors import InvalidTaskFormatError
from app.models import TaskLog
from app.services.audit import add_audit_event
from app.services.users import get_or_create_user

TASK_USAGE = (
    "Use `/task completed work | blockers or None | next working-day plan`."
)


def parse_task_text(text: str) -> tuple[str, str, str]:
    value = text.strip()
    if value.lower().startswith("log "):
        value = value[4:].strip()
    parts = [part.strip() for part in value.split("|", maxsplit=2)]
    if len(parts) != 3 or not parts[0] or not parts[2]:
        raise InvalidTaskFormatError(TASK_USAGE)
    completed, blockers, next_plan = parts
    return completed[:4000], (blockers or "None")[:4000], next_plan[:4000]


class TaskService:
    def __init__(self, timezone_name: str) -> None:
        self.timezone = ZoneInfo(timezone_name)

    def submit(
        self,
        db: Session,
        *,
        mattermost_user_id: str,
        username: str,
        channel_id: str | None,
        text: str,
        submitted_at: datetime | None = None,
    ) -> tuple[TaskLog, bool]:
        completed, blockers, next_plan = parse_task_text(text)
        instant = submitted_at or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        business_date = instant.astimezone(self.timezone).date()
        user = get_or_create_user(db, mattermost_user_id, username)

        log = db.scalar(
            select(TaskLog).where(
                TaskLog.user_id == user.id,
                TaskLog.business_date == business_date,
            )
        )
        created = log is None
        if log is None:
            log = TaskLog(user_id=user.id, business_date=business_date)
            db.add(log)

        log.tasks_completed = completed
        log.blockers = blockers
        log.next_day_plan = next_plan
        log.submitted_at = instant.astimezone(timezone.utc)
        log.channel_id = channel_id
        add_audit_event(
            db,
            "task_log_submitted" if created else "task_log_updated",
            "accepted",
            mattermost_user_id,
            {"business_date": str(business_date)},
        )
        db.commit()
        db.refresh(log)
        return log, created

    def render_digest(self, db: Session, business_date: date) -> str:
        logs = db.scalars(
            select(TaskLog)
            .options(joinedload(TaskLog.user))
            .where(TaskLog.business_date == business_date)
            .order_by(TaskLog.submitted_at)
        ).all()
        if not logs:
            return f"### Intern Daily Digest — {business_date}\n\nNo worklogs submitted."

        sections = [f"### Intern Daily Digest — {business_date}"]
        for item in logs:
            sections.extend(
                [
                    f"#### @{item.user.username}",
                    f"- **Completed:** {item.tasks_completed}",
                    f"- **Blockers:** {item.blockers}",
                    f"- **Next:** {item.next_day_plan}",
                ]
            )
        sections.append(f"\n**Submissions:** {len(logs)}")
        return "\n\n".join(sections)

