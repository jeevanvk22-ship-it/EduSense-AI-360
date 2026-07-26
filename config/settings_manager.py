"""
EduSense AI 360 - Settings Manager
==================================

User-facing configuration lifecycle on top of :class:`ConfigManager`.

Responsibilities
----------------
* Expose the current effective settings to the Settings UI.
* Validate proposed changes (reusing the ConfigManager schema) before applying.
* Persist user overrides to ``config/user_config.json`` (defaults are never
  written to; only the delta the user changed is stored).
* Reset to defaults, and import/export the user configuration as a portable file.

Invalid values are rejected with a clear message and the prior value retained, so
the user can never push the application into an incoherent state.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from config.config_manager import (
    ConfigManager,
    USER_CONFIG_PATH,
    _SCHEMA,
    _coerce,
)
from core.exceptions import ValidationError, ConfigError
from core.logger import get_logger

log = get_logger("application")


class SettingsManager:
    """Validate, persist, reset, and exchange user settings."""

    def __init__(self, config: ConfigManager, user_path: Path = USER_CONFIG_PATH) -> None:
        self._config = config
        self._user_path = user_path

    # -- read ---------------------------------------------------------------
    def current(self) -> dict[str, Any]:
        """Return the full effective configuration (defaults + user + env)."""
        return self._config.as_dict()

    def user_overrides(self) -> dict[str, Any]:
        """Return only the persisted user overrides (may be empty)."""
        if not self._user_path.exists():
            return {}
        try:
            with open(self._user_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    # -- validate -----------------------------------------------------------
    @staticmethod
    def validate_value(path: str, value: Any) -> Any:
        """Validate a single dot-path value against the schema.

        Returns the coerced value, or raises :class:`ValidationError`.
        Paths absent from the schema are accepted as-is (free-form).
        """
        rule = _SCHEMA.get(path)
        if rule is None:
            return value
        try:
            coerced = _coerce(value, rule["type"])
        except (ValueError, TypeError) as exc:
            raise ValidationError(f"'{path}': {exc}")
        if "min" in rule and coerced < rule["min"]:
            raise ValidationError(f"'{path}': below minimum {rule['min']}")
        if "max" in rule and coerced > rule["max"]:
            raise ValidationError(f"'{path}': above maximum {rule['max']}")
        if "allowed" in rule and coerced not in rule["allowed"]:
            raise ValidationError(f"'{path}': must be one of {rule['allowed']}")
        return coerced

    # -- write --------------------------------------------------------------
    def update(self, changes: dict[str, Any]) -> dict[str, Any]:
        """Validate and persist a set of ``{dot.path: value}`` changes.

        All changes are validated first; if any fail, nothing is written
        (atomic apply). Returns the new effective configuration.
        """
        validated: dict[str, Any] = {}
        for path, value in changes.items():
            validated[path] = self.validate_value(path, value)

        overrides = self.user_overrides()
        for path, value in validated.items():
            self._set_nested(overrides, path, value)

        self._write_user_config(overrides)
        self._config.reload()
        log.info("Settings updated: %s", ", ".join(changes.keys()))
        return self._config.as_dict()

    def reset(self) -> dict[str, Any]:
        """Remove all user overrides, reverting to shipped defaults."""
        try:
            if self._user_path.exists():
                self._user_path.unlink()
        except OSError as exc:
            raise ConfigError(f"Could not reset settings: {exc}")
        self._config.reload()
        log.info("Settings reset to defaults.")
        return self._config.as_dict()

    # -- import / export ----------------------------------------------------
    def export_settings(self, destination: Path) -> Path:
        """Write the current user overrides to a portable JSON file."""
        destination = Path(destination)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, "w", encoding="utf-8") as fh:
                json.dump(self.user_overrides(), fh, indent=2)
        except OSError as exc:
            raise ConfigError(f"Could not export settings: {exc}")
        log.info("Settings exported to %s", destination)
        return destination

    def import_settings(self, source: Path) -> dict[str, Any]:
        """Load, validate, and apply user overrides from a JSON file."""
        source = Path(source)
        try:
            with open(source, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            raise ConfigError(f"Settings file not found: {source}")
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid settings file: {exc}")
        if not isinstance(data, dict):
            raise ConfigError("Settings file must contain a JSON object.")

        flat = self._flatten(data)
        for path, value in flat.items():
            self.validate_value(path, value)

        self._write_user_config(data)
        self._config.reload()
        log.info("Settings imported from %s", source)
        return self._config.as_dict()

    # -- helpers ------------------------------------------------------------
    def _write_user_config(self, overrides: dict[str, Any]) -> None:
        try:
            self._user_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._user_path, "w", encoding="utf-8") as fh:
                json.dump(overrides, fh, indent=2)
        except OSError as exc:
            raise ConfigError(f"Could not save settings: {exc}")

    @staticmethod
    def _set_nested(target: dict[str, Any], path: str, value: Any) -> None:
        parts = path.split(".")
        node = target
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value

    @classmethod
    def _flatten(cls, data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
        flat: dict[str, Any] = {}
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(cls._flatten(value, path))
            else:
                flat[path] = value
        return flat
