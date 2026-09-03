import pytest
from backend.app.engine.confidence_engine import ConfidenceEngine

def test_confidence_all_sources_good():
    weather = {"rainfall_24h_mm": 120.0, "is_stale": False}
    terrain = {"slope_deg": 35.0}
    satellite = {"change_score": 0.65, "cloud_cover_pct": 20.0, "surface_change_indicator": "ACTIVE"}
    exposure = {"exposure_score": 75.0}

    conf, reason, missing, contradictory = ConfidenceEngine.assess_confidence(
        weather_obs=weather,
        terrain_obs=terrain,
        satellite_obs=satellite,
        exposure_obs=exposure
    )

    assert conf >= 0.80
    assert len(missing) == 0
    assert "Rainfall telemetry is recent" in reason

def test_confidence_penalty_missing_satellite():
    weather = {"rainfall_24h_mm": 180.0, "is_stale": False}
    terrain = {"slope_deg": 38.0}

    conf, reason, missing, contradictory = ConfidenceEngine.assess_confidence(
        weather_obs=weather,
        terrain_obs=terrain,
        satellite_obs=None,
        is_satellite_missing=True
    )

    # Should be heavily penalized
    assert conf <= 0.70
    assert "SATELLITE_OPTICAL" in missing
    assert "unavailable" in reason.lower()

def test_confidence_contradictory_evidence_detection():
    # Severe rain on virtually flat ground (<15 deg)
    weather = {"rainfall_24h_mm": 160.0, "is_stale": False}
    terrain = {"slope_deg": 8.0}
    satellite = {"change_score": 0.05, "cloud_cover_pct": 10.0, "surface_change_indicator": "STABLE"}

    conf, reason, missing, contradictory = ConfidenceEngine.assess_confidence(
        weather_obs=weather,
        terrain_obs=terrain,
        satellite_obs=satellite
    )

    assert contradictory is not None
    assert "gentle" in contradictory.lower() or "flooding" in contradictory.lower()
