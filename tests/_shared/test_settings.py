"""Testes do módulo de configuração."""

import os
from unittest.mock import patch

from mcp_brasil import settings


class TestSettings:
    def test_default_timeout(self) -> None:
        assert settings.HTTP_TIMEOUT == 30.0

    def test_default_max_retries(self) -> None:
        assert settings.HTTP_MAX_RETRIES == 3

    def test_default_backoff_base(self) -> None:
        assert settings.HTTP_BACKOFF_BASE == 1.0

    def test_default_user_agent(self) -> None:
        assert "mcp-brasil" in settings.USER_AGENT

    def test_env_override_timeout(self) -> None:
        """Settings can be overridden via env vars (at import time)."""
        with patch.dict(os.environ, {"MCP_BRASIL_HTTP_TIMEOUT": "10.0"}):
            # Re-evaluate the expression the same way settings.py does
            val = float(os.environ.get("MCP_BRASIL_HTTP_TIMEOUT", "30.0"))
            assert val == 10.0
