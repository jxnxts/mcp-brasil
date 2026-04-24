"""LGPD column masking for dataset results (ADR-004).

PII columns declared in :class:`DatasetSpec.pii_columns` are masked by
default. Liberation per-dataset via ``MCP_BRASIL_LGPD_ALLOW_PII``.
"""

from __future__ import annotations

import re
from typing import Any

from mcp_brasil import settings

from .dataset import DatasetSpec

# Accepts 11-digit CPFs and 14-digit CNPJs, possibly with punctuation
_DIGITS = re.compile(r"\D+")


def is_pii_allowed(spec: DatasetSpec) -> bool:
    """Return True if PII should be shown in full for this dataset."""
    return spec.id in settings.DATASETS_ALLOW_PII


def mask_value(value: Any) -> str:
    """Mask a CPF/CNPJ-like string, preserving last 3 digits for cross-ref."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text == "None":
        return ""
    digits = _DIGITS.sub("", text)
    if len(digits) == 11:  # CPF
        return f"***.***.{digits[6:9]}-**"
    if len(digits) == 14:  # CNPJ
        return f"**.***.***/{digits[8:12]}-**"
    if len(digits) > 4:
        return f"***{digits[-3:]}"
    return "***"


def redact_rows(rows: list[dict[str, Any]], spec: DatasetSpec) -> list[dict[str, Any]]:
    """Apply masking to every PII column in-place-safe (copies dicts)."""
    if not spec.pii_columns or is_pii_allowed(spec):
        return rows
    masked_cols = spec.pii_columns
    out: list[dict[str, Any]] = []
    for row in rows:
        new = dict(row)
        for col in masked_cols:
            if col in new:
                new[col] = mask_value(new[col])
        out.append(new)
    return out
