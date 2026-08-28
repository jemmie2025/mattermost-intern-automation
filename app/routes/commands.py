from __future__ import annotations

from datetime import timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.errors import (
    AttendanceOrderError,
    DuplicateAttendanceError,
    InvalidTaskFormatError,
)
from app.security import require_request_token

router = APIRouter(prefix="/mattermost/commands", tags=["Mattermost commands"])


async def _form_payload(request: Request) -> dict[str, str]:
    form = await request.form()
    payload = {key: str(value) for key, value in form.items()}
    for required in ("token", "user_id", "user_name"):
        if not payload.get(required):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing Mattermost field: {required}",
            )
    return payload


def _ephemeral(text: str) -> dict[str, str]:
    return {"response_type": "ephemeral", "text": text}


def _local_time(recorded_at: Any, target_timezone: Any):
    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(tzinfo=timezone.utc)
    return recorded_at.astimezone(target_timezone)


@router.post("/checkin")
async def checkin(request: Request) -> dict[str, str]:
    payload = await _form_payload(request)
    settings = request.app.state.settings
    require_request_token(payload.get("token"), settings.checkin_token)
    try:
        with request.app.state.database.session_factory() as db:
            record = request.app.state.attendance_service.record(
                db,
                event_type="checkin",
                mattermost_user_id=payload["user_id"],
                username=payload["user_name"],
                channel_id=payload.get("channel_id"),
                note=payload.get("text"),
            )
    except DuplicateAttendanceError as exc:
        return _ephemeral(str(exc))
    local_time = _local_time(
        record.recorded_at, request.app.state.attendance_service.timezone
    )
    return _ephemeral(
        f"Check-in recorded for **{record.business_date}** at "
        f"**{local_time:%H:%M %Z}**."
    )


@router.post("/checkout")
async def checkout(request: Request) -> dict[str, str]:
    payload = await _form_payload(request)
    settings = request.app.state.settings
    require_request_token(payload.get("token"), settings.checkout_token)
    try:
        with request.app.state.database.session_factory() as db:
            record = request.app.state.attendance_service.record(
                db,
                event_type="checkout",
                mattermost_user_id=payload["user_id"],
                username=payload["user_name"],
                channel_id=payload.get("channel_id"),
                note=payload.get("text"),
            )
    except (DuplicateAttendanceError, AttendanceOrderError) as exc:
        return _ephemeral(str(exc))
    local_time = _local_time(
        record.recorded_at, request.app.state.attendance_service.timezone
    )
    return _ephemeral(
        f"Check-out recorded for **{record.business_date}** at "
        f"**{local_time:%H:%M %Z}**."
    )


@router.post("/task")
async def task(request: Request) -> dict[str, str]:
    payload = await _form_payload(request)
    settings = request.app.state.settings
    require_request_token(payload.get("token"), settings.task_token)
    try:
        with request.app.state.database.session_factory() as db:
            log, created = request.app.state.task_service.submit(
                db,
                mattermost_user_id=payload["user_id"],
                username=payload["user_name"],
                channel_id=payload.get("channel_id"),
                text=payload.get("text", ""),
            )
    except InvalidTaskFormatError as exc:
        return _ephemeral(str(exc))
    action = "submitted" if created else "updated"
    return _ephemeral(f"Daily worklog {action} for **{log.business_date}**.")


@router.post("/faq")
async def faq(request: Request) -> dict[str, Any]:
    payload = await _form_payload(request)
    settings = request.app.state.settings
    require_request_token(payload.get("token"), settings.faq_token)
    with request.app.state.database.session_factory() as db:
        query = payload.get("text", "")
        entry = request.app.state.faq_service.find(db, query)
        if entry:
            return _ephemeral(f"### {entry.title}\n\n{entry.answer}")
        topics = request.app.state.faq_service.topics(db)
    topic_list = ", ".join(f"`{topic}`" for topic in topics)
    if query.strip():
        return _ephemeral(
            f"No approved FAQ matched **{query.strip()}**. Available topics: {topic_list}."
        )
    return _ephemeral(f"Available FAQ topics: {topic_list}.")
