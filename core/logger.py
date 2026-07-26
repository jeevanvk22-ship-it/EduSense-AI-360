"""
EduSense AI 360 - Logging
=========================

Enterprise logging built on the standard :mod:`logging` module.

Design
------
* Loggers are namespaced ``edusense.<category>`` where category is one of
  ``application, session, camera, ai, errors, performance, debug``.
* Each category writes to its own rotating file under ``logs/<category>/`` and,
  optionally, to the console. The dedicated ``errors`` logger additionally
  captures WARNING+ from every category so all problems are findable in one place.
* Logging never crashes the application: if a log directory is not writable the
  setup degrades to console-only and records the downgrade.

Usage
-----
    from core.logger import setup_logging, get_logger
    setup_logging(config)                  # once, at startup
    log = get_logger("camera")
    log.info("Camera initialised")
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # avoid a runtime import cycle; only needed for type hints
    from config.config_manager import ConfigManager

ROOT_LOGGER_NAME = "edusense"

CATEGORIES = (
    "application",
    "session",
    "camera",
    "ai",
    "performance",
    "debug",
    "errors",
)

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured: bool = False


def get_logger(category: str = "application") -> logging.Logger:
    """Return the namespaced logger for a category (creating it if needed)."""
    name = f"{ROOT_LOGGER_NAME}.{category}" if category else ROOT_LOGGER_NAME
    return logging.getLogger(name)


def _make_file_handler(
    directory: Path,
    filename: str,
    level: int,
    max_bytes: int,
    backup_count: int,
    formatter: logging.Formatter,
) -> Optional[RotatingFileHandler]:
    """Create a rotating file handler, or ``None`` if the path is unusable."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            directory / filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        return handler
    except OSError:
        return None


def setup_logging(config: "ConfigManager") -> None:
    """Configure the logging tree from the runtime configuration.

    Idempotent: calling it more than once has no additional effect.
    """
    global _configured
    if _configured:
        return

    level_name = str(config.get("logging.level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    console = bool(config.get("logging.console", True))
    max_bytes = int(config.get("logging.rotation_max_bytes", 2_097_152))
    backup_count = int(config.get("logging.retention_count", 5))
    logs_dir = Path(config.resolve_path("logs_dir"))

    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger(ROOT_LOGGER_NAME)
    root.setLevel(logging.DEBUG)   # handlers filter; root passes everything
    root.handlers.clear()
    root.propagate = False

    degraded = False

    # Optional console handler on the root (shared by all categories).
    if console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    # An aggregate error sink at the root captures WARNING+ from all categories.
    error_handler = _make_file_handler(
        logs_dir / "errors", "errors.log", logging.WARNING, max_bytes, backup_count, formatter
    )
    if error_handler is not None:
        root.addHandler(error_handler)
    else:
        degraded = True

    # Per-category file handlers attached to each category logger.
    for category in CATEGORIES:
        if category == "errors":
            continue  # handled at root as the aggregate sink
        cat_logger = logging.getLogger(f"{ROOT_LOGGER_NAME}.{category}")
        cat_logger.setLevel(logging.DEBUG if category == "debug" else level)
        cat_logger.handlers.clear()
        cat_logger.propagate = True   # bubble up to console + error sink

        cat_level = logging.DEBUG if category == "debug" else level
        handler = _make_file_handler(
            logs_dir / category, f"{category}.log", cat_level, max_bytes, backup_count, formatter
        )
        if handler is not None:
            cat_logger.addHandler(handler)
        else:
            degraded = True

    _configured = True

    startup = get_logger("application")
    startup.info("Logging initialised (level=%s, console=%s)", level_name, console)
    if degraded:
        startup.warning("Some log files were unwritable; affected categories use console only.")


def reset_logging() -> None:
    """Tear down logging configuration (used by tests)."""
    global _configured
    root = logging.getLogger(ROOT_LOGGER_NAME)
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()
    for category in CATEGORIES:
        logger = logging.getLogger(f"{ROOT_LOGGER_NAME}.{category}")
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
    _configured = False
