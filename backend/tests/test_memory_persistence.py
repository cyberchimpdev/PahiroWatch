from app.agent.loop import AgentController
from app.providers.memory import MemoryProvider

def test_memory_persistence_cross_runs():
    controller = AgentController()
    mem_provider = MemoryProvider()
    location_id = "LOC-JALBIRE-KM28"

    # Step 1: Run #001 - Monsoon scenario detects high risk and creates incident
    state_run_1 = controller.run_monitoring_cycle(
        location_id=location_id,
        trigger_type="RUN_1_BURST",
        scenario_override="MONSOON"
    )
    assert state_run_1.incident_id is not None

    # Step 2: Human approves the inspection for Run #001
    approval_result = controller.process_human_approval(
        incident_id=state_run_1.incident_id,
        operator_name="Ramesh, Disaster Officer",
        action_type="APPROVE",
        operator_notes="Dispatched ground crew to KM 28"
    )
    assert approval_result["status"] == "APPROVED_AND_DISPATCHED"

    # Step 3: Run #002 - MemoryProvider should now see Run #001 in history
    mem_context = mem_provider.get_incident_memory(location_id)
    assert len(mem_context["recent_monitoring_runs"]) >= 1
    assert any(r["id"] == state_run_1.run_id for r in mem_context["recent_monitoring_runs"])
    
    # Check that previous human decision is recalled
    assert len(mem_context["recent_human_decisions"]) >= 1
    assert mem_context["recent_human_decisions"][0]["action_type"] == "APPROVE"
