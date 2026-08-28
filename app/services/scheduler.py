from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import Settings
from app.database import Database
from app.services.mattermost import MattermostClient
from app.services.tasks import TaskService

logger = logging.getLogger(__name__)


def _parse_time(value: str) -> tuple[int, int]:
    hour, minute = value.split(":", maxsplit=1)
    return int(hour), int(minute)


class BotScheduler:
    def __init__(
        self,
        settings: Settings,
        database: Database,
        mattermost: MattermostClient,
        task_service: TaskService,
    ) -> None:
        self.settings = settings
        self.database = database
        self.mattermost = mattermost
        self.task_service = task_service
        self.scheduler = BackgroundScheduler(timezone=settings.business_timezone)

    def _post(self, channel_id: str, message: str) -> None:
        if not channel_id:
            logger.warning("scheduled message skipped: channel is not configured")
            return
        try:
            self.mattermost.post_message(channel_id, message)
        except Exception:
            logger.exception("scheduled Mattermost message failed")

    def _digest(self) -> None:
        today = datetime.now(ZoneInfo(self.settings.business_timezone)).date()
        with self.database.session_factory() as db:
            message = self.task_service.render_digest(db, today)
        self._post(self.settings.mentor_channel_id, message)

    def _add_daily_job(self, job_id: str, time_value: str, func: object) -> None:
        hour, minute = _parse_time(time_value)
        self.scheduler.add_job(
            func,
            CronTrigger(
                day_of_week="mon-fri",
                hour=hour,
                minute=minute,
                timezone=self.settings.business_timezone,
            ),
            id=job_id,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=900,
        )

    def start(self) -> None:
        self._add_daily_job(
            "checkin-reminder",
            self.settings.checkin_time,
            lambda: self._post(
                self.settings.attendance_channel_id,
                "Good morning. Record attendance with `/checkin [optional status note]`.",
            ),
        )
        self._add_daily_job(
            "worklog-reminder",
            self.settings.worklog_time,
            lambda: self._post(
                self.settings.attendance_channel_id,
                "Submit your daily worklog: `/task completed | blockers | next-day plan`.",
            ),
        )
        self._add_daily_job(
            "checkout-reminder",
            self.settings.checkout_time,
            lambda: self._post(
                self.settings.attendance_channel_id,
                "Please record the end of your workday with `/checkout [optional note]`.",
            ),
        )
        self._add_daily_job("mentor-digest", self.settings.digest_time, self._digest)
        self.scheduler.start()
        logger.info("scheduler started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

