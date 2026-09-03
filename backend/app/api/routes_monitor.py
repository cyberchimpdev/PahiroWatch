import json
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from backend.app.agent.loop import AgentController
from backend.app.db.database import get_db_connection

router = APIRouter(prefix="/api", tags=["Monitor & Scenarios"])
controller = AgentController()

@router.get("/locations")
def get_locations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations ORDER BY ward ASC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    
    locations = []
    for r in rows:
        item = dict(r)
        item["critical_infrastructure"] = json.loads(item["critical_infrastructure"]) if item.get("critical_infrastructure") else []
        locations.append(item)
    return locations

@router.get("/corridor/status")
def get_corridor_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Locations
    cursor.execute("SELECT * FROM locations")
    locs = [dict(r) for r in cursor.fetchall()]
    
    # Latest run
    cursor.execute("""
        SELECT r.*, a.risk_score, a.risk_level, a.confidence_score, a.confidence_reason
        FROM monitoring_runs r
        LEFT JOIN risk_assessments a ON r.id = a.run_id
        ORDER BY r.started_at DESC LIMIT 1
    """)
    latest_run = cursor.fetchone()
    latest_run_dict = dict(latest_run) if latest_run else None

    # Active incidents
    cursor.execute("""
        SELECT i.*, l.name as location_name, l.latitude, l.longitude
        FROM incidents i
        JOIN locations l ON i.location_id = l.id
        WHERE i.status IN ('PENDING_APPROVAL', 'ACTIVE_MONITORING', 'ACTION_DISPATCHED')
        ORDER BY i.created_at DESC
    """)
    active_incidents = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "corridor_code": "NH05-MUG",
        "corridor_name": "Narayanghat–Mugling Lifeline Highway",
        "jurisdiction": "Ichhyakamana Rural Municipality, Chitwan",
        "operator": "Ramesh, Municipal Disaster Management Officer",
        "agent_status": "WATCHING",
        "latest_run": latest_run_dict,
        "active_incidents": active_incidents,
        "total_monitored_segments": len(locs)
    }

@router.post("/monitor/run")
def trigger_run(location_id: str, trigger_type: str = "MANUAL_DISPATCH"):
    state = controller.run_monitoring_cycle(
        location_id=location_id,
        trigger_type=trigger_type
    )
    return {
        "run_id": state.run_id,
        "status": "PAUSED_HUMAN_GATE" if state.requires_human_approval else "COMPLETED",
        "risk_score": state.risk_score,
        "risk_level": state.risk_level,
        "confidence_score": state.confidence_score,
        "incident_id": state.incident_id,
        "requires_human_approval": state.requires_human_approval
    }

@router.post("/scenarios/monsoon")
def run_monsoon_scenario(location_id: Optional[str] = "LOC-JALBIRE-KM28"):
    """
    Deterministic Demo Scenario 1: Extreme Monsoon Cloudburst Event.
    High rainfall + steep slope + satellite timeout & retry + high road exposure + human approval gate.
    """
    state = controller.run_monitoring_cycle(
        location_id=location_id or "LOC-JALBIRE-KM28",
        trigger_type="THRESHOLD_MONSOON_BURST",
        scenario_override="MONSOON"
    )
    return {
        "scenario": "MONSOON_EVENT",
        "run_id": state.run_id,
        "location": state.location_name,
        "risk_score": state.risk_score,
        "risk_level": state.risk_level,
        "confidence_score": state.confidence_score,
        "confidence_reason": state.confidence_reason,
        "incident_id": state.incident_id,
        "requires_human_approval": state.requires_human_approval,
        "retries_count": state.retries_count
    }

@router.post("/scenarios/low-confidence")
def run_low_confidence_scenario(location_id: Optional[str] = "LOC-KURINTAR-KM36"):
    """
    Deterministic Demo Scenario 2: Low Confidence / False Alarm Suppressed.
    High rainfall on gentle terrain with low exposure -> Agent concludes 'Monitor only'.
    """
    state = controller.run_monitoring_cycle(
        location_id=location_id or "LOC-KURINTAR-KM36",
        trigger_type="ANOMALY_CHECK",
        scenario_override="LOW_CONFIDENCE"
    )
    return {
        "scenario": "LOW_CONFIDENCE_MONITOR_ONLY",
        "run_id": state.run_id,
        "location": state.location_name,
        "risk_score": state.risk_score,
        "risk_level": state.risk_level,
        "confidence_score": state.confidence_score,
        "decision": state.agent_decision,
        "requires_human_approval": state.requires_human_approval
    }

@router.post("/scenarios/bad-day")
def run_bad_day_scenario(location_id: Optional[str] = "LOC-CHARKILO-KM32"):
    """
    Deterministic Demo Scenario 3: Bad Day / Sensor Failure & Resilience Mode.
    Weather data is stale, Copernicus satellite times out completely, LLM unreachable ->
    Deterministic Safety Fallback active, honest confidence reduction.
    """
    state = controller.run_monitoring_cycle(
        location_id=location_id or "LOC-CHARKILO-KM32",
        trigger_type="RESILIENCE_FAILOVER_TEST",
        scenario_override="BAD_DAY"
    )
    return {
        "scenario": "BAD_DAY_RESILIENCE",
        "run_id": state.run_id,
        "location": state.location_name,
        "risk_score": state.risk_score,
        "risk_level": state.risk_level,
        "confidence_score": state.confidence_score,
        "confidence_reason": state.confidence_reason,
        "is_resilience_mode": state.is_resilience_mode,
        "incident_id": state.incident_id,
        "requires_human_approval": state.requires_human_approval
    }
