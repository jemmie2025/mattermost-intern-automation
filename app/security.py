from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, Request, status

from app.config import Settings
from app.services.audit import add_audit_event


def token_matches(received: str | None, expected: str) -> bool:
    return bool(received) and hmac.compare_digest(received, expected)


def require_request_token(received: str | None, expected: str) -> None:
    if not token_matches(received, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request verification failed",
        )


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def require_admin(
    request: Request,
    x_admin_key: str | None = Header(default=None),
    x_mattermost_user_id: str | None = Header(default=None),
) -> str:
    settings: Settings = request.app.state.settings
    authenticated = token_matches(x_admin_key, settings.admin_api_key)
    authorized = authenticated and bool(x_mattermost_user_id)
    if authorized and settings.mentor_user_ids:
        authorized = x_mattermost_user_id in settings.mentor_user_ids

    if not authorized:
        with request.app.state.database.session_factory() as db:
            add_audit_event(
                db,
                "admin_authorization",
                "rejected",
                x_mattermost_user_id,
                {},
            )
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor or administrator authorization required",
        )
    request.state.admin_user_id = x_mattermost_user_id
    return x_mattermost_user_id or ""


def require_automation(
    request: Request,
    x_automation_key: str | None = Header(default=None),
) -> str:
    settings: Settings = request.app.state.settings
    if not token_matches(x_automation_key, settings.automation_api_key):
        with request.app.state.database.session_factory() as db:
            add_audit_event(db, "automation_authorization", "rejected", "n8n", {})
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Automation authorization failed",
        )
    return "n8n"
