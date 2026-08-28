from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _csv_tuple(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///./data/intern_bot.db"
    faq_path: Path = Path("config/faqs.yaml")

    mattermost_url: str = ""
    mattermost_bot_token: str = ""
    mattermost_bot_user_id: str = ""
    attendance_channel_id: str = ""
    mentor_channel_id: str = ""
    tls_ca_file: str = ""
    request_timeout_seconds: float = 10.0

    checkin_token: str = "change-me-checkin"
    checkout_token: str = "change-me-checkout"
    task_token: str = "change-me-task"
    faq_token: str = "change-me-faq"
    outgoing_webhook_token: str = "change-me-webhook"
    action_token: str = "change-me-action"
    admin_api_key: str = "change-me-admin"
    automation_api_key: str = "change-me-automation"
    mentor_user_ids: tuple[str, ...] = field(default_factory=tuple)

    business_timezone: str = "Africa/Lagos"
    checkin_time: str = "08:30"
    worklog_time: str = "16:30"
    checkout_time: str = "17:00"
    digest_time: str = "17:15"
    scheduler_enabled: bool = True

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            database_url=os.getenv(
                "DATABASE_URL", "sqlite+pysqlite:///./data/intern_bot.db"
            ),
            faq_path=Path(os.getenv("FAQ_PATH", "config/faqs.yaml")),
            mattermost_url=os.getenv("MATTERMOST_URL", "").rstrip("/"),
            mattermost_bot_token=os.getenv("MATTERMOST_BOT_TOKEN", ""),
            mattermost_bot_user_id=os.getenv("MATTERMOST_BOT_USER_ID", ""),
            attendance_channel_id=os.getenv("ATTENDANCE_CHANNEL_ID", ""),
            mentor_channel_id=os.getenv("MENTOR_CHANNEL_ID", ""),
            tls_ca_file=os.getenv("TLS_CA_FILE", ""),
            request_timeout_seconds=float(
                os.getenv("REQUEST_TIMEOUT_SECONDS", "10")
            ),
            checkin_token=os.getenv("MM_CHECKIN_TOKEN", "change-me-checkin"),
            checkout_token=os.getenv("MM_CHECKOUT_TOKEN", "change-me-checkout"),
            task_token=os.getenv("MM_TASK_TOKEN", "change-me-task"),
            faq_token=os.getenv("MM_FAQ_TOKEN", "change-me-faq"),
            outgoing_webhook_token=os.getenv(
                "MM_OUTGOING_WEBHOOK_TOKEN", "change-me-webhook"
            ),
            action_token=os.getenv("MM_ACTION_TOKEN", "change-me-action"),
            admin_api_key=os.getenv("ADMIN_API_KEY", "change-me-admin"),
            automation_api_key=os.getenv(
                "AUTOMATION_API_KEY", "change-me-automation"
            ),
            mentor_user_ids=_csv_tuple(os.getenv("MENTOR_USER_IDS")),
            business_timezone=os.getenv("BUSINESS_TIMEZONE", "Africa/Lagos"),
            checkin_time=os.getenv("CHECKIN_TIME", "08:30"),
            worklog_time=os.getenv("WORKLOG_TIME", "16:30"),
            checkout_time=os.getenv("CHECKOUT_TIME", "17:00"),
            digest_time=os.getenv("DIGEST_TIME", "17:15"),
            scheduler_enabled=_as_bool(os.getenv("SCHEDULER_ENABLED"), True),
        )

    @property
    def mattermost_configured(self) -> bool:
        return bool(self.mattermost_url and self.mattermost_bot_token)

    def validate_runtime(self) -> list[str]:
        errors: list[str] = []
        if self.app_env.lower() == "production":
            placeholder_values = {
                "change-me-checkin",
                "change-me-checkout",
                "change-me-task",
                "change-me-faq",
                "change-me-webhook",
                "change-me-action",
                "change-me-admin",
                "change-me-automation",
            }
            configured_secrets = {
                self.checkin_token,
                self.checkout_token,
                self.task_token,
                self.faq_token,
                self.outgoing_webhook_token,
                self.action_token,
                self.admin_api_key,
                self.automation_api_key,
            }
            if configured_secrets & placeholder_values:
                errors.append("placeholder verification secrets are not allowed")
            if not self.mattermost_configured:
                errors.append("Mattermost URL and bot token are required")
            if not self.attendance_channel_id or not self.mentor_channel_id:
                errors.append("attendance and mentor channel IDs are required")
            if not self.mentor_user_ids:
                errors.append("at least one mentor user ID is required")
        return errors
