"""
EduSense AI 360 - Exception Hierarchy
=====================================

A single rooted exception tree (:class:`EduSenseError`) with specific subclasses
per subsystem. Modules raise the most specific exception that applies; the central
:mod:`core.error_handler` catches, classifies, logs, and recovers from them.

Using a dedicated hierarchy (rather than bare ``Exception``) lets the error handler
and tests distinguish *recoverable, expected* domain faults (a dropped frame, a
missing model) from genuinely unexpected programming errors, and lets each fault
carry a user-facing message separate from its technical detail.
"""

from __future__ import annotations

from typing import Optional


class EduSenseError(Exception):
    """Base class for every EduSense AI 360 error.

    Parameters
    ----------
    message:
        Technical message for logs and developers.
    user_message:
        Optional friendly message safe to show in the UI. Falls back to a generic
        line when not provided.
    recoverable:
        Whether the system can continue (degrade) after this fault. Defaults to
        ``True`` because the architecture favours graceful degradation.
    """

    default_user_message: str = "Something went wrong. The application will continue."

    def __init__(
        self,
        message: str,
        *,
        user_message: Optional[str] = None,
        recoverable: bool = True,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.user_message: str = user_message or self.default_user_message
        self.recoverable: bool = recoverable


# --- Configuration -----------------------------------------------------------
class ConfigError(EduSenseError):
    """Configuration could not be loaded, parsed, or validated."""

    default_user_message = "There is a problem with the configuration. Defaults were applied."


class ValidationError(EduSenseError):
    """A value failed validation against its permitted type/range/set."""

    default_user_message = "An entered value was invalid and was not applied."


# --- Camera / frames ---------------------------------------------------------
class CameraError(EduSenseError):
    """Camera device could not be opened, read, or controlled."""

    default_user_message = "The camera is unavailable. Please check the connection."


class FrameError(EduSenseError):
    """A frame was missing, empty, or malformed."""


# --- AI models ---------------------------------------------------------------
class ModelError(EduSenseError):
    """An AI model failed to load, initialise, or predict."""

    default_user_message = "An AI component is unavailable; analysis will continue with reduced detail."


class FaceDetectionError(ModelError):
    """Face detection failed for a frame."""


class EyeTrackingError(ModelError):
    """Eye/landmark analysis failed for a face."""


class EmotionError(ModelError):
    """Emotion prediction failed for a face."""


# --- Analytics / engagement --------------------------------------------------
class AnalyticsError(EduSenseError):
    """An analytics computation failed."""


class EngagementError(AnalyticsError):
    """The engagement engine failed to compute a score."""


# --- Session -----------------------------------------------------------------
class SessionError(EduSenseError):
    """A session lifecycle operation failed."""


# --- Reporting / export ------------------------------------------------------
class ReportError(EduSenseError):
    """A report could not be assembled."""

    default_user_message = "The report could not be generated. Your session data is safe."


class ExportError(ReportError):
    """A report could not be written to disk in the requested format."""

    default_user_message = "The export failed. Please check the export location and try again."
