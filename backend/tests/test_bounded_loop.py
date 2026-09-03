from app.agent.loop import AgentController

def test_monsoon_scenario_bounded_and_escalates():
    controller = AgentController()
    state = controller.run_monitoring_cycle(
        location_id="LOC-JALBIRE-KM28",
        trigger_type="THRESHOLD_BURST",
        scenario_override="MONSOON"
    )

    # 1. Bounded steps constraint (MUST NEVER EXCEED 10)
    assert state.step_count <= 10
    
    # 2. Risk & Escalation check
    assert state.risk_score >= 60.0
    assert state.risk_level in ["HIGH", "CRITICAL"]
    assert state.requires_human_approval is True
    assert state.approval_status == "PENDING"
    assert state.incident_id is not None

    # 3. Retry count on satellite tool
    assert state.retries_count >= 1

    # 4. Reduced confidence due to monsoon clouds/satellite degradation
    assert state.confidence_score <= 0.80

def test_low_confidence_scenario_suppresses_alarm():
    controller = AgentController()
    state = controller.run_monitoring_cycle(
        location_id="LOC-KURINTAR-KM36",
        trigger_type="ANOMALY_MONITOR",
        scenario_override="LOW_CONFIDENCE"
    )

    assert state.step_count <= 10
    assert state.risk_score < 55.0
    # Must NOT escalate or create emergency gate for false alarm
    assert state.requires_human_approval is False
    assert "not warrant operational highway escalation" in state.agent_decision or "routine" in state.agent_decision.lower()
