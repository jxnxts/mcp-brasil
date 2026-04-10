"""Authentication strategy factory for mcp-brasil.

Selects the auth provider based on environment variables:

- ``MCP_BRASIL_AUTH_MODE``: ``none`` | ``static`` | ``oauth``
- ``MCP_BRASIL_OAUTH_PROVIDER``: ``azure`` | ``google`` | ``github`` | ``workos``

Usage::

    from mcp_brasil._shared.auth import build_auth

    auth = build_auth()
    mcp = FastMCP("mcp-brasil", auth=auth)
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AuthConfigError(ValueError):
    """Raised when auth configuration is invalid (missing required env vars)."""


def build_auth() -> Any | None:
    """Build the auth provider from environment settings.

    Returns:
        The configured auth provider, or ``None`` when auth is disabled
        (``MCP_BRASIL_AUTH_MODE=none``).

    Raises:
        AuthConfigError: When the configured mode or provider is missing
            required environment variables.
    """
    from mcp_brasil import settings

    mode = settings.AUTH_MODE

    if mode == "none":
        logger.info("Auth disabled (MCP_BRASIL_AUTH_MODE=none)")
        return None

    if mode == "static":
        return _build_static_token()

    if mode == "oauth":
        return _build_oauth()

    raise AuthConfigError(
        f"Invalid MCP_BRASIL_AUTH_MODE={mode!r}. Expected one of: none, static, oauth."
    )


def _build_static_token() -> Any:
    from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

    from mcp_brasil import settings

    token = settings.MCP_BRASIL_API_TOKEN
    if not token:
        raise AuthConfigError(
            "MCP_BRASIL_AUTH_MODE=static requires MCP_BRASIL_API_TOKEN to be set."
        )

    logger.info("Auth enabled: StaticTokenVerifier (Bearer token required)")
    return StaticTokenVerifier(
        tokens={token: {"client_id": "mcp-client", "scopes": ["read"]}},
    )


def _build_oauth() -> Any:
    from mcp_brasil import settings

    provider = settings.OAUTH_PROVIDER
    base_url = settings.MCP_BRASIL_BASE_URL

    if not provider:
        raise AuthConfigError(
            "MCP_BRASIL_AUTH_MODE=oauth requires MCP_BRASIL_OAUTH_PROVIDER "
            "(azure|google|github|workos)."
        )
    if not base_url:
        raise AuthConfigError(
            "MCP_BRASIL_AUTH_MODE=oauth requires MCP_BRASIL_BASE_URL "
            "(public URL of this MCP server, e.g. https://mcp-brasil.example.com)."
        )

    dispatch = {
        "azure": _build_azure,
        "google": _build_google,
        "github": _build_github,
        "workos": _build_workos,
    }
    builder = dispatch.get(provider)
    if builder is None:
        raise AuthConfigError(
            f"Unknown MCP_BRASIL_OAUTH_PROVIDER={provider!r}. "
            f"Expected one of: {', '.join(dispatch.keys())}."
        )
    return builder(base_url)


def _require(name: str, value: str) -> str:
    if not value:
        raise AuthConfigError(f"{name} is required when using this OAuth provider.")
    return value


def _build_azure(base_url: str) -> Any:
    from fastmcp.server.auth.providers.azure import AzureProvider

    from mcp_brasil import settings

    logger.info("Auth enabled: AzureProvider (Entra ID)")
    return AzureProvider(
        client_id=_require("AZURE_CLIENT_ID", settings.AZURE_CLIENT_ID),
        client_secret=_require("AZURE_CLIENT_SECRET", settings.AZURE_CLIENT_SECRET),
        tenant_id=_require("AZURE_TENANT_ID", settings.AZURE_TENANT_ID),
        required_scopes=settings.AZURE_REQUIRED_SCOPES,
        base_url=base_url,
    )


def _build_google(base_url: str) -> Any:
    from fastmcp.server.auth.providers.google import GoogleProvider

    from mcp_brasil import settings

    logger.info("Auth enabled: GoogleProvider")
    return GoogleProvider(
        client_id=_require("GOOGLE_CLIENT_ID", settings.GOOGLE_CLIENT_ID),
        client_secret=_require("GOOGLE_CLIENT_SECRET", settings.GOOGLE_CLIENT_SECRET),
        base_url=base_url,
        required_scopes=settings.GOOGLE_REQUIRED_SCOPES or None,
    )


def _build_github(base_url: str) -> Any:
    from fastmcp.server.auth.providers.github import GitHubProvider

    from mcp_brasil import settings

    logger.info("Auth enabled: GitHubProvider")
    return GitHubProvider(
        client_id=_require("GITHUB_CLIENT_ID", settings.GITHUB_CLIENT_ID),
        client_secret=_require("GITHUB_CLIENT_SECRET", settings.GITHUB_CLIENT_SECRET),
        base_url=base_url,
        required_scopes=settings.GITHUB_REQUIRED_SCOPES or None,
    )


def _build_workos(base_url: str) -> Any:
    from fastmcp.server.auth.providers.workos import AuthKitProvider

    from mcp_brasil import settings

    logger.info("Auth enabled: AuthKitProvider (WorkOS)")
    return AuthKitProvider(
        authkit_domain=_require("AUTHKIT_DOMAIN", settings.AUTHKIT_DOMAIN),
        base_url=base_url,
        required_scopes=settings.AUTHKIT_REQUIRED_SCOPES or None,
    )
