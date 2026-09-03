from backend.app.agent.loop import AgentController

def test_bad_day_scenario_graceful_resilience():
    controller = AgentController()
    state = controller.run_monitoring_cycle(
        location_id="LOC-CHARKILO-KM32",
        trigger_type="FAILOVER_TEST",
        scenario_override="BAD_DAY"
    )

    # Must activate resilience mode
    assert state.is_resilience_mode is True
    
    # Must report missing satellite data
    assert "SATELLITE_OPTICAL" in state.missing_data or "SATELLITE_CLOUD_CONTAMINATED" in state.missing_data

    # Confidence must honestly drop
    assert state.confidence_score <= 0.70
    assert "unavailable" in state.confidence_reason.lower() or "stale" in state.confidence_reason.lower()

    # Even with missing satellite, strong terrain and rain trigger recommendation with honest disclaimer
    assert state.requires_human_approval is True
    assert "satellite confirmation is unavailable" in state.agent_decision.lower()
