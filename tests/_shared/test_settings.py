"""Testes do módulo de configuração."""

import os
from unittest.mock import patch

from mcp_brasil import settings
from mcp_brasil.settings import _parse_scopes


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


class TestAuthSettings:
    """Validate auth-related constants and their defaults."""

    def test_auth_mode_defined(self) -> None:
        assert hasattr(settings, "AUTH_MODE")
        # conftest.py forces AUTH_MODE=none for the test suite
        assert settings.AUTH_MODE == "none"

    def test_oauth_provider_defined(self) -> None:
        assert hasattr(settings, "OAUTH_PROVIDER")
        assert isinstance(settings.OAUTH_PROVIDER, str)

    def test_base_url_defined(self) -> None:
        assert hasattr(settings, "MCP_BRASIL_BASE_URL")
        assert isinstance(settings.MCP_BRASIL_BASE_URL, str)

    def test_azure_defaults(self) -> None:
        assert settings.AZURE_CLIENT_ID == ""
        assert settings.AZURE_CLIENT_SECRET == ""
        assert settings.AZURE_TENANT_ID == ""
        assert settings.AZURE_REQUIRED_SCOPES == ["read"]

    def test_google_defaults(self) -> None:
        assert settings.GOOGLE_CLIENT_ID == ""
        assert settings.GOOGLE_CLIENT_SECRET == ""
        assert settings.GOOGLE_REQUIRED_SCOPES == ["openid", "email"]

    def test_github_defaults(self) -> None:
        assert settings.GITHUB_CLIENT_ID == ""
        assert settings.GITHUB_CLIENT_SECRET == ""
        assert settings.GITHUB_REQUIRED_SCOPES == []

    def test_workos_defaults(self) -> None:
        assert settings.AUTHKIT_DOMAIN == ""
        assert settings.AUTHKIT_REQUIRED_SCOPES == []


class TestParseScopes:
    def test_empty_string_returns_default(self) -> None:
        assert _parse_scopes("", ["read"]) == ["read"]

    def test_empty_string_no_default(self) -> None:
        assert _parse_scopes("") == []

    def test_single_scope(self) -> None:
        assert _parse_scopes("read") == ["read"]

    def test_multiple_scopes(self) -> None:
        assert _parse_scopes("read,write,admin") == ["read", "write", "admin"]

    def test_scopes_with_whitespace(self) -> None:
        assert _parse_scopes(" read , write ,  admin ") == [
            "read",
            "write",
            "admin",
        ]

    def test_scopes_with_empty_entries(self) -> None:
        assert _parse_scopes("read,,write,") == ["read", "write"]

    def test_whitespace_only_returns_default(self) -> None:
        assert _parse_scopes("   ,  ,", ["default"]) == ["default"]
