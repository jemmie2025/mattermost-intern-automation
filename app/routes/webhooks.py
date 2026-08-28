from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.security import require_request_token

router = APIRouter(prefix="/mattermost/webhooks", tags=["Mattermost webhooks"])


async def _payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        value = await request.json()
        if not isinstance(value, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Webhook payload must be an object",
            )
        return value
    form = await request.form()
    return {key: str(value) for key, value in form.items()}


@router.post("/faq-keyword")
async def faq_keyword(request: Request) -> dict[str, Any]:
    payload = await _payload(request)
    require_request_token(
        str(payload.get("token", "")),
        request.app.state.settings.outgoing_webhook_token,
    )
    text = str(payload.get("text", ""))
    trigger_word = str(payload.get("trigger_word", ""))
    stripped_query = (
        text[len(trigger_word) :].strip() if text.startswith(trigger_word) else text
    )
    with request.app.state.database.session_factory() as db:
        entry = request.app.state.faq_service.find(db, text)
        if entry is None and stripped_query != text:
            entry = request.app.state.faq_service.find(db, stripped_query)
    if entry is None:
        return {
            "response_type": "comment",
            "text": "I could not match an approved FAQ. Use `/faq` to view available topics.",
        }
    return {
        "response_type": "comment",
        "text": f"### {entry.title}\n\n{entry.answer}",
    }
