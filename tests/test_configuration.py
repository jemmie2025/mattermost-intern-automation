from pathlib import Path

import pytest

from app.config import Settings
from app.errors import FAQConfigurationError, MattermostAPIError
from app.services.faqs import FAQService
from app.services.mattermost import MattermostClient


def test_production_configuration_rejects_placeholders():
    errors = Settings(app_env="production").validate_runtime()
    assert "placeholder verification secrets are not allowed" in errors
    assert "Mattermost URL and bot token are required" in errors
    assert "attendance and mentor channel IDs are required" in errors
    assert "at least one mentor user ID is required" in errors


def test_unconfigured_mattermost_client_fails_safely():
    with pytest.raises(MattermostAPIError, match="not configured"):
        MattermostClient(Settings()).connection_check()


def test_invalid_faq_configuration_is_rejected(tmp_path: Path):
    faq_path = tmp_path / "invalid.yaml"
    faq_path.write_text("version: 1\nentries: invalid\n", encoding="utf-8")
    with pytest.raises(FAQConfigurationError, match="entries list"):
        FAQService(faq_path)._read_entries()

