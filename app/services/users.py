from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_or_create_user(
    db: Session,
    mattermost_user_id: str,
    username: str,
    role: str = "intern",
) -> User:
    user = db.scalar(
        select(User).where(User.mattermost_user_id == mattermost_user_id)
    )
    if user is None:
        user = User(
            mattermost_user_id=mattermost_user_id,
            username=username,
            role=role,
        )
        db.add(user)
        db.flush()
    elif user.username != username:
        user.username = username
    return user

