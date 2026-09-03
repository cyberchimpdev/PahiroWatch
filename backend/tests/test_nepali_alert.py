import pytest
from backend.app.engine.alert_generator import AlertGenerator

def test_nepali_and_low_bw_alert_generation():
    alerts = AlertGenerator.generate_alerts(
        location_name="Jalbire Waterfall Sector (KM 28)",
        corridor_code="NH05-MUG",
        risk_level="HIGH",
        risk_score=78.5,
        confidence_score=0.62,
        rainfall_24h=184.0,
        slope_deg=38.5,
        recommended_action="Inspect road segment and prepare traffic warning",
        road_distance_m=115.0
    )

    # 1. English report check
    assert "HIGH RISK" in alerts["payload_en"]
    assert "184.0 mm" in alerts["payload_en"]

    # 2. Nepali alert check
    assert "पहिरोवाच" in alerts["payload_ne"]
    assert "उच्च जोखिम" in alerts["payload_ne"]
    assert "निरीक्षण" in alerts["payload_ne"]
    assert "सवारी आवागमन" in alerts["payload_ne"]

    # 3. Low-bandwidth SMS format (<160 chars)
    sms = alerts["payload_sms_compact"]
    assert len(sms) <= 160
    assert "PAHIROWATCH ALERT" in sms
    assert "Rain24h:" in sms
