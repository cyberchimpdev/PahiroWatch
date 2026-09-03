import json
import uuid
import datetime
from typing import Dict, Any, Tuple
from app.providers.weather import WeatherProvider
from app.providers.terrain import TerrainProvider
from app.providers.satellite import SatelliteProvider
from app.providers.exposure import ExposureProvider
from app.providers.memory import MemoryProvider
from app.engine.alert_generator import AlertGenerator
from app.db.database import get_db_connection

class AgentSecurityError(Exception):
    """Raised when an unauthorized consequential action is attempted."""
    pass

class ToolRegistry:
    def __init__(self):
        self.weather_provider = WeatherProvider()
        self.terrain_provider = TerrainProvider()
        self.satellite_provider = SatelliteProvider()
        self.exposure_provider = ExposureProvider()
        self.memory_provider = MemoryProvider()

    def get_weather_rainfall(self, state, time_window_hours: int = 24) -> Dict[str, Any]:
        scenario = "NORMAL"
        if state.scenario_override == "MONSOON":
            scenario = "MONSOON_BURST"
        elif state.scenario_override == "LOW_CONFIDENCE":
            scenario = "LOW_CONFIDENCE"
        elif state.scenario_override == "BAD_DAY":
            scenario = "STALE_CACHE"

        res = self.weather_provider.get_weather_rainfall(
            latitude=state.latitude,
            longitude=state.longitude,
            time_window_hours=time_window_hours,
            force_scenario=scenario
        )
        state.observations["weather"] = res
        return res

    def get_terrain_risk(self, state) -> Dict[str, Any]:
        baseline = state.baseline_slope
        if state.scenario_override == "LOW_CONFIDENCE":
            baseline = 14.0 # gentle slope for low confidence test
        
        res = self.terrain_provider.get_terrain_risk(
            latitude=state.latitude,
            longitude=state.longitude,
            baseline_slope=baseline,
            elevation=state.elevation_m
        )
        state.observations["terrain"] = res
        return res

    def get_satellite_change(self, state, simulate_failure: bool = False) -> Dict[str, Any]:
        status = "SUCCESS"
        if state.scenario_override == "MONSOON":
            if simulate_failure or state.retries_count == 0:
                state.retries_count += 1
                raise TimeoutError("Copernicus Sentinel Hub API timeout: satellite imagery processing pipeline unreachable (HTTP 504)")
            else:
                status = "HIGH_CLOUDS" # Cloud contaminated monsoon
        elif state.scenario_override == "LOW_CONFIDENCE":
            status = "NO_CHANGE"
        elif state.scenario_override == "BAD_DAY":
            raise TimeoutError("Copernicus Sentinel Hub connection refused: service unavailable (Bad Day simulation)")

        res = self.satellite_provider.get_satellite_change(
            latitude=state.latitude,
            longitude=state.longitude,
            simulate_status=status
        )
        state.observations["satellite"] = res
        return res

    def get_road_exposure(self, state) -> Dict[str, Any]:
        loc_name = state.location_name
        if state.scenario_override == "LOW_CONFIDENCE":
            loc_name = "Rural Track Remote"
        
        res = self.exposure_provider.get_road_exposure(
            latitude=state.latitude,
            longitude=state.longitude,
            location_name=loc_name
        )
        state.observations["exposure"] = res
        return res

    def get_incident_memory(self, state) -> Dict[str, Any]:
        res = self.memory_provider.get_incident_memory(state.location_id)
        state.historical_context = res
        state.observations["memory"] = res
        return res

    def create_incident_report(self, state, summary_en: str, summary_ne: str, recommended_action: str) -> Dict[str, Any]:
        incident_id = f"INC-{state.run_id[:8]}"
        state.incident_id = incident_id
        state.recommended_action = recommended_action
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO incidents 
            (id, run_id, location_id, title, status, severity, summary_en, summary_ne, recommended_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id, state.run_id, state.location_id,
            f"Active Hazard Escalation: {state.location_name}",
            "PENDING_APPROVAL",
            state.risk_level or "HIGH",
            summary_en, summary_ne, recommended_action
        ))
        conn.commit()
        conn.close()

        return {
            "incident_id": incident_id,
            "status": "PENDING_APPROVAL",
            "title": f"Active Hazard Escalation: {state.location_name}",
            "summary_en": summary_en,
            "summary_ne": summary_ne,
            "recommended_action": recommended_action
        }

    def request_human_approval(self, state, prompt: str, action_proposed: str) -> Dict[str, Any]:
        state.requires_human_approval = True
        state.approval_status = "PENDING"
        
        return {
            "checkpoint": "HUMAN_GATE_REQUIRED",
            "prompt": prompt,
            "action_proposed": action_proposed,
            "operator_target": "Ramesh, Municipal Disaster Management Officer",
            "status": "WAITING_FOR_HUMAN_APPROVAL",
            "message": "Consequential emergency alert dispatch blocked pending human operator review."
        }

    def send_alert(self, state, channel: str = "SIMULATED_SMS") -> Dict[str, Any]:
        # CRITICAL SAFETY GATE: Must verify approval in state and in SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check approval in DB
        cursor.execute("""
            SELECT id, action_type, operator_name FROM approvals
            WHERE run_id = ? AND action_type = 'APPROVE'
        """, (state.run_id,))
        approval_record = cursor.fetchone()

        if state.approval_status != "APPROVED" and not approval_record:
            conn.close()
            raise AgentSecurityError(
                "CRITICAL SECURITY VIOLATION: send_alert() failed closed. "
                "Official alert dispatch cannot execute without explicit human operator approval."
            )

        # Generate bilingual and low-bandwidth payload
        alerts = AlertGenerator.generate_alerts(
            location_name=state.location_name,
            corridor_code=state.location_id,
            risk_level=state.risk_level or "HIGH",
            risk_score=state.risk_score or 75.0,
            confidence_score=state.confidence_score or 0.70,
            rainfall_24h=state.observations.get("weather", {}).get("rainfall_24h_mm", 0.0),
            slope_deg=state.observations.get("terrain", {}).get("slope_deg", 35.0),
            recommended_action=state.recommended_action or "Ground inspection advised",
            road_distance_m=state.observations.get("exposure", {}).get("distance_to_road_m", 100.0)
        )

        action_id = f"ACT-{uuid.uuid4().hex[:8]}"
        approval_id = approval_record["id"] if approval_record else "AUTO-GATE-PASSED"

        cursor.execute("""
            INSERT INTO actions
            (id, approval_id, incident_id, action_type, channel, payload_en, payload_ne, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            action_id, approval_id, state.incident_id or f"INC-{state.run_id[:8]}",
            "EMERGENCY_DISPATCH", channel,
            alerts["payload_en"], alerts["payload_ne"], "SENT"
        ))

        # Update incident status to ACTION_DISPATCHED
        if state.incident_id:
            cursor.execute("UPDATE incidents SET status = 'ACTION_DISPATCHED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (state.incident_id,))

        conn.commit()
        conn.close()

        state.alert_sent = True
        return {
            "action_id": action_id,
            "status": "DELIVERED",
            "channel": f"{channel} [SIMULATED HIGHWAY DISPATCH]",
            "alerts": alerts,
            "disclaimer": "Simulated channel — not connected to live public telecom gateway"
        }
