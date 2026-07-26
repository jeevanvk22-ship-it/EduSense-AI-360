"""
EduSense AI 360 - Frame Processing
==================================

Prepares raw camera frames for analysis and assesses their quality, implementing
the early stages of the computer-vision pipeline (Architecture Part 3 §6) and the
"uncertainty lowers confidence, it does not manufacture a confident negative"
principle (AI Decision Logic Part 6 §14).

Responsibilities
----------------
* Validate a frame (non-empty, correctly shaped).
* Provide an RGB view (for the UI) alongside the BGR working frame.
* Assess lighting (too dark / too bright) and sharpness (blur).
* Produce an optional down-scaled frame for detection to bound per-frame cost.
* Emit a :class:`FrameQuality` contract carrying a ``quality_confidence`` multiplier
  that downstream AI uses to discount unreliable frames.

Only NumPy is required (imported lazily), so this module is importable and testable
without OpenCV. Colour conversion and the blur metric are computed with NumPy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from config.config_manager import ConfigManager
from backend.contracts.models import FrameQuality
from core.logger import get_logger
from utilities.helpers import clamp

log = get_logger("camera")


@dataclass
class ProcessedFrame:
    """A processed frame: the working (BGR) image, an RGB view, and its quality."""
    bgr: Any
    rgb: Any
    quality: FrameQuality
    analysis: Any  # possibly down-scaled BGR frame for detection


class FrameProcessor:
    """Validates, converts, and quality-assesses frames."""

    def __init__(self, config: ConfigManager) -> None:
        self._low_light = float(config.get("frame_processing.low_light_threshold", 50.0))
        self._overexposed = float(config.get("frame_processing.overexposed_threshold", 220.0))
        self._blur_threshold = float(config.get("frame_processing.blur_threshold", 100.0))
        self._downscale_width = int(config.get("frame_processing.analysis_downscale_width", 640))

    # -- validation ---------------------------------------------------------
    @staticmethod
    def is_valid(frame: Any) -> bool:
        """True if the frame is a non-empty, 3-channel image array."""
        if frame is None:
            return False
        shape = getattr(frame, "shape", None)
        size = getattr(frame, "size", 0)
        return bool(shape) and len(shape) == 3 and shape[2] == 3 and size > 0

    # -- colour conversion --------------------------------------------------
    @staticmethod
    def bgr_to_rgb(frame_bgr: Any) -> Any:
        """Reverse the channel order (BGR<->RGB) using a NumPy view."""
        return frame_bgr[:, :, ::-1]

    @staticmethod
    def to_grayscale(frame_bgr: Any) -> Any:
        """Luma (perceptual grayscale) from a BGR frame via NumPy."""
        import numpy as np
        b = frame_bgr[:, :, 0].astype(np.float32)
        g = frame_bgr[:, :, 1].astype(np.float32)
        r = frame_bgr[:, :, 2].astype(np.float32)
        return 0.114 * b + 0.587 * g + 0.299 * r

    # -- quality metrics ----------------------------------------------------
    def _brightness(self, gray: Any) -> float:
        return float(gray.mean())

    def _blur_score(self, gray: Any) -> float:
        """Variance of a discrete Laplacian; low variance == blurry.

        Implemented with NumPy slicing (no SciPy/OpenCV) so the metric is
        dependency-light and testable.
        """
        import numpy as np
        g = gray.astype(np.float32)
        lap = (
            -4.0 * g[1:-1, 1:-1]
            + g[:-2, 1:-1] + g[2:, 1:-1]
            + g[1:-1, :-2] + g[1:-1, 2:]
        )
        return float(lap.var()) if lap.size else 0.0

    def assess_quality(self, frame_bgr: Any) -> FrameQuality:
        """Assess lighting and sharpness; derive a confidence multiplier."""
        gray = self.to_grayscale(frame_bgr)
        brightness = self._brightness(gray)
        blur = self._blur_score(gray)

        is_low_light = brightness < self._low_light
        is_overexposed = brightness > self._overexposed
        is_blurry = blur < self._blur_threshold

        # Confidence multiplier: start at 1.0, degrade for each defect.
        confidence = 1.0
        reasons: list[str] = []
        if is_low_light:
            # Scale down toward the darkest acceptable point.
            confidence *= clamp(brightness / max(self._low_light, 1e-6), 0.3, 1.0)
            reasons.append("low light")
        if is_overexposed:
            confidence *= 0.6
            reasons.append("overexposed")
        if is_blurry:
            confidence *= clamp(blur / max(self._blur_threshold, 1e-6), 0.3, 1.0)
            reasons.append("blurry")

        confidence = round(clamp(confidence, 0.0, 1.0), 3)
        ok = not (is_low_light or is_overexposed or is_blurry)

        return FrameQuality(
            ok=ok,
            brightness=round(brightness, 1),
            is_low_light=is_low_light,
            is_overexposed=is_overexposed,
            blur_score=round(blur, 1),
            is_blurry=is_blurry,
            quality_confidence=confidence,
            reason="ok" if ok else ", ".join(reasons),
        )

    # -- downscaling --------------------------------------------------------
    def downscale_for_analysis(self, frame_bgr: Any) -> Any:
        """Return a width-bounded copy for detection, preserving aspect ratio.

        Uses simple NumPy strided sampling so no OpenCV resize is required. If the
        frame is already within the target width it is returned unchanged.
        """
        h, w = frame_bgr.shape[:2]
        if w <= self._downscale_width:
            return frame_bgr
        step = max(1, w // self._downscale_width)
        return frame_bgr[::step, ::step]

    # -- public api ---------------------------------------------------------
    def process(self, frame_bgr: Any) -> Optional[ProcessedFrame]:
        """Validate, convert, and assess a frame.

        Returns a :class:`ProcessedFrame`, or ``None`` if the frame is invalid.
        """
        if not self.is_valid(frame_bgr):
            log.debug("Discarded invalid frame")
            return None

        quality = self.assess_quality(frame_bgr)
        rgb = self.bgr_to_rgb(frame_bgr)
        analysis = self.downscale_for_analysis(frame_bgr)

        if not quality.ok:
            log.debug("Low-quality frame: %s (confidence %.2f)", quality.reason, quality.quality_confidence)

        return ProcessedFrame(bgr=frame_bgr, rgb=rgb, quality=quality, analysis=analysis)
