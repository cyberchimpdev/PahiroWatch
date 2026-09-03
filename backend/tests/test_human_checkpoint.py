import pytest
from app.agent.state import AgentState
from app.agent.tools import ToolRegistry, AgentSecurityError
from app.db.database import get_db_connection

def test_send_alert_fails_closed_without_approval():
    tools = ToolRegistry()
    unapproved_state = AgentState(
        run_id="TEST-RUN-UNAPPROVED",
        location_id="LOC-JALBIRE-KM28",
        location_name="Jalbire Sector",
        latitude=27.8182,
        longitude=84.5381,
        baseline_slope=38.5,
        elevation_m=340.0,
        goal="Test security checkpoint",
        approval_status="PENDING", # Not approved!
        requires_human_approval=True
    )

    with pytest.raises(AgentSecurityError) as exc_info:
        tools.send_alert(unapproved_state)

    assert "CRITICAL SECURITY VIOLATION" in str(exc_info.value)
    assert unapproved_state.alert_sent is False

def test_send_alert_succeeds_with_explicit_approval():
    tools = ToolRegistry()
    run_id = "TEST-RUN-APPROVED-01"
    incident_id = "INC-TEST-01"

    # Insert location and approval record into test DB
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO locations 
            (id, name, corridor_code, district, municipality, ward, latitude, longitude, elevation_m, baseline_slope_deg, road_name)
            VALUES ('LOC-GATE-TEST', 'Gate Check Location', 'NH05-TEST', 'Chitwan', 'Ichhyakamana', 5, 27.8182, 84.5381, 340.0, 38.5, 'NH05')
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO monitoring_runs (id, location_id, trigger_type, status)
            VALUES (?, 'LOC-GATE-TEST', 'TEST', 'PAUSED_HUMAN_GATE')
        """, (run_id,))
        cursor.execute("""
            INSERT OR REPLACE INTO incidents (id, run_id, location_id, title, status, severity, summary_en, summary_ne, recommended_action)
            VALUES (?, ?, 'LOC-GATE-TEST', 'Test Incident', 'PENDING_APPROVAL', 'HIGH', 'Test', 'परीक्षण', 'Inspect')
        """, (incident_id, run_id))
        cursor.execute("""
            INSERT OR REPLACE INTO approvals (id, incident_id, run_id, operator_name, action_type, operator_notes)
            VALUES ('APP-TEST-01', ?, ?, 'Ramesh', 'APPROVE', 'Verified by officer')
        """, (incident_id, run_id))
        conn.commit()
    finally:
        conn.close()

    approved_state = AgentState(
        run_id=run_id,
        location_id="LOC-GATE-TEST",
        location_name="Gate Check Location",
        latitude=27.8182,
        longitude=84.5381,
        baseline_slope=38.5,
        elevation_m=340.0,
        goal="Test security checkpoint approved",
        approval_status="APPROVED",
        incident_id=incident_id
    )

    result = tools.send_alert(approved_state)
    assert result["status"] == "DELIVERED"
    assert approved_state.alert_sent is True
    assert "alerts" in result
    assert "payload_ne" in result["alerts"]
