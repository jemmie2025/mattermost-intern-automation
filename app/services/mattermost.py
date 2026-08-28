from __future__ import annotations

import httpx

from app.config import Settings
from app.errors import MattermostAPIError


class MattermostClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def verify(self) -> bool | str:
        return self.settings.tls_ca_file or True

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.mattermost_bot_token}",
            "Content-Type": "application/json",
        }

    def post_message(self, channel_id: str, message: str) -> dict[str, object]:
        if not self.settings.mattermost_configured:
            raise MattermostAPIError("Mattermost connection is not configured")
        try:
            response = httpx.post(
                f"{self.settings.mattermost_url}/api/v4/posts",
                headers=self._headers(),
                json={"channel_id": channel_id, "message": message},
                timeout=self.settings.request_timeout_seconds,
                verify=self.verify,
            )
            response.raise_for_status()
            return dict(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise MattermostAPIError(f"Mattermost post failed: {exc}") from exc

    def connection_check(self) -> dict[str, object]:
        if not self.settings.mattermost_configured:
            raise MattermostAPIError("Mattermost connection is not configured")
        try:
            response = httpx.get(
                f"{self.settings.mattermost_url}/api/v4/users/me",
                headers=self._headers(),
                timeout=self.settings.request_timeout_seconds,
                verify=self.verify,
            )
            response.raise_for_status()
            return dict(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise MattermostAPIError(f"Mattermost connection check failed: {exc}") from exc

