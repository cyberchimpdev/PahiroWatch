import json
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from backend.app.db.database import get_db_connection

router = APIRouter(prefix="/api/agent", tags=["Agent Trace & Metrics"])

@router.get("/trace")
def get_trace(run_id: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if not run_id:
        # Get the latest run_id
        cursor.execute("SELECT id FROM monitoring_runs ORDER BY started_at DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"run_id": None, "traces": [], "run_info": None}
        run_id = row["id"]

    cursor.execute("""
        SELECT r.*, l.name as location_name, l.corridor_code,
               a.risk_score, a.risk_level, a.confidence_score, a.confidence_reason
        FROM monitoring_runs r
        JOIN locations l ON r.location_id = l.id
        LEFT JOIN risk_assessments a ON r.id = a.run_id
        WHERE r.id = ?
    """, (run_id,))
    run_row = cursor.fetchone()
    run_info = dict(run_row) if run_row else None

    cursor.execute("""
        SELECT id, step_number, event_type, content, metadata_json, timestamp
        FROM agent_traces
        WHERE run_id = ?
        ORDER BY step_number ASC, id ASC
    """, (run_id,))
    trace_rows = cursor.fetchall()

    traces = []
    for t in trace_rows:
        row_dict = dict(t)
        traces.append({
            "id": row_dict["id"],
            "step_number": row_dict["step_number"],
            "event_type": row_dict["event_type"],
            "content": row_dict["content"],
            "metadata": json.loads(row_dict["metadata_json"]) if row_dict.get("metadata_json") else None,
            "timestamp": row_dict["timestamp"]
        })

    conn.close()

    return {
        "run_id": run_id,
        "run_info": run_info,
        "traces": traces
    }

@router.get("/metrics")
def get_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as total_runs,
            SUM(total_tokens) as total_tokens,
            SUM(estimated_cost_npr) as total_cost_npr,
            AVG(total_latency_ms) as avg_latency_ms,
            SUM(CASE WHEN is_resilience_mode = 1 THEN 1 ELSE 0 END) as resilience_runs
        FROM monitoring_runs
    """)
    row = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as incident_count FROM incidents")
    inc_row = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) as approval_count FROM approvals WHERE action_type = 'APPROVE'")
    app_row = cursor.fetchone()

    conn.close()

    return {
        "total_runs": row["total_runs"] or 0,
        "total_tokens": row["total_tokens"] or 0,
        "total_cost_npr": round(row["total_cost_npr"] or 0.0, 4),
        "avg_latency_ms": int(row["avg_latency_ms"] or 0),
        "resilience_runs": row["resilience_runs"] or 0,
        "total_incidents": inc_row["incident_count"] or 0,
        "total_human_approvals": app_row["approval_count"] or 0,
        "cost_per_run_npr": round((row["total_cost_npr"] or 0.0) / max(1, row["total_runs"] or 1), 4)
    }

@router.get("/runs")
def list_runs(limit: int = 15):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, l.name as location_name, a.risk_score, a.risk_level, a.confidence_score
        FROM monitoring_runs r
        JOIN locations l ON r.location_id = l.id
        LEFT JOIN risk_assessments a ON r.id = a.run_id
        ORDER BY r.started_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
