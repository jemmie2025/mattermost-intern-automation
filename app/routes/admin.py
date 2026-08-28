from __future__ import annotations

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.errors import MattermostAPIError
from app.models import AttendanceRecord, TaskLog
from app.security import require_admin
from app.services.audit import add_audit_event

router = APIRouter(
    prefix="/admin",
    tags=["Mentor administration"],
    dependencies=[Depends(require_admin)],
)


def _csv_response(rows: list[list[object]], filename: str) -> Response:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerows(rows)
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exports/attendance")
def export_attendance(
    request: Request,
    start_date: date = Query(...),
    end_date: date = Query(...),
) -> Response:
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must not be before start_date",
        )
    with request.app.state.database.session_factory() as db:
        records = db.scalars(
            select(AttendanceRecord)
            .options(joinedload(AttendanceRecord.user))
            .where(
                AttendanceRecord.business_date >= start_date,
                AttendanceRecord.business_date <= end_date,
            )
            .order_by(AttendanceRecord.business_date, AttendanceRecord.recorded_at)
        ).all()
        rows: list[list[object]] = [
            [
                "business_date",
                "mattermost_user_id",
                "username",
                "event_type",
                "recorded_at_utc",
                "status_note",
            ]
        ]
        rows.extend(
            [
                item.business_date.isoformat(),
                item.user.mattermost_user_id,
                item.user.username,
                item.event_type,
                item.recorded_at.isoformat(),
                item.status_note or "",
            ]
            for item in records
        )
        add_audit_event(
            db,
            "attendance_export",
            "accepted",
            request.state.admin_user_id,
            details={
                "start_date": str(start_date),
                "end_date": str(end_date),
                "record_count": len(records),
            },
        )
        db.commit()
    return _csv_response(rows, f"attendance-{start_date}-{end_date}.csv")


@router.get("/exports/worklogs")
def export_worklogs(
    request: Request,
    start_date: date = Query(...),
    end_date: date = Query(...),
) -> Response:
    if end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must not be before start_date")
    with request.app.state.database.session_factory() as db:
        logs = db.scalars(
            select(TaskLog)
            .options(joinedload(TaskLog.user))
            .where(
                TaskLog.business_date >= start_date,
                TaskLog.business_date <= end_date,
            )
            .order_by(TaskLog.business_date, TaskLog.submitted_at)
        ).all()
        rows: list[list[object]] = [
            [
                "business_date",
                "mattermost_user_id",
                "username",
                "tasks_completed",
                "blockers",
                "next_day_plan",
                "submitted_at_utc",
            ]
        ]
        rows.extend(
            [
                item.business_date.isoformat(),
                item.user.mattermost_user_id,
                item.user.username,
                item.tasks_completed,
                item.blockers,
                item.next_day_plan,
                item.submitted_at.isoformat(),
            ]
            for item in logs
        )
        add_audit_event(
            db,
            "worklog_export",
            "accepted",
            request.state.admin_user_id,
            {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "record_count": len(logs),
            },
        )
        db.commit()
    return _csv_response(rows, f"worklogs-{start_date}-{end_date}.csv")


@router.post("/faqs/reload")
def reload_faqs(request: Request) -> dict[str, object]:
    with request.app.state.database.session_factory() as db:
        count = request.app.state.faq_service.sync(db)
        add_audit_event(
            db,
            "faq_reload",
            "accepted",
            request.state.admin_user_id,
            {"active_entries": count},
        )
        db.commit()
    return {"status": "ok", "active_entries": count}


@router.post("/digests/{business_date}")
def publish_digest(request: Request, business_date: date) -> dict[str, object]:
    with request.app.state.database.session_factory() as db:
        message = request.app.state.task_service.render_digest(db, business_date)
    try:
        result = request.app.state.mattermost_client.post_message(
            request.app.state.settings.mentor_channel_id, message
        )
    except MattermostAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    with request.app.state.database.session_factory() as db:
        add_audit_event(
            db,
            "digest_published",
            "accepted",
            request.state.admin_user_id,
            {"business_date": str(business_date), "post_id": result.get("id")},
        )
        db.commit()
    return {"status": "published", "post_id": result.get("id")}


@router.get("/mattermost-connection")
def mattermost_connection(request: Request) -> dict[str, object]:
    try:
        user = request.app.state.mattermost_client.connection_check()
    except MattermostAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "status": "ok",
        "bot_user_id": user.get("id"),
        "bot_username": user.get("username"),
    }
