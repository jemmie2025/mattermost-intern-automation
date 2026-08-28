from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> dict[str, object]:
    with request.app.state.database.session_factory() as db:
        db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "ok",
        "mattermost_configured": request.app.state.settings.mattermost_configured,
    }

