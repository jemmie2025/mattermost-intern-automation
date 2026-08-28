from __future__ import annotations

from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request

from app.errors import MattermostAPIError
from app.security import require_automation
from app.services.audit import add_audit_event

router = APIRouter(
    prefix="/automation",
    tags=["n8n automation"],
    dependencies=[Depends(require_automation)],
)


class ReminderType(str, Enum):
    CHECKIN = "checkin"
    WORKLOG = "worklog"
    CHECKOUT = "checkout"


REMINDERS = {
    ReminderType.CHECKIN: (
        "Good morning. Record attendance with "
        "`/checkin [optional status note]`."
    ),
    ReminderType.WORKLOG: (
        "Submit your daily worklog: "
        "`/task completed | blockers | next-day plan`."
    ),
    ReminderType.CHECKOUT: (
        "Please record the end of your workday with "
        "`/checkout [optional note]`."
    ),
}


def _post(request: Request, channel_id: str, message: str) -> dict[str, object]:
    if not channel_id:
        raise HTTPException(status_code=503, detail="Target channel is not configured")
    try:
        return request.app.state.mattermost_client.post_message(channel_id, message)
    except MattermostAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/reminders/{reminder_type}")
def publish_reminder(
    request: Request, reminder_type: ReminderType
) -> dict[str, object]:
    result = _post(
        request,
        request.app.state.settings.attendance_channel_id,
        REMINDERS[reminder_type],
    )
    with request.app.state.database.session_factory() as db:
        add_audit_event(
            db,
            "n8n_reminder_published",
            "accepted",
            "n8n",
            {"reminder_type": reminder_type.value, "post_id": result.get("id")},
        )
        db.commit()
    return {
        "status": "published",
        "reminder_type": reminder_type.value,
        "post_id": result.get("id"),
    }


@router.post("/digests/today")
def publish_today_digest(request: Request) -> dict[str, object]:
    settings = request.app.state.settings
    business_date = datetime.now(ZoneInfo(settings.business_timezone)).date()
    with request.app.state.database.session_factory() as db:
        message = request.app.state.task_service.render_digest(db, business_date)
    result = _post(request, settings.mentor_channel_id, message)
    with request.app.state.database.session_factory() as db:
        add_audit_event(
            db,
            "n8n_digest_published",
            "accepted",
            "n8n",
            {"business_date": str(business_date), "post_id": result.get("id")},
        )
        db.commit()
    return {
        "status": "published",
        "business_date": str(business_date),
        "post_id": result.get("id"),
    }
