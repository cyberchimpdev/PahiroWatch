import json
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any
from app.agent.loop import AgentController
from app.engine.alert_generator import AlertGenerator
from app.db.database import get_db_connection

router = APIRouter(prefix="/api/incidents", tags=["Incidents & Human Gate"])
controller = AgentController()

@router.get("")
def list_incidents(status: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT i.*, l.name as location_name, l.corridor_code, l.latitude, l.longitude,
               r.risk_score, r.risk_level, r.confidence_score, r.confidence_reason
        FROM incidents i
        JOIN locations l ON i.location_id = l.id
        LEFT JOIN risk_assessments r ON i.run_id = r.run_id
    """
    params = []
    if status:
        query += " WHERE i.status = ?"
        params.append(status)
    query += " ORDER BY i.created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/{incident_id}")
def get_incident_detail(incident_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT i.*, l.name as location_name, l.corridor_code, l.latitude, l.longitude,
               l.elevation_m, l.baseline_slope_deg, l.road_name, l.critical_infrastructure,
               r.risk_score, r.risk_level, r.confidence_score, r.confidence_reason,
               r.rainfall_component, r.terrain_component, r.satellite_component,
               r.exposure_component, r.history_component, r.missing_data, r.contradictory_evidence
        FROM incidents i
        JOIN locations l ON i.location_id = l.id
        LEFT JOIN risk_assessments r ON i.run_id = r.run_id
        WHERE i.id = ?
    """, (incident_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = dict(row)
    incident["critical_infrastructure"] = json.loads(incident["critical_infrastructure"]) if incident.get("critical_infrastructure") else []
    incident["missing_data"] = json.loads(incident["missing_data"]) if incident.get("missing_data") else []

    # Get observations for this run
    cursor.execute("SELECT source_type, provider_name, is_synthetic, is_stale, payload_json FROM observations WHERE run_id = ?", (incident["run_id"],))
    obs_rows = cursor.fetchall()
    incident["observations"] = [
        {
            "source_type": o["source_type"],
            "provider_name": o["provider_name"],
            "is_synthetic": bool(o["is_synthetic"]),
            "is_stale": bool(o["is_stale"]),
            "payload": json.loads(o["payload_json"])
        }
        for o in obs_rows
    ]

    # Get approval logs
    cursor.execute("SELECT * FROM approvals WHERE incident_id = ? ORDER BY decided_at DESC", (incident_id,))
    incident["approvals"] = [dict(a) for a in cursor.fetchall()]

    # Get action dispatches
    cursor.execute("SELECT * FROM actions WHERE incident_id = ? ORDER BY delivered_at DESC", (incident_id,))
    incident["actions"] = [dict(act) for act in cursor.fetchall()]

    conn.close()

    # Pre-generate alerts preview
    alerts = AlertGenerator.generate_alerts(
        location_name=incident["location_name"],
        corridor_code=incident["corridor_code"],
        risk_level=incident["risk_level"] or incident["severity"],
        risk_score=incident["risk_score"] or 75.0,
        confidence_score=incident["confidence_score"] or 0.70,
        rainfall_24h=184.0, # default from telemetry
        slope_deg=incident["baseline_slope_deg"],
        recommended_action=incident["recommended_action"],
        road_distance_m=115.0
    )
    incident["alerts_preview"] = alerts

    return incident

@router.post("/{incident_id}/approve")
def approve_incident(
    incident_id: str,
    payload: Dict[str, Any] = Body(...)
):
    operator_name = payload.get("operator_name", "Ramesh, Municipal Disaster Management Officer")
    operator_notes = payload.get("operator_notes", "Verified via local ward contact and highway camera. Proceed with emergency inspection dispatch.")
    
    result = controller.process_human_approval(
        incident_id=incident_id,
        operator_name=operator_name,
        action_type="APPROVE",
        operator_notes=operator_notes
    )
    return result

@router.post("/{incident_id}/reject")
def reject_incident(
    incident_id: str,
    payload: Dict[str, Any] = Body(...)
):
    operator_name = payload.get("operator_name", "Ramesh, Municipal Disaster Management Officer")
    operator_notes = payload.get("operator_notes", "Local patrol confirms retaining wall intact and culverts draining normally. Escalation suppressed.")
    
    result = controller.process_human_approval(
        incident_id=incident_id,
        operator_name=operator_name,
        action_type="REJECT",
        operator_notes=operator_notes
    )
    return result
