"""Unit tests: configuration and utilities."""

from __future__ import annotations

import pytest

from config.config_manager import ConfigManager
from config.settings_manager import SettingsManager
from core.exceptions import ValidationError
from utilities.helpers import (
    clamp, normalize, weighted_blend, MovingAverage, format_duration, safe_mean,
)


class TestConfig:
    def test_loads_defaults(self, config: ConfigManager):
        assert config.get("app.name") == "EduSense AI 360"
        assert config.get("engagement.weights.attention") == 0.5

    def test_dot_path_and_default(self, config: ConfigManager):
        assert config.get("does.not.exist", 42) == 42

    def test_bands_present(self, config: ConfigManager):
        labels = [b["label"] for b in config.get("engagement.bands")]
        assert labels == ["Excellent", "Good", "Average", "Poor"]

    def test_weight_normalisation(self):
        cm = ConfigManager.__new__(ConfigManager)
        cm.warnings = []
        cfg = {"engagement": {"weights": {"attention": 2.0, "emotion": 1.0, "presence": 1.0}}}
        out = cm._normalise_engagement_weights(cfg)
        total = sum(out["engagement"]["weights"].values())
        assert abs(total - 1.0) < 1e-6

    def test_resolve_path(self, config: ConfigManager):
        assert config.resolve_path("sessions_dir").name == "sessions"


class TestSettings:
    def test_rejects_out_of_range(self, config):
        sm = SettingsManager(config)
        with pytest.raises(ValidationError):
            sm.validate_value("camera.fps", 999)

    def test_accepts_valid(self, config):
        sm = SettingsManager(config)
        assert sm.validate_value("camera.fps", 24) == 24


class TestUtilities:
    def test_clamp(self):
        assert clamp(150) == 100
        assert clamp(-5) == 0
        assert clamp(50) == 50

    def test_normalize(self):
        assert normalize(5, 0, 10) == 0.5
        assert normalize(0, 0, 0) == 0.0

    def test_weighted_blend(self):
        assert weighted_blend({"a": 1.0, "b": 0.0}, {"a": 0.5, "b": 0.5}) == 0.5

    def test_moving_average(self):
        ma = MovingAverage(3)
        for v in (10, 20, 30, 40):
            ma.update(v)
        assert ma.value == 30  # last three: 20,30,40

    def test_format_duration(self):
        assert format_duration(3725) == "1h 02m 05s"
        assert format_duration(65) == "01m 05s"

    def test_safe_mean(self):
        assert safe_mean([]) == 0.0
        assert safe_mean([2, 4]) == 3.0
