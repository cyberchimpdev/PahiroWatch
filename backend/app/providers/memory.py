import json
from typing import Dict, Any, List
from app.providers.base import BaseMemoryProvider
from app.db.database import get_db_connection

class MemoryProvider(BaseMemoryProvider):
    """
    Persistent Memory Provider.
    Queries previous runs, historical records, and unresolved incidents from SQLite.
    Allows Run #002 to recall Run #001's assessments and actions.
    """
    def get_incident_memory(self, location_id: str) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch static/seeded historical baseline
        cursor.execute(
            "SELECT memory_value FROM agent_memory WHERE location_id = ? AND memory_key = 'HISTORICAL_INCIDENTS'",
            (location_id,)
        )
        row = cursor.fetchone()
        static_history = json.loads(row["memory_value"]) if row else {"incident_count_past_24m": 0}

        # 2. Fetch recent monitoring runs for this location
        cursor.execute("""
            SELECT r.id, r.status, r.trigger_type, r.started_at, a.risk_score, a.risk_level
            FROM monitoring_runs r
            LEFT JOIN risk_assessments a ON r.id = a.run_id
            WHERE r.location_id = ?
            ORDER BY r.started_at DESC
            LIMIT 5
        """, (location_id,))
        recent_runs = [dict(r) for r in cursor.fetchall()]

        # 3. Fetch unresolved incidents in this corridor
        cursor.execute("""
            SELECT id, title, status, severity, recommended_action, created_at
            FROM incidents
            WHERE location_id = ? AND status IN ('PENDING_APPROVAL', 'ACTIVE_MONITORING', 'ACTION_DISPATCHED')
            ORDER BY created_at DESC
        """, (location_id,))
        unresolved = [dict(r) for r in cursor.fetchall()]

        # 4. Fetch past human approvals/rejections
        cursor.execute("""
            SELECT ap.action_type, ap.operator_name, ap.operator_notes, ap.decided_at, i.title
            FROM approvals ap
            JOIN incidents i ON ap.incident_id = i.id
            WHERE i.location_id = ?
            ORDER BY ap.decided_at DESC
            LIMIT 3
        """, (location_id,))
        recent_approvals = [dict(r) for r in cursor.fetchall()]

        conn.close()

        total_previous = static_history.get("incident_count_past_24m", 0) + len(recent_runs)
        has_unresolved = len(unresolved) > 0

        # Memory impact assessment
        if has_unresolved:
            memory_context = f"WARNING: Active unresolved incident ({unresolved[0]['title']}) exists in this sector. Risk weight amplified due to accumulated ground saturation."
            history_multiplier = 1.25
        elif total_previous >= 2:
            memory_context = f"Known historical hotspot ({total_previous} recorded events). Previous major blockages documented."
            history_multiplier = 1.15
        else:
            memory_context = "No active unresolved incidents. Standard baseline historical record."
            history_multiplier = 1.0

        return {
            "location_id": location_id,
            "total_historical_events": total_previous,
            "static_baseline": static_history,
            "recent_monitoring_runs": recent_runs,
            "unresolved_incidents": unresolved,
            "has_unresolved_incidents": has_unresolved,
            "recent_human_decisions": recent_approvals,
            "history_multiplier": history_multiplier,
            "memory_summary": memory_context,
            "source": "SQLite Local Persistent State [REAL REPOSITORY DATABASE]"
        }
