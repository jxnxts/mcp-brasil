"""Testes do factory de autenticação (_shared/auth.py).

Usa ``monkeypatch`` para sobrescrever atributos do módulo ``settings`` após
ele já ter sido importado. Isso evita ter que fazer ``importlib.reload`` a
cada teste e mantém o padrão pytest-idiomático.
"""

from __future__ import annotations

from typing import Any

import pytest

from mcp_brasil import settings
from mcp_brasil._shared import auth
from mcp_brasil._shared.auth import AuthConfigError, build_auth


def _set_auth_env(
    monkeypatch: pytest.MonkeyPatch,
    *,
    mode: str = "none",
    token: str | None = None,
    provider: str = "",
    base_url: str = "",
    azure_client_id: str = "",
    azure_client_secret: str = "",
    azure_tenant_id: str = "",
    azure_required_scopes: list[str] | None = None,
    google_client_id: str = "",
    google_client_secret: str = "",
    google_required_scopes: list[str] | None = None,
    github_client_id: str = "",
    github_client_secret: str = "",
    github_required_scopes: list[str] | None = None,
    authkit_domain: str = "",
    authkit_required_scopes: list[str] | None = None,
) -> None:
    """Helper to patch all auth-related settings attributes at once."""
    monkeypatch.setattr(settings, "AUTH_MODE", mode)
    monkeypatch.setattr(settings, "MCP_BRASIL_API_TOKEN", token)
    monkeypatch.setattr(settings, "OAUTH_PROVIDER", provider)
    monkeypatch.setattr(settings, "MCP_BRASIL_BASE_URL", base_url)
    monkeypatch.setattr(settings, "AZURE_CLIENT_ID", azure_client_id)
    monkeypatch.setattr(settings, "AZURE_CLIENT_SECRET", azure_client_secret)
    monkeypatch.setattr(settings, "AZURE_TENANT_ID", azure_tenant_id)
    monkeypatch.setattr(settings, "AZURE_REQUIRED_SCOPES", azure_required_scopes or ["read"])
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", google_client_id)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", google_client_secret)
    monkeypatch.setattr(
        settings,
        "GOOGLE_REQUIRED_SCOPES",
        google_required_scopes or ["openid", "email"],
    )
    monkeypatch.setattr(settings, "GITHUB_CLIENT_ID", github_client_id)
    monkeypatch.setattr(settings, "GITHUB_CLIENT_SECRET", github_client_secret)
    monkeypatch.setattr(settings, "GITHUB_REQUIRED_SCOPES", github_required_scopes or [])
    monkeypatch.setattr(settings, "AUTHKIT_DOMAIN", authkit_domain)
    monkeypatch.setattr(settings, "AUTHKIT_REQUIRED_SCOPES", authkit_required_scopes or [])


class TestBuildAuthNone:
    def test_mode_none_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(monkeypatch, mode="none")
        assert build_auth() is None

    def test_mode_none_ignores_leftover_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Even if a token is set, mode=none wins."""
        _set_auth_env(monkeypatch, mode="none", token="leftover-token")
        assert build_auth() is None


class TestBuildAuthStatic:
    def test_static_with_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

        _set_auth_env(monkeypatch, mode="static", token="my-secret-token")
        provider = build_auth()
        assert isinstance(provider, StaticTokenVerifier)

    def test_static_without_token_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(monkeypatch, mode="static", token=None)
        with pytest.raises(AuthConfigError, match="MCP_BRASIL_API_TOKEN"):
            build_auth()


class TestBuildAuthOAuthValidation:
    def test_oauth_without_provider_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(monkeypatch, mode="oauth", provider="")
        with pytest.raises(AuthConfigError, match="MCP_BRASIL_OAUTH_PROVIDER"):
            build_auth()

    def test_oauth_without_base_url_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(monkeypatch, mode="oauth", provider="azure", base_url="")
        with pytest.raises(AuthConfigError, match="MCP_BRASIL_BASE_URL"):
            build_auth()

    def test_oauth_unknown_provider_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="okta",
            base_url="https://example.com",
        )
        with pytest.raises(AuthConfigError, match="Unknown MCP_BRASIL_OAUTH_PROVIDER"):
            build_auth()


class TestBuildAuthAzure:
    def test_azure_full_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fastmcp.server.auth.providers.azure import AzureProvider

        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="azure",
            base_url="https://mcp-brasil.example.com",
            azure_client_id="00000000-0000-0000-0000-000000000001",
            azure_client_secret="secret-value",
            azure_tenant_id="00000000-0000-0000-0000-000000000002",
            azure_required_scopes=["read"],
        )
        provider = build_auth()
        assert isinstance(provider, AzureProvider)

    def test_azure_missing_client_id_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="azure",
            base_url="https://mcp-brasil.example.com",
            azure_client_id="",
            azure_client_secret="secret-value",
            azure_tenant_id="00000000-0000-0000-0000-000000000002",
        )
        with pytest.raises(AuthConfigError, match="AZURE_CLIENT_ID"):
            build_auth()

    def test_azure_missing_client_secret_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="azure",
            base_url="https://mcp-brasil.example.com",
            azure_client_id="00000000-0000-0000-0000-000000000001",
            azure_client_secret="",
            azure_tenant_id="00000000-0000-0000-0000-000000000002",
        )
        with pytest.raises(AuthConfigError, match="AZURE_CLIENT_SECRET"):
            build_auth()

    def test_azure_missing_tenant_id_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="azure",
            base_url="https://mcp-brasil.example.com",
            azure_client_id="00000000-0000-0000-0000-000000000001",
            azure_client_secret="secret-value",
            azure_tenant_id="",
        )
        with pytest.raises(AuthConfigError, match="AZURE_TENANT_ID"):
            build_auth()


class TestBuildAuthGoogle:
    def test_google_full_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fastmcp.server.auth.providers.google import GoogleProvider

        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="google",
            base_url="https://mcp-brasil.example.com",
            google_client_id="google-client.apps.googleusercontent.com",
            google_client_secret="google-secret",
            google_required_scopes=["openid", "email"],
        )
        provider = build_auth()
        assert isinstance(provider, GoogleProvider)

    def test_google_missing_client_id_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="google",
            base_url="https://mcp-brasil.example.com",
            google_client_id="",
            google_client_secret="google-secret",
        )
        with pytest.raises(AuthConfigError, match="GOOGLE_CLIENT_ID"):
            build_auth()


class TestBuildAuthGitHub:
    def test_github_full_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fastmcp.server.auth.providers.github import GitHubProvider

        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="github",
            base_url="https://mcp-brasil.example.com",
            github_client_id="Iv1.abcdef0123456789",
            github_client_secret="github-secret",
        )
        provider = build_auth()
        assert isinstance(provider, GitHubProvider)

    def test_github_missing_client_secret_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="github",
            base_url="https://mcp-brasil.example.com",
            github_client_id="Iv1.abcdef0123456789",
            github_client_secret="",
        )
        with pytest.raises(AuthConfigError, match="GITHUB_CLIENT_SECRET"):
            build_auth()


class TestBuildAuthWorkOS:
    def test_workos_full_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fastmcp.server.auth.providers.workos import AuthKitProvider

        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="workos",
            base_url="https://mcp-brasil.example.com",
            authkit_domain="https://example.authkit.app",
        )
        provider = build_auth()
        assert isinstance(provider, AuthKitProvider)

    def test_workos_missing_domain_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(
            monkeypatch,
            mode="oauth",
            provider="workos",
            base_url="https://mcp-brasil.example.com",
            authkit_domain="",
        )
        with pytest.raises(AuthConfigError, match="AUTHKIT_DOMAIN"):
            build_auth()


class TestInvalidMode:
    def test_invalid_mode_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _set_auth_env(monkeypatch, mode="invalid")
        with pytest.raises(AuthConfigError, match="Invalid MCP_BRASIL_AUTH_MODE"):
            build_auth()


class TestRequireHelper:
    def test_require_raises_on_empty(self) -> None:
        with pytest.raises(AuthConfigError, match="FOO"):
            auth._require("FOO", "")

    def test_require_returns_value(self) -> None:
        assert auth._require("FOO", "bar") == "bar"


class TestAuthConfigError:
    def test_is_value_error(self) -> None:
        """AuthConfigError subclasses ValueError to play nicely with pytest.raises."""
        err: Any = AuthConfigError("boom")
        assert isinstance(err, ValueError)
