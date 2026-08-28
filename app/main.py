from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request

from app import __version__
from app.config import Settings
from app.database import Database
from app.routes import admin, automation, commands, health, webhooks
from app.services.attendance import AttendanceService
from app.services.faqs import FAQService
from app.services.mattermost import MattermostClient
from app.services.scheduler import BotScheduler
from app.services.tasks import TaskService


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings.from_env()
    runtime_errors = app_settings.validate_runtime()
    if runtime_errors:
        raise RuntimeError("Invalid runtime configuration: " + "; ".join(runtime_errors))

    database = Database(app_settings.database_url)
    attendance_service = AttendanceService(app_settings.business_timezone)
    task_service = TaskService(app_settings.business_timezone)
    faq_service = FAQService(app_settings.faq_path)
    mattermost_client = MattermostClient(app_settings)
    scheduler = BotScheduler(
        app_settings, database, mattermost_client, task_service
    )

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        configure_logging()
        database.create_schema()
        with database.session_factory() as db:
            faq_count = faq_service.sync(db)
        logging.getLogger(__name__).info("loaded %s FAQ entries", faq_count)
        if app_settings.scheduler_enabled and app_settings.mattermost_configured:
            scheduler.start()
        yield
        scheduler.shutdown()
        database.close()

    app = FastAPI(
        title="Mattermost Intern Automation Bot",
        description="Attendance, daily worklog, and FAQ automation PoC.",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if app_settings.app_env != "production" else None,
        redoc_url=None,
    )
    app.state.settings = app_settings
    app.state.database = database
    app.state.attendance_service = attendance_service
    app.state.task_service = task_service
    app.state.faq_service = faq_service
    app.state.mattermost_client = mattermost_client
    app.state.scheduler = scheduler

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["x-request-id"] = request_id
        logging.getLogger("http").info(
            "%s %s -> %s in %sms request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
        return response

    app.include_router(health.router)
    app.include_router(commands.router)
    app.include_router(webhooks.router)
    app.include_router(admin.router)
    app.include_router(automation.router)
    return app


app = create_app()
