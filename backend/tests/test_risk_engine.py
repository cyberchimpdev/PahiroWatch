import pytest
from backend.app.engine.risk_calculator import RiskCalculator

def test_risk_calculator_monsoon_high():
    weather = {"rainfall_24h_mm": 184.0}
    terrain = {"slope_deg": 38.5}
    satellite = {"change_score": 0.71, "cloud_cover_pct": 28.0}
    exposure = {"exposure_score": 82.0}
    memory = {"history_multiplier": 1.15, "total_historical_events": 2, "has_unresolved_incidents": False}

    score, level, breakdown = RiskCalculator.calculate_risk(
        weather_obs=weather,
        terrain_obs=terrain,
        satellite_obs=satellite,
        exposure_obs=exposure,
        memory_obs=memory
    )

    assert 70.0 <= score <= 95.0
    assert level in ["HIGH", "CRITICAL"]
    assert breakdown["rainfall_component"] == 35.0
    assert breakdown["total_score"] == score

def test_risk_calculator_low_conditions():
    weather = {"rainfall_24h_mm": 15.0}
    terrain = {"slope_deg": 12.0}
    satellite = {"change_score": 0.05, "cloud_cover_pct": 10.0}
    exposure = {"exposure_score": 25.0}
    memory = {"history_multiplier": 1.0, "total_historical_events": 0, "has_unresolved_incidents": False}

    score, level, breakdown = RiskCalculator.calculate_risk(
        weather_obs=weather,
        terrain_obs=terrain,
        satellite_obs=satellite,
        exposure_obs=exposure,
        memory_obs=memory
    )

    assert score < 30.0
    assert level == "LOW"

def test_risk_calculator_bounded_0_to_100():
    # Extreme hypothetical values
    weather = {"rainfall_24h_mm": 999.0}
    terrain = {"slope_deg": 85.0}
    satellite = {"change_score": 1.0, "cloud_cover_pct": 0.0}
    exposure = {"exposure_score": 100.0}
    memory = {"history_multiplier": 2.0, "total_historical_events": 10, "has_unresolved_incidents": True}

    score, level, breakdown = RiskCalculator.calculate_risk(
        weather_obs=weather,
        terrain_obs=terrain,
        satellite_obs=satellite,
        exposure_obs=exposure,
        memory_obs=memory
    )

    assert score <= 100.0
    assert score >= 0.0
    assert level == "CRITICAL"
