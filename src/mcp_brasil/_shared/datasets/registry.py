"""Dataset registry — discovers DATASET_SPEC exports in datasets/ features."""

from __future__ import annotations

import importlib
import logging
import pkgutil

from mcp_brasil import settings

from .dataset import DatasetSpec

logger = logging.getLogger(__name__)


class DatasetRegistry:
    """Enumerates datasets from the ``mcp_brasil.datasets`` package.

    Features auto-discovered here must:
    - Be at ``mcp_brasil.datasets.{id}``
    - Export a module-level ``DATASET_SPEC`` of type :class:`DatasetSpec`

    The registry filters by ``settings.DATASETS_ENABLED`` — datasets not in
    that list are NOT returned (they remain invisible even if the module is
    importable).
    """

    def __init__(self) -> None:
        self._specs: dict[str, DatasetSpec] = {}
        self._discovered = False

    def discover(self, package_name: str = "mcp_brasil.datasets") -> None:
        """Import all sub-packages and collect DATASET_SPEC exports."""
        try:
            package = importlib.import_module(package_name)
        except ImportError as exc:
            logger.debug("Datasets package not importable: %s", exc)
            self._discovered = True
            return

        for _finder, name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                continue
            full_name = f"{package_name}.{name}"
            try:
                module = importlib.import_module(full_name)
            except Exception:
                logger.exception("Failed to import dataset feature %s", full_name)
                continue
            spec = getattr(module, "DATASET_SPEC", None)
            if spec is None:
                continue
            if not isinstance(spec, DatasetSpec):
                logger.warning(
                    "%s exports DATASET_SPEC but not a DatasetSpec instance; skipping",
                    full_name,
                )
                continue
            self._specs[spec.id] = spec

        self._discovered = True
        logger.info(
            "DatasetRegistry discovered %d specs (enabled=%s)",
            len(self._specs),
            settings.DATASETS_ENABLED or "[]",
        )

    def all_specs(self) -> list[DatasetSpec]:
        """Every DATASET_SPEC ever exported (ignores env enable list)."""
        if not self._discovered:
            self.discover()
        return list(self._specs.values())

    def enabled_specs(self) -> list[DatasetSpec]:
        """DATASET_SPECs that are both discovered AND listed in env."""
        enabled = set(settings.DATASETS_ENABLED)
        return [s for s in self.all_specs() if s.id in enabled]

    def get(self, dataset_id: str) -> DatasetSpec | None:
        if not self._discovered:
            self.discover()
        return self._specs.get(dataset_id)

    def is_enabled(self, dataset_id: str) -> bool:
        return dataset_id in settings.DATASETS_ENABLED


_DEFAULT_REGISTRY: DatasetRegistry | None = None


def get_registry() -> DatasetRegistry:
    """Return a process-wide registry (lazy singleton)."""
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = DatasetRegistry()
    return _DEFAULT_REGISTRY


def reset_registry() -> None:
    """Test helper — drop the singleton."""
    global _DEFAULT_REGISTRY
    _DEFAULT_REGISTRY = None
