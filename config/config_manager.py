"""
EduSense AI 360 - Configuration Manager
=======================================

Owns the authoritative runtime configuration and serves validated values to every
module via dot-path access (e.g. ``config.get("engagement.weights.attention")``).

Precedence (later overrides earlier):
    1. ``config/default_config.json``   - shipped baseline (read-only)
    2. ``config/user_config.json``      - user overrides from the Settings page
    3. Environment variables            - ``EDUSENSE_<SECTION>__<KEY>`` overrides

All values are validated against an embedded schema (type + range/set). Invalid
values are rejected and the prior valid (or default) value is retained, so the
application always starts with a coherent configuration.

JSON is used for configuration (per the project technology stack) to avoid an
extra dependency and keep config human-readable and diff-friendly.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

from core.exceptions import ConfigError

# Project root = parent of the ``config`` package directory.
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "default_config.json"
USER_CONFIG_PATH = ROOT_DIR / "config" / "user_config.json"

ENV_PREFIX = "EDUSENSE_"

# ---------------------------------------------------------------------------
# Validation schema. Each leaf path maps to a rule describing its type and any
# numeric bounds or allowed values. Paths not listed are accepted as-is (e.g.
# free-form strings), but typed paths are strictly enforced.
# ---------------------------------------------------------------------------
_SCHEMA: dict[str, dict[str, Any]] = {
    "camera.device_index": {"type": int, "min": 0, "max": 16},
    "camera.width": {"type": int, "min": 320, "max": 3840},
    "camera.height": {"type": int, "min": 240, "max": 2160},
    "camera.fps": {"type": int, "min": 1, "max": 120},
    "camera.max_faces": {"type": int, "min": 1, "max": 50},
    "face_detection.min_confidence": {"type": float, "min": 0.0, "max": 1.0},
    "face_detection.model_selection": {"type": int, "allowed": [0, 1]},
    "face_detection.tracking_max_lost_frames": {"type": int, "min": 1, "max": 300},
    "eye_tracking.ear_open_threshold": {"type": float, "min": 0.05, "max": 0.5},
    "eye_tracking.gaze_center_tolerance": {"type": float, "min": 0.05, "max": 1.0},
    "eye_tracking.head_yaw_limit": {"type": float, "min": 5.0, "max": 90.0},
    "eye_tracking.head_pitch_limit": {"type": float, "min": 5.0, "max": 90.0},
    "eye_tracking.long_closure_seconds": {"type": float, "min": 0.5, "max": 30.0},
    "emotion.backend": {"type": str, "allowed": ["fer", "deepface"]},
    "emotion.confidence_threshold": {"type": float, "min": 0.0, "max": 1.0},
    "emotion.smoothing_window": {"type": int, "min": 1, "max": 60},
    "engagement.weights.attention": {"type": float, "min": 0.0, "max": 1.0},
    "engagement.weights.emotion": {"type": float, "min": 0.0, "max": 1.0},
    "engagement.weights.presence": {"type": float, "min": 0.0, "max": 1.0},
    "engagement.distraction_threshold": {"type": (int, float), "min": 0, "max": 100},
    "engagement.prolonged_inattention_seconds": {"type": (int, float), "min": 1, "max": 600},
    "engagement.smoothing_window": {"type": int, "min": 1, "max": 120},
    "analytics.trend_min_frames": {"type": int, "min": 2, "max": 1000},
    "frame_processing.low_light_threshold": {"type": (int, float), "min": 0, "max": 255},
    "frame_processing.overexposed_threshold": {"type": (int, float), "min": 0, "max": 255},
    "frame_processing.blur_threshold": {"type": (int, float), "min": 0, "max": 10000},
    "frame_processing.analysis_downscale_width": {"type": int, "min": 160, "max": 3840},
    "performance.target_fps": {"type": (int, float), "min": 1, "max": 120},
    "performance.max_frame_ms": {"type": (int, float), "min": 5, "max": 1000},
    "performance.max_cpu_percent": {"type": (int, float), "min": 1, "max": 100},
    "performance.max_memory_mb": {"type": (int, float), "min": 128, "max": 65536},
    "performance.sample_window": {"type": int, "min": 5, "max": 600},
    "dashboard.theme": {"type": str, "allowed": ["dark", "light", "system"]},
    "dashboard.live_refresh_hz": {"type": (int, float), "min": 0.2, "max": 10.0},
    "dashboard.chart_refresh_hz": {"type": (int, float), "min": 0.2, "max": 10.0},
    "logging.level": {"type": str, "allowed": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
    "logging.rotation_max_bytes": {"type": int, "min": 65536, "max": 104_857_600},
    "logging.retention_count": {"type": int, "min": 1, "max": 100},
    "report.default_format": {"type": str, "allowed": ["pdf", "excel", "csv"]},
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge ``override`` into a copy of ``base``."""
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _coerce(value: Any, expected: Any) -> Any:
    """Best-effort coercion of ``value`` to the expected type(s)."""
    types = expected if isinstance(expected, tuple) else (expected,)
    if isinstance(value, types):
        return value
    # Allow ints where floats are expected and vice-versa via explicit coercion.
    for t in types:
        try:
            if t is float:
                return float(value)
            if t is int and not isinstance(value, bool):
                return int(value)
            if t is str:
                return str(value)
        except (TypeError, ValueError):
            continue
    raise ValueError(f"expected {expected}, got {type(value).__name__}")


class ConfigManager:
    """Loads, validates, and serves the runtime configuration."""

    def __init__(
        self,
        default_path: Path = DEFAULT_CONFIG_PATH,
        user_path: Path = USER_CONFIG_PATH,
        apply_env: bool = True,
    ) -> None:
        self._default_path = default_path
        self._user_path = user_path
        self._apply_env = apply_env
        self._config: dict[str, Any] = {}
        self.warnings: list[str] = []
        self.reload()

    # -- loading ------------------------------------------------------------
    def reload(self) -> None:
        """(Re)load defaults + user overrides + env overrides, then validate."""
        self.warnings = []

        defaults = self._read_json(self._default_path, required=True)
        merged = defaults

        if self._user_path.exists():
            try:
                user = self._read_json(self._user_path, required=False)
                merged = _deep_merge(merged, user)
            except ConfigError as exc:
                self.warnings.append(f"User config ignored: {exc.message}")

        if self._apply_env:
            merged = self._apply_env_overrides(merged)

        self._config = self._validate(merged, defaults)
        self._ensure_directories()

    def _read_json(self, path: Path, *, required: bool) -> dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ConfigError(f"Config root must be an object: {path}")
            return data
        except FileNotFoundError:
            if required:
                raise ConfigError(f"Required configuration file missing: {path}")
            return {}
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {path}: {exc}")

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply ``EDUSENSE_SECTION__KEY=value`` style environment overrides."""
        result = deepcopy(config)
        for env_key, raw in os.environ.items():
            if not env_key.startswith(ENV_PREFIX):
                continue
            path = env_key[len(ENV_PREFIX):].lower().replace("__", ".")
            self._set_path(result, path, self._parse_env_value(raw))
        return result

    @staticmethod
    def _parse_env_value(raw: str) -> Any:
        for caster in (json.loads,):
            try:
                return caster(raw)
            except (ValueError, TypeError):
                pass
        return raw

    # -- validation ---------------------------------------------------------
    def _validate(self, config: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
        """Validate typed leaves; revert invalid values to defaults with a warning."""
        validated = deepcopy(config)

        for path, rule in _SCHEMA.items():
            value = self._get_path(validated, path, default=_MISSING)
            if value is _MISSING:
                continue
            try:
                coerced = _coerce(value, rule["type"])
                if "min" in rule and coerced < rule["min"]:
                    raise ValueError(f"below minimum {rule['min']}")
                if "max" in rule and coerced > rule["max"]:
                    raise ValueError(f"above maximum {rule['max']}")
                if "allowed" in rule and coerced not in rule["allowed"]:
                    raise ValueError(f"not in {rule['allowed']}")
                self._set_path(validated, path, coerced)
            except (ValueError, TypeError) as exc:
                fallback = self._get_path(defaults, path, default=None)
                self.warnings.append(f"Invalid config '{path}' ({exc}); using default {fallback!r}.")
                self._set_path(validated, path, fallback)

        validated = self._normalise_engagement_weights(validated)
        return validated

    def _normalise_engagement_weights(self, config: dict[str, Any]) -> dict[str, Any]:
        """Ensure engagement factor weights sum to 1.0; normalise if not."""
        weights = self._get_path(config, "engagement.weights", default={})
        if not isinstance(weights, dict) or not weights:
            return config
        total = sum(float(v) for v in weights.values())
        if total <= 0:
            self.warnings.append("Engagement weights sum to zero; reverting to defaults.")
            return config
        if abs(total - 1.0) > 1e-6:
            self.warnings.append(f"Engagement weights summed to {total:.3f}; normalised to 1.0.")
            self._set_path(
                config, "engagement.weights",
                {k: round(float(v) / total, 6) for k, v in weights.items()},
            )
        return config

    # -- accessors ----------------------------------------------------------
    def get(self, path: str, default: Any = None) -> Any:
        """Return a configuration value by dot-path, or ``default`` if absent."""
        value = self._get_path(self._config, path, default=_MISSING)
        return default if value is _MISSING else deepcopy(value)

    def section(self, name: str) -> dict[str, Any]:
        """Return a whole top-level section as a copy."""
        return deepcopy(self._config.get(name, {}))

    def as_dict(self) -> dict[str, Any]:
        """Return a deep copy of the entire runtime configuration."""
        return deepcopy(self._config)

    def resolve_path(self, path_key: str) -> Path:
        """Resolve a configured relative path (under ``paths``) to an absolute Path."""
        rel = self.get(f"paths.{path_key}")
        if rel is None:
            raise ConfigError(f"Unknown path key: {path_key}")
        return (ROOT_DIR / rel).resolve()

    # -- helpers ------------------------------------------------------------
    def _ensure_directories(self) -> None:
        for key in self._config.get("paths", {}):
            try:
                self.resolve_path(key).mkdir(parents=True, exist_ok=True)
            except OSError:
                self.warnings.append(f"Could not create directory for paths.{key}")

    @staticmethod
    def _get_path(config: dict[str, Any], path: str, default: Any = None) -> Any:
        node: Any = config
        for part in path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    @staticmethod
    def _set_path(config: dict[str, Any], path: str, value: Any) -> None:
        parts = path.split(".")
        node = config
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                return
        node[parts[-1]] = value


class _Missing:
    """Sentinel distinguishing 'absent' from a legitimate ``None`` value."""


_MISSING = _Missing()

# ---------------------------------------------------------------------------
# Process-wide singleton accessor.
# ---------------------------------------------------------------------------
_INSTANCE: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Return the shared ConfigManager, creating it on first use."""
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = ConfigManager()
    return _INSTANCE


def reset_config() -> None:
    """Drop the cached singleton (used by tests and after settings changes)."""
    global _INSTANCE
    _INSTANCE = None
